import sqlite3

conn = sqlite3.connect(r'behavioral-agentic-ai\backend\data\app.db')
c = conn.cursor()
c.execute("SELECT shipment_id, carrier, status, origin_city, destination_city, has_exception, exception_type FROM shipments LIMIT 10")
for row in c.fetchall():
    print(row)

c.execute("SELECT shipment_id FROM shipments WHERE shipment_id LIKE '%WB%'")
print("WB shipments:", c.fetchall())

c.execute("SELECT id, name, slug FROM tenants")
print("Tenants:", c.fetchall())
