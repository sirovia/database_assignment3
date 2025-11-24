from sqlalchemy import create_engine, MetaData, Table, select, update, delete, func, case, text
from sqlalchemy.orm import sessionmaker

# -----------------------------------------------------
# 1) CONNECT + START TRANSACTION
# -----------------------------------------------------
engine = create_engine("postgresql://postgres:kizaru@localhost:5432/online_platform")
Session = sessionmaker(bind=engine)
session = Session()

metadata = MetaData()
metadata.reflect(bind=engine)

USERS = metadata.tables["users"]
CAREGIVER = metadata.tables["caregiver"]
MEMBER = metadata.tables["member"]
ADDRESS = metadata.tables["address"]
JOB = metadata.tables["job"]
JOB_APPLICATION = metadata.tables["job_application"]
APPOINTMENT = metadata.tables["appointment"]

def print_rows(label, stmt):
    print(f"\n===== {label} =====")
    rows = session.execute(stmt).fetchall()
    for r in rows:
        print(r)

try:
    # -----------------------------------------------------
    # Show original starting state (OPTIONAL)
    # -----------------------------------------------------
    print_rows("STARTING USERS TABLE", select(USERS))
    print_rows("STARTING CAREGIVER TABLE", select(CAREGIVER))
    print_rows("STARTING MEMBER TABLE", select(MEMBER))
    print_rows("STARTING JOB TABLE", select(JOB))
    print_rows("STARTING APPOINTMENT TABLE", select(APPOINTMENT))

    # -----------------------------------------------------
    # 3.1 Update phone number of Arman Nurgaliyev
    # -----------------------------------------------------
    stmt = (
        update(USERS)
        .where(USERS.c.given_name == "Arman", USERS.c.surname == "Nurgaliyev")
        .values(phone_number="+77773414141")
    )
    session.execute(stmt)
    session.flush()

    print_rows("After 3.1 Update (Arman phone)", 
               select(USERS).where(USERS.c.given_name=="Arman", USERS.c.surname=="Nurgaliyev"))

    # -----------------------------------------------------
    # 3.2 Add commission to hourly rate
    # -----------------------------------------------------
    stmt = (
        update(CAREGIVER)
        .values(
            hourly_rate=case(
                (CAREGIVER.c.hourly_rate < 10, CAREGIVER.c.hourly_rate + 0.3),
                else_=CAREGIVER.c.hourly_rate * 1.10
            )
        )
    )
    session.execute(stmt)
    session.flush()

    print_rows("After 3.2 Update (Caregiver hourly rate)", select(CAREGIVER))

    # -----------------------------------------------------
    # 4.1 Delete jobs posted by Amina Akhmetova
    # -----------------------------------------------------
    sub = select(USERS.c.user_id).where(
        USERS.c.given_name == "Amina",
        USERS.c.surname == "Akhmetova"
    )

    stmt = delete(JOB).where(JOB.c.member_user_id == sub.scalar_subquery())
    session.execute(stmt)
    session.flush()

    print_rows("After 4.1 Delete jobs by Amina", select(JOB))

    # -----------------------------------------------------
    # 4.2 Delete members living on Kabanbay Batyr
    # -----------------------------------------------------
    sub = select(ADDRESS.c.member_user_id).where(ADDRESS.c.street == "Kabanbay Batyr")

    stmt = delete(MEMBER).where(MEMBER.c.member_user_id.in_(sub))
    session.execute(stmt)
    session.flush()

    print_rows("After 4.2 Delete members on Kabanbay Batyr", select(MEMBER))

    # -----------------------------------------------------
    # 5.1 Caregiver + member names for confirmed appointments
    # -----------------------------------------------------
    C = USERS.alias("c")
    M = USERS.alias("m")

    stmt = (
        select(
            C.c.given_name.label("caregiver_name"),
            C.c.surname.label("caregiver_surname"),
            M.c.given_name.label("member_name"),
            M.c.surname.label("member_surname")
        )
        .select_from(
            APPOINTMENT
            .join(C, APPOINTMENT.c.caregiver_user_id == C.c.user_id)
            .join(M, APPOINTMENT.c.member_user_id == M.c.user_id)
        )
        .where(APPOINTMENT.c.status == "confirmed")
    )

    print_rows("5.1 Confirmed appointments caregiver+member names", stmt)

    # -----------------------------------------------------
    # 5.2 Job IDs with “soft-spoken”
    # -----------------------------------------------------
    stmt = select(JOB.c.job_id).where(
        func.lower(JOB.c.other_requirements).like("%soft-spoken%")
    )
    print_rows("5.2 Jobs requiring soft-spoken", stmt)

    # -----------------------------------------------------
    # 5.3 Work hours of babysitter positions
    # -----------------------------------------------------
    stmt = (
        select(APPOINTMENT.c.work_hours)
        .select_from(
            APPOINTMENT.join(
                CAREGIVER, APPOINTMENT.c.caregiver_user_id == CAREGIVER.c.caregiver_user_id
            )
        )
        .where(CAREGIVER.c.caregiving_type == "babysitter")
    )

    print_rows("5.3 Babysitter work hours", stmt)

    # -----------------------------------------------------
    # 5.4 Members looking for elderly care in Astana with “No pets”
    # -----------------------------------------------------
    stmt = (
        select(USERS.c.given_name, USERS.c.surname)
        .select_from(
            MEMBER
            .join(USERS, USERS.c.user_id == MEMBER.c.member_user_id)
            .join(JOB, JOB.c.member_user_id == MEMBER.c.member_user_id)
            .join(ADDRESS, ADDRESS.c.member_user_id == MEMBER.c.member_user_id)
        )
        .where(
            JOB.c.required_caregiving_type == "caregiver for elderly",
            ADDRESS.c.town == "Astana",
            MEMBER.c.house_rules == "No pets"
        )
    )
    print_rows("5.4 Members looking for elderly care (Astana, No pets)", stmt)

    # -----------------------------------------------------
    # 6.1 Count applicants per job
    # -----------------------------------------------------
    stmt = (
        select(
            JOB.c.job_id,
            USERS.c.given_name.label("member_name"),
            func.count(JOB_APPLICATION.c.caregiver_user_id).label("applicants")
        )
        .select_from(
            JOB
            .join(MEMBER, JOB.c.member_user_id == MEMBER.c.member_user_id)
            .join(USERS, USERS.c.user_id == MEMBER.c.member_user_id)
            .outerjoin(JOB_APPLICATION, JOB.c.job_id == JOB_APPLICATION.c.job_id)
        )
        .group_by(JOB.c.job_id, USERS.c.given_name)
    )
    print_rows("6.1 Applicant counts per job", stmt)

    # -----------------------------------------------------
    # 6.2 Total hours spent per caregiver for confirmed appointments
    # -----------------------------------------------------
    stmt = (
        select(
            CAREGIVER.c.caregiver_user_id,
            USERS.c.given_name,
            USERS.c.surname,
            func.sum(APPOINTMENT.c.work_hours).label("total_hours")
        )
        .select_from(
            APPOINTMENT
            .join(CAREGIVER, APPOINTMENT.c.caregiver_user_id == CAREGIVER.c.caregiver_user_id)
            .join(USERS, USERS.c.user_id == CAREGIVER.c.caregiver_user_id)
        )
        .where(APPOINTMENT.c.status == "confirmed")
        .group_by(CAREGIVER.c.caregiver_user_id, USERS.c.given_name, USERS.c.surname)
    )
    print_rows("6.2 Confirmed hours per caregiver", stmt)

    # -----------------------------------------------------
    # 6.3 Average payout per confirmed appointment
    # -----------------------------------------------------
    payout = CAREGIVER.c.hourly_rate * APPOINTMENT.c.work_hours
    stmt = (
        select(func.avg(payout).label("avg_payout"))
        .select_from(
            APPOINTMENT.join(
                CAREGIVER,
                APPOINTMENT.c.caregiver_user_id == CAREGIVER.c.caregiver_user_id
            )
        )
        .where(APPOINTMENT.c.status == "confirmed")
    )
    print("\n6.3 Average payout per confirmed appointment =", session.execute(stmt).scalar())

    # -----------------------------------------------------
    # 6.4 Caregivers earning above average (confirmed appts)
    # -----------------------------------------------------
    earnings_per_caregiver = (
        select(
            APPOINTMENT.c.caregiver_user_id.label("cg_id"),
            func.sum(CAREGIVER.c.hourly_rate * APPOINTMENT.c.work_hours).label("total_earnings")
        )
        .select_from(
            APPOINTMENT.join(
                CAREGIVER,
                APPOINTMENT.c.caregiver_user_id == CAREGIVER.c.caregiver_user_id
            )
        )
        .where(APPOINTMENT.c.status == "confirmed")
        .group_by(APPOINTMENT.c.caregiver_user_id)
        .cte("earnings_per_caregiver")
    )

    avg_earnings = select(func.avg(earnings_per_caregiver.c.total_earnings)).scalar_subquery()

    stmt = (
        select(
            CAREGIVER.c.caregiver_user_id,
            USERS.c.given_name,
            USERS.c.surname,
            earnings_per_caregiver.c.total_earnings
        )
        .select_from(
            earnings_per_caregiver
            .join(CAREGIVER, CAREGIVER.c.caregiver_user_id == earnings_per_caregiver.c.cg_id)
            .join(USERS, USERS.c.user_id == CAREGIVER.c.caregiver_user_id)
        )
        .where(earnings_per_caregiver.c.total_earnings > avg_earnings)
    )
    print_rows("6.4 Caregivers earning above average", stmt)

    # -----------------------------------------------------
    # 7. Derived attribute: total cost of confirmed appointments
    # -----------------------------------------------------
    stmt = (
        select(func.sum(CAREGIVER.c.hourly_rate * APPOINTMENT.c.work_hours))
        .select_from(
            APPOINTMENT.join(CAREGIVER, APPOINTMENT.c.caregiver_user_id == CAREGIVER.c.caregiver_user_id)
        )
        .where(APPOINTMENT.c.status == "confirmed")
    )
    print("\n7. Total cost of confirmed appointments =", session.execute(stmt).scalar())

    # -----------------------------------------------------
    # 8. Create a VIEW
    # -----------------------------------------------------
    session.execute(text("""
        CREATE OR REPLACE VIEW view_job_applications AS
        SELECT 
            ja.job_id,
            ja.caregiver_user_id,
            u.given_name,
            u.surname,
            j.required_caregiving_type,
            j.other_requirements,
            ja.date_applied
        FROM job_application ja
        JOIN users u ON ja.caregiver_user_id = u.user_id
        JOIN job j ON ja.job_id = j.job_id;
    """))
    session.flush()

    print_rows("8. Created view_job_applications", text("SELECT * FROM view_job_applications"))

# -----------------------------------------------------
# ROLLBACK EVERYTHING
# -----------------------------------------------------
finally:
    print("\nROLLING BACK ALL CHANGES...")
    session.rollback()

    print_rows("STATE AFTER ROLLBACK — ORIGINAL DATA", select(USERS))

    session.close()
