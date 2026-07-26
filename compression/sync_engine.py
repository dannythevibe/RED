import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import urllib.request
import zlib
from compression.lattice_compress import LatticeCompressor

try:
    import zstandard as zstd
    HAS_ZSTD = True
except ImportError:
    HAS_ZSTD = False

class LatticeSyncEngine:
    """
    Syncs the local offline knowledge base (lattice_db.bin) with a remote endpoint.
    Downloads compressed delta packages containing new facts/embeddings and applies them in-place.
    """
    
    def __init__(self, compressor: LatticeCompressor):
        self.compressor = compressor

    def check_for_updates(self, check_url):
        """
        Sends the count of local facts to a remote check URL.
        Returns a dict containing update availability and metadata.
        """
        try:
            local_fact_count = len(self.compressor.triples)
            # Query remote registry with local version info
            url = f"{check_url}?local_count={local_fact_count}"
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'RED-Sync-Engine/1.0'}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                meta = json.loads(response.read().decode('utf-8'))
                return meta
        except Exception as e:
            print(f"LatticeSyncEngine: Failed to query update endpoint: {e}")
            return {"update_available": False, "error": str(e)}

    def apply_delta_patch(self, delta_data):
        """
        Applies a delta patch in-place to the local database.
        `delta_data` is a dictionary containing:
        - "new_triples": list of list/tuple of [sub_str, pred_str, obj_str]
        - "new_embeddings": list of list of floats (matching the number of new triples)
        """
        try:
            new_triples = delta_data.get("new_triples", [])
            new_embeddings = delta_data.get("new_embeddings", [])
            
            if not new_triples or not new_embeddings:
                print("LatticeSyncEngine: Empty delta patch received.")
                return 0
                
            if len(new_triples) != len(new_embeddings):
                print("LatticeSyncEngine: Mismatched triples and embeddings count in delta patch.")
                return 0

            print(f"LatticeSyncEngine: Applying {len(new_triples)} new facts to binary index...")
            
            added_count = 0
            for (sub, pred, obj), emb in zip(new_triples, new_embeddings):
                self.compressor.add_fact(
                    subject=sub,
                    predicate=pred,
                    object_val=obj,
                    float_vector=emb
                )
                added_count += 1
                
            self.compressor.save_database()
            print(f"LatticeSyncEngine: Sync completed successfully. Synced {added_count} records.")
            return added_count
            
        except Exception as e:
            print(f"LatticeSyncEngine: Failed to apply delta patch: {e}")
            return 0

if __name__ == "__main__":
    print("==================================================")
    print("          RED LATTICE DATABASE SYNC ENGINE        ")
    print("==================================================")
    
    # 1. Determine database path
    # Look for database in local directory or execution folder
    db_path = "knowledge/data/lattice_db.bin"
    if not os.path.exists(db_path):
        # Check inside dist/RED_DIST/_internal
        alt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "knowledge", "data", "lattice_db.bin")
        if os.path.exists(alt_path):
            db_path = alt_path
        else:
            # Check current working directory
            db_path = "lattice_db.bin"
            
    print(f"[*] Target Database: {os.path.abspath(db_path)}")
    
    if not os.path.exists(db_path):
        print("[!] Error: No database found to update. Run ingest_academy.py first.")
        input("\nPress Enter to exit...")
        sys.exit(1)
        
    compressor = LatticeCompressor(index_path=db_path)
    print(f"[*] Loaded {len(compressor.triples)} existing facts.")
    
    sync_engine = LatticeSyncEngine(compressor)
    
    # 2. Check for manual local patch file fallback
    local_patch_file = "lattice_update.json"
    if os.path.exists(local_patch_file):
        print(f"[*] Found local patch file: {local_patch_file}")
        try:
            with open(local_patch_file, "r") as f:
                patch_data = json.load(f)
            applied = sync_engine.apply_delta_patch(patch_data)
            if applied > 0:
                print(f"[+] Sync successful! Applied {applied} new facts to local database.")
                # Move/Delete local patch file so it doesn't run again
                os.rename(local_patch_file, local_patch_file + ".applied")
                print(f"[*] Renamed patch file to {local_patch_file}.applied")
            else:
                print("[-] No new facts were applied.")
        except Exception as e:
            print(f"[!] Failed to parse or apply local patch: {e}")
            
    else:
        # 3. Check remote updates endpoint
        default_url = "http://127.0.0.1:5000/updates"
        print(f"[*] Querying update server at: {default_url}")
        meta = sync_engine.check_for_updates(default_url)
        
        if meta.get("update_available"):
            print("[+] Update found! Downloading delta package...")
            # In a live setup, the server sends the delta package back.
            # We fetch from update payload
            delta_url = meta.get("delta_url")
            try:
                with urllib.request.urlopen(delta_url, timeout=10) as response:
                    delta_data = json.loads(response.read().decode('utf-8'))
                applied = sync_engine.apply_delta_patch(delta_data)
                print(f"[+] Applied {applied} new facts.")
            except Exception as e:
                print(f"[!] Failed to fetch delta payload: {e}")
        else:
            err = meta.get("error")
            if err:
                print(f"[-] Sync server offline or unreachable (Error: {err})")
                print("[*] Tip: Place a 'lattice_update.json' file in this folder to apply manual offline updates.")
            else:
                print("[+] Database is already up to date. No updates needed.")
                
    print("\n[+] Sync execution completed.")
    input("Press Enter to exit...")
