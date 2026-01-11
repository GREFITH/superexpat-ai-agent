import json
import uuid
from typing import List, Dict, Any

import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer

from app.config import settings


class VectorStore:
    def __init__(self):
        self.embedding_model = SentenceTransformer(settings.embedding_model)

        self.client = chromadb.PersistentClient(
            path=settings.vector_db_path,
            settings=ChromaSettings(anonymized_telemetry=False)
        )

        self.collection = self.client.get_or_create_collection(
            name=settings.collection_name
        )

    @staticmethod
    def _sanitize_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
        clean = {}
        for key, value in metadata.items():
            if isinstance(value, list):
                clean[key] = ", ".join(map(str, value))
            elif isinstance(value, (str, int, float, bool)):
                clean[key] = value
            else:
                clean[key] = str(value)
        return clean

    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        if not documents:
            return

        texts, metadatas, ids = [], [], []

        for doc in documents:
            texts.append(doc["content"])
            metadatas.append(self._sanitize_metadata(doc.get("metadata", {})))
            ids.append(str(uuid.uuid4()))

        embeddings = self.embedding_model.encode(texts).tolist()

        self.collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )

    def load_from_json(self, path: str) -> None:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        documents = []
        for item in data.get("documents", []):
            documents.append({
                "content": item["content"],
                "metadata": {
                    "category": item.get("category", "general"),
                    **item.get("metadata", {})
                }
            })

        self.add_documents(documents)

    def search(self, query: str, top_k: int = 5):
        embedding = self.embedding_model.encode(query).tolist()

        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k
        )

        response = []
        for i in range(len(results["documents"][0])):
            response.append({
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "score": results["distances"][0][i]
            })

        return response


# ✅ SINGLETON INSTANCE (CRITICAL)
vector_store = VectorStore()
