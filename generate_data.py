"""
Generates a sample dataset simulating 'cloud records' — includes
unique records, exact duplicates, near-duplicates, and invalid/false
records — so we can test the Data Redundancy Removal System.
"""
import csv
import random

random.seed(42)

first_names = ["Rahul", "Priya", "Aman", "Sneha", "Vikram", "Isha", "Karan",
               "Neha", "Rohan", "Divya", "Arjun", "Pooja", "Sahil", "Anjali"]
last_names = ["Sharma", "Verma", "Patel", "Iyer", "Gupta", "Reddy", "Nair",
              "Khan", "Joshi", "Mehta"]
domains = ["gmail.com", "yahoo.com", "outlook.com"]

records = []
rid = 1

# 1. Generate 20 clean, unique base records
base_records = []
for i in range(20):
    name = f"{random.choice(first_names)} {random.choice(last_names)}"
    email = f"{name.lower().replace(' ', '.')}{random.randint(1,99)}@{random.choice(domains)}"
    age = random.randint(18, 55)
    city = random.choice(["Pune", "Mumbai", "Nagpur", "Nashik", "Delhi", "Bangalore"])
    base_records.append({
        "id": rid, "name": name, "email": email, "age": age, "city": city
    })
    rid += 1

records.extend(base_records)

# 2. Add exact duplicates (same email, different id) - should be REJECTED
for r in random.sample(base_records, 5):
    dup = r.copy()
    dup["id"] = rid
    records.append(dup)
    rid += 1

# 3. Add near-duplicates (same email, slightly different name/age) - should be
#    detected as duplicate based on email match and UPDATED, not duplicated
for r in random.sample(base_records, 3):
    dup = r.copy()
    dup["id"] = rid
    dup["age"] = dup["age"] + 1  # simulate updated info
    records.append(dup)
    rid += 1

# 4. Add invalid/false records - should be REJECTED as invalid
invalid_records = [
    {"id": rid, "name": "", "email": "noemail@gmail.com", "age": 25, "city": "Pune"},
    {"id": rid + 1, "name": "Test User", "email": "not-an-email", "age": 30, "city": "Mumbai"},
    {"id": rid + 2, "name": "Bad Age", "email": "badage@gmail.com", "age": 200, "city": "Nashik"},
    {"id": rid + 3, "name": "Negative Age", "email": "negage@gmail.com", "age": -5, "city": "Pune"},
    {"id": rid + 4, "name": "No City", "email": "nocity@gmail.com", "age": 22, "city": ""},
]
records.extend(invalid_records)

with open("incoming_records.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "name", "email", "age", "city"])
    writer.writeheader()
    writer.writerows(records)

print(f"Generated {len(records)} incoming records -> incoming_records.csv")
print(f"  - {len(base_records)} unique clean records")
print("  - 5 exact duplicates")
print("  - 3 near-duplicates (same email, updated info)")
print("  - 5 invalid/false records")
