"""
Data Redundancy Removal System
--------------------------------
Task: Design a system to detect duplicate and false data, validate new
data against existing cloud records, prevent duplicate entries, store
only unique and verified data, and improve cloud storage efficiency.

This simulates a "cloud database" using SQLite (stand-in for a cloud
DB like AWS RDS). Each incoming record is:
  1. Validated (checks for missing/invalid fields)
  2. Checked against existing records (duplicate detection by email)
  3. Either inserted (new), updated (duplicate with new info), or
     rejected (invalid or exact duplicate)
"""

import sqlite3
import csv
import re

DB_FILE = "cloud_records.db"


def setup_database():
    """Creates the 'cloud storage' table (acts as our verified records store)."""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS records")
    cur.execute("""
        CREATE TABLE records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            age INTEGER NOT NULL,
            city TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


def is_valid_email(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_record(record):
    """Returns (is_valid, reason) for a single incoming record."""
    if not record.get("name", "").strip():
        return False, "Missing name"
    if not is_valid_email(record.get("email", "")):
        return False, "Invalid email format"
    try:
        age = int(record.get("age", -1))
    except ValueError:
        return False, "Age is not a number"
    if age < 0 or age > 120:
        return False, "Age out of valid range (0-120)"
    if not record.get("city", "").strip():
        return False, "Missing city"
    return True, "Valid"


def process_record(conn, record):
    """
    Validates a record, checks for duplicates by email, and either
    inserts, updates, or rejects it. Returns a status string for logging.
    """
    cur = conn.cursor()

    # Step 1: Validation
    valid, reason = validate_record(record)
    if not valid:
        return f"REJECTED (invalid): {reason}"

    email = record["email"].strip().lower()
    name = record["name"].strip()
    age = int(record["age"])
    city = record["city"].strip()

    # Step 2: Duplicate check against existing cloud records
    cur.execute("SELECT id, name, age, city FROM records WHERE email = ?", (email,))
    existing = cur.fetchone()

    if existing is None:
        # Step 3a: New unique record -> insert
        cur.execute(
            "INSERT INTO records (name, email, age, city) VALUES (?, ?, ?, ?)",
            (name, email, age, city)
        )
        conn.commit()
        return "INSERTED (new unique record)"

    else:
        existing_id, existing_name, existing_age, existing_city = existing
        if (name, age, city) == (existing_name, existing_age, existing_city):
            # Step 3b: Exact duplicate -> reject
            return "REJECTED (exact duplicate)"
        else:
            # Step 3c: Same person, updated info -> update instead of duplicating
            cur.execute(
                "UPDATE records SET name=?, age=?, city=? WHERE email=?",
                (name, age, city, email)
            )
            conn.commit()
            return "UPDATED (duplicate email, refreshed info)"


def run_pipeline(csv_file):
    conn = setup_database()
    log = []

    with open(csv_file, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            status = process_record(conn, row)
            log.append((row["id"], row.get("email", ""), status))

    # Summary
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM records")
    total_stored = cur.fetchone()[0]

    print("=" * 70)
    print("PROCESSING LOG")
    print("=" * 70)
    for rid, email, status in log:
        print(f"Record {rid:>3} | {email:<35} | {status}")

    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    total = len(log)
    inserted = sum(1 for _, _, s in log if s.startswith("INSERTED"))
    updated = sum(1 for _, _, s in log if s.startswith("UPDATED"))
    rejected_dup = sum(1 for _, _, s in log if "exact duplicate" in s)
    rejected_invalid = sum(1 for _, _, s in log if "invalid" in s)

    print(f"Total incoming records:      {total}")
    print(f"Inserted (new unique):       {inserted}")
    print(f"Updated (duplicate email):   {updated}")
    print(f"Rejected (exact duplicate):  {rejected_dup}")
    print(f"Rejected (invalid/false):    {rejected_invalid}")
    print(f"Final verified records in cloud storage (DB): {total_stored}")
    print("=" * 70)

    conn.close()


if __name__ == "__main__":
    run_pipeline("incoming_records.csv")
