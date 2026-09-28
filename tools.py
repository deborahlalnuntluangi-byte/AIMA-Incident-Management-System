from langchain_core.tools import tool
from datetime import datetime, timedelta
import ticket_db

@tool
def priority_calculator_tool(query: str) -> dict:
    """
    Calculates incident priority (P1-Critical to P4-Low), SLA window, and blast radius based on incident context.
    """
    try:
        text = query.lower()
        
        # Priority rules
        if any(word in text for word in ["critical", "outage", "down", "phishing", "breach", "hacked", "security", "emergency", "fire", "database down"]):
            priority = "P1 - Critical"
            sla_hours = 1
            blast_radius = "Organization-wide / Multiple Users Affected"
        elif any(word in text for word in ["vpn", "server", "system", "salary", "payroll", "unauthorized", "data loss", "api error"]):
            priority = "P2 - High"
            sla_hours = 4
            blast_radius = "Departmental / High Priority Service"
        elif any(word in text for word in ["leave", "portal", "password", "access", "software", "email", "hr"]):
            priority = "P3 - Medium"
            sla_hours = 12
            blast_radius = "Individual Employee / Non-Blocker"
        else:
            priority = "P4 - Low"
            sla_hours = 24
            blast_radius = "Minor Inquiry / Standard SOP"

        sla_due = (datetime.now() + timedelta(hours=sla_hours)).strftime("%Y-%m-%d %H:%M")
        
        return {
            "priority": priority,
            "sla_hours": sla_hours,
            "sla_due": sla_due,
            "blast_radius": blast_radius
        }

    except Exception as e:
        return {
            "priority": "P3 - Medium",
            "sla_hours": 12,
            "sla_due": (datetime.now() + timedelta(hours=12)).strftime("%Y-%m-%d %H:%M"),
            "blast_radius": f"Error calculating: {str(e)}"
        }

@tool
def routing_tool(category: str, priority: str) -> dict:
    """
    Routes incident to appropriate response team and determines escalation path.
    """
    cat_lower = category.lower()
    prio_lower = priority.lower()
    
    if "security" in cat_lower or "phishing" in cat_lower:
        team = "SecOps Incident Response"
        escalation = "Chief Information Security Officer (CISO)"
    elif "it" in cat_lower or "vpn" in cat_lower or "system" in cat_lower or "infra" in cat_lower:
        if "p1" in prio_lower or "p2" in prio_lower:
            team = "InfraOps - Tier 2"
            escalation = "VP of Infrastructure & DevOps"
        else:
            team = "IT Service Desk"
            escalation = "IT Helpdesk Lead"
    elif "payroll" in cat_lower or "salary" in cat_lower:
        team = "Payroll & Finance"
        escalation = "Head of Global Payroll"
    elif "hr" in cat_lower or "harassment" in cat_lower:
        team = "HR Ethics & Relations"
        escalation = "Chief Human Resources Officer (CHRO)"
    elif "leave" in cat_lower:
        team = "HR Operations"
        escalation = "HR Operations Lead"
    else:
        team = "General Support Desk"
        escalation = "Service Operations Manager"

    return {
        "assigned_team": team,
        "escalation_path": escalation
    }

@tool
def root_cause_analyzer_tool(query: str, category: str, memory_context: str) -> dict:
    """
    Generates diagnostic hypothesis and recommended resolution steps based on incident description and memory context.
    """
    text = query.lower()
    
    if "vpn" in text or "connection" in text or "network" in text:
        root_cause = "Potential RADIUS authentication gateway timeout or VPN server capacity limit reached."
        recommended_action = "1. Verify RADIUS server daemon health.\n2. Scale active VPN gateway instances.\n3. Clear stuck session tokens in session store."
    elif "salary" in text or "payroll" in text or "pay" in text:
        root_cause = "Discrepancy in automated batch direct-deposit transfer or payroll tax withholding script."
        recommended_action = "1. Re-verify payroll batch log for employee ID.\n2. Execute payroll reconciliation batch job.\n3. Issue manual offset credit if needed."
    elif "leave" in text or "vacation" in text:
        root_cause = "Workday API webhook synchronization failure or pending manager authorization token."
        recommended_action = "1. Trigger manual HR portal sync job.\n2. Resend manager approval email notification.\n3. Validate leave balance credits."
    elif "phishing" in text or "security" in text or "hack" in text:
        root_cause = "External malicious domain email spoofing attack targeting internal credentials."
        recommended_action = "1. Quarantine sender domain at email firewall gateway.\n2. Execute mail exchange purge script across mailboxes.\n3. Force password reset for compromised users."
    else:
        root_cause = f"General {category} service inquiry or operational anomaly."
        recommended_action = f"1. Review standard operating procedure for {category}.\n2. Assign incident to {category} lead for triage."

    return {
        "root_cause": root_cause,
        "recommended_action": recommended_action
    }

@tool
def ticket_creator_tool(title: str, description: str, reporter: str, category: str, priority: str, assigned_team: str, sla_due: str, root_cause: str, recommended_action: str, ai_reasoning: str) -> str:
    """
    Creates a new incident ticket in the ticket database.
    """
    ticket_id = ticket_db.create_ticket(
        title=title,
        description=description,
        reporter=reporter,
        category=category,
        priority=priority,
        assigned_team=assigned_team,
        sla_due=sla_due,
        root_cause=root_cause,
        recommended_action=recommended_action,
        ai_reasoning=ai_reasoning
    )
    return ticket_id