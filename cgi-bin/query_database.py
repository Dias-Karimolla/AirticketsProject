import sqlite3

# Connect to the database
db_path = r"C:\Apache24\htdocs\logs\flight_search.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Query 1: Recent search requests
print("Recent Search Requests:")
cursor.execute("SELECT * FROM search_requests ORDER BY timestamp DESC LIMIT 5")
for row in cursor.fetchall():
    print(f"ID: {row['id']}, Timestamp: {row['timestamp']}, Departure: {row['departure']}, Destination: {row['destination']}")

# Query 2: Search frequency by departure city
print("\nSearch Frequency by Departure City:")
cursor.execute("SELECT departure, COUNT(*) as count FROM search_requests GROUP BY departure")
for row in cursor.fetchall():
    print(f"Departure: {row['departure']}, Count: {row['count']}")

# Close connection
conn.close()