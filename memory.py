import chromadb
from chromadb.config import Settings


class AIMAMemory:

    def __init__(self):

        self.client = chromadb.PersistentClient(
            path="./chroma_db"
        )

        self.collection = self.client.get_or_create_collection(
            name="aima_memory"
        )

        self._initialize_memory()

    def _initialize_memory(self):

        if self.collection.count() == 0:

            self.collection.add(
                ids=["1", "2", "3", "4", "5"],
                documents=[
                    "Employee requested annual leave approval.",
                    "Laptop not connecting to company VPN.",
                    "Payroll salary credit delayed.",
                    "Password reset request for HR portal.",
                    "Employee raised workplace harassment complaint."
                ],
                metadatas=[
                    {"type": "Leave"},
                    {"type": "IT"},
                    {"type": "Payroll"},
                    {"type": "IT"},
                    {"type": "HR"}
                ]
            )

    def retrieve_memory(self, query, k=3):

        try:

            result = self.collection.query(
                query_texts=[query],
                n_results=k
            )

            docs = result.get("documents", [])

            if docs and len(docs[0]) > 0:
                return docs[0]

            return ["No relevant memory found."]

        except Exception as e:

            return [f"Memory Retrieval Error: {str(e)}"]

    def save_memory(self, query, category):

        try:

            new_id = str(self.collection.count() + 100)

            self.collection.add(
                ids=[new_id],
                documents=[query],
                metadatas=[
                    {
                        "category": category
                    }
                ]
            )

            return True

        except Exception:

            return False