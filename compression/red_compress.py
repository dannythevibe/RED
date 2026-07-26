import json
import os
import re
from collections import defaultdict

class RedCompression:
    """
    Specialized Compression & Retrieval System for Red.
    Designed to handle massive offline datasets by chunking and indexing.
    """
    
    def __init__(self, data_dir="knowledge/data", index_path="knowledge/index.json"):
        self.data_dir = data_dir
        self.index_path = index_path
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        self.index = self._load_index()

    def _load_index(self):
        if os.path.exists(self.index_path):
            with open(self.index_path, "r") as f:
                return json.load(f)
        return {"vocabulary": defaultdict(list), "files": []}

    def ingest_text(self, filename, text):
        """Process and 'compress' text into the searchable index."""
        print(f"📦 Red: Compressing {filename}...")
        
        # Simple chunking logic (500 chars)
        chunks = [text[i:i+500] for i in range(0, len(text), 500)]
        file_id = len(self.index["files"])
        self.index["files"].append({"name": filename, "chunks": chunks})
        
        # Tokenize and index
        words = set(re.findall(r'\w+', text.lower()))
        for word in words:
            if len(word) > 3: # Skip small fluff words
                self.index["vocabulary"][word].append(file_id)
        
        self._save_index()
        return f"Successfully compressed {len(chunks)} packets from {filename}."

    def search(self, query):
        """Fast offline retrieval of compressed packets."""
        query = query.lower()
        if query in self.index["vocabulary"]:
            file_ids = self.index["vocabulary"][query]
            results = []
            for fid in file_ids[:3]: # Return top 3 results
                file_info = self.index["files"][fid]
                results.append(f"Source: {file_info['name']}\nContent: {file_info['chunks'][0]}...")
            return "\n\n".join(results)
        return "I haven't compressed that knowledge yet."

    def _save_index(self):
        with open(self.index_path, "w") as f:
            json.dump(self.index, f)

if __name__ == "__main__":
    rc = RedCompression()
    # rc.ingest_text("Wikipedia_Sample.txt", "Cybersecurity is the practice of protecting systems...")
    # print(rc.search("cybersecurity"))
