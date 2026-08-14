"""
ADVANCED STAFF TASK MANAGEMENT & EXECUTIVE DASHBOARD
Single-file Streamlit application (app.py)

Run with:
    pip install streamlit pandas numpy plotly openpyxl
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import logging
import io
import os

# ============================================================
# 1. CONFIG & LOGGING
# ============================================================

st.set_page_config(
    page_title="Enterprise Task Management & Executive Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("TaskManager")

DB_PATH = "company_tasks.db"

CUSTOM_CSS = """
<style>
.kpi-card {
    background: linear-gradient(135deg, #1e3a5f 0%, #0f2540 100%);
    border-radius: 12px;
    padding: 16px 18px;
    color: white;
    box-shadow: 0 4px 10px rgba(0,0,0,0.15);
    margin-bottom: 8px;
}
.kpi-title { font-size: 13px; opacity: 0.85; margin-bottom: 4px; }
.kpi-value { font-size: 26px; font-weight: 700; }
.badge {
    padding: 3px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; color: white;
}
.badge-critical { background-color: #d32f2f; }
.badge-high { background-color: #f57c00; }
.badge-medium { background-color: #fbc02d; color:#333; }
.badge-low { background-color: #388e3c; }
.badge-overdue { background-color: #b71c1c; }
.badge-ontrack { background-color: #2e7d32; }
.badge-atrisk { background-color: #ef6c00; }
.badge-delayed { background-color: #c62828; }
.badge-completed { background-color: #1565c0; }
section[data-testid="stSidebar"] { background-color: #0f1b2b; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ============================================================
# 2. STATIC REFERENCE DATA
# ============================================================

SECTORS = ["IT", "Gaming", "Software Development", "Web Development", "Mobile App Development",
           "AI/ML", "Data Science", "Cyber Security", "Cloud/DevOps", "Finance", "HR",
           "Marketing", "Sales", "Customer Support", "Operations", "Administration",
           "UI/UX", "Software Testing/QA"]

DEPARTMENTS = {
    "IT": ["Infrastructure", "Support", "Networking"],
    "Gaming": ["Game Design", "Game Dev", "QA"],
    "Software Development": ["Backend", "Frontend", "Architecture"],
    "Web Development": ["Frontend", "Backend", "Full Stack"],
    "Mobile App Development": ["Android", "iOS", "Cross-Platform"],
    "AI/ML": ["Research", "ML Engineering", "MLOps"],
    "Data Science": ["Analytics", "Data Engineering", "BI"],
    "Cyber Security": ["SOC", "Pen Testing", "Compliance"],
    "Cloud/DevOps": ["Cloud Infra", "CI/CD", "SRE"],
    "Finance": ["Accounting", "Payroll", "Audit"],
    "HR": ["Recruitment", "Employee Relations", "Training"],
    "Marketing": ["Digital Marketing", "Content", "Branding"],
    "Sales": ["Inside Sales", "Enterprise Sales", "Sales Ops"],
    "Customer Support": ["Tier 1", "Tier 2", "Success"],
    "Operations": ["Logistics", "Process", "Admin Ops"],
    "Administration": ["Facilities", "Office Admin", "Procurement"],
    "UI/UX": ["Product Design", "Research", "Visual Design"],
    "Software Testing/QA": ["Manual QA", "Automation QA", "Performance"]
}

TEAMS = ["Alpha", "Bravo", "Charlie", "Delta", "Echo", "Falcon", "Nova", "Orion"]

PROJECTS = ["Gaming Platform Development", "Mobile Banking Application", "E-Commerce Platform",
            "HR Management System", "AI Recommendation Engine", "Customer Support Portal",
            "Cyber Security Monitoring System", "Cloud Migration", "Data Analytics Dashboard",
            "ERP Development", "CRM Implementation", "Website Redesign",
            "Mobile Application Upgrade", "Game Development", "Payment Gateway Integration"]

TASK_TYPES_BY_SECTOR = {
    "Gaming": ["Game Design", "Character Modeling", "Environment Design", "Gameplay Programming",
               "Multiplayer Development", "Game Testing", "Bug Fixing", "Unity Development",
               "Unreal Engine Development", "Animation", "Sound Design", "Performance Optimization",
               "Game Deployment"],
    "IT": ["Software Development", "Database Development", "API Development", "Cloud Deployment",
           "Server Configuration", "Cyber Security Audit", "Data Migration", "ETL Development",
           "Dashboard Development", "Testing", "Bug Fixing", "Documentation", "System Maintenance"],
    "HR": ["Recruitment Drive", "Onboarding", "Payroll Processing", "Policy Update", "Training Session"],
    "Finance": ["Budget Planning", "Invoice Processing", "Financial Audit", "Tax Filing", "Reporting"],
    "Marketing": ["Campaign Planning", "Content Creation", "SEO Optimization", "Social Media Strategy", "Ad Analytics"],
    "Sales": ["Lead Generation", "Client Follow-up", "Proposal Drafting", "Deal Closure", "CRM Update"],
    "Customer Support": ["Ticket Resolution", "Escalation Handling", "FAQ Update", "Chat Support", "Call Support"],
    "Operations": ["Inventory Check", "Vendor Coordination", "Process Optimization", "Compliance Review"],
    "Administration": ["Document Filing", "Facility Booking", "Procurement", "Travel Arrangement"],
    "AI/ML": ["Model Training", "Data Labeling", "Feature Engineering", "Model Deployment", "Research"],
    "Data Science": ["Data Cleaning", "Exploratory Analysis", "Report Generation", "Dashboard Build"],
    "Cyber Security": ["Vulnerability Scan", "Penetration Testing", "Incident Response", "Security Audit"],
    "Cloud/DevOps": ["CI/CD Pipeline Setup", "Server Provisioning", "Monitoring Setup", "Infra Automation"],
    "UI/UX": ["Wireframing", "Prototyping", "User Research", "Visual Design", "Usability Testing"],
    "Software Testing/QA": ["Test Case Design", "Manual Testing", "Automation Scripting", "Regression Testing"],
    "Web Development": ["Frontend Development", "Backend Development", "API Integration", "Responsive Design"],
    "Mobile App Development": ["Android Development", "iOS Development", "App Testing", "App Store Deployment"],
    "Software Development": ["Requirement Analysis", "Coding", "Code Review", "Unit Testing", "Deployment"],
}

PRIORITIES = ["Critical", "High", "Medium", "Low"]
STATUSES = ["Not Started", "Assigned", "In Progress", "On Hold", "Under Review",
            "Testing", "Blocked", "Completed", "Cancelled", "Overdue"]
PROCESS_STAGES = ["Planning", "Requirement Analysis", "Design", "Development", "Coding",
                   "Testing", "Bug Fixing", "Code Review", "Deployment", "Documentation",
                   "Client Review", "Maintenance", "Completed"]

DESIGNATIONS = ["Junior Engineer", "Senior Engineer", "Team Lead", "Manager", "Analyst",
                "Consultant", "Executive", "Associate", "Specialist"]
SKILLS = ["Python", "Java", "React", "SQL", "AWS", "Unity", "Figma", "Excel", "SEO",
          "Machine Learning", "Docker", "Kubernetes", "Selenium", "PowerBI", "Salesforce"]

FIRST_NAMES = ["Arjun", "Priya", "Karthik", "Ananya", "Vijay", "Divya", "Ramesh", "Sneha",
               "Suresh", "Meena", "Kiran", "Pooja", "Ravi", "Lakshmi", "Naveen", "Deepa",
               "Manoj", "Swathi", "Ganesh", "Aarti", "Sanjay", "Nithya", "Prakash", "Kavya",
               "Vikram", "Shalini", "Arun", "Rekha", "Mahesh", "Divakar", "Anitha", "Girish"]
LAST_NAMES = ["Kumar", "Sharma", "Iyer", "Reddy", "Nair", "Menon", "Rao", "Pillai", "Gupta",
              "Verma", "Das", "Chatterjee", "Mishra", "Patel", "Joshi", "Naidu"]

CLIENTS = ["Acme Corp", "Globex Industries", "TechNova", "Initech", "Umbrella Ltd",
           "Skyline Systems", "BrightPath Inc", "Zenith Solutions", "Internal", "Quantum Retail"]

REMARKS_POOL = ["Progressing as planned", "Waiting for client feedback", "Minor blockers resolved",
                "Needs additional resources", "On schedule", "Requires manager review",
                "Dependency pending", "Client requested changes", "Testing in progress",
                "Ready for deployment", "-"]

random.seed(42)
np.random.seed(42)

# ============================================================
# 3. DATABASE LAYER
# ============================================================

def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_database():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS staff (
            Staff_ID TEXT PRIMARY KEY,
            Staff_Name TEXT,
            Team TEXT,
            Department TEXT,
            Sector TEXT,
            Designation TEXT,
            Skill TEXT,
            Total_Working_Hours REAL,
            Availability_Status TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            Project_Name TEXT PRIMARY KEY,
            Sector TEXT,
            Client TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            Task_ID TEXT PRIMARY KEY,
            Task_Name TEXT,
            Task_Description TEXT,
            Assigned_Person TEXT,
            Team TEXT,
            Department TEXT,
            Sector TEXT,
            Project_Name TEXT,
            Task_Type TEXT,
            Priority TEXT,
            Status TEXT,
            Progress_Percentage INTEGER,
            Current_Process TEXT,
            Start_DateTime TEXT,
            End_DateTime TEXT,
            Estimated_Hours REAL,
            Actual_Hours REAL,
            Remaining_Hours REAL,
            Expected_Completion TEXT,
            Actual_Completion TEXT,
            Completion_Level TEXT,
            Dependency_Task_ID TEXT,
            Client_or_Project_Owner TEXT,
            Remarks TEXT,
            Created_At TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS activity_logs (
            Log_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Timestamp TEXT,
            User TEXT,
            Action TEXT,
            Task_ID TEXT,
            Old_Value TEXT,
            New_Value TEXT,
            Description TEXT
        )
    """)

    conn.commit()
    conn.close()


def log_activity(user, action, task_id, old_value, new_value, description):
    conn = get_connection()
    conn.execute("""
        INSERT INTO activity_logs (Timestamp, User, Action, Task_ID, Old_Value, New_Value, Description)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (datetime.now().isoformat(sep=" ", timespec="seconds"), user, action,
          task_id, str(old_value), str(new_value), description))
    conn.commit()
    conn.close()
    logger.info(f"{action} | Task {task_id} | {description}")


# ============================================================
# 4. SAMPLE DATA GENERATION
# ============================================================

def completion_level(progress):
    if progress <= 30:
        return "Low"
    elif progress <= 70:
        return "Medium"
    return "High"


def generate_staff(n=45):
    staff_rows = []
    used_names = set()
    for i in range(1, n + 1):
        sector = random.choice(SECTORS)
        dept = random.choice(DEPARTMENTS[sector])
        while True:
            name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
            if name not in used_names:
                used_names.add(name)
                break
        staff_rows.append({
            "Staff_ID": f"EMP{i:04d}",
            "Staff_Name": name,
            "Team": random.choice(TEAMS),
            "Department": dept,
            "Sector": sector,
            "Designation": random.choice(DESIGNATIONS),
            "Skill": random.choice(SKILLS),
            "Total_Working_Hours": round(random.uniform(120, 220), 1),
            "Availability_Status": random.choice(["Available", "Available", "Busy", "On Leave"])
        })
    return pd.DataFrame(staff_rows)


def generate_projects():
    rows = []
    for p in PROJECTS:
        rows.append({
            "Project_Name": p,
            "Sector": random.choice(SECTORS),
            "Client": random.choice(CLIENTS)
        })
    return pd.DataFrame(rows)


def generate_sample_tasks(n, staff_df, projects_df):
    tasks = []
    now = datetime.now()
    dep_pool = []

    for i in range(1, n + 1):
        staff_row = staff_df.sample(1).iloc[0]
        sector = staff_row["Sector"]
        dept = staff_row["Department"]
        team = staff_row["Team"]
        project_row = projects_df.sample(1).iloc[0]
        task_type = random.choice(TASK_TYPES_BY_SECTOR.get(sector, ["General Task"]))

        # Time bucket: past (35%), current (35%), future (30%)
        bucket = random.choices(["past", "current", "future"], weights=[0.35, 0.35, 0.30])[0]

        estimated_hours = round(random.uniform(4, 80), 1)

        if bucket == "past":
            start_dt = now - timedelta(days=random.randint(15, 120), hours=random.randint(0, 8))
            end_dt = start_dt + timedelta(hours=estimated_hours)
            status = random.choices(["Completed", "Cancelled"], weights=[0.85, 0.15])[0]
            progress = 100 if status == "Completed" else random.randint(10, 90)
            actual_hours = round(estimated_hours * random.uniform(0.8, 1.3), 1)
            actual_completion = (end_dt + timedelta(hours=random.randint(-5, 20))).isoformat(sep=" ", timespec="minutes") if status == "Completed" else ""
            current_process = "Completed" if status == "Completed" else random.choice(PROCESS_STAGES[:-1])
        elif bucket == "current":
            start_dt = now - timedelta(days=random.randint(0, 10), hours=random.randint(0, 12))
            end_dt = now + timedelta(days=random.randint(0, 10), hours=random.randint(1, 12))
            status = random.choices(
                ["In Progress", "Assigned", "On Hold", "Under Review", "Testing", "Blocked"],
                weights=[0.4, 0.15, 0.1, 0.15, 0.1, 0.1]
            )[0]
            progress = random.randint(5, 95)
            actual_hours = round(estimated_hours * random.uniform(0.2, 0.9), 1)
            actual_completion = ""
            current_process = random.choice(PROCESS_STAGES[:-1])
        else:  # future
            start_dt = now + timedelta(days=random.randint(1, 45), hours=random.randint(0, 8))
            end_dt = start_dt + timedelta(hours=estimated_hours)
            status = random.choices(["Not Started", "Assigned"], weights=[0.6, 0.4])[0]
            progress = 0
            actual_hours = 0.0
            actual_completion = ""
            current_process = "Planning"

        # push some current tasks into overdue territory
        if bucket == "current" and status not in ("Completed", "Cancelled") and random.random() < 0.25:
            end_dt = now - timedelta(hours=random.randint(1, 72))
            status = "Overdue"

        remaining_hours = max(0, round((end_dt - now).total_seconds() / 3600, 1)) if status not in ("Completed", "Cancelled") else 0
        expected_completion = (start_dt + timedelta(hours=estimated_hours * (100 / max(progress, 1)) if progress > 0 else estimated_hours)).isoformat(sep=" ", timespec="minutes")

        task_id = f"TSK{i:04d}"
        dependency = random.choice(dep_pool) if dep_pool and random.random() < 0.2 else ""
        dep_pool.append(task_id)

        tasks.append({
            "Task_ID": task_id,
            "Task_Name": f"{task_type} - {project_row['Project_Name']}",
            "Task_Description": f"{task_type} work required for {project_row['Project_Name']} under {sector} sector.",
            "Assigned_Person": staff_row["Staff_Name"],
            "Team": team,
            "Department": dept,
            "Sector": sector,
            "Project_Name": project_row["Project_Name"],
            "Task_Type": task_type,
            "Priority": random.choices(PRIORITIES, weights=[0.15, 0.3, 0.35, 0.2])[0],
            "Status": status,
            "Progress_Percentage": progress,
            "Current_Process": current_process,
            "Start_DateTime": start_dt.isoformat(sep=" ", timespec="minutes"),
            "End_DateTime": end_dt.isoformat(sep=" ", timespec="minutes"),
            "Estimated_Hours": estimated_hours,
            "Actual_Hours": actual_hours,
            "Remaining_Hours": remaining_hours,
            "Expected_Completion": expected_completion,
            "Actual_Completion": actual_completion,
            "Completion_Level": completion_level(progress),
            "Dependency_Task_ID": dependency,
            "Client_or_Project_Owner": project_row["Client"],
            "Remarks": random.choice(REMARKS_POOL),
            "Created_At": (start_dt - timedelta(days=random.randint(0, 5))).isoformat(sep=" ", timespec="minutes")
        })

    return pd.DataFrame(tasks)


def seed_database_if_empty():
    conn = get_connection()
    count = pd.read_sql("SELECT COUNT(*) as c FROM tasks", conn).iloc[0]["c"]
    if count == 0:
        staff_df = generate_staff(45)
        projects_df = generate_projects()
        tasks_df = generate_sample_tasks(200, staff_df, projects_df)

        staff_df.to_sql("staff", conn, if_exists="replace", index=False)
        projects_df.to_sql("projects", conn, if_exists="replace", index=False)
        tasks_df.to_sql("tasks", conn, if_exists="replace", index=False)

        log_activity("System", "Seed", "-", "-", "-", "Initial 200 sample tasks generated")
    conn.close()


# ============================================================
# 5. DATA ACCESS HELPERS
# ============================================================

def load_tasks():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM tasks", conn)
    conn.close()
    df["Start_DateTime"] = pd.to_datetime(df["Start_DateTime"], errors="coerce")
    df["End_DateTime"] = pd.to_datetime(df["End_DateTime"], errors="coerce")
    df["Created_At"] = pd.to_datetime(df["Created_At"], errors="coerce")
    return df


def load_staff():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM staff", conn)
    conn.close()
    return df


def load_projects():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM projects", conn)
    conn.close()
    return df


def load_logs():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM activity_logs ORDER BY Log_ID DESC", conn)
    conn.close()
    return df


def save_task(row_dict, is_new=True):
    conn = get_connection()
    cols = list(row_dict.keys())
    placeholders = ",".join(["?"] * len(cols))
    if is_new:
        conn.execute(f"INSERT INTO tasks ({','.join(cols)}) VALUES ({placeholders})", list(row_dict.values()))
    else:
        set_clause = ",".join([f"{c}=?" for c in cols if c != "Task_ID"])
        values = [row_dict[c] for c in cols if c != "Task_ID"] + [row_dict["Task_ID"]]
        conn.execute(f"UPDATE tasks SET {set_clause} WHERE Task_ID=?", values)
    conn.commit()
    conn.close()


def delete_task_db(task_id):
    conn = get_connection()
    conn.execute("DELETE FROM tasks WHERE Task_ID=?", (task_id,))
    conn.commit()
    conn.close()


def next_task_id():
    conn = get_connection()
    df = pd.read_sql("SELECT Task_ID FROM tasks", conn)
    conn.close()
    if df.empty:
        return "TSK0001"
    nums = df["Task_ID"].str.replace("TSK", "", regex=False).astype(int)
    return f"TSK{nums.max() + 1:04d}"


# ============================================================
# 6. LIVE CALCULATIONS
# ============================================================

def compute_live_fields(df):
    df = df.copy()
    now = pd.Timestamp.now()

    df["Elapsed_Hours"] = ((now - df["Start_DateTime"]).dt.total_seconds() / 3600).clip(lower=0)
    df["Total_Duration_Hours"] = (df["End_DateTime"] - df["Start_DateTime"]).dt.total_seconds() / 3600
    df["Remaining_Hours_Live"] = ((df["End_DateTime"] - now).dt.total_seconds() / 3600)

    def deadline_status(row):
        if row["Status"] in ("Completed", "Cancelled"):
            return "Completed" if row["Status"] == "Completed" else "Cancelled"
        if row["End_DateTime"] < now:
            return "Overdue"
        remaining_frac = (row["End_DateTime"] - now) / (row["End_DateTime"] - row["Start_DateTime"]) \
            if row["End_DateTime"] != row["Start_DateTime"] else 0
        expected_progress = (1 - remaining_frac) * 100
        if row["Progress_Percentage"] >= expected_progress - 10:
            return "On Track"
        elif row["Progress_Percentage"] >= expected_progress - 30:
            return "At Risk"
        else:
            return "Delayed"

    df["Live_Status"] = df.apply(deadline_status, axis=1)

    # Recompute effective status: mark overdue automatically
    def effective_status(row):
        if row["Status"] in ("Completed", "Cancelled"):
            return row["Status"]
        if row["End_DateTime"] < now:
            return "Overdue"
        return row["Status"]

    df["Effective_Status"] = df.apply(effective_status, axis=1)

    def alert_level(row):
        if row["Effective_Status"] == "Overdue":
            return "Overdue"
        hours_left = (row["End_DateTime"] - now).total_seconds() / 3600
        if hours_left <= 1:
            return "Critical"
        elif hours_left <= 4:
            return "Warning"
        elif hours_left <= 24:
            return "Upcoming"
        return "Normal"

    df["Alert_Level"] = df.apply(alert_level, axis=1)
    return df


# ============================================================
# 7. STAFF ANALYTICS
# ============================================================

def compute_staff_metrics(tasks_df, staff_df):
    metrics = []
    for _, s in staff_df.iterrows():
        person = s["Staff_Name"]
        t = tasks_df[tasks_df["Assigned_Person"] == person]
        assigned = len(t)
        completed = len(t[t["Effective_Status"] == "Completed"])
        active = len(t[t["Effective_Status"].isin(["In Progress", "Assigned", "Testing", "Under Review"])])
        pending = len(t[t["Effective_Status"].isin(["Not Started", "On Hold", "Blocked"])])
        overdue = len(t[t["Effective_Status"] == "Overdue"])
        est_hours = t["Estimated_Hours"].sum()
        act_hours = t["Actual_Hours"].sum()
        rem_hours = t["Remaining_Hours_Live"].clip(lower=0).sum()

        utilization = min(100, round((act_hours / s["Total_Working_Hours"]) * 100, 1)) if s["Total_Working_Hours"] else 0
        productivity = round((completed / assigned) * 100, 1) if assigned else 0

        if utilization < 40:
            workload_class = "Underutilized"
        elif utilization < 75:
            workload_class = "Normal"
        elif utilization < 95:
            workload_class = "High Workload"
        else:
            workload_class = "Overloaded"

        metrics.append({
            "Staff_ID": s["Staff_ID"], "Staff_Name": person, "Team": s["Team"],
            "Department": s["Department"], "Sector": s["Sector"], "Designation": s["Designation"],
            "Assigned_Tasks": assigned, "Active_Tasks": active, "Completed_Tasks": completed,
            "Pending_Tasks": pending, "Overdue_Tasks": overdue,
            "Estimated_Hours": round(est_hours, 1), "Actual_Hours": round(act_hours, 1),
            "Remaining_Hours": round(rem_hours, 1), "Utilization_%": utilization,
            "Productivity_%": productivity, "Workload_Class": workload_class,
            "Availability_Status": s["Availability_Status"]
        })
    return pd.DataFrame(metrics)


# ============================================================
# 8. INITIALIZE
# ============================================================

init_database()
seed_database_if_empty()

if "current_user" not in st.session_state:
    st.session_state.current_user = "Admin"

# ============================================================
# 9. SIDEBAR NAVIGATION
# ============================================================

st.sidebar.title("📊 Enterprise TMS")
st.sidebar.caption(f"Logged in as: **{st.session_state.current_user}**")

PAGES = [
    "Executive Dashboard", "Live Task Monitor", "Task Management", "Staff Management",
    "Project Management", "Sector Analytics", "Department Analytics", "Staff Performance",
    "Task History", "Future Tasks", "Reports", "Activity Logs", "Settings"
]
page = st.sidebar.radio("Navigate", PAGES)

# --- Auto-refresh control: Off, 10s, 30s, 60s, 5 minutes -----------------
REFRESH_OPTIONS = {
    "Off": None,
    "10 seconds": 10,
    "30 seconds": 30,
    "60 seconds": 60,
    "5 minutes": 300,
}
refresh_choice = st.sidebar.selectbox(
    "Auto-refresh interval (Live pages)",
    list(REFRESH_OPTIONS.keys()),
    index=2  # defaults to "30 seconds"
)
refresh_interval = REFRESH_OPTIONS[refresh_choice]

if st.sidebar.button("🔄 Refresh Now"):
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("SQLite DB: company_tasks.db")

# Auto-refresh mechanism (works without extra packages)
# Only injects the meta-refresh tag when auto-refresh is not Off.
if page in ("Executive Dashboard", "Live Task Monitor") and refresh_interval is not None:
    st.markdown(
        f"<meta http-equiv='refresh' content='{refresh_interval}'>",
        unsafe_allow_html=True
    )
    st.sidebar.caption(f"⏱️ Auto-refresh: every {refresh_choice}")
else:
    st.sidebar.caption("⏱️ Auto-refresh: Off")

# Load & compute
raw_tasks = load_tasks()
tasks_df = compute_live_fields(raw_tasks)
staff_df = load_staff()
projects_df = load_projects()
staff_metrics_df = compute_staff_metrics(tasks_df, staff_df)

# ============================================================
# 10. SHARED FILTER PANEL
# ============================================================

def filter_panel(df, key_prefix):
    with st.expander("🔍 Filters", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            f_sector = st.multiselect("Sector", sorted(df["Sector"].unique()), key=f"{key_prefix}_sector")
            f_dept = st.multiselect("Department", sorted(df["Department"].unique()), key=f"{key_prefix}_dept")
        with c2:
            f_team = st.multiselect("Team", sorted(df["Team"].unique()), key=f"{key_prefix}_team")
            f_project = st.multiselect("Project", sorted(df["Project_Name"].unique()), key=f"{key_prefix}_project")
        with c3:
            f_priority = st.multiselect("Priority", PRIORITIES, key=f"{key_prefix}_priority")
            f_status = st.multiselect("Status", sorted(df["Effective_Status"].unique()), key=f"{key_prefix}_status")
        with c4:
            f_person = st.multiselect("Assigned Person", sorted(df["Assigned_Person"].unique()), key=f"{key_prefix}_person")
            f_level = st.multiselect("Completion Level", ["Low", "Medium", "High"], key=f"{key_prefix}_level")

        search_term = st.text_input("🔎 Global Search (Task ID, Name, Employee, Project, Client)", key=f"{key_prefix}_search")

        col_a, col_b = st.columns(2)
        with col_a:
            date_from = st.date_input("Start Date From", value=None, key=f"{key_prefix}_from")
        with col_b:
            date_to = st.date_input("Start Date To", value=None, key=f"{key_prefix}_to")

        if st.button("Clear Filters", key=f"{key_prefix}_clear"):
            for k in list(st.session_state.keys()):
                if k.startswith(key_prefix):
                    del st.session_state[k]
            st.rerun()

    filtered = df.copy()
    if f_sector: filtered = filtered[filtered["Sector"].isin(f_sector)]
    if f_dept: filtered = filtered[filtered["Department"].isin(f_dept)]
    if f_team: filtered = filtered[filtered["Team"].isin(f_team)]
    if f_project: filtered = filtered[filtered["Project_Name"].isin(f_project)]
    if f_priority: filtered = filtered[filtered["Priority"].isin(f_priority)]
    if f_status: filtered = filtered[filtered["Effective_Status"].isin(f_status)]
    if f_person: filtered = filtered[filtered["Assigned_Person"].isin(f_person)]
    if f_level: filtered = filtered[filtered["Completion_Level"].isin(f_level)]
    if date_from:
        filtered = filtered[filtered["Start_DateTime"] >= pd.Timestamp(date_from)]
    if date_to:
        filtered = filtered[filtered["Start_DateTime"] <= pd.Timestamp(date_to) + pd.Timedelta(days=1)]
    if search_term:
        s = search_term.lower()
        filtered = filtered[
            filtered["Task_ID"].str.lower().str.contains(s) |
            filtered["Task_Name"].str.lower().str.contains(s) |
            filtered["Assigned_Person"].str.lower().str.contains(s) |
            filtered["Project_Name"].str.lower().str.contains(s) |
            filtered["Client_or_Project_Owner"].str.lower().str.contains(s) |
            filtered["Department"].str.lower().str.contains(s) |
            filtered["Sector"].str.lower().str.contains(s)
        ]
    return filtered


def kpi_card(col, title, value):
    with col:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """, unsafe_allow_html=True)


def priority_badge(p):
    cls = {"Critical": "badge-critical", "High": "badge-high", "Medium": "badge-medium", "Low": "badge-low"}.get(p, "badge-medium")
    return f"<span class='badge {cls}'>{p}</span>"


def export_buttons(df, filename_prefix):
    c1, c2 = st.columns(2)
    with c1:
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download CSV", csv, f"{filename_prefix}.csv", "text/csv")
    with c2:
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Data")
        st.download_button("⬇️ Download Excel", buf.getvalue(), f"{filename_prefix}.xlsx",
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


# ============================================================
# 11. PAGE: EXECUTIVE DASHBOARD
# ============================================================

if page == "Executive Dashboard":
    st.title("📈 Executive Dashboard")
    st.caption(f"Live as of {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    filtered = filter_panel(tasks_df, "exec")

    total = len(filtered)
    completed = len(filtered[filtered["Effective_Status"] == "Completed"])
    active = len(filtered[filtered["Effective_Status"].isin(["In Progress", "Assigned", "Testing", "Under Review"])])
    pending = len(filtered[filtered["Effective_Status"].isin(["Not Started", "On Hold", "Blocked"])])
    overdue = len(filtered[filtered["Effective_Status"] == "Overdue"])
    critical = len(filtered[filtered["Priority"] == "Critical"])
    completion_rate = round((completed / total) * 100, 1) if total else 0
    avg_duration = round(filtered["Total_Duration_Hours"].mean(), 1) if total else 0

    row1 = st.columns(6)
    kpi_card(row1[0], "Total Tasks", total)
    kpi_card(row1[1], "Completed", completed)
    kpi_card(row1[2], "Active", active)
    kpi_card(row1[3], "Pending", pending)
    kpi_card(row1[4], "Overdue", overdue)
    kpi_card(row1[5], "Critical", critical)

    row2 = st.columns(6)
    kpi_card(row2[0], "Completion Rate", f"{completion_rate}%")
    kpi_card(row2[1], "Avg Duration (hrs)", avg_duration)
    kpi_card(row2[2], "Active Staff", staff_df["Staff_Name"].nunique())
    kpi_card(row2[3], "Projects", projects_df["Project_Name"].nunique())
    kpi_card(row2[4], "Avg Productivity", f"{round(staff_metrics_df['Productivity_%'].mean(),1)}%")
    kpi_card(row2[5], "Avg Utilization", f"{round(staff_metrics_df['Utilization_%'].mean(),1)}%")

    st.markdown("---")

    c1, c2, c3 = st.columns(3)
    with c1:
        fig = px.pie(filtered, names="Effective_Status", title="Task Status Distribution", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.pie(filtered, names="Priority", title="Task Priority Distribution", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    with c3:
        fig = px.pie(filtered, names="Completion_Level", title="Completion Level Distribution", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

    c4, c5 = st.columns(2)
    with c4:
        sector_counts = filtered["Sector"].value_counts().reset_index()
        sector_counts.columns = ["Sector", "Count"]
        fig = px.bar(sector_counts, x="Count", y="Sector", orientation="h", title="Tasks by Sector")
        st.plotly_chart(fig, use_container_width=True)
    with c5:
        dept_counts = filtered["Department"].value_counts().reset_index()
        dept_counts.columns = ["Department", "Count"]
        fig = px.bar(dept_counts, x="Count", y="Department", orientation="h", title="Tasks by Department")
        st.plotly_chart(fig, use_container_width=True)

    c6, c7 = st.columns(2)
    with c6:
        top_staff = filtered["Assigned_Person"].value_counts().head(15).reset_index()
        top_staff.columns = ["Staff", "Tasks"]
        fig = px.bar(top_staff, x="Tasks", y="Staff", orientation="h", title="Tasks by Staff (Top 15)")
        st.plotly_chart(fig, use_container_width=True)
    with c7:
        proj_counts = filtered["Project_Name"].value_counts().reset_index()
        proj_counts.columns = ["Project", "Count"]
        fig = px.bar(proj_counts, x="Count", y="Project", orientation="h", title="Tasks by Project")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Estimated vs Actual Hours (by Sector)")
    hrs = filtered.groupby("Sector")[["Estimated_Hours", "Actual_Hours"]].sum().reset_index()
    fig = px.bar(hrs, x="Sector", y=["Estimated_Hours", "Actual_Hours"], barmode="group")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Daily Task Creation Trend")
    daily = filtered.groupby(filtered["Created_At"].dt.date).size().reset_index(name="Tasks Created")
    fig = px.area(daily, x="Created_At", y="Tasks Created")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("High-Risk Tasks (At Risk / Delayed / Overdue)")
    risk_df = filtered[filtered["Live_Status"].isin(["At Risk", "Delayed", "Overdue"])]
    st.dataframe(risk_df[["Task_ID", "Task_Name", "Assigned_Person", "Priority", "Live_Status",
                           "Progress_Percentage", "End_DateTime"]], use_container_width=True)

    export_buttons(filtered, "executive_dashboard_export")


# ============================================================
# 12. PAGE: LIVE TASK MONITOR
# ============================================================

elif page == "Live Task Monitor":
    st.title("🟢 Live Task Monitor")
    st.markdown(f"### 🕒 Current Time: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`")

    live_tasks = tasks_df[~tasks_df["Effective_Status"].isin(["Completed", "Cancelled"])].copy()

    alert_order = {"Critical": 0, "Overdue": 1, "Warning": 2, "Upcoming": 3, "Normal": 4}
    priority_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    live_tasks["sort_key"] = live_tasks["Alert_Level"].map(alert_order).fillna(5) * 10 + \
                              live_tasks["Priority"].map(priority_order).fillna(5)
    live_tasks = live_tasks.sort_values("sort_key")

    c1, c2, c3, c4 = st.columns(4)
    kpi_card(c1, "Critical (≤1h)", len(live_tasks[live_tasks["Alert_Level"] == "Critical"]))
    kpi_card(c2, "Warning (≤4h)", len(live_tasks[live_tasks["Alert_Level"] == "Warning"]))
    kpi_card(c3, "Upcoming (≤24h)", len(live_tasks[live_tasks["Alert_Level"] == "Upcoming"]))
    kpi_card(c4, "Overdue", len(live_tasks[live_tasks["Alert_Level"] == "Overdue"]))

    st.markdown("---")
    if refresh_interval is not None:
        st.caption(f"Auto-refreshing every {refresh_choice}")
    else:
        st.caption("Auto-refresh is Off")

    filtered_live = filter_panel(live_tasks, "live")

    for _, row in filtered_live.head(60).iterrows():
        badge_map = {"Critical": "badge-critical", "Overdue": "badge-overdue", "Warning": "badge-high",
                     "Upcoming": "badge-medium", "Normal": "badge-ontrack"}
        alert_badge = f"<span class='badge {badge_map.get(row['Alert_Level'],'badge-low')}'>{row['Alert_Level']}</span>"
        live_badge_map = {"On Track": "badge-ontrack", "At Risk": "badge-atrisk", "Delayed": "badge-delayed"}
        live_status_badge = f"<span class='badge {live_badge_map.get(row['Live_Status'], 'badge-low')}'>{row['Live_Status']}</span>"

        with st.container(border=True):
            c1, c2, c3 = st.columns([3, 2, 2])
            with c1:
                st.markdown(f"**{row['Task_Name']}**  \n`{row['Task_ID']}` — {row['Project_Name']}")
                st.markdown(f"{priority_badge(row['Priority'])} {alert_badge} {live_status_badge}", unsafe_allow_html=True)
            with c2:
                st.write(f"👤 {row['Assigned_Person']}")
                st.write(f"📍 {row['Current_Process']}")
                st.write(f"🏢 {row['Sector']} / {row['Department']}")
            with c3:
                st.progress(min(100, max(0, int(row["Progress_Percentage"]))) / 100,
                            text=f"{row['Progress_Percentage']}% complete")
                rem = row["Remaining_Hours_Live"]
                rem_text = f"{rem:.1f} hrs remaining" if rem > 0 else "Deadline passed"
                st.write(f"⏳ {rem_text}")
                st.caption(f"Deadline: {row['End_DateTime']}")


# ============================================================
# 13. PAGE: TASK MANAGEMENT (CRUD)
# ============================================================

elif page == "Task Management":
    st.title("🗂️ Task Management")

    tab1, tab2, tab3 = st.tabs(["➕ Add Task", "✏️ Edit / Delete Task", "📋 All Tasks"])

    with tab1:
        st.subheader("Add New Task")
        with st.form("add_task_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                task_name = st.text_input("Task Name*")
                sector = st.selectbox("Sector*", SECTORS)
                dept = st.selectbox("Department*", DEPARTMENTS[sector])
                team = st.selectbox("Team*", TEAMS)
            with c2:
                assigned_person = st.selectbox("Assigned Person*", sorted(staff_df["Staff_Name"].unique()))
                project_name = st.selectbox("Project*", sorted(projects_df["Project_Name"].unique()))
                task_type = st.selectbox("Task Type*", TASK_TYPES_BY_SECTOR.get(sector, ["General Task"]))
                priority = st.selectbox("Priority*", PRIORITIES)
            with c3:
                status = st.selectbox("Status*", STATUSES)
                current_process = st.selectbox("Current Process*", PROCESS_STAGES)
                progress = st.slider("Progress %*", 0, 100, 0)
                client = st.selectbox("Client / Owner*", CLIENTS)

            c4, c5 = st.columns(2)
            with c4:
                start_date = st.date_input("Start Date*", value=datetime.now().date())
                start_time = st.time_input("Start Time*", value=datetime.now().time())
            with c5:
                end_date = st.date_input("End Date*", value=(datetime.now() + timedelta(days=3)).date())
                end_time = st.time_input("End Time*", value=datetime.now().time())

            estimated_hours = st.number_input("Estimated Hours*", min_value=0.5, value=8.0, step=0.5)
            description = st.text_area("Task Description")
            dependency = st.selectbox("Dependency Task ID (optional)", ["None"] + list(tasks_df["Task_ID"].unique()))
            remarks = st.text_input("Remarks", value="-")

            submitted = st.form_submit_button("Add Task")

            if submitted:
                start_dt = datetime.combine(start_date, start_time)
                end_dt = datetime.combine(end_date, end_time)

                if not task_name.strip():
                    st.error("❌ Task Name is required.")
                elif end_dt <= start_dt:
                    st.error("❌ Invalid duration: End DateTime must be after Start DateTime.")
                elif not (0 <= progress <= 100):
                    st.error("❌ Progress must be between 0 and 100.")
                else:
                    new_id = next_task_id()
                    row = {
                        "Task_ID": new_id,
                        "Task_Name": task_name,
                        "Task_Description": description,
                        "Assigned_Person": assigned_person,
                        "Team": team,
                        "Department": dept,
                        "Sector": sector,
                        "Project_Name": project_name,
                        "Task_Type": task_type,
                        "Priority": priority,
                        "Status": status,
                        "Progress_Percentage": progress,
                        "Current_Process": current_process,
                        "Start_DateTime": start_dt.isoformat(sep=" ", timespec="minutes"),
                        "End_DateTime": end_dt.isoformat(sep=" ", timespec="minutes"),
                        "Estimated_Hours": estimated_hours,
                        "Actual_Hours": 0.0,
                        "Remaining_Hours": estimated_hours,
                        "Expected_Completion": end_dt.isoformat(sep=" ", timespec="minutes"),
                        "Actual_Completion": "",
                        "Completion_Level": completion_level(progress),
                        "Dependency_Task_ID": "" if dependency == "None" else dependency,
                        "Client_or_Project_Owner": client,
                        "Remarks": remarks,
                        "Created_At": datetime.now().isoformat(sep=" ", timespec="minutes"),
                    }
                    save_task(row, is_new=True)
                    log_activity(st.session_state.current_user, "Task Created", new_id, "-", task_name,
                                 f"New task created and assigned to {assigned_person}")
                    st.success(f"✅ Task {new_id} added successfully.")
                    st.rerun()

    with tab2:
        st.subheader("Edit or Delete Task")
        task_ids = tasks_df["Task_ID"].tolist()
        if task_ids:
            selected_id = st.selectbox("Select Task ID", task_ids)
            row = tasks_df[tasks_df["Task_ID"] == selected_id].iloc[0]

            with st.form("edit_task_form"):
                c1, c2, c3 = st.columns(3)
                with c1:
                    new_person = st.selectbox("Assigned Person", sorted(staff_df["Staff_Name"].unique()),
                                               index=list(sorted(staff_df["Staff_Name"].unique())).index(row["Assigned_Person"]) if row["Assigned_Person"] in staff_df["Staff_Name"].values else 0)
                    new_priority = st.selectbox("Priority", PRIORITIES, index=PRIORITIES.index(row["Priority"]) if row["Priority"] in PRIORITIES else 0)
                with c2:
                    new_status = st.selectbox("Status", STATUSES, index=STATUSES.index(row["Status"]) if row["Status"] in STATUSES else 0)
                    new_process = st.selectbox("Current Process", PROCESS_STAGES, index=PROCESS_STAGES.index(row["Current_Process"]) if row["Current_Process"] in PROCESS_STAGES else 0)
                with c3:
                    new_progress = st.slider("Progress %", 0, 100, int(row["Progress_Percentage"]))
                    new_remarks = st.text_input("Remarks", value=row["Remarks"] or "-")

                c4, c5 = st.columns(2)
                with c4:
                    new_end_date = st.date_input("New Deadline Date", value=row["End_DateTime"].date())
                with c5:
                    new_end_time = st.time_input("New Deadline Time", value=row["End_DateTime"].time())

                col_update, col_delete = st.columns(2)
                update_btn = col_update.form_submit_button("💾 Update Task")
                delete_btn = col_delete.form_submit_button("🗑️ Delete Task")

                if update_btn:
                    new_end_dt = datetime.combine(new_end_date, new_end_time)
                    if new_end_dt <= row["Start_DateTime"]:
                        st.error("❌ Deadline must be after start time.")
                    else:
                        actual_completion = datetime.now().isoformat(sep=" ", timespec="minutes") if new_status == "Completed" else row["Actual_Completion"]
                        updated_row = {
                            "Task_ID": selected_id,
                            "Task_Name": row["Task_Name"], "Task_Description": row["Task_Description"],
                            "Assigned_Person": new_person, "Team": row["Team"], "Department": row["Department"],
                            "Sector": row["Sector"], "Project_Name": row["Project_Name"], "Task_Type": row["Task_Type"],
                            "Priority": new_priority, "Status": new_status, "Progress_Percentage": new_progress,
                            "Current_Process": new_process,
                            "Start_DateTime": row["Start_DateTime"].isoformat(sep=" ", timespec="minutes"),
                            "End_DateTime": new_end_dt.isoformat(sep=" ", timespec="minutes"),
                            "Estimated_Hours": row["Estimated_Hours"], "Actual_Hours": row["Actual_Hours"],
                            "Remaining_Hours": max(0, (new_end_dt - datetime.now()).total_seconds() / 3600),
                            "Expected_Completion": new_end_dt.isoformat(sep=" ", timespec="minutes"),
                            "Actual_Completion": actual_completion,
                            "Completion_Level": completion_level(new_progress),
                            "Dependency_Task_ID": row["Dependency_Task_ID"],
                            "Client_or_Project_Owner": row["Client_or_Project_Owner"],
                            "Remarks": new_remarks, "Created_At": row["Created_At"].isoformat(sep=" ", timespec="minutes"),
                        }
                        save_task(updated_row, is_new=False)
                        log_activity(st.session_state.current_user, "Task Updated", selected_id,
                                     f"Status:{row['Status']}, Progress:{row['Progress_Percentage']}%",
                                     f"Status:{new_status}, Progress:{new_progress}%", "Task updated via form")
                        st.success("✅ Task updated.")
                        st.rerun()

                if delete_btn:
                    delete_task_db(selected_id)
                    log_activity(st.session_state.current_user, "Task Deleted", selected_id,
                                 row["Task_Name"], "-", "Task removed")
                    st.warning(f"🗑️ Task {selected_id} deleted.")
                    st.rerun()
        else:
            st.info("No tasks available.")

    with tab3:
        st.subheader("All Tasks")
        filtered_all = filter_panel(tasks_df, "alltasks")
        display_cols = ["Task_ID", "Task_Name", "Assigned_Person", "Sector", "Project_Name",
                         "Priority", "Effective_Status", "Progress_Percentage", "Start_DateTime",
                         "End_DateTime", "Remaining_Hours_Live", "Completion_Level"]
        st.dataframe(filtered_all[display_cols], use_container_width=True, height=450)
        export_buttons(filtered_all, "all_tasks_export")


# ============================================================
# 14. PAGE: STAFF MANAGEMENT
# ============================================================

elif page == "Staff Management":
    st.title("👥 Staff Management")
    tab1, tab2 = st.tabs(["➕ Add Staff", "📋 Staff Directory"])

    with tab1:
        with st.form("add_staff_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                s_name = st.text_input("Staff Name*")
                s_sector = st.selectbox("Sector*", SECTORS)
                s_dept = st.selectbox("Department*", DEPARTMENTS[s_sector])
                s_team = st.selectbox("Team*", TEAMS)
            with c2:
                s_designation = st.selectbox("Designation*", DESIGNATIONS)
                s_skill = st.selectbox("Primary Skill*", SKILLS)
                s_hours = st.number_input("Total Working Hours (period)", min_value=1.0, value=160.0)
                s_avail = st.selectbox("Availability Status", ["Available", "Busy", "On Leave"])

            if st.form_submit_button("Add Staff"):
                if not s_name.strip():
                    st.error("❌ Staff Name required.")
                else:
                    conn = get_connection()
                    count = pd.read_sql("SELECT COUNT(*) c FROM staff", conn).iloc[0]["c"]
                    new_id = f"EMP{count + 1:04d}"
                    conn.execute("""INSERT INTO staff VALUES (?,?,?,?,?,?,?,?,?)""",
                                 (new_id, s_name, s_team, s_dept, s_sector, s_designation, s_skill, s_hours, s_avail))
                    conn.commit()
                    conn.close()
                    log_activity(st.session_state.current_user, "Staff Added", "-", "-", s_name, "New staff member added")
                    st.success(f"✅ Staff {new_id} - {s_name} added.")
                    st.rerun()

    with tab2:
        merged = staff_metrics_df.copy()
        st.dataframe(merged, use_container_width=True, height=450)
        export_buttons(merged, "staff_directory_export")

        st.subheader("Staff Detail")
        sel_staff = st.selectbox("Select Staff Member", sorted(staff_df["Staff_Name"].unique()))
        s_row = merged[merged["Staff_Name"] == sel_staff]
        if not s_row.empty:
            s_row = s_row.iloc[0]
            c1, c2, c3, c4 = st.columns(4)
            kpi_card(c1, "Assigned Tasks", s_row["Assigned_Tasks"])
            kpi_card(c2, "Completed", s_row["Completed_Tasks"])
            kpi_card(c3, "Overdue", s_row["Overdue_Tasks"])
            kpi_card(c4, "Productivity", f"{s_row['Productivity_%']}%")

            person_tasks = tasks_df[tasks_df["Assigned_Person"] == sel_staff]
            st.write("**Task History**")
            st.dataframe(person_tasks[["Task_ID", "Task_Name", "Priority", "Effective_Status",
                                        "Progress_Percentage", "Start_DateTime", "End_DateTime"]],
                         use_container_width=True)

            fig = px.pie(person_tasks, names="Effective_Status", title=f"{sel_staff} — Task Status Breakdown")
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Workload Classification")
        fig = px.histogram(merged, x="Workload_Class", color="Workload_Class",
                            title="Staff Workload Distribution")
        st.plotly_chart(fig, use_container_width=True)

        overloaded = merged[merged["Workload_Class"] == "Overloaded"]
        if not overloaded.empty:
            st.warning(f"⚠️ {len(overloaded)} staff member(s) are Overloaded:")
            st.dataframe(overloaded[["Staff_Name", "Utilization_%", "Assigned_Tasks", "Overdue_Tasks"]])


# ============================================================
# 15. PAGE: PROJECT MANAGEMENT
# ============================================================

elif page == "Project Management":
    st.title("📁 Project Management")

    proj_summary = []
    for p in projects_df["Project_Name"].unique():
        pt = tasks_df[tasks_df["Project_Name"] == p]
        total = len(pt)
        completed = len(pt[pt["Effective_Status"] == "Completed"])
        in_progress = len(pt[pt["Effective_Status"] == "In Progress"])
        pending = len(pt[pt["Effective_Status"].isin(["Not Started", "Assigned", "On Hold"])])
        overdue = len(pt[pt["Effective_Status"] == "Overdue"])
        progress_pct = round(pt["Progress_Percentage"].mean(), 1) if total else 0
        est = pt["Estimated_Hours"].sum()
        act = pt["Actual_Hours"].sum()
        rem = pt["Remaining_Hours_Live"].clip(lower=0).sum()

        if overdue > 0 or progress_pct < 30:
            health = "Red"
        elif progress_pct < 70:
            health = "Yellow"
        else:
            health = "Green"

        proj_summary.append({
            "Project": p, "Total_Tasks": total, "Completed": completed, "In_Progress": in_progress,
            "Pending": pending, "Overdue": overdue, "Progress_%": progress_pct,
            "Estimated_Hours": round(est, 1), "Actual_Hours": round(act, 1),
            "Remaining_Hours": round(rem, 1), "Health": health
        })

    proj_df = pd.DataFrame(proj_summary)
    health_color = {"Green": "🟢", "Yellow": "🟡", "Red": "🔴"}
    proj_df["Health"] = proj_df["Health"].apply(lambda h: f"{health_color[h]} {h}")

    st.dataframe(proj_df, use_container_width=True, height=400)
    export_buttons(proj_df, "project_dashboard_export")

    fig = px.bar(proj_df, x="Project", y=["Completed", "In_Progress", "Pending", "Overdue"],
                 barmode="stack", title="Project Task Breakdown")
    st.plotly_chart(fig, use_container_width=True)

    sel_project = st.selectbox("View Project Detail", projects_df["Project_Name"].unique())
    pdetail = tasks_df[tasks_df["Project_Name"] == sel_project]
    st.dataframe(pdetail[["Task_ID", "Task_Name", "Assigned_Person", "Priority",
                           "Effective_Status", "Progress_Percentage", "End_DateTime"]],
                use_container_width=True)


# ============================================================
# 16. PAGE: SECTOR ANALYTICS
# ============================================================

elif page == "Sector Analytics":
    st.title("🏭 Sector Analytics")
    sel_sector = st.selectbox("Select Sector", ["All"] + SECTORS)
    sdf = tasks_df if sel_sector == "All" else tasks_df[tasks_df["Sector"] == sel_sector]
    sstaff = staff_df if sel_sector == "All" else staff_df[staff_df["Sector"] == sel_sector]

    c1, c2, c3, c4 = st.columns(4)
    kpi_card(c1, "Total Employees", sstaff["Staff_Name"].nunique())
    kpi_card(c2, "Total Tasks", len(sdf))
    kpi_card(c3, "Completed", len(sdf[sdf["Effective_Status"] == "Completed"]))
    kpi_card(c4, "Overdue", len(sdf[sdf["Effective_Status"] == "Overdue"]))

    comp_rate = round(len(sdf[sdf["Effective_Status"] == "Completed"]) / len(sdf) * 100, 1) if len(sdf) else 0
    st.metric("Completion Rate", f"{comp_rate}%")

    sector_compare = tasks_df.groupby("Sector").agg(
        Total_Tasks=("Task_ID", "count"),
        Completed=("Effective_Status", lambda x: (x == "Completed").sum()),
        Overdue=("Effective_Status", lambda x: (x == "Overdue").sum()),
        Avg_Progress=("Progress_Percentage", "mean")
    ).reset_index()

    fig = px.bar(sector_compare, x="Sector", y="Total_Tasks", title="Tasks per Sector", color="Sector")
    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.line(sector_compare, x="Sector", y="Avg_Progress", markers=True, title="Average Progress by Sector")
    st.plotly_chart(fig2, use_container_width=True)

    fig3 = px.treemap(tasks_df, path=["Sector", "Department"], values="Estimated_Hours",
                       title="Sector → Department Hours Treemap")
    st.plotly_chart(fig3, use_container_width=True)


# ============================================================
# 17. PAGE: DEPARTMENT ANALYTICS
# ============================================================

elif page == "Department Analytics":
    st.title("🏢 Department Analytics")
    sel_dept = st.selectbox("Select Department", ["All"] + sorted(tasks_df["Department"].unique()))
    ddf = tasks_df if sel_dept == "All" else tasks_df[tasks_df["Department"] == sel_dept]

    c1, c2, c3, c4 = st.columns(4)
    kpi_card(c1, "Total Tasks", len(ddf))
    kpi_card(c2, "Active", len(ddf[ddf["Effective_Status"].isin(["In Progress", "Assigned"])]))
    kpi_card(c3, "Overdue", len(ddf[ddf["Effective_Status"] == "Overdue"]))
    kpi_card(c4, "Avg Progress", f"{round(ddf['Progress_Percentage'].mean(),1) if len(ddf) else 0}%")

    dept_compare = tasks_df.groupby("Department").agg(
        Total=("Task_ID", "count"),
        Completed=("Effective_Status", lambda x: (x == "Completed").sum())
    ).reset_index()
    fig = px.bar(dept_compare, x="Department", y=["Total", "Completed"], barmode="group",
                 title="Department Performance Comparison")
    st.plotly_chart(fig, use_container_width=True)

    heat = tasks_df.pivot_table(index="Department", columns="Priority", values="Task_ID", aggfunc="count", fill_value=0)
    fig2 = px.imshow(heat, text_auto=True, title="Department vs Priority Heatmap", aspect="auto")
    st.plotly_chart(fig2, use_container_width=True)


# ============================================================
# 18. PAGE: STAFF PERFORMANCE
# ============================================================

elif page == "Staff Performance":
    st.title("🏆 Staff Performance")

    top_perf = staff_metrics_df.sort_values("Productivity_%", ascending=False).head(15)
    fig = px.bar(top_perf, x="Productivity_%", y="Staff_Name", orientation="h",
                 title="Top 15 Staff by Productivity %", color="Productivity_%")
    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.scatter(staff_metrics_df, x="Utilization_%", y="Productivity_%", size="Assigned_Tasks",
                       color="Workload_Class", hover_name="Staff_Name",
                       title="Utilization vs Productivity")
    st.plotly_chart(fig2, use_container_width=True)

    fig3 = px.bar(staff_metrics_df.sort_values("Overdue_Tasks", ascending=False).head(15),
                  x="Overdue_Tasks", y="Staff_Name", orientation="h", title="Top Overdue Task Counts by Staff")
    st.plotly_chart(fig3, use_container_width=True)

    st.dataframe(staff_metrics_df, use_container_width=True, height=400)
    export_buttons(staff_metrics_df, "staff_performance_export")


# ============================================================
# 19. PAGE: TASK HISTORY (Previous Tasks)
# ============================================================

elif page == "Task History":
    st.title("🕓 Task History — Previous Tasks")
    hist_df = tasks_df[tasks_df["Effective_Status"].isin(["Completed", "Cancelled"])]
    filtered_hist = filter_panel(hist_df, "hist")

    c1, c2 = st.columns(2)
    kpi_card(c1, "Completed Tasks", len(filtered_hist[filtered_hist["Effective_Status"] == "Completed"]))
    kpi_card(c2, "Cancelled Tasks", len(filtered_hist[filtered_hist["Effective_Status"] == "Cancelled"]))

    st.dataframe(filtered_hist[["Task_ID", "Task_Name", "Assigned_Person", "Project_Name",
                                 "Effective_Status", "Start_DateTime", "End_DateTime",
                                 "Actual_Completion", "Actual_Hours"]], use_container_width=True, height=400)
    export_buttons(filtered_hist, "task_history_export")


# ============================================================
# 20. PAGE: FUTURE TASKS
# ============================================================

elif page == "Future Tasks":
    st.title("📅 Future / Upcoming Tasks")
    future_df = tasks_df[tasks_df["Start_DateTime"] > pd.Timestamp.now()]
    filtered_future = filter_panel(future_df, "future")

    st.dataframe(filtered_future[["Task_ID", "Task_Name", "Assigned_Person", "Project_Name",
                                   "Priority", "Start_DateTime", "End_DateTime", "Status"]],
                use_container_width=True, height=400)

    fig = px.timeline(filtered_future.head(40), x_start="Start_DateTime", x_end="End_DateTime",
                       y="Task_Name", color="Priority", title="Upcoming Task Timeline (Top 40)")
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)
    export_buttons(filtered_future, "future_tasks_export")


# ============================================================
# 21. PAGE: REPORTS
# ============================================================

elif page == "Reports":
    st.title("📑 Executive Reports")

    st.subheader("Overall Task Performance")
    total = len(tasks_df)
    completed = len(tasks_df[tasks_df["Effective_Status"] == "Completed"])
    st.write(f"- Total Tasks: **{total}**")
    st.write(f"- Completed: **{completed}** ({round(completed/total*100,1) if total else 0}%)")
    st.write(f"- Overdue: **{len(tasks_df[tasks_df['Effective_Status']=='Overdue'])}**")
    st.write(f"- Average Progress: **{round(tasks_df['Progress_Percentage'].mean(),1)}%**")

    st.subheader("Employee Performance Summary")
    st.dataframe(staff_metrics_df.sort_values("Productivity_%", ascending=False), use_container_width=True)

    st.subheader("Department Performance Summary")
    dept_perf = tasks_df.groupby("Department").agg(
        Total_Tasks=("Task_ID", "count"),
        Completed=("Effective_Status", lambda x: (x == "Completed").sum()),
        Overdue=("Effective_Status", lambda x: (x == "Overdue").sum()),
        Avg_Progress=("Progress_Percentage", "mean")
    ).reset_index()
    st.dataframe(dept_perf, use_container_width=True)

    st.subheader("Sector Performance Summary")
    sector_perf = tasks_df.groupby("Sector").agg(
        Total_Tasks=("Task_ID", "count"),
        Completed=("Effective_Status", lambda x: (x == "Completed").sum()),
        Overdue=("Effective_Status", lambda x: (x == "Overdue").sum()),
        Avg_Progress=("Progress_Percentage", "mean")
    ).reset_index()
    st.dataframe(sector_perf, use_container_width=True)

    st.subheader("Project Performance Summary")
    proj_perf = tasks_df.groupby("Project_Name").agg(
        Total_Tasks=("Task_ID", "count"),
        Completed=("Effective_Status", lambda x: (x == "Completed").sum()),
        Avg_Progress=("Progress_Percentage", "mean")
    ).reset_index()
    st.dataframe(proj_perf, use_container_width=True)

    st.subheader("Overdue Analysis")
    overdue_df = tasks_df[tasks_df["Effective_Status"] == "Overdue"]
    st.dataframe(overdue_df[["Task_ID", "Task_Name", "Assigned_Person", "Sector", "End_DateTime"]],
                use_container_width=True)

    st.markdown("---")
    st.subheader("Download Executive Summary")
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        staff_metrics_df.to_excel(writer, index=False, sheet_name="Employee Performance")
        dept_perf.to_excel(writer, index=False, sheet_name="Department Performance")
        sector_perf.to_excel(writer, index=False, sheet_name="Sector Performance")
        proj_perf.to_excel(writer, index=False, sheet_name="Project Performance")
        overdue_df.to_excel(writer, index=False, sheet_name="Overdue Analysis")
    st.download_button("⬇️ Download Executive Summary (Excel)", buf.getvalue(),
                        "executive_summary.xlsx",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


# ============================================================
# 22. PAGE: ACTIVITY LOGS
# ============================================================

elif page == "Activity Logs":
    st.title("📜 Activity Logs / Audit Trail")
    logs_df = load_logs()
    st.dataframe(logs_df, use_container_width=True, height=500)
    export_buttons(logs_df, "activity_logs_export")


# ============================================================
# 23. PAGE: SETTINGS
# ============================================================

elif page == "Settings":
    st.title("⚙️ Settings")

    st.subheader("Current User")
    new_user = st.text_input("Set Current User Name", value=st.session_state.current_user)
    if st.button("Update User"):
        st.session_state.current_user = new_user
        st.success("✅ User updated.")

    st.subheader("Database Info")
    st.write(f"Database File: `{os.path.abspath(DB_PATH)}`")
    conn = get_connection()
    counts = {
        "Tasks": pd.read_sql("SELECT COUNT(*) c FROM tasks", conn).iloc[0]["c"],
        "Staff": pd.read_sql("SELECT COUNT(*) c FROM staff", conn).iloc[0]["c"],
        "Projects": pd.read_sql("SELECT COUNT(*) c FROM projects", conn).iloc[0]["c"],
        "Activity Logs": pd.read_sql("SELECT COUNT(*) c FROM activity_logs", conn).iloc[0]["c"],
    }
    conn.close()
    st.json(counts)

    st.subheader("⚠️ Danger Zone")
    if st.button("Regenerate Sample Data (Deletes existing tasks/staff/projects)"):
        conn = get_connection()
        conn.execute("DELETE FROM tasks")
        conn.execute("DELETE FROM staff")
        conn.execute("DELETE FROM projects")
        conn.commit()
        conn.close()
        seed_database_if_empty()
        log_activity(st.session_state.current_user, "Data Reset", "-", "-", "-", "Sample data regenerated")
        st.success("✅ Sample data regenerated.")
        st.rerun()
