import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import torch
import numpy as np
from sentence_transformers import SentenceTransformer
from compression.lattice_compress import LatticeCompressor

class RedRAG:
    """
    Red's Knowledge Brain.
    Processes and retrieves offline data using the hyper-compressed NK-PBH Lattice Compressor.
    """
    
    def __init__(self, model_name="all-MiniLM-L6-v2", db_path="knowledge/data/lattice_db.bin"):
        self.model_name = model_name
        self.db_path = db_path
        self._model = None # Lazy load
        self.lattice = LatticeCompressor(index_path=self.db_path)

    @property
    def model(self):
        if self._model is None:
            print(f"Red: Awakening Knowledge Engine ({self.model_name})...")
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def ingest_document(self, title, text):
        """Chunk, embed, and store document in the local compressed lattice DB."""
        print(f"Red: Ingesting '{title}' into compressed lattice bank...")
        
        # Simple chunking by paragraph or length
        chunks = [c.strip() for c in text.split("\n\n") if len(c.strip()) > 20]
        if not chunks:
            chunks = [text[i:i+500] for i in range(0, len(text), 500)]

        # Generate embeddings (Local CPU)
        embeddings = self.model.encode(chunks)
        
        # If the lattice has no prior PCA alignment (default zero mean), fit it on this initial ingestion
        if np.all(self.lattice.pca_mean == 0.0) and len(embeddings) >= 5:
            self.lattice.fit_pca(embeddings)
        
        # Store facts in NK-PBH format
        for chunk, emb in zip(chunks, embeddings):
            self.lattice.add_fact(
                subject=title,
                predicate="discusses",
                object_val=chunk,
                float_vector=emb
            )
            
        return f"Successfully ingested {len(chunks)} packets from '{title}' into binary lattice."

    def query(self, text_query, top_k=3):
        """Perform semantic search across local compressed knowledge graph."""
        if not self.lattice.triples:
            return "Knowledge bank is empty. Start ingestion first."

        query_emb = self.model.encode([text_query])[0]
        results = self.lattice.search(query_emb, top_k=top_k)
        
        output_results = []
        for res in results:
            output_results.append(f"[{res['subject']}] (Sim: {res['score']:.2f})\n{res['object']}")
            
        return "\n\n---\n\n".join(output_results)

if __name__ == "__main__":
    rag = RedRAG(db_path="knowledge/data/test_vector_lattice.bin")
    doc_text = (
        "SQL Injection (SQLi) is a common web attack vector that involves placing malicious SQL statements in input fields. "
        "It can lead to database leaks, authorization bypass, and complete remote server takeover."
    )
    print(rag.ingest_document("SQL Injection Guide", doc_text))
    print("\nQuerying 'How does SQL injection work?'...")
    print(rag.query("How does SQL injection work?"))
    
    # Cleanup test file
    if os.path.exists("knowledge/data/test_vector_lattice.bin"):
        os.remove("knowledge/data/test_vector_lattice.bin")
