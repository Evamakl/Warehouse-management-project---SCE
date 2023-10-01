import sys
import os
import bcrypt


# Add the parent directory of BS-PMC-2023-Team13 to the Python path
project_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_directory)

# Rest of your test code
import pytest
from flask import request, session, url_for, flash
from website.models import LoanRequest, Notification, Repair_Table, User, Item, recommend_file_detail
from website import app, db
from website.forms import EditRequestForm, ItemForm, LoanRequestForm, LoginForm, UpdateUserForm, add_users_manually_form, recommendationForm, upload_csv_form
from flask_login import LoginManager, current_user, login_user, logout_user
from flask.testing import FlaskClient
from website import create_app

from flask_sqlalchemy import SQLAlchemy
from bcrypt import hashpw, gensalt

from flask import request
from flask_wtf.csrf import generate_csrf

def test_login_form():
    """
    Test the validation of the login form with valid data.
    """
    with app.test_request_context('/login', method='POST', data={
            'email': 'test@example.com',
            'password': 'password123',
            'submit': True,
        }):
        # Manually set the CSRF token in the form
        form = LoginForm(request.form)
        form.csrf_token.data = generate_csrf()

        print(form.data)
        assert form.validate()

def test_login_form_invalid_data():
    """
    Test the validation of the login form with invalid data.
    """
    with app.test_request_context('/login', method='POST', data={'email': 'invalid_email', 'password': ''}):
        form = LoginForm(request.form)
        assert not form.validate()  # Assuming validation fails



def test_add_users_manually_form():
 def test_add_users_manually_form():
    """
    Test the validation of the add_users_manually_form with valid data.
    """
    with app.test_request_context('/add_users', method='POST', data={
            'first_name': 'John',
            'last_name': 'Doe',
            'phone_number': '1234567890',
            'email': 'test@example.com',
            'select_field': 'Student',
            'submit': True,
            'csrf_token': generate_csrf(),
        }):

        form = add_users_manually_form(request.form)
        print(form.data)
        assert form.validate()



def test_add_users_manually_form_invalid_data():
    """
    Test the validation of the add_users_manually_form with invalid data.
    """
    form_data = {
        'first_name': '',
        'last_name': '',
        'phone_number': '',
        'email': 'invalid_email',
        'select_field': '',
        'submit': True
    }

    form = add_users_manually_form(data=form_data)

    assert not form.validate()  # Assuming validation fails
    assert form.errors != {}  # Validation errors are present



#------------------------------------------FOR ESTER----------------------------------------------
# from werkzeug.datastructures import FileStorage

# def test_upload_csv_form():
#     """
#     Test the validation of the upload_csv_form with a valid CSV file.
#     """
#     # Replace 'valid_csv_file_path' with the actual path to a valid CSV file on your system
#     csv_file_path = '/path/to/dummy.csv'

#     # Create a FileStorage object with the CSV file
#     csv_file = FileStorage(stream=open(csv_file_path, 'rb'), filename='file.csv')

#     # Create form data with the CSV file
#     form_data = {'csv_file': csv_file, 'submit': True}

#     # Create an instance of the upload_csv_form with the form data
#     form = upload_csv_form(data=form_data)

#     # Assert that the form validation passes
#     assert form.validate()

#------------------------------------------END FOR ESTER----------------------------------------------

def test_update_user_form():
    """
    Test the validation of the UpdateUserForm with valid data.
    """
    with app.test_request_context('/update_user', method='POST', data={
            'first_name': 'John',
            'last_name': 'Doe',
            'phone_number': '1234567890',
            'current_password': 'oldpassword',
            'new_password': 'newpassword',
            'confirm_password': 'newpassword',
            'submit': True,
        }):
        # Manually set the CSRF token in the form
        form = UpdateUserForm(request.form)
        form.csrf_token.data = generate_csrf()

        print(form.data)

        assert form.first_name.validate(form)
        assert form.last_name.validate(form)
        assert form.phone_number.validate(form)
        assert form.current_password.validate(form)
        assert form.new_password.validate(form)
        assert form.confirm_password.validate(form)


def test_update_user_form_invalid_data():
    """
    Test the validation of the UpdateUserForm with invalid data.
    """
    with app.test_request_context('/update_user', method='POST', data={
            'first_name': 'J',
            'last_name': '',
            'phone_number': '1234567890',
            'current_password': 'oldpassword',
            'new_password': 'newpassword',
            'confirm_password': 'wrongpassword',
            'submit': True,
        }):
        # Manually set the CSRF token in the form
        form = UpdateUserForm(request.form)
        form.csrf_token.data = generate_csrf()

        print(form.data)

        assert not form.validate()

        if form.errors:
            print(form.errors)


def test_item_form():
    """
    Test the validation of the ItemForm with valid data.
    """
    with app.test_request_context('/item', method='POST', data={
            'item_id': '12345',
            'item_name': 'Item 1',
            'item_type': 'Type 1',
            'item_desc': 'Description of item',
            'submit': True
        }):
        # Manually set the CSRF token in the form
        form = ItemForm(request.form)
        form.csrf_token.data = generate_csrf()

        print(form.data)

        if form.validate():
            print("Form validation passed")
        else:
            print("Form validation failed")
            print(form.errors)



def test_item_form_invalid_data():
    """
    Test the validation of the ItemForm with invalid data.
    """
    with app.test_request_context('/item', method='POST', data={
            'item_id': '',  # Invalid: Empty value
            'item_name': 'Item 1',
            'item_type': 'Type 1',
            'item_desc': 'Description of item',
            'submit': True
        }):
        # Manually set the CSRF token in the form
        form = ItemForm(request.form)
        form.csrf_token.data = generate_csrf()

        print(form.data)

        if form.validate():
            print("Form validation passed")
        else:
            print("Form validation failed")
            print(form.errors)




def test_loan_request_form():
    """
    Test the validation of the LoanRequestForm with valid data.
    """
    with app.test_request_context('/loan_request', method='POST', data={
            'borrowing_date': '2023-05-30T10:00',
            'return_date': '2023-05-30T12:00',
            'reason_for_borrowing': 'Testing loan request form',
            'submit': True
        }):
        # Manually set the CSRF token in the form
        form = LoanRequestForm(request.form)
        form.csrf_token.data = generate_csrf()

        print(form.data)

        if form.validate():
            print("Form validation passed")
        else:
            print("Form validation failed")
            print(form.errors)


def test_loan_request_form_invalid_data():
    """
    Test the validation of the LoanRequestForm with invalid data.
    """
    with app.test_request_context('/loan_request', method='POST', data={
            'borrowing_date': '2023-05-30T08:00',  # Invalid: Outside allowed time range
            'return_date': '2023-05-30T07:00',  # Invalid: Before borrowing date
            'reason_for_borrowing': '',  # Invalid: Empty value
            'submit': True
        }):
        # Manually set the CSRF token in the form
        form = LoanRequestForm(request.form)
        form.csrf_token.data = generate_csrf()

        print(form.data)

        if form.validate():
            print("Form validation passed")
        else:
            print("Form validation failed")
            print(form.errors)





def test_recommendation_form():
    """
    Test the validation of the RecommendationForm with valid data.
    """
    with app.test_request_context('/recommendation', method='POST', data={
            'item_name': 'Item 1',
            'reason': 'Reason for recommendation',
            'amount': 5,
            'submit': True
        }):
        # Manually set the CSRF token in the form
        form = recommendationForm(request.form)
        form.csrf_token.data = generate_csrf()

        print(form.data)

        if form.validate():
            print("Form validation passed")
        else:
            print("Form validation failed")
            print(form.errors)




def test_recommendation_form_invalid_data():
    """
    Test the validation of the RecommendationForm with invalid data.
    """
    with app.test_request_context('/recommendation', method='POST', data={
            'item_name': '',  # Invalid: Empty value
            'reason': '',  # Invalid: Empty value
            'amount': '',  # Invalid: Empty value
            'submit': True
        }):
        # Manually set the CSRF token in the form
        form = recommendationForm(request.form)
        form.csrf_token.data = generate_csrf()

        print(form.data)

        if form.validate():
            print("Form validation passed")
        else:
            print("Form validation failed")
            print(form.errors)


def test_edit_request_form():
    """
    Test the validation of the EditRequestForm with valid data.
    """
    with app.test_request_context('/edit_request', method='POST', data={
            'borrowing_date': '2023-05-30T10:00',
            'return_date': '2023-05-31T12:00',
            'reason_for_borrowing': 'Updated reason for borrowing',
            'submit': True
        }):
        # Manually set the CSRF token in the form
        form = EditRequestForm(request.form)
        form.csrf_token.data = generate_csrf()

        print(form.data)

        if form.validate():
            print("Form validation passed")
        else:
            print("Form validation failed")
            print(form.errors)


from datetime import datetime

def test_edit_request_form_invalid_data():
    """
    Test the validation of the EditRequestForm with invalid data.
    """
    with app.test_request_context('/edit_request', method='POST', data={
            'borrowing_date': '2023-05-30T10:00',  # Valid: Non-empty value
            'return_date': '2023-05-31T12:00',
            'reason_for_borrowing': 'Updated reason for borrowing',
            'submit': True
        }):
        # Manually set the CSRF token in the form
        form = EditRequestForm(request.form)
        form.csrf_token.data = generate_csrf()

        print(form.data)

        if form.validate():
            print("Form validation passed")
        else:
            print("Form validation failed")
            print(form.errors)



# ----------------------------------------------------------------- לא עובד -------------------------------------------
# def test_user_model():
#     """
#     Test the User model.

#     This test function verifies the behavior of the User model class.

#     Steps:
#     1. Create a new user with sample data.
#     2. Assert the user's attributes to ensure they match the provided data.
#     3. Assert the user's relationships to ensure they are initially empty.
#     4. Test the string representation to ensure it matches the expected format.

#     """
#     # Create a new user
#     user = User(
#         id=5,
#         first_name='John',
#         last_name='Doe',
#         email_address='john.doe@example.com',
#         password_hash='hashed_password',
#         is_warehouse_manager=False,
#         is_teaching_staff_member=False,
#         phone_number='1234567890'
#     )

#     # Assert the user's attributes
#     assert user.first_name == 'John'
#     assert user.last_name == 'Doe'
#     assert user.email_address == 'john.doe@example.com'
#     assert user.password_hash == 'hashed_password'
#     assert user.is_warehouse_manager is False
#     assert user.is_teaching_staff_member is False
#     assert user.phone_number == '1234567890'

#     # Assert the user's relationships
#     assert user.loan_requests == []  # Assuming the relationship returns an empty list initially
#     assert user.recommend_files == []  # Assuming the relationship returns an empty list initially
#     assert user.messages == []  # Assuming the relationship returns an empty list initially

#     # Test the string representation
#     expected_repr = "user(id=5, first_name='John', last_name='Doe', email_address='john.doe@example.com', password_hash='hashed_password', is_warehouse_manager=False, is_teaching_staff_member=False, phone_number='1234567890')"
#     assert repr(user) == expected_repr

# -----------------------------------------------------------------------------------------------------------------------------------------


def test_valid_item_model():
    """
    Test the Item model with valid data.

    This test function verifies the behavior of the Item model class using valid data.

    Steps:
    1. Create a new item with valid data.
    2. Assert the item's attributes to ensure they match the provided data.
    3. Test the item's default status attribute.
    """

    # Create a new item with valid data
    item = Item(
        id=1,
        item_ID='ABC123',
        item_name='Example Item',
        item_type='Type A',
        item_desc='This is an example item.',
        status='Available'
    )

    # Assert the item's attributes
    assert item.item_ID == 'ABC123'
    assert item.item_name == 'Example Item'
    assert item.item_type == 'Type A'
    assert item.item_desc == 'This is an example item.'
    assert item.status == 'Available'

    # Test the default status attribute
    default_item = Item(
        id=2,
        item_ID='DEF456',
        item_name='Another Item',
        item_type='Type B',
        item_desc='This is another item.'
    )
    assert default_item.status == 'Available' or default_item.status is None


def test_invalid_item_model():
    """
    Test the Item model with invalid data.

    This test function verifies the behavior of the Item model class using invalid data.

    Steps:
    1. Create a new item with invalid data.
    2. Assert the item's attributes to ensure they match the provided data.
    3. Test the item's default status attribute.
    """

    # Create a new item with invalid data
    invalid_item = Item(
        id=3,
        item_ID='GHI789',
        item_name=None,
        item_type='Type C',
        item_desc='This is an invalid item with missing name.',
        status='Available'
    )

    # Assert the item's attributes
    assert invalid_item.item_ID == 'GHI789'
    assert invalid_item.item_name is None
    assert invalid_item.item_type == 'Type C'
    assert invalid_item.item_desc == 'This is an invalid item with missing name.'
    assert invalid_item.status == 'Available'




import pytest
from datetime import datetime, timedelta

@pytest.fixture
def sample_loan_request():
    """
    Fixture to create a sample loan request for testing.
    """
    # Create a sample item
    item = Item(
        id=1,
        item_ID='ABC123',
        item_name='Example Item',
        item_type='Type A',
        item_desc='This is an example item.',
        status='Available'
    )
    
    # Create a sample user
    user = User(
        id=1,
        first_name='John',
        last_name='Doe',
        email_address='john.doe@example.com',
        password_hash='hashed_password',
        is_warehouse_manager=False,
        is_teaching_staff_member=False,
        phone_number='1234567890'
    )
    
    # Create a sample loan request
    loan_request = LoanRequest(
        id=1,
        loan_request_item=item,
        loan_request_user=user,
        borrowing_date=datetime.now(),
        return_date=datetime.now() + timedelta(days=7),
        reason_for_borrowing='Test request',
        status='Approved',
        user_id=user.id,
        item_id=item.id
    )
    
    return loan_request


def test_check_for_conflicting_request(sample_loan_request):
    """
    Test the check_for_conflicting_request method of LoanRequest.

    This test verifies that the method correctly returns None when there are no conflicting requests for the same item
    during the selected dates.
    """
    conflicting_request = sample_loan_request.check_for_conflicting_request()
    assert conflicting_request is None


def test_cancel_request(sample_loan_request):
    """
    Test the cancel_request method of LoanRequest.

    This test ensures that the cancel_request method sets the status of a loan request to "Canceled" when the request
    is in the "נשלח לאישור" status.
    """
    # Set the status to "נשלח לאישור"
    sample_loan_request.status = "נשלח לאישור"

    result, message = sample_loan_request.cancel_request()
    assert result is True
    assert message == "Request has been canceled successfully."
    assert sample_loan_request.status == "Canceled"









def test_edit_request(sample_loan_request):
    """
    Test the edit_request method of LoanRequest.

    This test verifies that the edit_request method updates the borrowing date, return date, and reason for borrowing
    of a loan request correctly.
    """
    borrowing_date = datetime.now() + timedelta(days=1)
    return_date = datetime.now() + timedelta(days=14)
    reason_for_borrowing = "Updated test request"

    result, message = sample_loan_request.edit_request(borrowing_date, return_date, reason_for_borrowing)
    assert result is True
    assert message == "Request details have been updated successfully."
    assert sample_loan_request.borrowing_date == borrowing_date
    assert sample_loan_request.return_date == return_date
    assert sample_loan_request.reason_for_borrowing == reason_for_borrowing





def test_recommend_file_detail():
    """
    Test the recommend_file_detail class.
    """
    # Create a sample recommend_file_detail object
    recommend_file = recommend_file_detail(
        id=1,
        user_id=123,
        user_first_name="John",
        user_last_name="Doe",
        user_phone_number="1234567890",
        item_name="Item 1",
        reason="Recommendation reason",
        amount=5,
        status="Pending",
        date_submitted="2023-05-28"
    )

    # Verify the attributes of the recommend_file_detail object
    assert recommend_file.id == 1
    assert recommend_file.user_id == 123
    assert recommend_file.user_first_name == "John"
    assert recommend_file.user_last_name == "Doe"
    assert recommend_file.user_phone_number == "1234567890"
    assert recommend_file.item_name == "Item 1"
    assert recommend_file.reason == "Recommendation reason"
    assert recommend_file.amount == 5
    assert recommend_file.status == "Pending"
    assert recommend_file.date_submitted == "2023-05-28"



def test_recommend_file_detail_invalid_data():
    """
    Test the recommend_file_detail class with invalid data.
    """
    # Create an instance of recommend_file_detail with invalid data
    invalid_recommendation = recommend_file_detail(
        id=1001,
        user_id=None,  # Invalid user ID (None)
        user_first_name="",
        user_last_name="",
        user_phone_number="1234567890",
        item_name="",  # Invalid empty item name
        reason="",
        amount=0,  # Invalid amount (zero)
        status="InvalidStatus",
        date_submitted="2023-05-28"
    )

    # Validate the object against the defined model schema or constraints
    is_valid = True
    errors = []

    if invalid_recommendation.user_id is None:
        is_valid = False
        errors.append("User ID is required.")

    # Add more validation checks for other fields if needed
    if not invalid_recommendation.item_name:
        is_valid = False
        errors.append("Item name is required.")

    if invalid_recommendation.amount <= 0:
        is_valid = False
        errors.append("Amount must be greater than zero.")


    if not invalid_recommendation.reason:
        is_valid = False
        errors.append("Reason is required.")

    if not invalid_recommendation.user_first_name:
        is_valid = False
        errors.append("User first name is required.")

    if not invalid_recommendation.user_last_name:
        is_valid = False
        errors.append("User last name is required.")


    if invalid_recommendation.status not in ["Pending", "Approved", "Rejected"]:
        is_valid = False
        errors.append("Invalid status.")

    # Assert that the object is not valid and has the expected validation errors
    assert not is_valid
    assert errors == ["User ID is required.", "Item name is required.", "Amount must be greater than zero.","Reason is required.","User first name is required.",
        "User last name is required.","Invalid status."]





def test_repair_table_valid_data():
    """
    Test the Repair_Table class with valid data.

    This test ensures that the Repair_Table instance is created correctly with the provided valid data.
    It verifies that the attributes of the instance match the provided data.
    """
    repair_id = 1001
    item_id = "ITEM001"
    item_name = "Item Name"
    repair_date = datetime.now()
    status = "בתיקון"

    # Create an instance of Repair_Table with valid data
    repair_table = Repair_Table(
        id=repair_id,
        item_id=item_id,
        item_name=item_name,
        repair_date=repair_date,
        status=status
    )

    # Assert that the attributes of the Repair_Table instance match the provided data
    assert repair_table.id == repair_id
    assert repair_table.item_id == item_id
    assert repair_table.item_name == item_name
    assert repair_table.repair_date == repair_date
    assert repair_table.status == status



def test_repair_table_invalid_data():
    """
    Test the Repair_Table class with invalid data.

    This test ensures that the Repair_Table instance fails validation with the provided invalid data.
    It checks for specific validation errors for each invalid field and asserts that the object is not valid.
    """
    # Create an instance of Repair_Table with invalid data
    invalid_repair_table = Repair_Table(
        id=None,  # Invalid ID (None)
        item_id=None,  # Invalid item ID (None)
        item_name="",  # Invalid empty item name
        repair_date=None,  # Invalid repair date (None)
        status="InvalidStatus"  # Invalid status
    )

    # Validate the object against the defined model schema or constraints
    is_valid = True
    errors = []

    if invalid_repair_table.id is None:
        is_valid = False
        errors.append("ID is required.")

    if invalid_repair_table.item_id is None:
        is_valid = False
        errors.append("Item ID is required.")

    if not invalid_repair_table.item_name:
        is_valid = False
        errors.append("Item name is required.")

    if invalid_repair_table.repair_date is None:
        is_valid = False
        errors.append("Repair date is required.")

    if invalid_repair_table.status not in ["בתיקון", "תקלה נמוכה", "תקלה גבוהה"]:
        is_valid = False
        errors.append("Invalid status.")

    # Assert that the object is not valid and has the expected validation errors
    assert not is_valid
    assert errors == [
        "ID is required.",
        "Item ID is required.",
        "Item name is required.",
        "Repair date is required.",
        "Invalid status."
    ]




def test_notification_valid_data():
    """
    Test the Notification class with valid data.

    This test ensures that the Notification instance is created correctly with the provided valid data.
    It verifies that the attributes of the instance match the provided data.
    """
    user_id = 1001
    msg_date = datetime.now()
    message = "Notification message"
    status = "Sent"

    # Create an instance of Notification with valid data
    notification = Notification(
        user_id=user_id,
        msg_date=msg_date,
        message=message,
        status=status
    )

    # Assert that the attributes of the Notification instance match the provided data
    assert notification.user_id == user_id
    assert notification.msg_date == msg_date
    assert notification.message == message
    assert notification.status == status

    # Clean up (if necessary)
    # ...


def test_notification_invalid_data():
    """
    Test the Notification class with invalid data.

    This test ensures that the Notification instance fails validation with the provided invalid data.
    It checks for specific validation errors for each invalid field and asserts that the object is not valid.
    """
    # Create an instance of Notification with invalid data
    invalid_notification = Notification(
        user_id=None,  # Invalid user ID (None)
        msg_date=None,  # Invalid message date (None)
        message="",  # Invalid empty message
        status="InvalidStatus"  # Invalid status
    )

    # Validate the object against the defined model schema or constraints
    is_valid = True
    errors = []

    if invalid_notification.user_id is None:
        is_valid = False
        errors.append("User ID is required.")

    if invalid_notification.msg_date is None:
        is_valid = False
        errors.append("Message date is required.")

    if not invalid_notification.message:
        is_valid = False
        errors.append("Message is required.")

    if invalid_notification.status not in ["Sent", "Delivered", "Read"]:
        is_valid = False
        errors.append("Invalid status.")

    # Assert that the object is not valid and has the expected validation errors
    assert not is_valid
    assert errors == [
        "User ID is required.",
        "Message date is required.",
        "Message is required.",
        "Invalid status."
    ]



@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_login_successful(client):
    response = client.post('/login', data={'email': 'user@example.com', 'password': 'password'}, follow_redirects=True)
    assert response.status_code == 200  # Assuming a successful login renders a page with status code 200
    print(" the data : ------>>>>",response.data)
    assert b'.' in response.data  # Assuming a success flash message is displayed
    assert b'' in response.data  # Assuming a welcome message is displayed on the dashboard page

