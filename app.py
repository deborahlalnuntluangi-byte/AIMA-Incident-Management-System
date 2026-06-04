import streamlit as st
from aima_backend import run_agent

st.set_page_config(
    page_title="AIMA - Incident Management Assistant",
    layout="wide"
)

st.title("AIMA - Incident Management Assistant")

with st.sidebar:

    st.header("System Information")
    st.success("LangGraph Agent Active")
    st.info("ChromaDB Connected")

    st.header("Workflow Overview")

    st.markdown("""
1. Retrieve Memory
2. Classify Incident
3. Calculate Priority
4. Execute Tool
5. Generate Response
6. Save Memory
""")

    st.header("Agent Status")
    st.success("Operational")

left, right = st.columns([2, 1])

with left:

    query = st.text_area(
        "Enter Employee Incident",
        height=150
    )

    submit = st.button(
        "Analyze Incident"
    )

with right:

    st.metric(
        "Workflow Nodes",
        6
    )

    st.metric(
        "Memory System",
        "Active"
    )

if submit:

    if not query.strip():

        st.error(
            "Please enter an incident."
        )

    else:

        try:

            result = run_agent(query)

            col1, col2 = st.columns(2)

            with col1:

                st.subheader(
                    "Classification"
                )

                st.success(
                    result["classification"]
                )

            with col2:

                st.subheader(
                    "Priority"
                )

                st.warning(
                    result["priority"]
                )

            with st.expander(
                "Memory Retrieval"
            ):

                st.write(
                    result["memory_context"]
                )

            with st.expander(
                "Tool Execution"
            ):

                st.write(
                    result["tool_result"]
                )

            st.subheader(
                "Agent Response"
            )

            st.code(
                result["final_response"]
            )

            st.subheader(
                "Reasoning Trace"
            )

            for step in result["reasoning_trace"]:

                with st.status(
                    step,
                    expanded=False
                ):
                    st.write(step)

        except Exception as e:

            st.error(
                f"Unexpected Error: {e}"
            )