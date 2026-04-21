import sqlite3
import os
import argparse
import pandas as pd

script_dir = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(os.path.abspath(script_dir), "pipeline.db")
parser = argparse.ArgumentParser(description="Enter name of the target .csv")
parser.add_argument("--name", type=str, default="5_librun_low_method4", help="Enter name of the target .csv")
arg = parser.parse_args()
csv_path = arg.name

run_id = int(csv_path[0])
if run_id == 1:
    run_environment = "Lab Calibration"
elif run_id == 2:
    run_environment = "Lab Run (High)"
elif run_id == 3:
    run_environment = "Lab Run (Low)"
elif run_id == 4:
    run_environment = "Library Run (High)"
else:
    run_environment = "Library Run (Low)"
run_method = csv_path[-7:]
if run_method == "method3":
    run_method = "PDOP"
else:
    run_method = "LOS"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("""
            CREATE TABLE IF NOT EXISTS measurements
            (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            error_xy REAL,
            voxel_value REAL, 
            runs_id INTEGER,
            FOREIGN KEY (runs_id) REFERENCES runs(id)
            );
            """)

cur.execute("""
            CREATE TABLE IF NOT EXISTS runs
            (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER,
            environment TEXT,
            method TEXT
            );
            """)

cur.execute("DELETE FROM measurements WHERE runs_id = (SELECT id FROM runs WHERE run_id = ? AND method = ?)", (run_id, run_method))
cur.execute("DELETE FROM runs WHERE run_id = ? AND method = ?", (run_id, run_method))
cur.execute("INSERT INTO runs (run_id, environment, method) VALUES (?, ?, ?)", (run_id, run_environment, run_method))
conn.commit()
runs_id = cur.lastrowid
csv_full_path = os.path.join(script_dir, csv_path) + ".csv"
df = pd.read_csv(csv_full_path)
df = df.rename(columns={'rmse_xy': 'error_xy'}) # change column name from rmse to error for correctness
df = df[['error_xy', 'voxel_value']] # Remove unintended columns
df.insert(0, 'runs_id', runs_id)

df.to_sql("measurements", conn, if_exists='append', index=False)

cur.execute("""
            SELECT COUNT(error_xy), AVG(error_xy), MIN(error_xy), MAX(error_xy)
            FROM measurements
            WHERE runs_id = ?
            """
            , (runs_id,))

result = cur.fetchone()
print(f"COUNT: {result[0]}, AVG: {result[1]:.4f}, MIN: {result[2]:.4f}, MAX: {result[3]:.4f}")

conn.close()