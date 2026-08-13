"""Enterprise Task Management & Executive Dashboard — Full-Feature Compact (<300 lines)"""
import streamlit as st, pandas as pd, numpy as np, sqlite3, plotly.express as px
from datetime import datetime, timedelta
import random, io, os

st.set_page_config("Enterprise TMS", "📊", layout="wide")
DB = "company_tasks.db"; random.seed(42); np.random.seed(42)

SECTORS = ["IT","Gaming","Software Development","Web Development","Mobile App Development","AI/ML",
    "Data Science","Cyber Security","Cloud/DevOps","Finance","HR","Marketing","Sales",
    "Customer Support","Operations","Administration","UI/UX","Software Testing/QA"]
TEAMS = ["Alpha","Bravo","Charlie","Delta","Echo","Falcon","Nova","Orion"]
PROJECTS = ["Gaming Platform Development","Mobile Banking Application","E-Commerce Platform",
    "HR Management System","AI Recommendation Engine","Customer Support Portal",
    "Cyber Security Monitoring System","Cloud Migration","Data Analytics Dashboard",
    "ERP Development","CRM Implementation","Website Redesign","Game Development",
    "Payment Gateway Integration"]
TASK_TYPES = ["Requirement Analysis","Design","Development","Coding","Testing","Bug Fixing",
    "Code Review","Deployment","Documentation","Client Review","Maintenance"]
PRIORITIES = ["Critical","High","Medium","Low"]
STATUSES = ["Not Started","Assigned","In Progress","On Hold","Under Review","Testing","Blocked",
    "Completed","Cancelled","Overdue"]
PROCESS_STAGES = ["Planning","Requirement Analysis","Design","Development","Testing","Bug Fixing",
    "Code Review","Deployment","Documentation","Client Review","Completed"]
DESIGNATIONS = ["Junior Engineer","Senior Engineer","Team Lead","Manager","Analyst","Consultant"]
FIRST = ["Arjun","Priya","Karthik","Ananya","Vijay","Divya","Ramesh","Sneha","Suresh","Meena",
    "Kiran","Pooja","Ravi","Lakshmi","Naveen","Deepa","Manoj","Swathi","Ganesh","Aarti"]
LAST = ["Kumar","Sharma","Iyer","Reddy","Nair","Menon","Rao","Pillai","Gupta","Verma"]
CLIENTS = ["Acme Corp","Globex Industries","TechNova","Initech","Internal","Zenith Solutions"]
REMARKS = ["Progressing as planned","Waiting for client feedback","On schedule","Needs resources","-"]

def conn(): return sqlite3.connect(DB, check_same_thread=False)

def init_db():
    c = conn()
    c.execute("""CREATE TABLE IF NOT EXISTS staff(Staff_ID TEXT PRIMARY KEY, Staff_Name TEXT,
        Team TEXT, Department TEXT, Sector TEXT, Designation TEXT, Total_Working_Hours REAL,
        Availability_Status TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS tasks(Task_ID TEXT PRIMARY KEY, Task_Name TEXT,
        Task_Description TEXT, Assigned_Person TEXT, Team TEXT, Department TEXT, Sector TEXT,
        Project_Name TEXT, Task_Type TEXT, Priority TEXT, Status TEXT, Progress_Percentage INTEGER,
        Current_Process TEXT, Start_DateTime TEXT, End_DateTime TEXT, Estimated_Hours REAL,
        Actual_Hours REAL, Completion_Level TEXT, Client_or_Project_Owner TEXT, Remarks TEXT,
        Created_At TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS logs(Log_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Timestamp TEXT, User TEXT, Action TEXT, Task_ID TEXT, Description TEXT)""")
    c.commit(); c.close()

def log(user, action, tid, desc):
    c = conn(); c.execute("INSERT INTO logs(Timestamp,User,Action,Task_ID,Description) VALUES(?,?,?,?,?)",
        (datetime.now().isoformat(sep=" ", timespec="seconds"), user, action, tid, desc))
    c.commit(); c.close()

def level(p): return "Low" if p<=30 else "Medium" if p<=70 else "High"

def gen_staff(n=45):
    rows, used = [], set()
    for i in range(1, n+1):
        sector = random.choice(SECTORS)
        while True:
            name = f"{random.choice(FIRST)} {random.choice(LAST)}"
            if name not in used: used.add(name); break
        rows.append((f"EMP{i:04d}", name, random.choice(TEAMS), sector+" Dept", sector,
            random.choice(DESIGNATIONS), round(random.uniform(120,220),1),
            random.choice(["Available","Available","Busy","On Leave"])))
    return rows

def gen_tasks(n, staff):
    rows, now = [], datetime.now()
    for i in range(1, n+1):
        s = random.choice(staff)
        sector, dept, team, person = s[4], s[3], s[2], s[1]
        project, ttype = random.choice(PROJECTS), random.choice(TASK_TYPES)
        bucket = random.choices(["past","current","future"], weights=[.35,.35,.3])[0]
        est = round(random.uniform(4,80),1)
        if bucket == "past":
            start = now - timedelta(days=random.randint(15,120))
            end = start + timedelta(hours=est)
            status = random.choices(["Completed","Cancelled"], weights=[.85,.15])[0]
            progress = 100 if status=="Completed" else random.randint(10,90)
            actual = round(est*random.uniform(.8,1.3),1)
        elif bucket == "current":
            start = now - timedelta(days=random.randint(0,10))
            end = now + timedelta(days=random.randint(0,10), hours=random.randint(1,12))
            status = random.choices(["In Progress","Assigned","On Hold","Under Review","Testing"],
                weights=[.4,.15,.1,.2,.15])[0]
            progress = random.randint(5,95)
            actual = round(est*random.uniform(.2,.9),1)
            if random.random() < 0.25:
                end = now - timedelta(hours=random.randint(1,72)); status = "Overdue"
        else:
            start = now + timedelta(days=random.randint(1,45))
            end = start + timedelta(hours=est)
            status, progress, actual = random.choice(["Not Started","Assigned"]), 0, 0.0
        process = "Completed" if status=="Completed" else random.choice(PROCESS_STAGES[:-1])
        rows.append((f"TSK{i:04d}", f"{ttype} - {project}", f"{ttype} work for {project}",
            person, team, dept, sector, project, ttype,
            random.choices(PRIORITIES, weights=[.15,.3,.35,.2])[0], status, progress, process,
            start.isoformat(sep=" ", timespec="minutes"), end.isoformat(sep=" ", timespec="minutes"),
            est, actual, level(progress), random.choice(CLIENTS), random.choice(REMARKS),
            (start-timedelta(days=random.randint(0,5))).isoformat(sep=" ", timespec="minutes")))
    return rows

def seed():
    c = conn()
    if pd.read_sql("SELECT COUNT(*) n FROM tasks", c).iloc[0]["n"] == 0:
        staff = gen_staff(45)
        c.executemany("INSERT INTO staff VALUES(?,?,?,?,?,?,?,?)", staff)
        c.executemany("INSERT INTO tasks VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            gen_tasks(200, staff))
        c.commit(); log("System","Seed","-","Initial 200 tasks generated")
    c.close()

def load(t):
    c = conn(); df = pd.read_sql(f"SELECT * FROM {t}", c); c.close()
    for col in ["Start_DateTime","End_DateTime","Created_At"]:
        if col in df.columns: df[col] = pd.to_datetime(df[col])
    return df

def live(df):
    now = pd.Timestamp.now(); df = df.copy()
    df["Remaining_Hours"] = (df["End_DateTime"]-now).dt.total_seconds()/3600
    df["Duration_Hours"] = (df["End_DateTime"]-df["Start_DateTime"]).dt.total_seconds()/3600
    df["Effective_Status"] = np.where(df["Status"].isin(["Completed","Cancelled"]), df["Status"],
        np.where(df["End_DateTime"]<now, "Overdue", df["Status"]))
    def alert(r):
        if r["Effective_Status"]=="Overdue": return "Overdue"
        h = r["Remaining_Hours"]
        return "Critical" if h<=1 else "Warning" if h<=4 else "Upcoming" if h<=24 else "Normal"
    df["Alert"] = df.apply(alert, axis=1)
    return df

def staff_metrics(tasks, staff):
    rows = []
    for _, s in staff.iterrows():
        t = tasks[tasks["Assigned_Person"]==s["Staff_Name"]]
        assigned, completed = len(t), len(t[t["Effective_Status"]=="Completed"])
        overdue = len(t[t["Effective_Status"]=="Overdue"])
        act, est = t["Actual_Hours"].sum(), t["Estimated_Hours"].sum()
        util = min(100, round(act/s["Total_Working_Hours"]*100,1)) if s["Total_Working_Hours"] else 0
        prod = round(completed/assigned*100,1) if assigned else 0
        wc = "Underutilized" if util<40 else "Normal" if util<75 else "High Workload" if util<95 else "Overloaded"
        rows.append({"Staff_Name": s["Staff_Name"], "Sector": s["Sector"], "Department": s["Department"],
            "Team": s["Team"], "Designation": s["Designation"], "Assigned_Tasks": assigned,
            "Completed_Tasks": completed, "Overdue_Tasks": overdue, "Estimated_Hours": round(est,1),
            "Actual_Hours": round(act,1), "Utilization_%": util, "Productivity_%": prod,
            "Workload_Class": wc, "Availability_Status": s["Availability_Status"]})
    return pd.DataFrame(rows)

def kpi_row(items):
    for col, (label, val) in zip(st.columns(len(items)), items):
        col.metric(label, val)

def export(df, name):
    c1, c2 = st.columns(2)
    c1.download_button("⬇️ CSV", df.to_csv(index=False).encode(), f"{name}.csv")
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w: df.to_excel(w, index=False)
    c2.download_button("⬇️ Excel", buf.getvalue(), f"{name}.xlsx")

def search_box(df, key):
    q = st.text_input("🔎 Search (ID, Name, Person, Project, Client)", key=key)
    if q:
        s = q.lower()
        df = df[df["Task_ID"].str.lower().str.contains(s) | df["Task_Name"].str.lower().str.contains(s) |
            df["Assigned_Person"].str.lower().str.contains(s) | df["Project_Name"].str.lower().str.contains(s) |
            df["Client_or_Project_Owner"].str.lower().str.contains(s)]
    return df

# ---------- INIT ----------
init_db(); seed()
if "user" not in st.session_state: st.session_state.user = "Admin"

st.sidebar.title("📊 Enterprise TMS")
st.sidebar.caption(f"User: **{st.session_state.user}**")
page = st.sidebar.radio("Navigate", ["Executive Dashboard","Live Task Monitor","Task Management",
    "Staff Management","Project Management","Sector Analytics","Department Analytics",
    "Staff Performance","Task History","Future Tasks","Reports","Activity Logs","Settings"])

st.sidebar.markdown("---")
auto_refresh = st.sidebar.toggle("🔁 Auto-Refresh", value=True)
refresh_interval = st.sidebar.selectbox("Interval (sec)", [10,30,60], index=1, disabled=not auto_refresh)
if st.sidebar.button("🔄 Refresh Now"): st.rerun()
st.sidebar.caption(f"⏱️ ON every {refresh_interval}s" if auto_refresh else "⏸️ Auto-refresh OFF")
if auto_refresh and page in ("Executive Dashboard","Live Task Monitor"):
    st.markdown(f"<meta http-equiv='refresh' content='{refresh_interval}'>", unsafe_allow_html=True)

tasks_df = live(load("tasks")); staff_df = load("staff")
metrics_df = staff_metrics(tasks_df, staff_df)

# ---------- EXECUTIVE DASHBOARD ----------
if page == "Executive Dashboard":
    st.title("📈 Executive Dashboard"); st.caption(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    total = len(tasks_df); completed = len(tasks_df[tasks_df.Effective_Status=="Completed"])
    overdue = len(tasks_df[tasks_df.Effective_Status=="Overdue"])
    active = len(tasks_df[tasks_df.Effective_Status.isin(["In Progress","Assigned"])])
    critical = len(tasks_df[tasks_df.Priority=="Critical"])
    kpi_row([("Total", total), ("Completed", completed), ("Active", active), ("Overdue", overdue),
        ("Critical", critical), ("Completion %", f"{round(completed/total*100,1) if total else 0}%")])
    kpi_row([("Staff", staff_df.Staff_Name.nunique()), ("Projects", tasks_df.Project_Name.nunique()),
        ("Avg Productivity", f"{round(metrics_df.Productivity_%.mean(),1)}%"),
        ("Avg Utilization", f"{round(metrics_df['Utilization_%'].mean(),1)}%")])
    c1, c2, c3 = st.columns(3)
    c1.plotly_chart(px.pie(tasks_df, names="Effective_Status", title="Status", hole=.4), use_container_width=True)
    c2.plotly_chart(px.pie(tasks_df, names="Priority", title="Priority", hole=.4), use_container_width=True)
    c3.plotly_chart(px.pie(tasks_df, names="Completion_Level", title="Completion Level", hole=.4), use_container_width=True)
    c4, c5 = st.columns(2)
    c4.plotly_chart(px.bar(tasks_df.Sector.value_counts().reset_index(), x="count", y="Sector",
        orientation="h", title="Tasks by Sector"), use_container_width=True)
    c5.plotly_chart(px.bar(tasks_df.Assigned_Person.value_counts().head(15).reset_index(),
        x="count", y="Assigned_Person", orientation="h", title="Top 15 Staff by Tasks"), use_container_width=True)
    hrs = tasks_df.groupby("Sector")[["Estimated_Hours","Actual_Hours"]].sum().reset_index()
    st.plotly_chart(px.bar(hrs, x="Sector", y=["Estimated_Hours","Actual_Hours"], barmode="group",
        title="Estimated vs Actual Hours"), use_container_width=True)
    st.subheader("High-Risk Tasks")
    st.dataframe(tasks_df[tasks_df.Alert.isin(["Critical","Overdue","Warning"])][
        ["Task_ID","Task_Name","Assigned_Person","Priority","Alert","Progress_Percentage","End_DateTime"]],
        use_container_width=True)
    export(tasks_df, "dashboard_export")

# ---------- LIVE MONITOR ----------
elif page == "Live Task Monitor":
    st.title("🟢 Live Task Monitor"); st.caption(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    lt = tasks_df[~tasks_df.Effective_Status.isin(["Completed","Cancelled"])].copy()
    order = {"Critical":0,"Overdue":1,"Warning":2,"Upcoming":3,"Normal":4}
    lt = lt.sort_values(by="Alert", key=lambda s: s.map(order))
    kpi_row([("Critical", len(lt[lt.Alert=="Critical"])), ("Warning", len(lt[lt.Alert=="Warning"])),
        ("Upcoming", len(lt[lt.Alert=="Upcoming"])), ("Overdue", len(lt[lt.Alert=="Overdue"]))])
    st.caption(f"Auto-refreshing every {refresh_interval}s" if auto_refresh else "Auto-refresh OFF")
    lt = search_box(lt, "live_search")
    for _, r in lt.head(50).iterrows():
        with st.container(border=True):
            c1, c2 = st.columns([3,2])
            c1.write(f"**{r.Task_Name}** ({r.Task_ID}) — {r.Priority} — **{r.Alert}**")
            c1.write(f"👤 {r.Assigned_Person} | {r.Current_Process} | {r.Sector}/{r.Department}")
            c2.progress(min(100,max(0,int(r.Progress_Percentage)))/100, text=f"{r.Progress_Percentage}%")
            rem = r.Remaining_Hours
            c2.caption(f"{'Deadline: '+str(r.End_DateTime)} | {f'{rem:.1f}h left' if rem>0 else 'Passed'}")

# ---------- TASK MANAGEMENT ----------
elif page == "Task Management":
    st.title("🗂️ Task Management")
    t1, t2, t3 = st.tabs(["Add", "Edit/Delete", "All Tasks"])
    with t1:
        with st.form("add", clear_on_submit=True):
            name = st.text_input("Task Name*")
            sector = st.selectbox("Sector", SECTORS); person = st.selectbox("Assigned Person", sorted(staff_df.Staff_Name))
            project = st.selectbox("Project", PROJECTS); priority = st.selectbox("Priority", PRIORITIES)
            status = st.selectbox("Status", STATUSES); progress = st.slider("Progress %", 0, 100, 0)
            c1, c2 = st.columns(2)
            sd, stt = c1.date_input("Start Date"), c1.time_input("Start Time")
            ed, et = c2.date_input("End Date", value=datetime.now()+timedelta(days=3)), c2.time_input("End Time")
            est = st.number_input("Estimated Hours", min_value=0.5, value=8.0)
            if st.form_submit_button("Add Task"):
                s_dt, e_dt = datetime.combine(sd, stt), datetime.combine(ed, et)
                if not name.strip(): st.error("Task name required")
                elif e_dt <= s_dt: st.error("End must be after start")
                else:
                    c = conn(); n = pd.read_sql("SELECT COUNT(*) c FROM tasks", c).iloc[0]["c"]
                    tid = f"TSK{n+1:04d}"
                    c.execute("INSERT INTO tasks VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (tid, name, name, person, TEAMS[0], sector+" Dept", sector, project, TASK_TYPES[0],
                         priority, status, progress, PROCESS_STAGES[0], s_dt.isoformat(sep=" ",timespec="minutes"),
                         e_dt.isoformat(sep=" ",timespec="minutes"), est, 0.0, level(progress), CLIENTS[0], "-",
                         datetime.now().isoformat(sep=" ",timespec="minutes")))
                    c.commit(); c.close()
                    log(st.session_state.user, "Task Created", tid, f"Assigned to {person}")
                    st.success(f"✅ {tid} added"); st.rerun()
    with t2:
        tid = st.selectbox("Task ID", tasks_df.Task_ID)
        row = tasks_df[tasks_df.Task_ID==tid].iloc[0]
        with st.form("edit"):
            status = st.selectbox("Status", STATUSES, index=STATUSES.index(row.Status))
            progress = st.slider("Progress %", 0, 100, int(row.Progress_Percentage))
            c1, c2 = st.columns(2)
            upd, dele = c1.form_submit_button("💾 Update"), c2.form_submit_button("🗑️ Delete")
            if upd:
                c = conn(); c.execute("UPDATE tasks SET Status=?, Progress_Percentage=?, Completion_Level=? WHERE Task_ID=?",
                    (status, progress, level(progress), tid)); c.commit(); c.close()
                log(st.session_state.user, "Task Updated", tid, f"Status={status}, Progress={progress}%")
                st.success("Updated"); st.rerun()
            if dele:
                c = conn(); c.execute("DELETE FROM tasks WHERE Task_ID=?", (tid,)); c.commit(); c.close()
                log(st.session_state.user, "Task Deleted", tid, "Removed"); st.warning("Deleted"); st.rerun()
    with t3:
        df = search_box(tasks_df, "all_search")
        st.dataframe(df[["Task_ID","Task_Name","Assigned_Person","Sector","Project_Name","Priority",
            "Effective_Status","Progress_Percentage","End_DateTime"]], use_container_width=True, height=420)
        export(df, "all_tasks")

# ---------- STAFF MANAGEMENT ----------
elif page == "Staff Management":
    st.title("👥 Staff Management")
    with st.form("add_staff", clear_on_submit=True):
        name = st.text_input("Name*"); sector = st.selectbox("Sector", SECTORS)
        desig = st.selectbox("Designation", DESIGNATIONS); hours = st.number_input("Working Hours", value=160.0)
        if st.form_submit_button("Add Staff") and name.strip():
            c = conn(); n = pd.read_sql("SELECT COUNT(*) c FROM staff", c).iloc[0]["c"]
            c.execute("INSERT INTO staff VALUES(?,?,?,?,?,?,?,?)",
                (f"EMP{n+1:04d}", name, TEAMS[0], sector+" Dept", sector, desig, hours, "Available"))
            c.commit(); c.close(); log(st.session_state.user,"Staff Added","-",name); st.success("Added"); st.rerun()
    st.dataframe(metrics_df, use_container_width=True, height=380); export(metrics_df, "staff_metrics")
    sel = st.selectbox("Staff Detail", sorted(staff_df.Staff_Name.unique()))
    pt = tasks_df[tasks_df.Assigned_Person==sel]
    st.dataframe(pt[["Task_ID","Task_Name","Priority","Effective_Status","Progress_Percentage","End_DateTime"]],
        use_container_width=True)
    overloaded = metrics_df[metrics_df.Workload_Class=="Overloaded"]
    if not overloaded.empty:
        st.warning(f"⚠️ {len(overloaded)} staff member(s) Overloaded")
        st.dataframe(overloaded[["Staff_Name","Utilization_%","Assigned_Tasks","Overdue_Tasks"]])

# ---------- PROJECT MANAGEMENT ----------
elif page == "Project Management":
    st.title("📁 Project Management")
    summary = []
    for p in tasks_df.Project_Name.unique():
        pt = tasks_df[tasks_df.Project_Name==p]
        completed, overdue = len(pt[pt.Effective_Status=="Completed"]), len(pt[pt.Effective_Status=="Overdue"])
        prog = round(pt.Progress_Percentage.mean(),1) if len(pt) else 0
        health = "🔴 Red" if overdue>0 or prog<30 else "🟡 Yellow" if prog<70 else "🟢 Green"
        summary.append({"Project": p, "Total": len(pt), "Completed": completed, "Overdue": overdue,
            "Progress_%": prog, "Health": health})
    pdf = pd.DataFrame(summary)
    st.dataframe(pdf, use_container_width=True)
    st.plotly_chart(px.bar(pdf, x="Project", y="Total", color="Health"), use_container_width=True)
    export(pdf, "project_summary")

# ---------- SECTOR / DEPARTMENT ANALYTICS (shared logic) ----------
elif page in ("Sector Analytics", "Department Analytics"):
    field = "Sector" if page == "Sector Analytics" else "Department"
    st.title(f"🏭 {page}")
    sel = st.selectbox(f"Select {field}", ["All"] + sorted(tasks_df[field].unique()))
    df = tasks_df if sel == "All" else tasks_df[tasks_df[field] == sel]
    kpi_row([("Total Tasks", len(df)), ("Completed", len(df[df.Effective_Status=="Completed"])),
        ("Overdue", len(df[df.Effective_Status=="Overdue"])),
        ("Avg Progress", f"{round(df.Progress_Percentage.mean(),1) if len(df) else 0}%")])
    cmp = tasks_df.groupby(field).agg(Total=("Task_ID","count"),
        Completed=("Effective_Status", lambda x:(x=="Completed").sum()),
        Overdue=("Effective_Status", lambda x:(x=="Overdue").sum())).reset_index()
    st.plotly_chart(px.bar(cmp, x=field, y=["Total","Completed","Overdue"], barmode="group",
        title=f"{field} Comparison"), use_container_width=True)
    heat = tasks_df.pivot_table(index=field, columns="Priority", values="Task_ID", aggfunc="count", fill_value=0)
    st.plotly_chart(px.imshow(heat, text_auto=True, title=f"{field} vs Priority", aspect="auto"), use_container_width=True)

# ---------- STAFF PERFORMANCE ----------
elif page == "Staff Performance":
    st.title("🏆 Staff Performance")
    st.plotly_chart(px.bar(metrics_df.sort_values("Productivity_%",ascending=False).head(15),
        x="Productivity_%", y="Staff_Name", orientation="h", title="Top 15 Productivity", color="Productivity_%"),
        use_container_width=True)
    st.plotly_chart(px.scatter(metrics_df, x="Utilization_%", y="Productivity_%", size="Assigned_Tasks",
        color="Workload_Class", hover_name="Staff_Name", title="Utilization vs Productivity"), use_container_width=True)
    st.dataframe(metrics_df, use_container_width=True, height=380); export(metrics_df, "staff_performance")

# ---------- TASK HISTORY ----------
elif page == "Task History":
    st.title("🕓 Task History")
    df = tasks_df[tasks_df.Effective_Status.isin(["Completed","Cancelled"])]
    kpi_row([("Completed", len(df[df.Effective_Status=="Completed"])),
        ("Cancelled", len(df[df.Effective_Status=="Cancelled"]))])
    st.dataframe(df[["Task_ID","Task_Name","Assigned_Person","Project_Name","Effective_Status",
        "Start_DateTime","End_DateTime","Actual_Hours"]], use_container_width=True, height=400)
    export(df, "task_history")

# ---------- FUTURE TASKS ----------
elif page == "Future Tasks":
    st.title("📅 Future / Upcoming Tasks")
    df = tasks_df[tasks_df.Start_DateTime > pd.Timestamp.now()]
    st.dataframe(df[["Task_ID","Task_Name","Assigned_Person","Project_Name","Priority","Start_DateTime",
        "End_DateTime","Status"]], use_container_width=True, height=400)
    fig = px.timeline(df.head(40), x_start="Start_DateTime", x_end="End_DateTime", y="Task_Name",
        color="Priority", title="Upcoming Timeline (Top 40)")
    fig.update_yaxes(autorange="reversed"); st.plotly_chart(fig, use_container_width=True)
    export(df, "future_tasks")

# ---------- REPORTS ----------
elif page == "Reports":
    st.title("📑 Executive Reports")
    total = len(tasks_df); completed = len(tasks_df[tasks_df.Effective_Status=="Completed"])
    st.write(f"Total: **{total}**, Completed: **{completed}** ({round(completed/total*100,1) if total else 0}%), "
        f"Overdue: **{len(tasks_df[tasks_df.Effective_Status=='Overdue'])}**")
    dept_perf = tasks_df.groupby("Department").agg(Total=("Task_ID","count"),
        Completed=("Effective_Status", lambda x:(x=="Completed").sum())).reset_index()
    sector_perf = tasks_df.groupby("Sector").agg(Total=("Task_ID","count"),
        Completed=("Effective_Status", lambda x:(x=="Completed").sum())).reset_index()
    st.subheader("Department Performance"); st.dataframe(dept_perf, use_container_width=True)
    st.subheader("Sector Performance"); st.dataframe(sector_perf, use_container_width=True)
    st.subheader("Staff Performance"); st.dataframe(metrics_df, use_container_width=True)
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        metrics_df.to_excel(w, index=False, sheet_name="Staff")
        dept_perf.to_excel(w, index=False, sheet_name="Department")
        sector_perf.to_excel(w, index=False, sheet_name="Sector")
    st.download_button("⬇️ Executive Summary (Excel)", buf.getvalue(), "executive_summary.xlsx")

# ---------- ACTIVITY LOGS ----------
elif page == "Activity Logs":
    st.title("📜 Activity Logs"); df = load("logs").sort_values("Log_ID", ascending=False)
    st.dataframe(df, use_container_width=True, height=450); export(df, "activity_logs")

# ---------- SETTINGS ----------
elif page == "Settings":
    st.title("⚙️ Settings")
    new_user = st.text_input("Current User", value=st.session_state.user)
    if st.button("Update User"): st.session_state.user = new_user; st.success("✅ Updated")
    c = conn()
    st.json({"Tasks": pd.read_sql("SELECT COUNT(*) c FROM tasks", c).iloc[0]["c"],
        "Staff": pd.read_sql("SELECT COUNT(*) c FROM staff", c).iloc[0]["c"],
        "Logs": pd.read_sql("SELECT COUNT(*) c FROM logs", c).iloc[0]["c"]})
    c.close()
    if st.button("⚠️ Regenerate Sample Data"):
        c = conn(); c.execute("DELETE FROM tasks"); c.execute("DELETE FROM staff"); c.commit(); c.close()
        seed(); log(st.session_state.user, "Data Reset", "-", "Regenerated")
        st.success("✅ Regenerated"); st.rerun()
