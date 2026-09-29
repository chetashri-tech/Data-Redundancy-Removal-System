# Data Redundancy Removal System

**Task 1 – Cloud Computing Task List (Horizon TechX)**

## Objective
Design a system that detects duplicate and false data, validates new
records against existing cloud records, prevents duplicate entries,
and stores only unique, verified data — improving cloud storage
efficiency and accuracy.

## How It Works
1. **Validation** – Every incoming record is checked for:
   - Non-empty name
   - Valid email format
   - Age within a valid range (0–120)
   - Non-empty city

2. **Duplicate Detection** – Each record's email is checked against
   existing records already stored in the database.
   - **New email** → record is treated as unique and inserted.
   - **Same email, identical details** → treated as an exact
     duplicate and rejected.
   - **Same email, different details** → treated as an update to the
     existing record (refreshes the data instead of storing a
     duplicate row).

3. **Storage** – Only validated, unique/updated records are kept in
   the database (`cloud_records.db`, a stand-in for a cloud database
   like AWS RDS).

## Files
- `generate_data.py` – Generates a sample dataset of 33 incoming
  records: 20 unique, 5 exact duplicates, 3 near-duplicates (updated
  info), and 5 invalid/false records.
- `redundancy_system.py` – The core system: validates, deduplicates,
  and stores records; prints a processing log and summary.
- `incoming_records.csv` – Sample generated input data.
- `cloud_records.db` – Output SQLite database containing only the
  final, verified, unique records.

## How to Run
```bash
pip install -r requirements.txt   # no external deps needed (uses stdlib)
python generate_data.py           # creates incoming_records.csv
python redundancy_system.py       # runs the redundancy removal pipeline
```

## Sample Output Summary
```
Total incoming records:      33
Inserted (new unique):       20
Updated (duplicate email):   3
Rejected (exact duplicate):  5
Rejected (invalid/false):    5
Final verified records in cloud storage (DB): 20
```

## Tech Used
- Python 3
- SQLite (simulating cloud database storage)
- Regex-based validation

---
*Part of the Cloud Computing Task List – Horizon TechX Internship*
