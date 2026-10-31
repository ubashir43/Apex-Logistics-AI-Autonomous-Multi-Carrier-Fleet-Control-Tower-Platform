import sqlite3
conn = sqlite3.connect(r'behavioral-agentic-ai\backend\data\app.db')
c = conn.cursor()
c.execute("SELECT id, name, widget_api_key, is_active FROM tenants")
for t in c.fetchall():
    print(t)
