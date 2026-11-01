import sqlite3
conn = sqlite3.connect(r'behavioral-agentic-ai\backend\data\app.db')
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
for t in c.fetchall():
    print(t[0])

