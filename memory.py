import chromadb
from chromadb.config import Settings
import uuid

class AIMAMemory:

    def __init__(self):
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client.get_or_create_collection(
            name="aima_memory"
        )
        self._initialize_memory()

    def _initialize_memory(self):
        # Seed rich knowledge base if empty or missing initial docs
        if self.collection.count() < 5:
            seed_kb = [
                (
                    "kb_1",
                    "VPN Gateway 504 Timeout Resolution Playbook: Check RADIUS auth server thread pool. Restart container `docker restart radius-auth`. Check load balancer connection limits.",
                    {"title": "VPN Outage Troubleshooting", "category": "IT Support", "type": "Playbook"}
                ),
                (
                    "kb_2",
                    "Payroll Salary Delay Resolution Protocol: If direct deposit is missing, verify ACH batch release log in Finance portal. Run payroll reconciliation script `python reconcile_payroll.py`.",
                    {"title": "Payroll Discrepancy Guide", "category": "Payroll", "type": "Protocol"}
                ),
                (
                    "kb_3",
                    "Workday HR Leave Request Sync Procedure: If annual leave status is stuck in Pending status, trigger manual webhook endpoint `/api/hr/sync-leave` and notify department supervisor.",
                    {"title": "Leave Approval Workday Sync", "category": "Leave Request", "type": "SOP"}
                ),
                (
                    "kb_4",
                    "Phishing & Mailbox Spoofing Emergency Defense: Quarantine malicious domain at gateway firewall. Extract recipient headers and run Exchange PowerShell purge rule `Search-Mailbox -DeleteContent`.",
                    {"title": "Phishing Incident Playbook", "category": "Security", "type": "SecOps Playbook"}
                ),
                (
                    "kb_5",
                    "Workplace Harassment & Confidential HR Grievance Handling: All complaints involving managers must be immediately routed to HR Ethics Committee under Confidential Protocol CP-9.",
                    {"title": "HR Confidential Grievance SOP", "category": "HR Issue", "type": "Policy"}
                ),
                (
                    "kb_6",
                    "SSO & Password Reset Self-Service Failure: Clear browser cookies and test SAML assertion in Okta admin dashboard. Force sync user Active Directory state.",
                    {"title": "Password & SSO Access SOP", "category": "IT Support", "type": "SOP"}
                ),
                (
                    "kb_7",
                    "PostgreSQL Database Connection Pool Exhaustion: Scale PgBouncer pool count from 50 to 200 connection slots. Kill long-running idle backend queries.",
                    {"title": "DB Connection Outage Playbook", "category": "IT Support", "type": "Playbook"}
                ),
                (
                    "kb_8",
                    "AWS EC2 Instance Out of Memory (OOM) Crash: Run `free -m` and inspect kernel log `/var/log/messages`. Restart app worker processes and upgrade instance family.",
                    {"title": "Server Infrastructure Crash SOP", "category": "IT Support", "type": "Playbook"}
                )
            ]
            
            ids = [item[0] for item in seed_kb]
            docs = [item[1] for item in seed_kb]
            metas = [item[2] for item in seed_kb]
            
            self.collection.add(
                ids=ids,
                documents=docs,
                metadatas=metas
            )

    def retrieve_memory(self, query, k=3):
        try:
            result = self.collection.query(
                query_texts=[query],
                n_results=min(k, max(1, self.collection.count()))
            )

            docs = result.get("documents", [])
            metas = result.get("metadatas", [])
            distances = result.get("distances", [])

            formatted_results = []
            if docs and len(docs[0]) > 0:
                for idx, doc in enumerate(docs[0]):
                    meta = metas[0][idx] if metas and len(metas[0]) > idx else {}
                    dist = distances[0][idx] if distances and len(distances[0]) > idx else 0.0
                    similarity = max(0.0, round(100 * (1.0 - (dist / 2.0)), 1)) if dist else 90.0
                    formatted_results.append({
                        "document": doc,
                        "title": meta.get("title", "KB Record"),
                        "category": meta.get("category", "General"),
                        "type": meta.get("type", "Memory"),
                        "similarity": f"{similarity}%"
                    })
                return formatted_results

            return [{"document": "No matching knowledge base records found.", "title": "N/A", "category": "N/A", "type": "N/A", "similarity": "0%"}]

        except Exception as e:
            return [{"document": f"Memory Retrieval Error: {str(e)}", "title": "Error", "category": "N/A", "type": "N/A", "similarity": "0%"}]

    def save_memory(self, document, category="General", metadata=None):
        try:
            doc_id = f"mem_{uuid.uuid4().hex[:8]}"
            meta = metadata or {}
            meta["category"] = category
            meta["type"] = "Incident Resolution History"

            self.collection.add(
                ids=[doc_id],
                documents=[document],
                metadatas=[meta]
            )
            return True
        except Exception:
            return False

    def get_all_documents(self):
        try:
            data = self.collection.get()
            docs = data.get("documents", [])
            metas = data.get("metadatas", [])
            ids = data.get("ids", [])
            
            records = []
            for idx in range(len(ids)):
                meta = metas[idx] if idx < len(metas) else {}
                records.append({
                    "id": ids[idx],
                    "title": meta.get("title", meta.get("category", "Knowledge Base")),
                    "category": meta.get("category", "General"),
                    "type": meta.get("type", "Memory"),
                    "content": docs[idx]
                })
            return records
        except Exception:
            return []

    def add_kb_article(self, title, content, category, doc_type="Knowledge Base"):
        try:
            doc_id = f"kb_{uuid.uuid4().hex[:8]}"
            meta = {
                "title": title,
                "category": category,
                "type": doc_type
            }
            self.collection.add(
                ids=[doc_id],
                documents=[content],
                metadatas=[meta]
            )
            return True
        except Exception:
            return False