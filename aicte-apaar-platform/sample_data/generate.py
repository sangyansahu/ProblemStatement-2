import csv

def generate():
    rows = []
    # Header: required columns: student_number, apaar_id, course_code, academic_year, seat_category (optional: name, admission_date)
    headers = ["student_number", "apaar_id", "course_code", "academic_year", "seat_category", "name", "admission_date"]

    # Fictional names
    first_names = ["Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan", "Krishna", "Ishaan",
                   "Shaurya", "Atharva", "Advik", "Pranav", "Advaith", "Aaryan", "Dhruv", "Kabir", "Ritvik", "Darsh",
                   "Diya", "Saanvi", "Ananya", "Aadhya", "Pari", "Chiara", "Riya", "Avani", "Ira", "Ahana",
                   "Anvi", "Prisha", "Myra", "Sara", "Navya", "Rhea", "Siya", "Vanya", "Aditi", "Isha"]
    last_names = ["Sharma", "Verma", "Patel", "Gupta", "Rao", "Reddy", "Nair", "Singh", "Kumar", "Iyer",
                  "Joshi", "Bose", "Mehta", "Chauhan", "Bhat", "Deshmukh", "Kulkarni", "Ghosh", "Das", "Menon"]

    row_idx = 1

    # 1. Standard valid rows for CS101 in 2025-26 (approx 65 rows)
    for i in range(1, 66):
        fn = first_names[i % len(first_names)]
        ln = last_names[i % len(last_names)]
        rows.append({
            "student_number": f"2025-CS-{i:03d}",
            "apaar_id": f"DEMO-9824-0001-{i:04d}",
            "course_code": "CS101",
            "academic_year": "2025-26",
            "seat_category": "regular" if i % 5 != 0 else "supernumerary",
            "name": f"{fn} {ln}",
            "admission_date": f"2025-07-{(i % 25) + 1:02d}"
        })

    # 2. 10 Missing APAAR IDs (MISSING_APAAR)
    for i in range(1, 11):
        fn = first_names[(i+5) % len(first_names)]
        ln = last_names[(i+3) % len(last_names)]
        rows.append({
            "student_number": f"2025-CS-MISS-{i:02d}",
            "apaar_id": "",  # missing
            "course_code": "CS101",
            "academic_year": "2025-26",
            "seat_category": "regular",
            "name": f"{fn} {ln}",
            "admission_date": "2025-07-15"
        })

    # 3. 5 In-file duplicates (DUPLICATE_IN_UPLOAD)
    for i in range(1, 6):
        target = rows[i]  # repeat identifier
        rows.append({
            "student_number": f"2025-CS-DUP-{i:02d}",
            "apaar_id": target["apaar_id"],
            "course_code": "CS101",
            "academic_year": "2025-26",
            "seat_category": "regular",
            "name": f"Copy of {target['name']}",
            "admission_date": "2025-07-16"
        })

    # 4. Invalid course codes (INVALID_COURSE_CODE)
    for i in range(1, 4):
        rows.append({
            "student_number": f"2025-BAD-CRS-{i:02d}",
            "apaar_id": f"DEMO-9824-0002-{i:04d}",
            "course_code": "XX999",  # non-existent course
            "academic_year": "2025-26",
            "seat_category": "regular",
            "name": f"Invalid Course Candidate {i}",
            "admission_date": "2025-07-18"
        })

    # 5. Invalid seat categories (INVALID_SEAT_CATEGORY)
    for i in range(1, 4):
        rows.append({
            "student_number": f"2025-BAD-SEAT-{i:02d}",
            "apaar_id": f"DEMO-9824-0003-{i:04d}",
            "course_code": "IT102",
            "academic_year": "2025-26",
            "seat_category": "management_quota",  # invalid seat category
            "name": f"Invalid Seat Candidate {i}",
            "admission_date": "2025-07-20"
        })

    # 6. One simulated APAAR timeout
    rows.append({
        "student_number": f"2025-IT-TIMEOUT-01",
        "apaar_id": "DEMO-TIMEOUT-9999",
        "course_code": "IT102",
        "academic_year": "2025-26",
        "seat_category": "regular",
        "name": "Simulated Timeout Candidate",
        "admission_date": "2025-07-22"
    })

    # 7. Rows pushing IT102 over capacity (approved 60 + extra 5 = 65 ceiling; we add 70 rows)
    for i in range(1, 72):
        fn = first_names[(i+7) % len(first_names)]
        ln = last_names[(i+8) % len(last_names)]
        rows.append({
            "student_number": f"2025-IT-{i:03d}",
            "apaar_id": f"DEMO-9824-0004-{i:04d}",
            "course_code": "IT102",
            "academic_year": "2025-26",
            "seat_category": "regular",
            "name": f"{fn} {ln}",
            "admission_date": "2025-07-25"
        })

    # Write CSV
    with open("c:/Users/sanni/Desktop/SIHPS2/aicte-apaar-platform/sample_data/synthetic_students.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} synthetic student rows.")

if __name__ == "__main__":
    generate()
