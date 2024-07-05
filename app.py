import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Connect to the SQLite database
conn = sqlite3.connect('tasks.db')
c = conn.cursor()

# Create the tasks table if it does not exist
c.execute('''CREATE TABLE IF NOT EXISTS tasks (task TEXT, status TEXT, due_date TEXT, priority TEXT, completed TEXT DEFAULT 'No')''')
conn.commit()

# Add the 'completed' column to the tasks table if it does not exist
c.execute("PRAGMA table_info(tasks)")
columns = [col[1] for col in c.fetchall()]
if 'completed' not in columns:
    c.execute("ALTER TABLE tasks ADD COLUMN completed TEXT DEFAULT 'No'")
    conn.commit()

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["To-Do List", "Dashboard"])

def todo_list():
    st.title("To-Do List")
    task = st.text_input("Enter a task")
    status = st.selectbox("Select status", ["Pending", "In Progress"])
    due_date = st.date_input("Select due date")
    priority = st.radio("Select priority", ["Low", "Medium", "High"])

    if st.button("Add Task"):
        c.execute("INSERT INTO tasks (task, status, due_date, priority, completed) VALUES (?, ?, ?, ?, ?)",
                  (task, status, due_date.strftime('%Y-%m-%d'), priority, "No"))
        conn.commit()
        st.success(f"Task '{task}' added!")

    st.subheader("Your Tasks")
    tasks = pd.read_sql_query("SELECT rowid, * from tasks", conn)

    if tasks.empty:
        st.write("No tasks found")
        empty_df = pd.DataFrame(columns=["Task","Status","Due Date","Priority","Completed"])
        st.table(empty_df)
    else:
        col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
        with col1:
            st.write("Task")
        with col2:
            st.write("Status")
        with col3:
            st.write("Due Date")
        with col4:
            st.write("Priority")
        with col5:
            st.write("Completed")
        
        for index, row in tasks.iterrows():
            col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
            with col1:
                st.write(row['task'])
            with col2:
                st.write(row['status'])
            with col3:
                st.write(row['due_date'])
            with col4:
                st.write(row['priority'])
            with col5:
                if st.checkbox("", key=row['rowid']):
                    c.execute("DELETE FROM tasks WHERE rowid=?", (row['rowid'],))
                    conn.commit()
                    st.experimental_rerun()

    if st.button("Clear All Tasks"):
        c.execute("DELETE FROM tasks")
        conn.commit()
        st.warning("All tasks cleared!")
        st.experimental_rerun()

def dashboard():
    st.title("Dashboard")
    tasks = pd.read_sql_query("SELECT * from tasks", conn)
    st.subheader("Analytics Dashboard")
    status_counts = tasks['status'].value_counts()
    fig, ax = plt.subplots()
    ax.bar(status_counts.index, status_counts.values)
    ax.set_xlabel('Status')
    ax.set_ylabel('Number of Tasks')
    ax.set_title('Tasks Status Overview')
    st.pyplot(fig)

if page == "To-Do List":
    todo_list()
elif page == "Dashboard":
    dashboard()

conn.close()
