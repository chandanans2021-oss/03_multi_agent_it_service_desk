import sqlite3
from flask import Flask, render_template, request
from langchain_ollama import ChatOllama

app = Flask(__name__)
DB = "service_desk.db"
llm = ChatOllama(model="llama3.2")

def init_db():
    conn = sqlite3.connect(DB)
    conn.execute("""CREATE TABLE IF NOT EXISTS tickets(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee TEXT, request TEXT, category TEXT,
        troubleshooting TEXT, knowledge TEXT,
        device_info TEXT, status TEXT, final_response TEXT
    )""")
    conn.commit()
    conn.close()

def ask_agent(role, task):
    prompt = f"""You are the {role} in an AI IT Service Desk.
Your responsibility: {task}
Give a concise useful result."""
    return llm.invoke(prompt).content

def manager_agent(user_request):
    return ask_agent("Manager Agent", f"""Classify and route this employee request:
{user_request}
Return the most suitable category and next action.""")

def troubleshooting_agent(user_request):
    return ask_agent("Troubleshooting Agent", f"""Provide technical troubleshooting steps for:
{user_request}""")

def knowledge_agent(user_request):
    return ask_agent("Knowledge Agent", f"""Search a simulated company knowledge base and provide relevant policy or troubleshooting guidance for:
{user_request}""")

def database_agent(employee):
    # Replace this simulated information with a real employee/device database.
    return f"Employee: {employee}. Device record: Company laptop assigned. VPN access: Active."

def response_agent(user_request, manager, troubleshooting, knowledge, database):
    prompt = f"""You are the Response Agent.
Prepare the final response for an IT support ticket.

Request: {user_request}
Manager result: {manager}
Troubleshooting: {troubleshooting}
Knowledge: {knowledge}
Database: {database}

State whether the problem is likely solved. If not, recommend human escalation.
"""
    return llm.invoke(prompt).content

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        employee = request.form["employee"]
        user_request = request.form["request"]

        manager = manager_agent(user_request)
        troubleshooting = troubleshooting_agent(user_request)
        knowledge = knowledge_agent(user_request)
        database = database_agent(employee)
        final_response = response_agent(
            user_request, manager, troubleshooting, knowledge, database
        )

        status = "Closed" if "solved" in final_response.lower() else "Human Escalation"

        conn = sqlite3.connect(DB)
        conn.execute("""INSERT INTO tickets
        (employee, request, category, troubleshooting, knowledge, device_info, status, final_response)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (employee, user_request, manager, troubleshooting, knowledge,
         database, status, final_response))
        conn.commit()
        conn.close()

        result = {
            "manager": manager,
            "troubleshooting": troubleshooting,
            "knowledge": knowledge,
            "database": database,
            "final": final_response,
            "status": status
        }

    return render_template("index.html", result=result)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
