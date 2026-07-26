import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from datasets import load_dataset

# === Configuration ===
MODEL_ID = "gpt2"  # Change to a larger model (e.g., "meta-llama/Llama-3.2-1B-Instruct") for better results
DATASET_PATH = "data/red_dataset.jsonl"
OUTPUT_DIR = "../models/red-custom-v1"

def train():
    print(f"[TRAIN] Initializing training for Red using {MODEL_ID}...")
    
    # Check for GPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[DEVICE] Training on: {device.upper()}")
    if device == "cpu":
        print("[WARNING] CPU training will be extremely slow. A GPU is highly recommended.")

    # Load Tokenizer & Model
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID).to(device)

    # Load Dataset
    dataset = load_dataset("json", data_files=DATASET_PATH, split="train")

    def tokenize_function(examples):
        text = [f"### Instruction: {i}\n### Response: {o}" for i, o in zip(examples["instruction"], examples["output"])]
        return tokenizer(text, truncation=True, padding="max_length", max_length=512)

    tokenized_dataset = dataset.map(tokenize_function, batched=True)

    # Training Arguments
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        num_train_epochs=3,
        learning_rate=2e-5,
        logging_steps=10,
        save_steps=100,
        evaluation_strategy="no",
        fp16=torch.cuda.is_available(),
    )

    # Initialize Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
    )

    # Start Training
    print("[TRAIN] Starting training...")
    trainer.train()
    
    # Save the custom model
    print(f"[SAVE] Saving model to {OUTPUT_DIR}...")
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

if __name__ == "__main__":
    # Check for missing dependencies
    try:
        import datasets
    except ImportError:
        print("[ERROR] Missing dependency: 'datasets'. Run: pip install datasets")
        exit(1)
        
    train()
