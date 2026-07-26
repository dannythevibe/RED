import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from knowledge.red_rag import RedRAG
from polymath_core.academy import PolymathAcademy

def ingest_core_academy():
    print("--- Ingesting Core Academy Curriculum into Lattice Database ---")
    
    # Initialize RAG Engine
    db_path = "knowledge/data/lattice_db.bin"
    
    # Delete old database if we want a fresh start
    if os.path.exists(db_path):
        print(f"Removing old database: {db_path} for a fresh import...")
        os.remove(db_path)
        
    rag = RedRAG(db_path=db_path)
    academy = PolymathAcademy()
    
    # 1. Ingest Curriculum Lessons
    for key, item in academy.curriculum.items():
        title = item["title"]
        content = f"Lesson Content:\n{item['lesson']}\n\nPolymath Challenge:\n{item['challenge']}"
        print(f"Ingesting Lesson: {title}...")
        result = rag.ingest_document(title, content)
        print(result)
        
    # 2. Ingest Handbook Operational Guides
    for key, item in academy.handbook.items():
        title = item["title"]
        content = f"Operational Guide / Steps:\n" + "\n".join(item["steps"])
        print(f"Ingesting Guide: {title}...")
        result = rag.ingest_document(title, content)
        print(result)
        
    print("\n--- Ingestion Complete. Verifying retrieval... ---")
    query_result = rag.query("How do I practice 3:4 polyrhythms?")
    print("Test Query: 'How do I practice 3:4 polyrhythms?'")
    print(query_result)
    
if __name__ == "__main__":
    ingest_core_academy()
