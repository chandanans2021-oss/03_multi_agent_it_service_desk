# 03 Multi-Agent IT Service Desk

Agent flow:
Employee Request
-> Manager Agent
-> Troubleshooting Agent
-> Knowledge Agent
-> Database Agent
-> Response Agent
-> Close Ticket / Human Escalation

Run:
1. `ollama pull llama3.2`
2. `pip install -r requirements.txt`
3. `python app.py`

This starter uses individual agent functions. CrewAI or LangGraph can later be added for advanced orchestration.
