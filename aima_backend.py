try:
    print("STARTING AGENT_BACKEND")

    from typing import TypedDict
    print("Imported TypedDict")

    from langgraph.graph import StateGraph
    from langgraph.graph import END
    print("Imported LangGraph")

    from memory import AIMAMemory
    print("Imported Memory")

    from tools import priority_calculator_tool
    print("Imported Tool")

except Exception as e:
    print("IMPORT ERROR:")
    print(type(e))
    print(e)
    raise

from typing import TypedDict

print("Imported TypedDict")

from langgraph.graph import StateGraph
from langgraph.graph import END

print("Imported LangGraph")

from memory import AIMAMemory

print("Imported Memory")

from tools import priority_calculator_tool

print("Imported Tool")
print("LOADING AGENT_BACKEND")
memory = AIMAMemory()


class AgentState(TypedDict):

    user_query: str

    memory_context: str

    classification: str

    priority: str

    tool_result: str

    reasoning_trace: list

    final_response: str


def retrieve_memory(state):

    memories = memory.retrieve_memory(
        state["user_query"]
    )

    state["memory_context"] = "\n".join(memories)

    state["reasoning_trace"].append(
        "Step 1: Memory Retrieved"
    )

    return state


def classify_incident(state):

    query = state["user_query"].lower()

    if any(
        word in query
        for word in ["leave", "vacation"]
    ):
        category = "Leave Request"

    elif any(
        word in query
        for word in ["salary", "payroll"]
    ):
        category = "Payroll"

    elif any(
        word in query
        for word in [
            "vpn",
            "laptop",
            "password",
            "portal",
            "system"
        ]
    ):
        category = "IT Support"

    elif any(
        word in query
        for word in [
            "harassment",
            "employee",
            "hr"
        ]
    ):
        category = "HR Issue"

    else:
        category = "General Inquiry"

    state["classification"] = category

    state["reasoning_trace"].append(
        f"Step 2: Classified as {category}"
    )

    return state


def calculate_priority(state):

    priority = priority_calculator_tool.invoke(
        state["user_query"]
    )

    state["priority"] = priority

    state["reasoning_trace"].append(
        f"Step 3: Priority = {priority}"
    )

    return state


def execute_tool(state):

    state["tool_result"] = (
        f"Priority Tool Output: "
        f"{state['priority']}"
    )

    state["reasoning_trace"].append(
        "Step 4: Tool Executed"
    )

    return state


def generate_response(state):

    response = f"""
AIMA Incident Assessment

Incident:
{state['user_query']}

Category:
{state['classification']}

Priority:
{state['priority']}

Relevant Memory:
{state['memory_context']}

Recommended Action:
Forward incident to responsible team
and create tracking ticket.
"""

    state["final_response"] = response

    state["reasoning_trace"].append(
        "Step 5: Response Generated"
    )

    return state


def save_memory(state):

    memory.save_memory(
        state["user_query"],
        state["classification"]
    )

    state["reasoning_trace"].append(
        "Step 6: Memory Saved"
    )

    return state


builder = StateGraph(AgentState)

builder.add_node(
    "retrieve_memory",
    retrieve_memory
)

builder.add_node(
    "classify_incident",
    classify_incident
)

builder.add_node(
    "calculate_priority",
    calculate_priority
)

builder.add_node(
    "execute_tool",
    execute_tool
)

builder.add_node(
    "generate_response",
    generate_response
)

builder.add_node(
    "save_memory",
    save_memory
)

builder.set_entry_point(
    "retrieve_memory"
)

builder.add_edge(
    "retrieve_memory",
    "classify_incident"
)

builder.add_edge(
    "classify_incident",
    "calculate_priority"
)

builder.add_edge(
    "calculate_priority",
    "execute_tool"
)

builder.add_edge(
    "execute_tool",
    "generate_response"
)

builder.add_edge(
    "generate_response",
    "save_memory"
)

builder.add_edge(
    "save_memory",
    END
)

graph = builder.compile()

print("RUN_AGENT CREATED")
def run_agent(query):

    state = {
        "user_query": query,
        "memory_context": "",
        "classification": "",
        "priority": "",
        "tool_result": "",
        "reasoning_trace": [],
        "final_response": ""
    }

    return graph.invoke(state)