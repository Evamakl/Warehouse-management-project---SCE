"""
This module defines the database models used in the website.

It includes the following models:
- User: Represents a user in the system.
- Item: Represents an item in the warehouse.
- LoanRequest: Represents a loan request made by a user for an item.
- recommend_file_detail: Represents the details of a recommended file.
- Repair_Table: Represents a row in the repair table.
- Notification: Represents a notification message sent to a user.

This module also imports the required dependencies and 
sets up the necessary relationships between the models.

Note: This module relies on the Flask-SQLAlchemy library 
for interacting with the database.
"""
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy import or_, and_
from website import db, login_manager
from website import bcrypt
# from datetime import datetime
@login_manager.user_loader
def load_user(id):
    """Load a user from the database by their ID.

    Args:
        id (int): The ID of the user to load.

    Returns:
        User or None: The user object corresponding to the given ID,
        or None if not found.
    """
    return User.query.get(int(id))

class User(db.Model, UserMixin):
    """A model representing a user in the system.

    Attributes:
        id (int): The unique identifier of the user.
        first_name (str): The user's first name.
        last_name (str): The user's last name.
        email_address (str): The user's email address (must be unique).
        password_hash (str): The hashed password of the user.
        is_warehouse_manager (bool): Whether the user is a warehouse manager or not.
        is_teaching_staff_member (bool): Whether the user is a teaching staff member or not.
        phone_number (str): The user's phone number (optional).
        loan_requests:
            A relationship with the LoanRequest model representing all the user's requests.
        recommend_files: 
            A relationship with the recommend_file_detail model 
            representing all the user's recommended files.

    Methods:
        password (property): The user's password (read-only).
        password (setter method):
            Set the user's password by generating a hash from the plain text password.
        check_password_correction:
            Check if the given password matches the user's hashed password.
        __repr__: Return a string representation of the user.
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    email_address = db.Column(db.String(length=50),nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    is_warehouse_manager = db.Column(
        db.Boolean,
        default=False
    )
    is_teaching_staff_member = db.Column(db.Boolean, default=False)
    phone_number = db.Column(db.String(length=20), nullable=True)
    loan_requests = db.relationship('LoanRequest', back_populates='loan_request_user')
    recommend_files = db.relationship(
        'recommend_file_detail',
        foreign_keys='recommend_file_detail.user_id'
    )
    messages = db.relationship('Notification', back_populates='loan_request_user')



    @property
    def password(self):
        """Get the user's password (read-only)."""
        return self.password
    #convert plain text password to encrypted password
    @password.setter
    def password(self, plain_text_password):
        """Set the user's password by generating a hash from the plain text password.

        Args:
            plain_text_password (str): The plain text password to set.

        Returns:
            None
        """
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        """Check if the given password matches the user's hashed password.

        Args:
            attempted_password (str): The password to check.

        Returns:
            bool: 
                True if the password is correct, 
                False otherwise.
        """
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

    def __repr__(self):
        """Return a string representation of the user.

        Returns:
            str: String representation of the user.
        """
        return f'user(id={self.id}, first_name="{self.first_name}", last_name="{self.last_name}", email_address="{self.email_address}", password_hash="{self.password_hash}", is_warehouse_manager={self.is_warehouse_manager}, is_teaching_staff_member={self.is_teaching_staff_member})'
class Item(db.Model):
    """
    Represents an item in the warehouse.

    Attributes:
    - id (int): the unique identifier for the item in the database
    - item_ID (str): the unique identifier for the item, used for tracking purposes
    - item_name (str): the name of the item
    - item_type (str): the type/category of the item
    - item_desc (str): a brief description of the item
    - status (str): the current status of the item, either "Available" or "Borrowed"

    Note: This class is a subclass of the `db.Model` class in the Flask-SQLAlchemy
    library, which provides an interface for interacting with the database.
    """
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key = True)
    item_ID = db.Column(db.String(length=30), nullable=False, unique=True)
    item_name = db.Column(db.String(length=50), nullable=False)
    item_type = db.Column(db.String(length=50), nullable=False)
    item_desc = db.Column(db.String(length=200))
    status = db.Column(
        db.String(length=20),
        nullable=False,
        default="Available"
    )  # Available / Under Repair / Loan

class LoanRequest(db.Model):
    """
    Represents a loan request made by a user for an item.

    Attributes:
    - id (int): The unique identifier for the loan request.
    - loan_request_item (relationship):
        A relationship with the Item model representing the item being requested.
    - loan_request_user (relationship): 
        A relationship with the User model representing the user making the request.
    - opened_on (datetime): The date and time the request was opened.
    - borrowing_date (datetime): The date and time the user wishes to borrow the item.
    - return_date (datetime): The date and time the user wishes to return the item.
    - reason_for_borrowing (str): The reason the user is requesting to borrow the item.
    - status (str): The status of the request. Possible values are:
          "Approved", "Pending", "Canceled", or "Closed".
    - user_id (int): The foreign key representing the user making the request.
    - item_id (int): The foreign key representing the item being requested.

    Methods:
    - check_for_conflicting_request(): 
        Checks if there is any conflicting request for the same item during the selected dates.
    - cancel_request(): Cancels a request that is still pending.
    - edit_request(): Edits the borrowing date, return date, and reason for borrowing of a request.
    """
    __tablename__ = 'requests'
    id = db.Column(db.Integer, primary_key=True)
    loan_request_item = db.relationship('Item', backref='requests')
    loan_request_user = db.relationship("User", back_populates="loan_requests")

    opened_on = db.Column(db.DateTime(timezone=True), nullable=False, default=func.now())
    borrowing_date = db.Column(db.DateTime(timezone=True), nullable=False)
    return_date = db.Column(db.DateTime(timezone=True), nullable=False)
    reason_for_borrowing = db.Column(db.String(length=300), nullable=False)
    status = db.Column(
        db.String(length=20),
        nullable=False,
        default="נשלח לאישור"
    )# Approved / Pending / Canceled / Closed
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'))
    def check_for_conflicting_request(self):
        """Checks if there is any conflicting loan request 
        for the same item during the selected dates.

    Returns:
        LoanRequest or None: The conflicting loan request if found, 
        or None if no conflicting request exists.
    """
        conflicting_request = LoanRequest.query.filter_by(
        item_id=self.loan_request_item.id,
        status='Approved'
    ).filter(
        or_(
            and_(LoanRequest.borrowing_date <= self.borrowing_date,
                 LoanRequest.return_date > self.borrowing_date),
            and_(LoanRequest.borrowing_date >= self.borrowing_date,
                 LoanRequest.borrowing_date < self.return_date)
        ))
        if conflicting_request.first():
            return conflicting_request
        return None
    def cancel_request(self):
        """Cancels the loan request if it is in the 'נשלח לאישור' status.

    Returns:
        tuple: A tuple containing a boolean indicating the success status 
        and a message explaining the result.
    """
        if self.status == "נשלח לאישור":
            self.status = "Canceled"
            db.session.commit()
            return True, "Request has been canceled successfully."
        else:
            return False, "רק בקשות שנשלחו לאישור יכולות להיות מבוטלות"
    def edit_request(self, borrowing_date, return_date, reason_for_borrowing):
        """Edits the details of the loan request.

    Args:
        borrowing_date (datetime): The new borrowing date for the request.
        return_date (datetime): The new return date for the request.
        reason_for_borrowing (str): The new reason for borrowing.

    Returns:
        tuple: A tuple containing a boolean indicating the success status 
        and a message explaining the result.
    """
        # check for any conflicting requests
        conflicting_request = LoanRequest.query.filter_by(
            item_id=self.loan_request_item.id,
            status='Approved').filter(or_(
            and_(LoanRequest.borrowing_date <= borrowing_date, 
                LoanRequest.return_date > borrowing_date),
            and_(LoanRequest.borrowing_date >= borrowing_date,
                LoanRequest.borrowing_date < return_date))).first()

        if conflicting_request and conflicting_request.id != self.id:
            return False, "There is a conflicting request for the same item during the selected dates."
        # update request details
        self.borrowing_date = borrowing_date
        self.return_date = return_date
        self.reason_for_borrowing = reason_for_borrowing
        db.session.commit()
        return True, "Request details have been updated successfully."
       
class recommend_file_detail(db.Model):
    """
    A class to represent the details of a recommended file.

    Attributes
    ----------
    id : int
        The unique identifier of the recommended file.
    user_id : int
        The ID of the user who recommended the file.
    user_first_name : str
        The first name of the user who recommended the file.
    user_last_name : str
        The last name of the user who recommended the file.
    user_phone_number : str
        The phone number of the user who recommended the file.
    item_name : str
        The name of the recommended item.
    reason : str
        The reason why the item is being recommended.
    amount : int
        The amount of the item that is being recommended.
    status : str
        The status of the recommended item (default is 'Pending').
    date_submitted : str
        The date when the recommendation was submitted.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user_first_name = db.Column(db.String, db.ForeignKey('users.first_name'))
    user_last_name = db.Column(db.String, db.ForeignKey('users.last_name'))
    user_phone_number = db.Column(db.String, db.ForeignKey('users.phone_number'))
    item_name = db.Column(db.String(50), nullable=False)
    reason = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=True, default='Pending')
    date_submitted = db.Column(db.String(50), nullable=False)


class Repair_Table(db.Model):
    """
    A class represanting row in repair table.

    Attributes
    ----------
    id : int
        The unique identifier of the item need to be repaired
    item_id : string
        Foreign key related to the item need to be repaired.
    item_name : string
        Item name.
    repair_date: DateTime
        The date the item sent to repair.
    status: string
        Current repair status
    """
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.String, db.ForeignKey('items.item_ID'))
    item_name = db.Column(db.String, db.ForeignKey('items.item_name'))
    repair_date = db.Column(db.DateTime(timezone=True), nullable=False)
    status = db.Column(db.String(length=20), nullable=False, default="בתיקון")



class Notification(db.Model):
    """Represents a notification message sent to a user.

    Attributes:
        loan_request_user (Relationship): 
            Relationship to the User model, 
            indicating the user associated with the notification.
        id (int): Primary key of the notification.
        user_id (int): Foreign key referencing the user associated with the notification.
        msg_date (DateTime): Date and time when the notification was sent.
        message (str): Content of the notification message.
        flag (int): Flag indicating the priority or importance of the notification.
        status (str): Status of the notification, indicating whether it has been sent.

    """
    loan_request_user = db.relationship("User", back_populates="messages")
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    msg_date = db.Column(db.DateTime(timezone=True), nullable=False)
    message = db.Column(db.String(200), nullable=False)
    flag = db.Column(db.Integer, nullable=False, default=4)
    status = db.Column(db.String(10), default="Sent")
