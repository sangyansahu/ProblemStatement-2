import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Institution, Programme, User, Admission, Student
from app.security import generate_apaar_token


def seed_database_defaults(db: Session):
    """Seed ~5 fictional institutions, programmes with intake, and users for each role."""
    if db.query(Institution).first():
        return  # Already seeded

    institutions_data = [
        {
            "aicte_code": "AICTE-1-001",
            "name": "Delhi Institute of Advanced Engineering & Technology",
            "state": "Delhi",
            "district": "New Delhi",
            "programmes": [
                {"course_code": "CS101", "name": "B.Tech Computer Science & Engineering", "intake": 120, "extra": 10},
                {"course_code": "IT102", "name": "B.Tech Information Technology", "intake": 60, "extra": 5},
                {"course_code": "EC103", "name": "B.Tech Electronics & Communication", "intake": 60, "extra": 0},
            ]
        },
        {
            "aicte_code": "AICTE-1-002",
            "name": "Mumbai Technical Institute of Engineering",
            "state": "Maharashtra",
            "district": "Mumbai City",
            "programmes": [
                {"course_code": "ME201", "name": "B.Tech Mechanical Engineering", "intake": 120, "extra": 0},
                {"course_code": "CS101", "name": "B.Tech Computer Engineering", "intake": 90, "extra": 10},
            ]
        },
        {
            "aicte_code": "AICTE-1-003",
            "name": "Bengaluru Academy of Technology & Sciences",
            "state": "Karnataka",
            "district": "Bengaluru Urban",
            "programmes": [
                {"course_code": "AI301", "name": "B.Tech Artificial Intelligence & Data Science", "intake": 60, "extra": 5},
                {"course_code": "CS101", "name": "B.Tech Computer Science", "intake": 120, "extra": 12},
            ]
        },
        {
            "aicte_code": "AICTE-1-004",
            "name": "Chennai Institute of Higher Technology",
            "state": "Tamil Nadu",
            "district": "Chennai",
            "programmes": [
                {"course_code": "EE401", "name": "B.Tech Electrical Engineering", "intake": 60, "extra": 0},
                {"course_code": "CV402", "name": "B.Tech Civil Engineering", "intake": 60, "extra": 0},
            ]
        },
        {
            "aicte_code": "AICTE-1-005",
            "name": "Kolkata Technical University Campus",
            "state": "West Bengal",
            "district": "Kolkata",
            "programmes": [
                {"course_code": "CS101", "name": "B.Tech Computer Science", "intake": 60, "extra": 6},
                {"course_code": "BT501", "name": "B.Tech Biotechnology", "intake": 30, "extra": 0},
            ]
        }
    ]

    created_institutions = {}
    academic_years = ["2024-25", "2025-26"]

    for inst_data in institutions_data:
        inst = Institution(
            aicte_code=inst_data["aicte_code"],
            name=inst_data["name"],
            state=inst_data["state"],
            district=inst_data["district"],
            created_at=datetime.utcnow()
        )
        db.add(inst)
        db.flush()
        created_institutions[inst_data["aicte_code"]] = inst

        for p_data in inst_data["programmes"]:
            for ay in academic_years:
                prog = Programme(
                    institution_id=inst.id,
                    course_code=p_data["course_code"],
                    programme_name=p_data["name"],
                    academic_year=ay,
                    approved_intake=p_data["intake"],
                    approved_extra_seats=p_data["extra"],
                    created_at=datetime.utcnow()
                )
                db.add(prog)

    # Seed one user per role
    primary_inst = created_institutions["AICTE-1-001"]
    users_data = [
        {
            "username": "aicte_admin",
            "email": "aicte_admin@aicte.gov.in",
            "full_name": "Dr. V. K. Sharma (AICTE National Admin)",
            "role": "aicte_admin",
            "institution_id": None
        },
        {
            "username": "inst_admin",
            "email": "director@diaet.edu.in",
            "full_name": "Prof. Rajesh Kumar (Director, DIAET)",
            "role": "institution_admin",
            "institution_id": primary_inst.id
        },
        {
            "username": "inst_operator",
            "email": "registrar@diaet.edu.in",
            "full_name": "Sunita Verma (Operator, DIAET)",
            "role": "institution_operator",
            "institution_id": primary_inst.id
        },
        {
            "username": "verifier",
            "email": "verifier@credential.gov.in",
            "full_name": "Amit Saxena (Verification Officer)",
            "role": "verifier",
            "institution_id": None
        },
        {
            "username": "auditor",
            "email": "auditor@aicte.gov.in",
            "full_name": "P. N. Murthy (Compliance Auditor)",
            "role": "auditor",
            "institution_id": None
        }
    ]

    for u_data in users_data:
        user = User(
            username=u_data["username"],
            email=u_data["email"],
            full_name=u_data["full_name"],
            role=u_data["role"],
            institution_id=u_data["institution_id"],
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.add(user)

    db.commit()
