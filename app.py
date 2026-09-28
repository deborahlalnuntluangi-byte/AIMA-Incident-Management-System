import streamlit as st
import pandas as pd
import altair as alt
import json
from datetime import datetime
from aima_backend import run_agent
import ticket_db
from memory import AIMAMemory

# Page Config
st.set_page_config(
    page_title="AIMA - Incident Management Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.0rem;
        color: #64748B;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
    }
    .prio-p1 {
        background-color: #FEF2F2;
        color: #991B1B;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
    }
    .prio-p2 {
        background-color: #FFEDD5;
        color: #9A3412;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
    }
    .prio-p3 {
        background-color: #FEF9C3;
        color: #854D0E;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
    }
    .prio-p4 {
        background-color: #F0FDF4;
        color: #166534;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Vector Memory
memory_system = AIMAMemory()

# Sidebar Setup
with st.sidebar:
    st.image("https://img.icons8.com/isometric-line/100/shield-error.png", width=64)
    st.markdown("### **AIMA Platform**")
    st.caption("AI Incident Management Assistant v2.0")
    
    st.divider()
    
    st.markdown("#### ⚙️ System Status")
    st.success("🟢 LangGraph Orchestrator")
    st.success("🟢 ChromaDB RAG Vector Store")
    st.success("🟢 SQLite Ticket Database")
    
    st.divider()
    
    nav_selection = st.radio(
        "Navigation",
        [
            "📥 Incident Desk (AI Assistant)",
            "🎫 Ticket Center (Operations)",
            "📊 Analytics & SLA Dashboard",
            "🧠 Knowledge Base & Vector RAG",
            "⚙️ System Settings"
        ]
    )

# ---------------------------------------------------------
# TAB 1: INCIDENT DESK (AI ASSISTANT)
# ---------------------------------------------------------
if nav_selection == "📥 Incident Desk (AI Assistant)":
    st.markdown('<div class="main-header">📥 AI Incident Desk</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Submit workplace or system incidents for autonomous classification, SLA priority scoring, and resolution routing.</div>', unsafe_allow_html=True)
    
    col_input, col_preset = st.columns([3, 2])
    
    with col_preset:
        st.subheader("⚡ Quick Load Sample Incidents")
        st.caption("Click any preset below to populate the incident form:")
        
        sample_query = ""
        if st.button("🔴 Critical VPN Outage (IT)"):
            sample_query = "Multiple users across remote offices reporting 504 Gateway Timeouts when connecting to US-East VPN server."
        if st.button("🟠 Salary Payment Discrepancy (Payroll)"):
            sample_query = "My monthly salary credited to my bank account for September is 15% lower than my paystub amount."
        if st.button("🔴 Phishing & Spoofing Mail Campaign (Security)"):
            sample_query = "Several engineering employees received urgent fake emails claiming to be the CEO asking for giftcards."
        if st.button("🟢 Leave Approval Stuck in Pending (HR)"):
            sample_query = "My manager approved my annual leave request yesterday but Workday status is still stuck on Pending."
            
    with col_input:
        reporter_name = st.text_input("Reporter Name / Department", value="Deborah (Engineering Ops)")
        
        default_val = sample_query if sample_query else ""
        query_input = st.text_area(
            "Describe the Incident / Problem",
            value=default_val,
            height=140,
            placeholder="e.g. Cannot access database connection pool after deployment..."
        )
        
        submit_button = st.button("🚀 Analyze & Process Incident with AI", type="primary", use_container_width=True)

    if submit_button:
        if not query_input.strip():
            st.error("Please provide a description of the incident before submitting.")
        else:
            with st.spinner("🤖 Running 8-Node LangGraph Agent Workflow (Memory RAG -> Classification -> Priority -> Routing -> RCA -> Ticket Log)..."):
                result = run_agent(query_input, reporter_name)
                
            st.toast(f"✅ Incident successfully processed! Created Ticket {result['created_ticket_id']}", icon="🎉")
            st.divider()
            
            # Key Outcome Metrics Banner
            m1, m2, m3, m4, m5 = st.columns(5)
            with m1:
                st.metric("Ticket ID", result["created_ticket_id"])
            with m2:
                st.metric("Category", result["classification"])
            with m3:
                st.metric("Priority", result["priority"])
            with m4:
                st.metric("Assigned Team", result["assigned_team"])
            with m5:
                st.metric("SLA Due Target", result["sla_due"])
                
            st.divider()
            
            # Executive Assessment & Details
            c_left, c_right = st.columns([3, 2])
            
            with c_left:
                st.markdown("### 📋 Executive Incident Report")
                st.markdown(result["final_response"])
                
            with c_right:
                st.markdown("### 🔍 LangGraph Reasoning Trace")
                st.caption("Node-by-node execution trajectory:")
                
                for step in result["reasoning_trace"]:
                    with st.status(step, expanded=False, state="complete"):
                        st.write(f"Executed step: **{step}**")
                        
                st.markdown("### 🧠 Retrieved RAG Knowledge Matches")
                for m in result["memory_context"]:
                    if m.get("title") != "N/A":
                        with st.expander(f"📌 {m['title']} (Similarity: {m['similarity']})"):
                            st.write(m['document'])
                            st.caption(f"Category: {m['category']} | Type: {m['type']}")

# ---------------------------------------------------------
# TAB 2: TICKET CENTER (OPERATIONS DESK)
# ---------------------------------------------------------
elif nav_selection == "🎫 Ticket Center (Operations)":
    st.markdown('<div class="main-header">🎫 Incident Operations Center</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Manage, track, triage, and update incident ticket life cycles across departments.</div>', unsafe_allow_html=True)
    
    all_tickets = ticket_db.get_all_tickets()
    
    if not all_tickets:
        st.info("No tickets currently logged.")
    else:
        # Filters Bar
        f1, f2, f3 = st.columns([2, 2, 3])
        with f1:
            status_filter = st.selectbox("Filter by Status", ["All", "Open", "In Progress", "Resolved"])
        with f2:
            cat_filter = st.selectbox("Filter by Category", ["All", "IT Support", "Payroll", "Leave Request", "Security", "HR Issue"])
        with f3:
            search_query = st.text_input("Search Ticket Title / ID", placeholder="INC-1001 or VPN...")
            
        # Apply filters
        filtered_tickets = all_tickets
        if status_filter != "All":
            filtered_tickets = [t for t in filtered_tickets if t["status"] == status_filter]
        if cat_filter != "All":
            filtered_tickets = [t for t in filtered_tickets if t["category"] == cat_filter]
        if search_query.strip():
            sq = search_query.lower()
            filtered_tickets = [t for t in filtered_tickets if sq in t["id"].lower() or sq in t["title"].lower() or sq in t["description"].lower()]
            
        st.subheader(f"Showing {len(filtered_tickets)} Incident Tickets")
        
        # Display Table
        df = pd.DataFrame(filtered_tickets)
        if not df.empty:
            display_df = df[["id", "title", "reporter", "category", "priority", "status", "assigned_team", "sla_due", "created_at"]]
            display_df.columns = ["Ticket ID", "Title / Incident", "Reporter", "Category", "Priority", "Status", "Assigned Team", "SLA Due", "Created"]
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
        st.divider()
        
        # Ticket Inspector & Action Drawer
        st.markdown("### 🔍 Ticket Inspector & Status Action")
        selected_ticket_id = st.selectbox("Select Ticket ID to Inspect or Update", [t["id"] for t in filtered_tickets])
        
        if selected_ticket_id:
            ticket_data = ticket_db.get_ticket(selected_ticket_id)
            if ticket_data:
                col_det1, col_det2 = st.columns([3, 2])
                
                with col_det1:
                    st.markdown(f"#### **{ticket_data['id']}: {ticket_data['title']}**")
                    st.write(f"**Description:** {ticket_data['description']}")
                    st.write(f"**Reporter:** `{ticket_data['reporter']}` | **Category:** `{ticket_data['category']}` | **Priority:** `{ticket_data['priority']}`")
                    st.write(f"**Assigned Team:** `{ticket_data['assigned_team']}` | **SLA Target:** `{ticket_data['sla_due']}`")
                    
                    st.markdown("##### ⚙️ Root Cause Hypothesis")
                    st.info(ticket_data['root_cause'] or "N/A")
                    
                    st.markdown("##### 🛠 Recommended Action Plan")
                    st.success(ticket_data['recommended_action'] or "N/A")
                    
                with col_det2:
                    st.markdown("#### ⚡ Operational Actions")
                    st.write(f"Current Status: **{ticket_data['status']}**")
                    
                    act_col1, act_col2, act_col3 = st.columns(3)
                    with act_col1:
                        if st.button("▶️ In Progress", key=f"prog_{ticket_data['id']}"):
                            ticket_db.update_ticket_status(ticket_data['id'], "In Progress", "Ops Desk")
                            st.toast("Status updated to In Progress.")
                            st.rerun()
                    with act_col2:
                        if st.button("✅ Resolve", key=f"res_{ticket_data['id']}"):
                            ticket_db.update_ticket_status(ticket_data['id'], "Resolved", "Ops Desk")
                            st.toast("Status updated to Resolved.")
                            st.rerun()
                    with act_col3:
                        if st.button("🚨 Re-Open", key=f"reop_{ticket_data['id']}"):
                            ticket_db.update_ticket_status(ticket_data['id'], "Open", "Ops Desk")
                            st.toast("Status updated to Open.")
                            st.rerun()
                            
                    st.markdown("##### 💬 Add Internal Note / Comment")
                    new_comment = st.text_input("Comment text", key=f"txt_{ticket_data['id']}")
                    if st.button("Post Note", key=f"post_{ticket_data['id']}"):
                        if new_comment.strip():
                            ticket_db.add_ticket_comment(ticket_data['id'], "Ops Engineer", new_comment)
                            st.toast("Comment added.")
                            st.rerun()
                            
                    # Audit Log
                    st.markdown("##### 📜 Ticket Activity Log")
                    comments_list = json.loads(ticket_data['comments'] or "[]")
                    for c in reversed(comments_list):
                        st.caption(f"⏱ **{c.get('time', '')}** - `{c.get('author', 'System')}`: {c.get('text', '')}")

# ---------------------------------------------------------
# TAB 3: ANALYTICS & SLA DASHBOARD
# ---------------------------------------------------------
elif nav_selection == "📊 Analytics & SLA Dashboard":
    st.markdown('<div class="main-header">📊 Operations Analytics & SLA Metrics</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Real-time KPI metrics, SLA compliance performance, and incident category breakdown.</div>', unsafe_allow_html=True)
    
    all_tickets = ticket_db.get_all_tickets()
    total_count = len(all_tickets)
    open_count = len([t for t in all_tickets if t["status"] == "Open"])
    in_prog_count = len([t for t in all_tickets if t["status"] == "In Progress"])
    resolved_count = len([t for t in all_tickets if t["status"] == "Resolved"])
    p1_count = len([t for t in all_tickets if "P1" in t["priority"]])
    
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.metric("Total Incidents", total_count)
    with k2:
        st.metric("Open Queue", open_count, delta=f"{open_count} pending")
    with k3:
        st.metric("In Progress", in_prog_count)
    with k4:
        st.metric("Resolved", resolved_count, delta=f"{(resolved_count/max(1,total_count)*100):.0f}% rate")
    with k5:
        st.metric("P1 Criticals", p1_count, delta_color="inverse")
        
    st.divider()
    
    if all_tickets:
        df = pd.DataFrame(all_tickets)
        
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("### 📁 Incidents by Category")
            cat_counts = df["category"].value_counts().reset_index()
            cat_counts.columns = ["Category", "Count"]
            
            chart_cat = alt.Chart(cat_counts).mark_bar(cornerRadius=6, color="#3B82F6").encode(
                x=alt.X("Count:Q", title="Number of Incidents"),
                y=alt.Y("Category:N", sort="-x", title="Category"),
                tooltip=["Category", "Count"]
            ).properties(height=300)
            
            st.altair_chart(chart_cat, use_container_width=True)
            
        with c2:
            st.markdown("### ⚡ Incidents by Priority Level")
            prio_counts = df["priority"].value_counts().reset_index()
            prio_counts.columns = ["Priority", "Count"]
            
            chart_prio = alt.Chart(prio_counts).mark_arc(innerRadius=50).encode(
                theta=alt.Theta(field="Count", type="quantitative"),
                color=alt.Color(field="Priority", type="nominal", scale=alt.Scale(scheme="category10")),
                tooltip=["Priority", "Count"]
            ).properties(height=300)
            
            st.altair_chart(chart_prio, use_container_width=True)
            
        st.markdown("### 📊 Status Breakdown by Category")
        cat_status = df.groupby(["category", "status"]).size().reset_index(name="Count")
        
        chart_stacked = alt.Chart(cat_status).mark_bar().encode(
            x=alt.X("category:N", title="Category"),
            y=alt.Y("Count:Q", title="Incident Count"),
            color=alt.Color("status:N", title="Status"),
            tooltip=["category", "status", "Count"]
        ).properties(height=320)
        
        st.altair_chart(chart_stacked, use_container_width=True)

# ---------------------------------------------------------
# TAB 4: KNOWLEDGE BASE & VECTOR RAG
# ---------------------------------------------------------
elif nav_selection == "🧠 Knowledge Base & Vector RAG":
    st.markdown('<div class="main-header">🧠 ChromaDB Vector Memory & Knowledge Base</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Persistent vector storage for incident resolution memory, SOP playbooks, and semantic RAG search.</div>', unsafe_allow_html=True)
    
    col_kb1, col_kb2 = st.columns([3, 2])
    
    with col_kb1:
        st.markdown("### 🔎 Vector Similarity Search Playground")
        test_query = st.text_input("Enter query to test RAG similarity retrieval:", value="VPN connection timeout RADIUS server")
        top_k = st.slider("Select Top K matches", 1, 5, 3)
        
        if st.button("Run Vector RAG Search"):
            search_results = memory_system.retrieve_memory(test_query, k=top_k)
            st.markdown(f"#### Top {len(search_results)} Vector Matches:")
            for res in search_results:
                with st.expander(f"⭐ {res.get('title', 'KB Record')} (Similarity: {res.get('similarity')})"):
                    st.write(res["document"])
                    st.caption(f"Category: {res.get('category')} | Type: {res.get('type')}")
                    
    with col_kb2:
        st.markdown("### ➕ Add New SOP Playbook to ChromaDB")
        new_title = st.text_input("Playbook Title", placeholder="e.g. Database Outage Recovery")
        new_cat = st.selectbox("Category", ["IT Support", "Payroll", "Leave Request", "Security", "HR Issue"])
        new_content = st.text_area("SOP Document Content / Instructions", height=120, placeholder="Steps to resolve database pool exhaustion...")
        
        if st.button("Save Playbook to ChromaDB Vector Store"):
            if new_title.strip() and new_content.strip():
                ok = memory_system.add_kb_article(new_title, new_content, new_cat)
                if ok:
                    st.success("Playbook successfully embedded and saved to ChromaDB!")
                    st.rerun()
            else:
                st.error("Please fill in title and content.")

    st.divider()
    st.markdown("### 📚 Stored Knowledge Base Records")
    all_docs = memory_system.get_all_documents()
    if all_docs:
        kb_df = pd.DataFrame(all_docs)
        st.dataframe(kb_df[["id", "title", "category", "type", "content"]], use_container_width=True, hide_index=True)

# ---------------------------------------------------------
# TAB 5: SYSTEM SETTINGS
# ---------------------------------------------------------
elif nav_selection == "⚙️ System Settings":
    st.markdown('<div class="main-header">⚙️ System Settings & Diagnostics</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">System configuration, database maintenance, and architecture specs.</div>', unsafe_allow_html=True)
    
    st.markdown("### 🏛️ LangGraph Workflow Architecture")
    st.markdown("""
    ```mermaid
    graph TD
        A[User Incident Query] --> B[1. Vector RAG Memory Retrieval]
        B --> C[2. Multi-Factor Incident Classification]
        C --> D[3. Priority & SLA Calculation]
        D --> E[4. Team Assignment & Escalation Routing]
        E --> F[5. Root Cause Analysis & Resolution Plan]
        F --> G[6. Executive Assessment Formatting]
        G --> H[7. SQLite Ticket Database Logging]
        H --> I[8. ChromaDB Memory Update]
    ```
    """)
    
    st.divider()
    
    st.markdown("### 🛠️ Maintenance & Reset")
    col_rst1, col_rst2 = st.columns(2)
    
    with col_rst1:
        st.warning("Reset Ticket Database")
        st.caption("Deletes all tickets and re-seeds default initial enterprise tickets.")
        if st.button("Reset & Re-Seed SQLite Tickets"):
            ticket_db.reset_and_reseed_db()
            st.success("Database reset to clean seed state!")
            st.rerun()
            
    with col_rst2:
        st.info("ChromaDB Storage Directory")
        st.caption("Path: `./chroma_db` (Persistent vector collection)")
        st.code("Collection: aima_memory")