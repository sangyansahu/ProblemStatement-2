import json
from datetime import datetime, timedelta
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.institution import Institution
from app.models.programme import Programme
from app.models.student import Student
from app.models.upload import UploadBatch
from app.models.duplicate_case import DuplicateReviewCase
from app.models.notification import Notification
from app.models.audit import AuditLog
from app.models.change_history import RecordChangeHistory
from app.services.security_service import generate_apaar_hmac, encrypt_apaar, mask_apaar

def seed_database():
    app = create_app()
    with app.app_context():
        print("Dropping and recreating database tables...")
        db.drop_all()
        db.create_all()

        print("Seeding sample educational institutions...")
        inst1 = Institution(
            code="AICTE-1-001293",
            name="Delhi Institute of Advanced Engineering & Technology",
            type="Affiliated Engineering College",
            state="Delhi",
            district="New Delhi",
            address="Plot 14, Sector 7, Institutional Area, Dwarka, New Delhi 110075",
            contact_email="registrar@diaet.edu.in",
            contact_phone="+91-11-28034500",
            principal_name="Dr. Sunita Ramanathan",
            status="active"
        )
        inst2 = Institution(
            code="AICTE-1-004812",
            name="Maharashtra State Institute of Science and Technology",
            type="State University",
            state="Maharashtra",
            district="Pune",
            address="Ganeshkhind Road, Shivaji Nagar, Pune 411007",
            contact_email="admissions@msist.ac.in",
            contact_phone="+91-20-25698000",
            principal_name="Prof. Rajesh Deshmukh",
            status="active"
        )
        inst3 = Institution(
            code="AICTE-1-008921",
            name="Karnataka National College of Engineering",
            type="Deemed University",
            state="Karnataka",
            district="Bengaluru Urban",
            address="Mysore Road, RV Vidyaniketan Post, Bengaluru 560059",
            contact_email="director@knce.edu.in",
            contact_phone="+91-80-67178000",
            principal_name="Dr. Anil Kulkarni",
            status="active"
        )
        inst4 = Institution(
            code="AICTE-1-009450",
            name="Tamil Nadu Polytechnic Institute",
            type="Polytechnic",
            state="Tamil Nadu",
            district="Chennai",
            address="Guindy Industrial Estate, Chennai 600032",
            contact_email="principal@tnpoly.edu.in",
            contact_phone="+91-44-22351000",
            principal_name="Dr. K. Swaminathan",
            status="active"
        )
        db.session.add_all([inst1, inst2, inst3, inst4])
        db.session.flush()

        print("Seeding academic programmes and approved intakes...")
        prog1 = Programme(
            institution_id=inst1.id,
            programme_code="BTECH-CSE",
            programme_name="Bachelor of Technology",
            branch_or_department="Computer Science & Engineering",
            level="UG",
            academic_year="2025-2026",
            approved_intake=120,
            supernumerary_intake=12,
            is_demo_intake=True
        )
        prog2 = Programme(
            institution_id=inst1.id,
            programme_code="BTECH-ECE",
            programme_name="Bachelor of Technology",
            branch_or_department="Electronics & Communication Engineering",
            level="UG",
            academic_year="2025-2026",
            approved_intake=60,
            supernumerary_intake=6,
            is_demo_intake=True
        )
        prog3 = Programme(
            institution_id=inst1.id,
            programme_code="MTECH-AI",
            programme_name="Master of Technology",
            branch_or_department="Artificial Intelligence & Data Science",
            level="PG",
            academic_year="2025-2026",
            approved_intake=30,
            supernumerary_intake=3,
            is_demo_intake=True
        )
        prog4 = Programme(
            institution_id=inst2.id,
            programme_code="BTECH-MECH",
            programme_name="Bachelor of Technology",
            branch_or_department="Mechanical Engineering",
            level="UG",
            academic_year="2025-2026",
            approved_intake=90,
            supernumerary_intake=9,
            is_demo_intake=True
        )
        prog5 = Programme(
            institution_id=inst2.id,
            programme_code="BTECH-CIVIL",
            programme_name="Bachelor of Technology",
            branch_or_department="Civil Engineering",
            level="UG",
            academic_year="2025-2026",
            approved_intake=60,
            supernumerary_intake=6,
            is_demo_intake=True
        )
        db.session.add_all([prog1, prog2, prog3, prog4, prog5])
        db.session.flush()

        print("Seeding standard role user accounts...")
        # 1. Institute user (linked to DIAET)
        u_institute = User(
            username="institute_demo",
            email="registrar@diaet.edu.in",
            phone="+91-11-28034501",
            full_name="Prof. Ramanathan (Registrar, DIAET)",
            role="institute",
            institution_id=inst1.id,
            is_active=True,
            created_at=datetime.utcnow() - timedelta(days=30),
            last_login=datetime.utcnow() - timedelta(minutes=15)
        )
        u_institute.set_password("Demo123!")

        # 2. Admin user (controlled read-only cross-institution)
        u_admin = User(
            username="admin_demo",
            email="regional.officer@aicte-india.org",
            phone="+91-11-29581040",
            full_name="Rajiv Menon (Regional Officer)",
            role="admin",
            institution_id=None,
            is_active=True,
            created_at=datetime.utcnow() - timedelta(days=60),
            last_login=datetime.utcnow() - timedelta(hours=2)
        )
        u_admin.set_password("Demo123!")

        # 3. Super Admin user (full system administrative oversight)
        u_super = User(
            username="superadmin_demo",
            email="superadmin@aicte-india.org",
            phone="+91-11-29581001",
            full_name="Dr. V. K. Saxena (AICTE Director General)",
            role="super_admin",
            institution_id=None,
            is_active=True,
            created_at=datetime.utcnow() - timedelta(days=90),
            last_login=datetime.utcnow() - timedelta(minutes=5)
        )
        u_super.set_password("Demo123!")

        db.session.add_all([u_institute, u_admin, u_super])
        db.session.flush()

        print("Seeding synthetic student records...")
        raw_students = [
            ("STU-2025-001", "Aarav Sharma", "781290345612", prog1, inst1, "Active", "General", False, "verified", "simulated", "[SIMULATED VERIFICATION] Matched synthetic repository."),
            ("STU-2025-002", "Priya Patel", "654321987012", prog1, inst1, "Active", "OBC", False, "verified", "simulated", "[SIMULATED VERIFICATION] Matched synthetic repository."),
            ("STU-2025-003", "Rohan Verma", "891234567890", prog1, inst1, "Active", "EWS", True, "verified", "simulated", "[SIMULATED VERIFICATION] Matched synthetic repository."),
            ("STU-2025-004", "Ananya Reddy", "432156789012", prog1, inst1, "Active", "SC", False, "pending", "simulated", "Verification queue awaiting automated batch run."),
            ("STU-2025-005", "Kabir Mehta", "321456789012", prog1, inst1, "Active", "General", False, "mismatch_detected", "simulated", "[SIMULATED VERIFICATION] Student name variation between board and admission sheet."),
            ("STU-2025-006", "Sneha Nair", "987612345098", prog2, inst1, "Active", "General", False, "requires_manual_review", "simulated", "[SIMULATED VERIFICATION] Discrepancy in date of registration. Flagged for reviewer."),
            ("STU-2025-007", "Aditya Joshi", "213456789012", prog2, inst1, "Active", "OBC", False, "unable_to_verify", "simulated", "[SIMULATED VERIFICATION] Remote directory lookup returned timeout status."),
            ("STU-2025-008", "Meera Pillai", None, prog2, inst1, "Active", "General", False, "not_submitted", "simulated", "Identifier not yet assigned by institution."),
            ("STU-2025-009", "Vikram Rathore", "567890123456", prog3, inst1, "Active", "General", False, "verified", "simulated", "[SIMULATED VERIFICATION] Matched PG registry."),
            ("STU-2025-010", "Ishita Sengupta", "876543210987", prog3, inst1, "Active", "General", False, "verified", "simulated", "[SIMULATED VERIFICATION] Matched PG registry."),
            # Inst 2 students (Maharashtra State Institute)
            ("STU-2025-101", "Gaurav Shinde", "112233445566", prog4, inst2, "Active", "General", False, "verified", "simulated", "[SIMULATED VERIFICATION] Matched state repository."),
            ("STU-2025-102", "Pooja Patil", "223344556677", prog4, inst2, "Active", "OBC", False, "verified", "simulated", "[SIMULATED VERIFICATION] Matched state repository."),
            ("STU-2025-103", "Sameer Deshpande", "781290345612", prog4, inst2, "Active", "General", False, "requires_manual_review", "simulated", "[SIMULATED VERIFICATION] Duplicate APAAR match flagged against DIAET enrolment.")
        ]

        students_objs = []
        for sid, sname, raw_apaar, prog, inst, estat, cat, sup, vstat, vsrc, vnote in raw_students:
            apaar_hmac = generate_apaar_hmac(raw_apaar) if raw_apaar else None
            apaar_enc = encrypt_apaar(raw_apaar) if raw_apaar else None
            masked = mask_apaar(raw_apaar) if raw_apaar else "Not Assigned"
            
            s = Student(
                institution_id=inst.id,
                student_id=sid,
                apaar_id_encrypted=apaar_enc,
                apaar_id_hmac=apaar_hmac,
                apaar_id_masked=masked,
                student_name=sname,
                programme_id=prog.id if prog else None,
                programme_name=prog.programme_name if prog else "Bachelor of Technology",
                branch_or_department=prog.branch_or_department if prog else "Engineering",
                academic_year="2025-2026",
                admission_date="2025-08-01",
                enrolment_status=estat,
                admission_category=cat,
                supernumerary_status=sup,
                verification_status=vstat,
                verification_source=vsrc,
                verification_notes=vnote,
                verified_at=datetime.utcnow() if vstat == 'verified' else None,
                is_duplicate_flagged=(sid == "STU-2025-103" or sid == "STU-2025-001"),
                created_at=datetime.utcnow() - timedelta(days=10)
            )
            db.session.add(s)
            students_objs.append(s)

        db.session.flush()

        print("Seeding initial upload batches...")
        batch1 = UploadBatch(
            batch_id="UB-2025-00412",
            institution_id=inst1.id,
            file_name="btech_cse_admissions_2025_batch1.csv",
            file_size_bytes=142300,
            total_rows=65,
            valid_rows=62,
            invalid_rows=3,
            warning_rows=4,
            duplicate_rows=1,
            status="completed",
            error_report_json=json.dumps([
                {"row_number": 14, "student_id": "STU-2025-014", "field": "apaar_id", "error": "APAAR ID must be exactly 12 digits, found 11", "suggestion": "Verify 12-digit APAAR from DigiLocker card"},
                {"row_number": 28, "student_id": "STU-2025-028", "field": "admission_date", "error": "Invalid date format '08/01/2025'", "suggestion": "Format as YYYY-MM-DD"},
                {"row_number": 43, "student_id": "STU-2025-043", "field": "enrolment_status", "error": "Unknown status 'PendingApproval'", "suggestion": "Use 'Active' or 'Transferred'"}
            ]),
            created_by_user_id=u_institute.id,
            created_at=datetime.utcnow() - timedelta(days=12),
            completed_at=datetime.utcnow() - timedelta(days=12)
        )
        batch2 = UploadBatch(
            batch_id="UB-2025-00418",
            institution_id=inst1.id,
            file_name="mtech_ai_intake_2025.csv",
            file_size_bytes=48500,
            total_rows=28,
            valid_rows=28,
            invalid_rows=0,
            warning_rows=1,
            duplicate_rows=0,
            status="completed",
            created_by_user_id=u_institute.id,
            created_at=datetime.utcnow() - timedelta(days=5),
            completed_at=datetime.utcnow() - timedelta(days=5)
        )
        db.session.add_all([batch1, batch2])
        db.session.flush()

        print("Seeding duplicate review cases...")
        dup_case1 = DuplicateReviewCase(
            case_reference="DUP-2025-00109",
            issue_type="apaar_cross_institution",
            severity="critical",
            status="open",
            institution_id=inst2.id,
            secondary_institution_id=inst1.id,
            student_id="STU-2025-103",
            student_name="Sameer Deshpande",
            apaar_id_masked="APAAR-****-****-5612",
            description="APAAR identifier 781290345612 registered for student 'Sameer Deshpande' at Maharashtra State Institute matches active student 'Aarav Sharma' (STU-2025-001) at Delhi Institute.",
            details_json=json.dumps({
                "student_1": {"id": "STU-2025-103", "name": "Sameer Deshpande", "institution": inst2.name, "programme": "B.Tech Mechanical"},
                "student_2": {"id": "STU-2025-001", "name": "Aarav Sharma", "institution": inst1.name, "programme": "B.Tech CSE"},
                "collision_key": "APAAR-HMAC-MATCH"
            }),
            detected_at=datetime.utcnow() - timedelta(days=4)
        )
        dup_case2 = DuplicateReviewCase(
            case_reference="DUP-2025-00114",
            issue_type="transfer_record_discrepancy",
            severity="caution",
            status="resolved",
            institution_id=inst1.id,
            secondary_institution_id=inst3.id,
            student_id="STU-2025-003",
            student_name="Rohan Verma",
            apaar_id_masked="APAAR-****-****-7890",
            description="Student migrated from Karnataka National College. Confirmed lateral transfer with official NOC.",
            resolution_decision="verified_valid_transfer",
            resolution_notes="Authorized transfer documents verified from AICTE National Transfer Portal. Record confirmed.",
            resolved_by_user_id=u_super.id,
            detected_at=datetime.utcnow() - timedelta(days=8),
            resolved_at=datetime.utcnow() - timedelta(days=6)
        )
        db.session.add_all([dup_case1, dup_case2])
        db.session.flush()

        print("Seeding system notifications...")
        n1 = Notification(
            institution_id=inst1.id,
            role_target="institute",
            title="CSV Batch Upload Completed (UB-2025-00412)",
            message="Batch UB-2025-00412 processed: 62 valid records committed, 3 invalid rows flagged for correction.",
            link="/uploads",
            type="warning",
            created_at=datetime.utcnow() - timedelta(days=12)
        )
        n2 = Notification(
            role_target="all",
            title="AICTE Mandatory APAAR Verification Phase 2 Announced",
            message="All affiliated institutions are requested to complete APAAR identifier mapping for 2025-2026 admissions before the deadline.",
            link="/students",
            type="info",
            created_at=datetime.utcnow() - timedelta(days=2)
        )
        n3 = Notification(
            role_target="super_admin",
            title="Duplicate Conflict Case Requires Authorized Review",
            message="Cross-institution duplicate conflict DUP-2025-00109 between Delhi Institute and Maharashtra State Institute requires resolution.",
            link="/duplicate-review",
            type="critical",
            created_at=datetime.utcnow() - timedelta(days=1)
        )
        db.session.add_all([n1, n2, n3])

        print("Seeding administrative audit logs...")
        aud1 = AuditLog(
            actor_id=u_super.id,
            actor_name=u_super.full_name,
            actor_role="super_admin",
            action="SYSTEM_INITIALIZATION",
            target_type="System",
            target_id="portal_core",
            summary="System initialized with security policies and verification sandbox",
            outcome="SUCCESS",
            ip_address="127.0.0.1",
            details_json=json.dumps({"version": "1.0.0", "status": "deployed"}),
            created_at=datetime.utcnow() - timedelta(days=20)
        )
        aud2 = AuditLog(
            actor_id=u_institute.id,
            actor_name=u_institute.full_name,
            actor_role="institute",
            action="CSV_IMPORT_COMMITTED",
            target_type="UploadBatch",
            target_id="UB-2025-00412",
            summary="Committed bulk import for B.Tech CSE (62 valid rows)",
            outcome="SUCCESS",
            ip_address="192.168.1.105",
            details_json=json.dumps({"file_name": "btech_cse_admissions_2025_batch1.csv", "valid_rows": 62, "invalid_rows": 3}),
            created_at=datetime.utcnow() - timedelta(days=12)
        )
        aud3 = AuditLog(
            actor_id=u_super.id,
            actor_name=u_super.full_name,
            actor_role="super_admin",
            action="DUPLICATE_RESOLVED",
            target_type="DuplicateCase",
            target_id="DUP-2025-00114",
            summary="Approved legitimate institutional transfer for student STU-2025-0041",
            outcome="SUCCESS",
            ip_address="10.0.0.14",
            details_json=json.dumps({"decision": "verified_valid_transfer", "reason": "Inter-university NOC verified"}),
            created_at=datetime.utcnow() - timedelta(days=6)
        )
        aud4 = AuditLog(
            actor_id=u_admin.id,
            actor_name=u_admin.full_name,
            actor_role="admin",
            action="ENROLMENT_STATUS_CHANGED",
            target_type="Student",
            target_id="STU-2025-0012",
            summary="Updated enrolment status to Active following registration verification",
            outcome="SUCCESS",
            ip_address="10.0.4.82",
            details_json=json.dumps({"changed_fields": ["enrolment_status"], "previous": {"enrolment_status": "Pending"}, "new": {"enrolment_status": "Active"}}),
            created_at=datetime.utcnow() - timedelta(days=3)
        )
        aud5 = AuditLog(
            actor_id=u_super.id,
            actor_name=u_super.full_name,
            actor_role="super_admin",
            action="INSTITUTION_PROFILE_UPDATED",
            target_type="Institution",
            target_id="AICTE-1-001293",
            summary="Updated principal contact and affiliation renewal status",
            outcome="SUCCESS",
            ip_address="10.0.0.14",
            details_json=json.dumps({"changed_fields": ["principal_name", "status"], "status": "active"}),
            created_at=datetime.utcnow() - timedelta(days=1)
        )
        aud6 = AuditLog(
            actor_id=u_super.id,
            actor_name=u_super.full_name,
            actor_role="super_admin",
            action="VERIFICATION_STATUS_CHANGED",
            target_type="Student",
            target_id="STU-2025-0001",
            summary="Manual verification override approved with university gazette record",
            outcome="SUCCESS",
            ip_address="10.0.0.14",
            details_json=json.dumps({"previous_status": "requires_manual_review", "new_status": "verified"}),
            created_at=datetime.utcnow() - timedelta(hours=4)
        )
        db.session.add_all([aud1, aud2, aud3, aud4, aud5, aud6])

        db.session.commit()
        print("Database seeding completed successfully!")

if __name__ == '__main__':
    seed_database()
