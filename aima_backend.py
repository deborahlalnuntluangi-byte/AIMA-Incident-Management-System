from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from memory import AIMAMemory
from tools import priority_calculator_tool, routing_tool, root_cause_analyzer_tool, ticket_creator_tool

memory = AIMAMemory()

class AgentState(TypedDict):
    user_query: str
    reporter: str
    memory_context: List[dict]
    classification: str
    priority: str
    sla_due: str
    blast_radius: str
    assigned_team: str
    escalation_path: str
    root_cause: str
    recommended_action: str
    created_ticket_id: str
    reasoning_trace: List[str]
    final_response: str


def retrieve_memory(state: AgentState) -> AgentState:
    query = state["user_query"]
    memory_records = memory.retrieve_memory(query, k=3)
    state["memory_context"] = memory_records
    
    match_str = ", ".join([f"'{m['title']}' ({m['similarity']})" for m in memory_records if m['title'] != 'N/A'])
    if not match_str:
        match_str = "None (New Incident Pattern)"
        
    state["reasoning_trace"].append(
        f"Node 1: Vector RAG Memory Retrieved -> Matches: {match_str}"
    )
    return state


def classify_incident(state: AgentState) -> AgentState:
    query = state["user_query"].lower()

    if any(w in query for w in ["phishing", "breach", "security", "hacked", "malware", "virus", "unauthorized"]):
        category = "Security"
    elif any(w in query for w in ["leave", "vacation", "pto", "holiday"]):
        category = "Leave Request"
    elif any(w in query for w in ["salary", "payroll", "paystub", "pay", "compensation", "tax"]):
        category = "Payroll"
    elif any(w in query for w in ["vpn", "laptop", "password", "portal", "system", "wifi", "network", "server", "error", "crash", "db", "database"]):
        category = "IT Support"
    elif any(w in query for w in ["harassment", "complaint", "manager", "policy", "benefit", "hr", "grievance"]):
        category = "HR Issue"
    else:
        category = "General Inquiry"

    state["classification"] = category
    state["reasoning_trace"].append(
        f"Node 2: Incident Classified -> Category: {category}"
    )
    return state


def calculate_priority(state: AgentState) -> AgentState:
    prio_res = priority_calculator_tool.invoke(state["user_query"])
    
    state["priority"] = prio_res["priority"]
    state["sla_due"] = prio_res["sla_due"]
    state["blast_radius"] = prio_res["blast_radius"]

    state["reasoning_trace"].append(
        f"Node 3: Priority & SLA Calculated -> Priority: {prio_res['priority']} (SLA Due: {prio_res['sla_due']})"
    )
    return state


def route_and_assign(state: AgentState) -> AgentState:
    route_res = routing_tool.invoke({
        "category": state["classification"],
        "priority": state["priority"]
    })
    
    state["assigned_team"] = route_res["assigned_team"]
    state["escalation_path"] = route_res["escalation_path"]

    state["reasoning_trace"].append(
        f"Node 4: Team Assignment Routed -> Assigned Team: {route_res['assigned_team']} (Escalation: {route_res['escalation_path']})"
    )
    return state


def root_cause_analysis(state: AgentState) -> AgentState:
    # Summarize memory context for analyzer tool
    mem_summary = " ".join([m["document"] for m in state["memory_context"] if "document" in m])
    
    rca_res = root_cause_analyzer_tool.invoke({
        "query": state["user_query"],
        "category": state["classification"],
        "memory_context": mem_summary
    })

    state["root_cause"] = rca_res["root_cause"]
    state["recommended_action"] = rca_res["recommended_action"]

    state["reasoning_trace"].append(
        "Node 5: Root Cause & Mitigation Plan Generated"
    )
    return state


def generate_response(state: AgentState) -> AgentState:
    query = state["user_query"]
    category = state["classification"]
    priority = state["priority"]
    team = state["assigned_team"]
    root_cause = state["root_cause"]
    actions = state["recommended_action"]
    memories = state["memory_context"]

    mem_bullets = ""
    for m in memories:
        if m.get("title") != "N/A":
            mem_bullets += f"- [{m['type']}] **{m['title']}** (Relevance: {m['similarity']})\n  {m['document']}\n"
    if not mem_bullets:
        mem_bullets = "- No relevant historical incidents found in ChromaDB.\n"

    response = f"""
### ⚡ AIMA Incident Assessment Summary

**Incident Description:**  
{query}

---

#### 📌 Classification & Assignment
* **Category:** `{category}`
* **Priority Level:** `{priority}`
* **Assigned Team:** `{team}`
* **SLA Target Due:** `{state['sla_due']}`
* **Blast Radius:** `{state['blast_radius']}`

---

#### 🔍 Suspected Root Cause Diagnostic
{root_cause}

---

#### 🛠 Recommended Action Plan
{actions}

---

#### 🧠 Vector RAG Knowledge Context
{mem_bullets}
"""
    state["final_response"] = response
    state["reasoning_trace"].append(
        "Node 6: Executive Incident Report Formatted"
    )
    return state


def create_ticket_node(state: AgentState) -> AgentState:
    title = state["user_query"][:60] + "..." if len(state["user_query"]) > 60 else state["user_query"]
    reporter = state.get("reporter", "Employee User")
    
    ticket_id = ticket_creator_tool.invoke({
        "title": title,
        "description": state["user_query"],
        "reporter": reporter,
        "category": state["classification"],
        "priority": state["priority"],
        "assigned_team": state["assigned_team"],
        "sla_due": state["sla_due"],
        "root_cause": state["root_cause"],
        "recommended_action": state["recommended_action"],
        "ai_reasoning": " -> ".join(state["reasoning_trace"])
    })
    
    state["created_ticket_id"] = ticket_id
    state["reasoning_trace"].append(
        f"Node 7: Ticket Logged to Database -> Ticket ID: {ticket_id}"
    )
    return state


def save_memory_node(state: AgentState) -> AgentState:
    doc_to_save = f"Incident: {state['user_query']} | Category: {state['classification']} | Resolution: {state['root_cause']}"
    memory.save_memory(
        document=doc_to_save,
        category=state["classification"],
        metadata={
            "ticket_id": state["created_ticket_id"],
            "priority": state["priority"]
        }
    )
    state["reasoning_trace"].append(
        "Node 8: Resolution Vector Saved to ChromaDB Memory"
    )
    return state


# Build LangGraph Workflow
builder = StateGraph(AgentState)

builder.add_node("retrieve_memory", retrieve_memory)
builder.add_node("classify_incident", classify_incident)
builder.add_node("calculate_priority", calculate_priority)
builder.add_node("route_and_assign", route_and_assign)
builder.add_node("root_cause_analysis", root_cause_analysis)
builder.add_node("generate_response", generate_response)
builder.add_node("create_ticket", create_ticket_node)
builder.add_node("save_memory", save_memory_node)

builder.set_entry_point("retrieve_memory")

builder.add_edge("retrieve_memory", "classify_incident")
builder.add_edge("classify_incident", "calculate_priority")
builder.add_edge("calculate_priority", "route_and_assign")
builder.add_edge("route_and_assign", "root_cause_analysis")
builder.add_edge("root_cause_analysis", "generate_response")
builder.add_edge("generate_response", "create_ticket")
builder.add_edge("create_ticket", "save_memory")
builder.add_edge("save_memory", END)

graph = builder.compile()


def run_agent(query: str, reporter: str = "Employee User") -> dict:
    initial_state = {
        "user_query": query,
        "reporter": reporter,
        "memory_context": [],
        "classification": "",
        "priority": "",
        "sla_due": "",
        "blast_radius": "",
        "assigned_team": "",
        "escalation_path": "",
        "root_cause": "",
        "recommended_action": "",
        "created_ticket_id": "",
        "reasoning_trace": [],
        "final_response": ""
    }
    return graph.invoke(initial_state)