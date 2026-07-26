import os
import json
import numpy as np
import zlib

try:
    import zstandard as zstd
    HAS_ZSTD = True
except ImportError:
    HAS_ZSTD = False

# Global precomputed Popcount Table for all 256 byte values
POPCOUNT_TABLE = np.array([bin(i).count("1") for i in range(256)], dtype=np.uint8)

class LatticeCompressor:
    """
    NK-PBH (Neural Knowledge Graph + PCA Binary Hashing) Extreme Compression Engine.
    Compresses high-dimensional float32 vector embeddings to 128-bit (16-byte) binary signatures via PCA,
    and stores knowledge graph facts as 10-byte integer triples.
    """
    
    def __init__(self, index_path="knowledge/data/lattice_db.bin"):
        self.index_path = index_path
        
        # Knowledge Graph Dictionary
        self.entity_to_id = {}
        self.id_to_entity = []
        self.predicate_to_id = {}
        self.id_to_predicate = []
        
        # Graph Triples: list of tuples (sub_id, pred_id, obj_id)
        self.triples = []
        
        # Packed binary vector search database: NumPy uint8 array of shape (N, 16)
        self.binary_vectors = None
        
        # PCA matrix: 384 dimensions to 128 dimensions
        self.pca_mean = None
        self.pca_components = None
        
        # Initialize default random orthogonal projection matrix until PCA is fitted
        self._init_default_pca()
        
        # Load database if it exists
        self._load_database()

    def _init_default_pca(self):
        """Initializes a deterministic pseudo-random orthogonal projection matrix as default."""
        state = np.random.RandomState(42)  # Deterministic seed
        # Generate random matrix (384, 128)
        Q, _ = np.linalg.qr(state.normal(0, 1, (384, 128)))
        self.pca_components = Q.astype(np.float32)
        self.pca_mean = np.zeros(384, dtype=np.float32)

    def fit_pca(self, embeddings):
        """
        Fits PCA on a representative sample of float32 embeddings to align binarization dimensions
        with the highest directions of variance.
        """
        X = np.array(embeddings, dtype=np.float32)
        if len(X) < 10:
            print("LatticeCompressor: Not enough samples to fit PCA (< 10). Keeping current projection.")
            return
            
        self.pca_mean = np.mean(X, axis=0)
        X_centered = X - self.pca_mean
        
        # Covariance matrix
        cov = np.cov(X_centered, rowvar=False)
        
        # Eigen decomposition
        eigenvalues, eigenvectors = np.linalg.eigh(cov)
        
        # Sort descending
        idx = np.argsort(eigenvalues)[::-1]
        eigenvectors = eigenvectors[:, idx]
        
        # Select top 128 dimensions
        self.pca_components = eigenvectors[:, :128].astype(np.float32)
        print(f"LatticeCompressor: Trained and updated PCA components on {len(embeddings)} vectors.")

    def binarize_vector(self, float_vector):
        """
        Projects a 384-dimensional vector to 128-dimensions via PCA and sign-binarizes to 16 bytes.
        """
        v = np.array(float_vector, dtype=np.float32)
        v_centered = v - self.pca_mean
        v_proj = np.dot(v_centered, self.pca_components)
        
        # Sign binarization: bit is 1 if component > 0, else 0
        binary_bools = v_proj > 0.0
        packed = np.packbits(binary_bools)
        return packed

    def _load_database(self):
        """Loads database from its custom binary format."""
        if not os.path.exists(self.index_path):
            return
            
        try:
            with open(self.index_path, "rb") as f:
                # 1. Check Magic bytes
                magic = f.read(4)
                if magic != b"LTC\x01":
                    print("LatticeCompressor: Invalid file format.")
                    return
                
                # 2. Read counts
                num_facts = int.from_bytes(f.read(4), byteorder='big')
                dict_size = int.from_bytes(f.read(4), byteorder='big')
                
                if num_facts == 0:
                    return
                
                # 3. Read PCA mean and components
                self.pca_mean = np.frombuffer(f.read(384 * 4), dtype=np.float32).copy()
                self.pca_components = np.frombuffer(f.read(384 * 128 * 4), dtype=np.float32).reshape(384, 128).copy()
                
                # 4. Read binary vectors: (num_facts, 16)
                vector_bytes = f.read(num_facts * 16)
                self.binary_vectors = np.frombuffer(vector_bytes, dtype=np.uint8).reshape(num_facts, 16).copy()
                
                # 5. Read triples: (num_facts, 10)
                triple_bytes = f.read(num_facts * 10)
                
                self.triples = []
                for i in range(num_facts):
                    offset = i * 10
                    sub_id = int.from_bytes(triple_bytes[offset:offset+4], byteorder='big')
                    pred_id = int.from_bytes(triple_bytes[offset+4:offset+6], byteorder='big')
                    obj_id = int.from_bytes(triple_bytes[offset+6:offset+10], byteorder='big')
                    self.triples.append((sub_id, pred_id, obj_id))
                
                # 6. Read compressed dictionary JSON payload
                compressed_dict = f.read()
                if HAS_ZSTD:
                    decompressor = zstd.ZstdDecompressor()
                    dict_bytes = decompressor.decompress(compressed_dict)
                else:
                    dict_bytes = zlib.decompress(compressed_dict)
                    
                dict_data = json.loads(dict_bytes.decode('utf-8'))
                self.entity_to_id = dict_data.get("entity_to_id", {})
                self.id_to_entity = dict_data.get("id_to_entity", [])
                self.predicate_to_id = dict_data.get("predicate_to_id", {})
                self.id_to_predicate = dict_data.get("id_to_predicate", [])
                
                print(f"LatticeCompressor: Loaded {num_facts} facts from binary index.")
        except Exception as e:
            print(f"LatticeCompressor: Failed to load database: {e}")

    def save_database(self):
        """Saves current database state into the custom binary format."""
        if not self.triples or self.binary_vectors is None:
            return
            
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        try:
            with open(self.index_path, "wb") as f:
                # 1. Magic bytes
                f.write(b"LTC\x01")
                
                # 2. Write counts
                num_facts = len(self.triples)
                f.write(num_facts.to_bytes(4, byteorder='big'))
                dict_size = len(self.id_to_entity)
                f.write(dict_size.to_bytes(4, byteorder='big'))
                
                # 3. Write PCA metadata
                f.write(self.pca_mean.tobytes())
                f.write(self.pca_components.tobytes())
                
                # 4. Write binary vectors
                f.write(self.binary_vectors.tobytes())
                
                # 5. Write triples: 10 bytes per fact (uint32, uint16, uint32)
                for sub, pred, obj in self.triples:
                    f.write(sub.to_bytes(4, byteorder='big'))
                    f.write(pred.to_bytes(2, byteorder='big'))
                    f.write(obj.to_bytes(4, byteorder='big'))
                
                # 6. Compress and write dictionaries
                dict_data = {
                    "entity_to_id": self.entity_to_id,
                    "id_to_entity": self.id_to_entity,
                    "predicate_to_id": self.predicate_to_id,
                    "id_to_predicate": self.id_to_predicate
                }
                dict_json = json.dumps(dict_data).encode('utf-8')
                if HAS_ZSTD:
                    compressor = zstd.ZstdCompressor(level=15)
                    compressed = compressor.compress(dict_json)
                else:
                    compressed = zlib.compress(dict_json, level=9)
                f.write(compressed)
                
        except Exception as e:
            print(f"LatticeCompressor: Failed to save database: {e}")

    def get_or_create_entity(self, name):
        name = name.strip()
        if name not in self.entity_to_id:
            self.entity_to_id[name] = len(self.id_to_entity)
            self.id_to_entity.append(name)
        return self.entity_to_id[name]

    def get_or_create_predicate(self, name):
        name = name.strip()
        if name not in self.predicate_to_id:
            self.predicate_to_id[name] = len(self.id_to_predicate)
            self.id_to_predicate.append(name)
        return self.predicate_to_id[name]

    def add_fact(self, subject, predicate, object_val, float_vector):
        """Ingests fact, binarizes its embedding, and saves to database."""
        sub_id = self.get_or_create_entity(subject)
        pred_id = self.get_or_create_predicate(predicate)
        obj_id = self.get_or_create_entity(object_val)
        
        self.triples.append((sub_id, pred_id, obj_id))
        
        bin_vec = self.binarize_vector(float_vector)
        if self.binary_vectors is None:
            self.binary_vectors = bin_vec.reshape(1, 16)
        else:
            self.binary_vectors = np.vstack([self.binary_vectors, bin_vec])
            
        self.save_database()
        return len(self.triples) - 1

    def search(self, query_float_vector, top_k=3):
        """
        Dynamic Popcount-optimized search.
        Projects and binarizes query embedding, then scans index using POPCOUNT_TABLE.
        """
        if self.binary_vectors is None or not self.triples:
            return []
            
        # 1. Binarize query vector
        query_bin = self.binarize_vector(query_float_vector)
        
        # 2. Vectorized Hamming distance in NumPy
        xor_result = np.bitwise_xor(self.binary_vectors, query_bin)
        
        # Count set bits using global lookup table
        hamming_distances = POPCOUNT_TABLE[xor_result].sum(axis=1)
        
        # 3. Sort by lowest Hamming distance
        top_indices = np.argsort(hamming_distances)[:top_k]
        
        results = []
        for idx in top_indices:
            sub_id, pred_id, obj_id = self.triples[idx]
            sub = self.id_to_entity[sub_id]
            pred = self.id_to_predicate[pred_id]
            obj = self.id_to_entity[obj_id]
            
            dist = hamming_distances[idx]
            score = (128.0 - dist) / 128.0
            
            results.append({
                "subject": sub,
                "predicate": pred,
                "object": obj,
                "score": float(score)
            })
            
        return results

if __name__ == "__main__":
    print("--- Testing NK-PBH Lattice Compression Engine ---")
    
    # 1. Instantiate
    compressor = LatticeCompressor(index_path="knowledge/data/test_lattice.bin")
    
    # Generate random 384-dimensional mock embeddings to fit PCA
    np.random.seed(42)
    sample_embeddings = np.random.uniform(-1, 1, (50, 384))
    compressor.fit_pca(sample_embeddings)
    
    # Ingest facts
    print("Ingesting test facts...")
    compressor.add_fact("SQL Injection", "is_a", "web vulnerability", sample_embeddings[0])
    compressor.add_fact("Polyrhythms", "define", "conflicting musical rhythms", sample_embeddings[1])
    compressor.add_fact("Glassmorphism", "style", "frosted glass UI layout", sample_embeddings[2])
    
    # Search
    query = sample_embeddings[2] + np.random.normal(0, 0.05, 384)
    results = compressor.search(query, top_k=2)
    print(f"Search Results: {results}")
    
    # Clean up
    if os.path.exists("knowledge/data/test_lattice.bin"):
        os.remove("knowledge/data/test_lattice.bin")
