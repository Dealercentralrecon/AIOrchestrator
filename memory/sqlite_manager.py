import numpy as np
from sqlalchemy import JSON, Column, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .embeddings import VectorEngine

Base = declarative_base()


class CodeSolution(Base):
    __tablename__ = "code_solutions"
    id = Column(Integer, primary_key=True)
    task_hash = Column(String(64), unique=True)
    code = Column(Text)
    embeddings = Column(JSON)  # Storing as JSON for ONNX/TFLite compatibility
    dependencies = Column(JSON)
    success_metrics = Column(JSON)


class MemoryManager:
    def __init__(self, db_path="ai_memory.db"):
        self.engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.vector_engine = VectorEngine()

    def store_solution(self, task_hash, code):
        embedding = self.vector_engine.generate_embedding(code)
        session = self.Session()
        solution = CodeSolution(
            task_hash=task_hash, code=code, embeddings=embedding.tolist()
        )
        session.add(solution)
        session.commit()

    def retrieve_similar(self, code_snippet, threshold=0.8):
        query_embedding = self.vector_engine.generate_embedding(code_snippet)
        session = self.Session()
        solutions = session.query(CodeSolution).all()
        return [
            sol
            for sol in solutions
            if self._cosine_similarity(query_embedding, np.array(sol.embeddings))
            > threshold
        ]

    def _cosine_similarity(self, a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
