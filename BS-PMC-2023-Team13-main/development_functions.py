from website import db
from website.models import User, Item, LoanRequest
from datetime import datetime

def database_start_over():
    print("start over database...")
    db.drop_all()
    db.create_all()
    user1 = User(
        first_name="Ken", 
        last_name="Adams", 
        email_address="teacher@email.com",
        password="12345", 
        is_warehouse_manager = False,
        is_teaching_staff_member = True,
        phone_number="0587872437")

    db.session.add(user1)
    db.session.commit()

    user2 = User(
        first_name="Regina", 
        last_name="Phalange", 
        email_address="admin@email.com",
        password="12345", 
        is_warehouse_manager = True,
        is_teaching_staff_member = False,
        phone_number="0538389945")

    db.session.add(user2)
    db.session.commit()

    user3 = User(
        first_name="stu", 
        last_name="student", 
        email_address="student@email.com",
        password="12345", 
        is_warehouse_manager = False,
        is_teaching_staff_member = False,
        phone_number="0503251150")
    
    db.session.add(user3)
    db.session.commit()

    item1 = Item(
        item_ID = "123456789",
        item_name = "מצלמה",
        item_type = "סוני",
        item_desc = "המצלמה הכי חדשה של סוני"
    )

    db.session.add(item1)
    db.session.commit()

    req = LoanRequest(
        opened_on = datetime(2023, 5, 31, 10, 00),
        borrowing_date = datetime(2023, 5, 31, 10, 00),
        return_date = datetime(2023, 6, 2, 11, 30),
        reason_for_borrowing = "test",
        status = "Activated",
        user_id = user3.id,
        item_id = item1.id
    )

    db.session.add(req)
    db.session.commit()
    
    print("database create...")
