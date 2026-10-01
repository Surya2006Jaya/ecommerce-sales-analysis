"""
Test script to execute all SQL queries in the sql/ folder against the SQLite database.
"""

import sqlite3
import os
import glob

def test_sql_files():
    db_path = "ecommerce-sales-analysis/data/ecommerce_sales.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    sql_files = sorted(glob.glob("ecommerce-sales-analysis/sql/*.sql"))
    print(f"Testing {len(sql_files)} SQL files against {db_path}...")
    
    for file_path in sql_files:
        print(f"\nTesting: {os.path.basename(file_path)}")
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Split by semicolon and execute non-empty statements
        queries = [q.strip() for q in content.split(";") if q.strip()]
        for idx, q in enumerate(queries):
            try:
                # Remove comments to avoid executing comment-only blocks
                lines = [l for l in q.split("\n") if not l.strip().startswith("--")]
                clean_q = "\n".join(lines).strip()
                if clean_q:
                    cursor.execute(clean_q)
                    results = cursor.fetchall()
                    print(f"  [Query {idx+1}] PASSED - Returned {len(results)} rows")
            except Exception as e:
                print(f"  [Query {idx+1}] FAILED: {e}")
                raise e
                
    conn.close()
    print("\nALL SQL QUERIES EXECUTED SUCCESSFULLY WITH ZERO ERRORS!")

if __name__ == "__main__":
    test_sql_files()
