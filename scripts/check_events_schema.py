import sqlite3
conn = sqlite3.connect(r'behavioral-agentic-ai\backend\data\app.db')
c = conn.cursor()
c.execute("PRAGMA table_info(shipment_events)")
for col in c.fetchall():
    print(col[1], col[2])
