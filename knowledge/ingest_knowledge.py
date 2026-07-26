import os
from knowledge.red_rag import RedRAG

def ingest():
    rag = RedRAG()
    
    # You can point this to a directory of .txt files or just add topics here
    # Example: Add a specific technical topic
    print("📚 Red: Ready for knowledge ingestion.")
    
    while True:
        title = input("Enter Topic Title (or 'exit' to stop): ")
        if title.lower() == 'exit':
            break
        
        # In a real scenario, you could also read from a file here
        content_path = input("Enter path to text file (or type content directly): ")
        
        if os.path.exists(content_path):
            with open(content_path, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            content = content_path # Assume direct input if path doesn't exist

        result = rag.ingest_document(title, content)
        print(f"✅ {result}")

if __name__ == "__main__":
    ingest()
