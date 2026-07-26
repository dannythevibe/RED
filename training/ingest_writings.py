import os
from docx import Document

def extract_writings(directory, output_file="training/personal/cupids_arrow_synthesis.txt"):
    """Extract text from all docx files in the specified directory."""
    full_text = []
    
    if not os.path.exists(directory):
        return f"Directory {directory} not found."

    for filename in os.listdir(directory):
        if filename.endswith(".docx"):
            print(f"Red: Extracting {filename}...")
            try:
                doc = Document(os.path.join(directory, filename))
                full_text.append(f"--- SOURCE: {filename} ---")
                for para in doc.paragraphs:
                    full_text.append(para.text)
            except Exception as e:
                print(f"Error reading {filename}: {e}")

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(full_text))
    
    return f"Successfully synthesized {len(full_text)} segments into {output_file}."

if __name__ == "__main__":
    src = r"c:\Users\Danny's PC\OneDrive\Documents\CUPID'S ARROW"
    print(extract_writings(src))
