import sqlite3
import json
from datetime import datetime, timedelta

DB_FILE = "tickets.db"

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tickets (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        reporter TEXT NOT NULL,
        category TEXT NOT NULL,
        priority TEXT NOT NULL,
        status TEXT NOT NULL,
        assigned_team TEXT NOT NULL,
        sla_due TEXT NOT NULL,
        root_cause TEXT,
        recommended_action TEXT,
        ai_reasoning TEXT,
        comments TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)
    
    conn.commit()
    
    # Check if DB needs initial seeding
    cursor.execute("SELECT COUNT(*) FROM tickets")
    count = cursor.fetchone()[0]
    if count == 0:
        seed_db(cursor)
        conn.commit()
        
    conn.close()

def seed_db(cursor):
    now = datetime.now()
    seed_tickets = [
        (
            "INC-1001",
            "Global VPN Gateway Timeout",
            "Multiple employees across remote offices reporting 504 Gateway Timeouts when connecting to US-East VPN server.",
            "Alex Mercer (DevOps)",
            "IT Support",
            "P1 - Critical",
            "In Progress",
            "InfraOps - Tier 2",
            (now + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M"),
            "RADIUS authentication server threadpool exhaustion.",
            "Restart RADIUS service container and scale load balancer instances.",
            "Classified as Critical IT Infrastructure failure impacting >50 users.",
            json.dumps([{"author": "System", "time": now.strftime("%H:%M"), "text": "Incident auto-created by AIMA."}]),
            (now - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M"),
            now.strftime("%Y-%m-%d %H:%M")
        ),
        (
            "INC-1002",
            "September Payroll Discrepancy",
            "Monthly salary transfer credited 15% lower than paystub for Engineering department.",
            "Sarah Jenkins (Engineering)",
            "Payroll",
            "P2 - High",
            "Open",
            "Payroll & Finance",
            (now + timedelta(hours=6)).strftime("%Y-%m-%d %H:%M"),
            "Automated tax withholding calculation script logic error.",
            "Re-run payroll reconciliation batch script for September pay cycle.",
            "Classified as High Priority Finance issue affecting employee compensation.",
            json.dumps([{"author": "System", "time": now.strftime("%H:%M"), "text": "Ticket routed to Payroll queue."}]),
            (now - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M"),
            now.strftime("%Y-%m-%d %H:%M")
        ),
        (
            "INC-1003",
            "Annual Leave Approval Stuck",
            "Manager submitted vacation approval but status remains Pending in Workday HR portal.",
            "David Chen (Product)",
            "Leave Request",
            "P4 - Low",
            "Resolved",
            "HR Operations",
            (now - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M"),
            "Workday webhook notification sync delay.",
            "Manually trigger HR portal sync job and notify manager.",
            "Standard low-priority workflow request.",
            json.dumps([{"author": "HR Ops", "time": now.strftime("%H:%M"), "text": "Sync job executed. Leave approved."}]),
            (now - timedelta(hours=24)).strftime("%Y-%m-%d %H:%M"),
            now.strftime("%Y-%m-%d %H:%M")
        ),
        (
            "INC-1004",
            "Suspicious Phishing Email Campaign",
            "Several employees received fake CEO urgent giftcard request emails.",
            "Security Monitoring Bot",
            "Security",
            "P1 - Critical",
            "In Progress",
            "SecOps Incident Response",
            (now + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M"),
            "External domain spoofing targeting company leadership names.",
            "Purge suspicious emails from exchange mailboxes and update email gateway filter rules.",
            "Critical InfoSec threat detected across multiple mailboxes.",
            json.dumps([{"author": "SecOps", "time": now.strftime("%H:%M"), "text": "Domain blocked at firewall."}]),
            (now - timedelta(minutes=45)).strftime("%Y-%m-%d %H:%M"),
            now.strftime("%Y-%m-%d %H:%M")
        ),
        (
            "INC-1005",
            "Workplace Policy Inquiry",
            "Inquiry regarding home office equipment ergonomics allowance policy.",
            "Elena Rostova (Design)",
            "HR Issue",
            "P3 - Medium",
            "Open",
            "HR Ethics & Relations",
            (now + timedelta(hours=12)).strftime("%Y-%m-%d %H:%M"),
            "General HR benefit policy clarification.",
            "Send HR Benefits Ergonomics FAQ document link to employee.",
            "Standard HR policy inquiry.",
            json.dumps([]),
            (now - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M"),
            now.strftime("%Y-%m-%d %H:%M")
        )
    ]
    
    cursor.executemany("""
    INSERT INTO tickets VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, seed_tickets)

def create_ticket(title, description, reporter, category, priority, assigned_team, sla_due, root_cause="", recommended_action="", ai_reasoning=""):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM tickets")
    next_num = cursor.fetchone()[0] + 1001
    ticket_id = f"INC-{next_num}"
    
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    initial_comments = json.dumps([
        {"author": "AIMA System", "time": datetime.now().strftime("%H:%M"), "text": f"Incident auto-created with priority {priority}."}
    ])
    
    cursor.execute("""
    INSERT INTO tickets (id, title, description, reporter, category, priority, status, assigned_team, sla_due, root_cause, recommended_action, ai_reasoning, comments, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ticket_id, title, description, reporter, category, priority, "Open",
        assigned_team, sla_due, root_cause, recommended_action, ai_reasoning,
        initial_comments, now_str, now_str
    ))
    
    conn.commit()
    conn.close()
    return ticket_id

def get_all_tickets():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_ticket(ticket_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def update_ticket_status(ticket_id, new_status, comment_author="System", comment_text=""):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT comments FROM tickets WHERE id = ?", (ticket_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False
        
    comments = json.loads(row["comments"] or "[]")
    if comment_text:
        comments.append({
            "author": comment_author,
            "time": datetime.now().strftime("%H:%M"),
            "text": f"Status changed to {new_status}: {comment_text}"
        })
    else:
        comments.append({
            "author": comment_author,
            "time": datetime.now().strftime("%H:%M"),
            "text": f"Status changed to {new_status}."
        })
        
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute("""
    UPDATE tickets 
    SET status = ?, comments = ?, updated_at = ?
    WHERE id = ?
    """, (new_status, json.dumps(comments), now_str, ticket_id))
    
    conn.commit()
    conn.close()
    return True

def add_ticket_comment(ticket_id, author, text):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT comments FROM tickets WHERE id = ?", (ticket_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False
        
    comments = json.loads(row["comments"] or "[]")
    comments.append({
        "author": author,
        "time": datetime.now().strftime("%H:%M"),
        "text": text
    })
    
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute("UPDATE tickets SET comments = ?, updated_at = ? WHERE id = ?", 
                   (json.dumps(comments), now_str, ticket_id))
    conn.commit()
    conn.close()
    return True

def reset_and_reseed_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS tickets")
    conn.commit()
    conn.close()
    init_db()

# Initialize DB on import
init_db()
