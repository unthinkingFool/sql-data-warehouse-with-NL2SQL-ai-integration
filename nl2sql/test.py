"""
Standalone connection test. Run this BEFORE running the full Streamlit app.
Usage: python test_connection.py
"""
import pyodbc

# --- EDIT THESE THREE LINES TO MATCH YOUR SETUP ---
SERVER = r"Swapnil\SQLEXPRESS"   # from SSMS "Server name" field
DATABASE = "DataWareHouse"          # your gold-layer database name
DRIVER = "ODBC Driver 17 for SQL Server"  # change to 18 if that's what Step 1 showed
# ----------------------------------------------------

conn_str = (
    f"DRIVER={{{DRIVER}}};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    "Trusted_Connection=yes;"
)

print(f"Connecting with:\n{conn_str}\n")

try:
    conn = pyodbc.connect(conn_str, timeout=10)
    print("✅ Connection successful!")

    cursor = conn.cursor()
    cursor.execute("SELECT TOP 5 TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES")
    rows = cursor.fetchall()

    print("\nSample tables found in this database:")
    for row in rows:
        print(f"  - {row.TABLE_SCHEMA}.{row.TABLE_NAME}")

    conn.close()

except pyodbc.Error as e:
    print(f"❌ Connection failed:\n{e}")
    print("\nCommon fixes:")
    print("  - Double check SERVER name matches SSMS exactly")
    print("  - Try DRIVER = 'ODBC Driver 18 for SQL Server' instead of 17")
    print("  - Make sure SQL Server service is running (services.msc)")