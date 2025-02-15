from pathlib import Path

from sentence_transformers import SentenceTransformer

if __name__ == "__main__":
    model_dir = Path("models/all-MiniLM-L6-v2")
    model_dir.mkdir(parents=True, exist_ok=True)

    print("Downloading pretrained model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    model.save(str(model_dir))
    print(f"Model saved to {model_dir}")
