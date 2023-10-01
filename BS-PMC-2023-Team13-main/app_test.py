from datetime import datetime, timedelta
import re
import unittest
from urllib.parse import urlparse
import bcrypt
from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy
from website.forms import LoanRequestForm, LoginForm, add_users_manually_form, ItemForm, EditRequestForm
from flask_login import current_user, logout_user
from flask_testing import TestCase
from website.models import LoanRequest, User, Item, Repair_Table, Notification
from website import create_app, db, app
from development_functions import database_start_over

import unittest
from website.models import User

TEST_FIRST_NAME = "Unit Test FN"
TEST_LAST_NAME = "Unit Test LN"
TEST_PHONE = "0555555555"
TEST_EMAIL =  "UnitTestUser@Test.com"
TEST_PASSWORD = "123456" 
TEST_FAILURE_PASSWORD = "000000"
TEST_NEW_PASSWORD = "1234567"
TEST_STUDENT_FIELD = "Student"
TEST_TEACHER_FIELD = "Teacher"
TEST_ADD_USER_MAIL = "UnitTestUser22@Test.com"

TEST_ITEM_ID = "1234567890"
TEST_ITEM_NAME = "Camera"
TEST_ITEM_TYPE = "Sony"
TEST_ITEM_DESC = "Newest Sony's camera"

def make_student_test_user(self):
    user = User.query.filter_by(email_address=TEST_EMAIL).first()
    if not user:
        self.user = User(
            first_name= TEST_FIRST_NAME,
            last_name= TEST_LAST_NAME,
            email_address= TEST_EMAIL,
            password= TEST_PASSWORD,
            phone_number= TEST_PHONE,
        )
        db.session.add(self.user)
        db.session.commit()

def make_teacher_test_user(self):
    user = User.query.filter_by(email_address=TEST_EMAIL).first()
    if not user:
        self.user = User(
            first_name= TEST_FIRST_NAME,
            last_name= TEST_LAST_NAME,
            email_address= TEST_EMAIL,
            password= TEST_PASSWORD,
            phone_number= TEST_PHONE,
            is_teaching_staff_member = True,
        )
        db.session.add(self.user)
        db.session.commit()

def make_manager_test_user(self):
    user = User.query.filter_by(email_address=TEST_EMAIL).first()
    if not user:
        self.user = User(
            first_name= TEST_FIRST_NAME,
            last_name= TEST_LAST_NAME,
            email_address= TEST_EMAIL,
            password= TEST_PASSWORD,
            phone_number= TEST_PHONE,
            is_warehouse_manager = True,
            
        )
        db.session.add(self.user)
        db.session.commit()

class TestUpdateUser(TestCase):    

    def create_app(self):
        print("::create_app()")
        with app.app_context():
            db.session.remove()
            app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
            app.config['TESTING'] = True
            app.config['WTF_CSRF_ENABLED'] = False
        return app

    def setUp(self):
        print("::setUp()")
        with self.app.app_context():
            db.session.remove()
            db.create_all()

        db.session.expunge_all()

    def tearDown(self):
        print("::tearDown()")
        user = User.query.filter_by(email_address=TEST_EMAIL).first()
        if user:
            db.session.delete(user)
            db.session.commit()

    def test_update_user(self):
        make_student_test_user(self)
        print("::test_update_user()")
        with self.client:
            self.client.post('/login', data=dict(
                email= TEST_EMAIL,
                password= TEST_PASSWORD
            ))

            response = self.client.post('/update_user', data=dict(
                first_name='NewUnitTest',
                last_name='NewUnitTest',
                phone_number='0555555555',
                current_password= TEST_PASSWORD,
                new_password=TEST_NEW_PASSWORD,
                confirm_password= TEST_NEW_PASSWORD
            ), follow_redirects=True)

            user = User.query.filter_by(email_address=TEST_EMAIL).first()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(user.first_name, 'NewUnitTest')
            self.assertEqual(user.last_name, 'NewUnitTest')
            self.assertEqual(user.phone_number, '0555555555')
            self.assertTrue(user.check_password_correction('1234567'))
            self.assertFalse(user.check_password_correction('123456'))

    def test_logout_route(self):
        make_student_test_user(self)
        print("::test_logout_route()")
        logout_user()
        response = self.client.get('/logout')
        assert response.status_code == 401

        # Log in a user
        with self.client:
            self.client.post('/login', data=dict(
                email= TEST_EMAIL,
                password= TEST_PASSWORD
            ))

        # Access the logout page
        response = self.client.get('/logout')

        # Verify that the user is logged out and redirected to the index page
        assert response.status_code == 302
        assert response.headers['Location'] == url_for("login")
        assert current_user.is_authenticated == False

    def test_login_success(self):
        make_student_test_user(self)
        form = LoginForm(email=TEST_EMAIL, password=TEST_PASSWORD)
        response = self.client.post('/login', data=form.data, follow_redirects=True)

        # Assert that user is logged in and redirected to home page
        assert current_user.is_authenticated
        assert 'התחברת בהצלחה' in response.data.decode('utf-8')
        assert response.status_code == 200

    # Test user login with incorrect credentials
    
    def test_login_failure(self):
        make_student_test_user(self)
        print("::test_login_failure()")
        # Send POST request with invalid credentials
        form = LoginForm(email=TEST_EMAIL, password=TEST_FAILURE_PASSWORD)
        response = self.client.post('/login', data=form.data, follow_redirects=True)

        # Assert that user is not logged in and error message is displayed
        assert not current_user.is_authenticated
        assert 'שם המשתמש והסיסמה אינם תואמים.' in response.data.decode('utf-8')
        assert response.status_code == 200        

    def test_add_user_manually(self):
        print("::test_add_user_manually()")
        make_manager_test_user(self)
        with self.client:
            self.client.post('/login', data=dict(
                email= TEST_EMAIL,
                password= TEST_PASSWORD
            ))

        form = add_users_manually_form(first_name=TEST_FIRST_NAME, last_name=TEST_LAST_NAME, phone_number=TEST_PHONE, email=TEST_ADD_USER_MAIL,select_field = TEST_STUDENT_FIELD)  
        self.assertFalse(form.validate())
        response = self.client.post('/add_manually', data=form.data, follow_redirects=True)
        user = User.query.filter_by(email_address=TEST_ADD_USER_MAIL).first()    
        self.assertEqual(response.status_code, 200)
        self.assertEqual(user.first_name, TEST_FIRST_NAME)
        self.assertEqual(user.last_name, TEST_LAST_NAME)
        self.assertEqual(user.phone_number, TEST_PHONE)
        if user:
            db.session.delete(user)
            db.session.commit()
        logout_user()   



    def test_add_item(self):
        print("::test_add_item()")
        make_manager_test_user(self) 
        with self.client:
            self.client.post('/login', data=dict(
                email=TEST_EMAIL,
                password=TEST_PASSWORD
            ))

        response = self.client.post('/add_item', data=dict(
            item_id = TEST_ITEM_ID,
            item_name = TEST_ITEM_NAME,
            item_type = TEST_ITEM_TYPE,
            item_desc = TEST_ITEM_DESC
        ), follow_redirects=True)

        item = Item.query.filter_by(item_ID=TEST_ITEM_ID).first()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(item.item_ID, TEST_ITEM_ID)
        self.assertEqual(item.item_name, TEST_ITEM_NAME)
        self.assertEqual(item.item_type, TEST_ITEM_TYPE)
        self.assertEqual(item.item_desc, TEST_ITEM_DESC)

        if item:
            db.session.delete(item)
            db.session.commit()
        logout_user()


    def test_show_item(self):
        item = Item(item_ID="11112222", item_name=TEST_ITEM_NAME, item_type=TEST_ITEM_TYPE, item_desc=TEST_ITEM_DESC)
        db.session.add(item)
        db.session.commit()

        # Simulate a logged-in user with warehouse_manager role
        user = User(
            first_name= TEST_FIRST_NAME,
            last_name= TEST_LAST_NAME,
            email_address= TEST_EMAIL,
            password= TEST_PASSWORD,
            phone_number= TEST_PHONE,
            is_teaching_staff_member = True,
        )
        db.session.add(user)
        db.session.commit()

        with self.client:
            # Ensure that a warehouse manager can access the show_item route
            self.client.post('/login', data=dict(
                email= TEST_EMAIL,
                password= TEST_PASSWORD
            ))

            response = self.client.get(url_for('repairs'))

            item = Item.query.filter_by(item_ID=TEST_ITEM_ID).first()
            response = self.client.get(url_for('show_item', item_id=item.id))
            self.assertEqual(response.status_code, 302)

            # Ensure that a non-warehouse manager is redirected to home_page
            user.is_warehouse_manager = False
            db.session.commit()
            response = self.client.get(url_for('show_item', item_id=item.id))
            self.assertEqual(response.status_code, 302)
            expected_location = url_for('home_page', _external=True)
            expected_path = urlparse(expected_location).path
            actual_path = urlparse(response.location).path
            self.assertEqual(actual_path, expected_path)


            # Ensure that an invalid item id is redirected to repairs
            response = self.client.get(url_for('show_item', item_id=100))
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.location, '/dashboard')
            logout_user()


    def test_repair_item(self):

        item_ = Item(item_ID=TEST_ITEM_ID, item_name=TEST_ITEM_NAME, item_type=TEST_ITEM_TYPE, item_desc=TEST_ITEM_DESC)
        db.session.add(item_)
        db.session.commit()

        # Create a warehouse manager user
        warehouse_manager = User(
            first_name= TEST_FIRST_NAME,
            last_name= TEST_LAST_NAME,
            email_address= TEST_EMAIL,
            password= TEST_PASSWORD,
            phone_number= TEST_PHONE,
            is_warehouse_manager = True,
        )
        db.session.add(warehouse_manager)
        db.session.commit()


        loan_request = LoanRequest(
                borrowing_date = datetime(2023, 5, 31, 12, 0),
                return_date = datetime(2023, 6, 1, 12, 0),
                reason_for_borrowing = "Test",
                status = "Approved",
                user_id = 1,
                item_id = item_.id
            )
        db.session.add(loan_request)
        db.session.commit()


        # Simulate a logged-in warehouse manager
        with self.client:
            self.client.post('/login', data=dict(
                email= TEST_EMAIL,
                password= TEST_PASSWORD
            ))

            # Create a test item
            response = self.client.get(url_for('repairs'))
            self.assertEqual(response.status_code, 200)


            item = Item.query.filter_by(item_ID=TEST_ITEM_ID).first()
            response = self.client.get(url_for('show_item', item_id=item.id))
            self.assertEqual(response.status_code, 200)

            
            # Test POST request to repair_item route
            response = self.client.post(url_for('repair_item', item_id=item.id))
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.location, '/repairs')

            # Assert that the item, loan request, and repair are updated correctly
            updated_item = Item.query.get(item.id)
            assert updated_item.status == 'Under Repair'
            

            updated_loan_request = LoanRequest.query.get(loan_request.id)
            assert updated_loan_request.status == 'Canceled'
            db.session.commit()

            repair = Repair_Table.query.filter_by(item_id=item.id).first()
            assert repair is not None

            # Test non-existing item
            response = self.client.post(url_for('repair_item', item_id=100))
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.location, '/repairs')
            logout_user()
    
    
class TestReports(TestCase):
    def create_app(self):
        print("::create_app()")
        with app.app_context():
            db.session.remove()
            app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
            app.config['TESTING'] = True
            app.config['WTF_CSRF_ENABLED'] = False
        return app

    def setUp(self):
        print("::setUp()")
        with self.app.app_context():
            db.session.remove()
            db.create_all()

        db.session.expunge_all()

    def tearDown(self):
        print("::tearDown()")
        user = User.query.filter_by(email_address=TEST_EMAIL).first()
        if user:
            db.session.delete(user)
            db.session.commit()     
    def test_last_orders_report(self):
        """
        Test the last_orders_report route.

        This method performs the following steps:
        
        Creates a test user and logs in.
        Creates a loan request for testing.
        Sends a POST request to the last_orders_report route with a search start date.
        Asserts that the response status code is 200 (OK).
        Asserts that the loan request is included in the response.
        Deletes the loan request to clean up.

        """
        make_manager_test_user(self)
        print("::test_last_orders_report()")
        with self.client:
            self.client.post('/login', data=dict(
                email=TEST_EMAIL,
                password=TEST_PASSWORD
            ))

        # Create a loan request for testing
        loan_request = LoanRequest(
            user_id=current_user.id,
            borrowing_date=datetime.now(),
            return_date=datetime.now(),
            reason_for_borrowing="Testing",
            status="נשלח לאישור",
            opened_on=datetime.now()
        )
        db.session.add(loan_request)
        db.session.commit()

        # Simulate a POST request to the last_orders_report route
        response = self.client.post('/last_orders_report', data={
            'search_start_date': datetime.now().strftime('%Y-%m-%d'),
        }, follow_redirects=True)

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Assert that the loan request is included in the response
        self.assertIn(bytes(loan_request.reason_for_borrowing, 'utf-8'), response.data)

        # Clean up: Delete the loan request
        db.session.delete(loan_request)
        db.session.commit()   


class TestReturnedOrdersReport(TestCase):
    def create_app(self):
        # Perform any necessary app configurations
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        return app

    def setUp(self):
        # Perform any necessary setup for the test
        # Example: initialize the app and any other dependencies
        self.app = self.create_app()
        self.client = self.app.test_client()

        with self.app.app_context():
            # Set up the database and any required data
            db.create_all()

    def tearDown(self):
        # Perform any necessary clean-up after the test
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_generate_returned_orders_report_get(self):
        # Send a GET request to the generate_returned_orders_report route
        response = self.client.get('/reports/returned_orders')

        # Assert that the response is successful
        self.assertEqual(response.status_code, 200)


class TestReturnedOrders(unittest.TestCase):
    def setUp(self):
        print("::setUp")
        self.app = app.test_client()
        self.app.testing = True

    def test_generate_returned_orders_report(self):
        # Simulate a POST request with return-date parameter
        response = self.app.post('/reports/returned_orders', data={'return-date': '2023-05-30'})
        self.assertEqual(response.status_code, 200)

        # Simulate a GET request
        response = self.app.get('/reports/returned_orders')
        self.assertEqual(response.status_code, 200)


class Test_approve_request(unittest.TestCase):
    def setUp(self):
        # Create a test Flask app
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Create a test client
        self.client = self.app.test_client()
        
        # Create the test database and bind it to the app
        with self.app.app_context():
            db.create_all()
        
    def tearDown(self):
        # Remove the test database and close the app context
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
        
        self.app_context.pop()
        
    def test_approve_request(self):
        """Test the /approve_request/<request_id> route."""
        # Create a user
        user = User(first_name='John', last_name='Doe', password=TEST_PASSWORD, email_address='johndoe@example.com')
        db.session.add(user)
        db.session.commit()

        # Create an item
        item = Item(item_ID='item123', item_name='Test Item', item_type='Type A', item_desc='Test item description')
        db.session.add(item)
        db.session.commit()

        # Create a loan request
        loan_request = LoanRequest(
            loan_request_user=user,
            loan_request_item=item,
            borrowing_date=datetime.utcnow(),
            return_date=datetime.utcnow() + timedelta(days=7),
            reason_for_borrowing='Test reason',
            status='Pending'
        )
        db.session.add(loan_request)
        db.session.commit()

        # Log in as a warehouse manager
        warehouse_manager = User(first_name='Warehouse', last_name='Manager', password=TEST_PASSWORD, email_address='warehouse@example.com', is_warehouse_manager=True)
        db.session.add(warehouse_manager)
        db.session.commit()

        with self.client:
            # Authenticate as the warehouse manager
            response = self.client.post('/login', data={'email': 'warehouse@example.com', 'password': TEST_PASSWORD}, follow_redirects=True)
            self.assertEqual(response.status_code, 200)




class TestOrders(TestCase):
    def create_app(self):
        print("::create_app()")
        with app.app_context():
            db.session.remove()
            app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
            app.config['TESTING'] = True
            app.config['WTF_CSRF_ENABLED'] = False
        return app

    def setUp(self):
        print("::setUp()")
        with self.app.app_context():
            db.session.remove()
            db.create_all()

        db.session.expunge_all()

    def tearDown(self):
        print("::tearDown()")
        user = User.query.filter_by(email_address=TEST_EMAIL).first()
        if user:
            db.session.delete(user)
            db.session.commit()
    def test_income_orders(self):
        # Test the income_orders route
        make_manager_test_user(self) 
        # Create a user with warehouse manager role
        with self.client:
            self.client.post('/login', data=dict(
                email= TEST_EMAIL,
                password= TEST_PASSWORD
            ))

            
        # Make a GET request to the income_orders route
        response = self.client.get(url_for('income_orders'))

        # Assert that the response is successful (status code 200)
        self.assertEqual(response.status_code, 200)

        logout_user()  




def create_app():
    # Your app configuration and other setup code here
    # ...

    return app

# Register the blueprint outside of create_app function
# app.register_blueprint(bp)

class AboutPageIntegrationTest(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def test_about_route(self):
        """
        Test the '/about' route.

        Sends a GET request to the '/about' route and asserts various conditions on the response.

        Assertions:
        - Response status code should be 200 (OK). 
        - The response should have the expected Content-Type header.
        - The response body should contain the expected HTML content.
        """        
        response = self.app.get('/about')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'text/html; charset=utf-8')
        self.assertIn("<h1>עלינו</h1>", response.data.decode('utf-8'))
        self.assertIn("<h2>ברוכים הבאים למחסן של המחלקה לתקשורת חזותית!</h2>", response.data.decode('utf-8'))
        self.assertIn("&copy; 2023 המחלקה להנדסת תוכנה.", response.data.decode('utf-8'))
        self.assertIn("האתר WH-Organization נוצר על מנת ליעיל את אופן השאלות הציוד בין אנשי המחלקה לתקשורת", response.data.decode('utf-8'))
        self.assertIn("חזותית לבין מנהלי מחסן המחלקה. האתר מספק פלטפורמה נוחה לפתיחת בקשות לאישורם ולמעקבם.", response.data.decode('utf-8'))
        self.assertIn("מפתחי האתר: Klassen Eva-Maria , Moiseyev Ester,Dali Yarden, Abitbul Gilad", response.data.decode('utf-8'))
        self.assertIn("אנשי מחסן המחלקה:  {המייל של שי }", response.data.decode('utf-8'))


if __name__ == '__main__':
    database_start_over()
    unittest.main()

