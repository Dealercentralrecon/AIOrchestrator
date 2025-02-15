from pathlib import Path

import numpy as np
import onnxruntime as ort
from sentence_transformers import SentenceTransformer


class VectorEngine:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.onnx_path = Path(f"models/{model_name}.onnx")
        self.ort_session = self._convert_to_onnx()

    def _convert_to_onnx(self):
        if not self.onnx_path.exists():
            self.onnx_path.parent.mkdir(exist_ok=True, parents=True)
            dummy_input = ["conversion example"]
            self.model.save_as_onnx(str(self.onnx_path), dummy_input)
        return ort.InferenceSession(str(self.onnx_path))

    def generate_embedding(self, text: str) -> np.ndarray:
        input_features = self.model.tokenize([text])
        onnx_input = {
            self.ort_session.get_inputs()[0].name: input_features["input_ids"],
            self.ort_session.get_inputs()[1].name: input_features["attention_mask"],
        }
        return self.ort_session.run(None, onnx_input)[0][0]
