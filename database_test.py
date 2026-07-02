import pyodbc

server = "localhost"
database = "BudgetApp"
print("test")
# Build the connection string for Windows Authentication
conn_str = (
    f"DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;"
)
try:
    # Establish connection
    connection = pyodbc.connect(conn_str)
    cursor = connection.cursor()
except Exception as e:
    print(f"Error connecting to database: {e}")
