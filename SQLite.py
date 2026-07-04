import sqlite3

DB_FILE = "./cache/BudgetApp.db"

conn = sqlite3.connect(DB_FILE)

cursor = conn.cursor()

# cursor.execute("CREATE TABLE movie(title, year, score)")
# cursor.execute("DROP TABLE IF EXISTS movie")
row = cursor.execute("SELECT name FROM sqlite_master WHERE name='movie';")

print(row.fetchone())