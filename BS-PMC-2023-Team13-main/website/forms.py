"""
This module contains Flask forms for user input validation.
"""
from datetime import datetime, timedelta
from flask_wtf import FlaskForm
# from flask_wtf.form import _Auto
from flask_wtf.file import FileField
from wtforms import StringField, PasswordField,SelectField, SubmitField
from wtforms.validators import Length, Email, DataRequired,Optional, InputRequired, ValidationError
from wtforms import IntegerField
from wtforms.validators import EqualTo
from wtforms import DateTimeField
from wtforms.fields import DateTimeLocalField
import pytz
class LoginForm(FlaskForm):
    """
    Represents a login form.

    Attributes:
        email (StringField): The email field for the user to enter their email address.
        password (PasswordField): The password field for the user to enter their password.
        submit (SubmitField): The submit button for the form.
    """
    email = StringField(
        'כתובת מייל',
        validators=[DataRequired(message="שדה חובה"),
                    Email(message="כתובת המייל אינה חוקית")
                   ])
    password = PasswordField('סיסמה', validators=[DataRequired(message="שדה חובה")])
    submit = SubmitField('Log In')

class add_users_manually_form(FlaskForm):
    """
    Represents a form for manually adding users.

    Attributes:
        first_name (StringField): The field for entering the user's first name.
        last_name (StringField): The field for entering the user's last name.
        phone_number (StringField): The field for entering the user's phone number (optional).
        email (StringField): The field for entering the user's email address.
        select_field (SelectField): The field for selecting the user's type (student or teacher).
        submit (SubmitField): The submit button for the form.
    """
    first_name = StringField(
        'שם פרטי',
        [InputRequired("שדה חובה"),
         Length(min=2, message="אנא הכנס שם פרטי מעל 2 תווים"),
         DataRequired(message="שדה חובה")
        ])
    last_name = StringField(
        'שם משפחה',
        [InputRequired("שדה חובה"),
         Length(min=2, message="אנא הכנס שם משפחה מעל 2 תווים"),
         DataRequired(message="שדה חובה")]
    )
    phone_number = StringField(
        'מספר טלפון',
        validators=[Optional(),
                    Length(max=20),
                    DataRequired(message="שדה חובה")]
    )
    email = StringField(
        'כתובת מייל',
        validators=[DataRequired(message="שדה חובה"),
                    Email(message="כתובת המייל אינה חוקית")]
    )
    select_field = SelectField(
        'סוג המשתמש',
        choices=[('Student', 'סטודנט'),
                 ('Teacher', 'מרצה')],
        validators=[DataRequired(message="שדה חובה")]
    )
    submit = SubmitField('הוסף')

class upload_csv_form(FlaskForm):
    """
    Represents a form for uploading a CSV file containing user details.

    Attributes:
        csv_file (FileField): The field for uploading the CSV file.
        submit (SubmitField): The submit button for the form.
    """
    csv_file = FileField(
        'הכנס את קובץ ה-CSV (סיומת .csv) המכיל את פרטי המשתמשים שברצונך להוסיף'
    )
    submit = SubmitField('הוסף')


#-------------EVA---------------------------------------------------------------------------------
class UpdateUserForm(FlaskForm):
    """
    Represents a form for updating user details.

    Attributes:
        first_name (StringField): The field for entering the first name of the user.
        last_name (StringField): The field for entering the last name of the user.
        phone_number (StringField): The field for entering the phone number of the user.
        current_password (PasswordField): The field for entering the current password of the user.
        new_password (PasswordField): The field for entering the new password of the user.
        confirm_password (PasswordField): The field for confirming the new password of the user.
        submit (SubmitField): The submit button for the form.
    """
    first_name = StringField('שם פרטי', validators=[DataRequired(), Length(min=2, max=20)])
    last_name = StringField('שם משפחה', validators=[DataRequired(), Length(min=2, max=20)])
    phone_number = StringField("מס' טלפון", validators=[Optional(), Length(max=20)])
    current_password = PasswordField('סיסמא נוכחית')
    new_password = PasswordField('סיסמא חדשה', validators=[Length(min=5)])
    confirm_password = PasswordField('אימות סיסמא', validators=[EqualTo('new_password')])
    submit = SubmitField('עדכן פרטים')



class ItemForm(FlaskForm):
    """
    Represents a form for adding an item.

    Attributes:
        item_id (StringField): The field for entering the item ID.
        item_name (StringField): The field for entering the item name.
        item_type (StringField): The field for entering the item type.
        item_desc (StringField): The field for entering the item description.
        submit (SubmitField): The submit button for the form.
    """
    item_id = StringField('מק"ט', validators=[DataRequired(message="שדה חובה"), Length(max=30)])
    item_name = StringField(
        'שם פריט',
        validators=[DataRequired(message="שדה חובה"), Length(max=50)]
    )
    item_type = StringField(
        'סוג פריט',
        validators=[DataRequired(message="שדה חובה"), Length(max=50)]
    )
    item_desc = StringField('תיאור פריט', validators=[Length(max=200)])
    submit = SubmitField('הוסף פריט')

class UpdateItemForm(FlaskForm):
    """Form for updating item details.

    This form provides fields to update the item ID, name, type, and description.
    It is designed to be used in conjunction with Flask-WTF and Flask.

    Attributes:
        item_id (StringField): Field for entering the item ID.
            Required field with a maximum length of 30 characters.
        item_name (StringField): Field for entering the item name.
            Required field with a maximum length of 50 characters.
        item_type (StringField): Field for entering the item type.
            Required field with a maximum length of 50 characters.
        item_desc (StringField): Field for entering the item description.
            Optional field with a maximum length of 200 characters.
        submit (SubmitField): Submit button for the form.

    """
    item_id = StringField('מק"ט', validators=[DataRequired(message="שדה חובה"), Length(max=30)])
    item_name = StringField(
        'שם פריט', 
        validators=[DataRequired(message="שדה חובה"), Length(max=50)]
    )
    item_type = StringField(
        'סוג פריט', 
        validators=[DataRequired(message="שדה חובה"), Length(max=50)]
    )
    item_desc = StringField('תיאור פריט', validators=[Length(max=200)])
    submit = SubmitField('עדכן פרטים')



class LoanRequestForm(FlaskForm):
    """Form for submitting a loan request.

    This form provides fields to input the borrowing date, return date, and reason for borrowing.
    It also includes validation methods to ensure the entered dates 
    are valid and within the allowed range.

    Attributes:
        borrowing_date (DateTimeLocalField): Field for entering the borrowing date and time.
        The format is '%Y-%m-%dT%H:%M'.
            Required field with a minimum value of the current date and time.
        return_date (DateTimeLocalField): Field for entering the return date and time.
        The format is '%Y-%m-%dT%H:%M'. 
            Required field with a minimum value of the current date and time.
        reason_for_borrowing (StringField): Field for entering the reason for borrowing.
        Required field.
        submit (SubmitField): Submit button for the form.

    Methods:
        validate_borrowing_date(form, field):
            Custom validator for the borrowing date field.
        Checks that the borrowing date is valid and meets certain criteria.
        validate_return_date(form, field):
            Custom validator for the return date field.
        Checks that the return date is valid and meets certain criteria.

    """
    borrowing_date = DateTimeLocalField(
        'תאריך ההשאלה',
        format='%Y-%m-%dT%H:%M',
        validators=[DataRequired()],
        render_kw={'min': datetime.now().strftime('%Y-%m-%dT%H:%M')}
    )
    return_date = DateTimeLocalField(
        'תאריך ההחזרה',
        format='%Y-%m-%dT%H:%M',
        validators=[DataRequired()],
        render_kw={'min': datetime.now().strftime('%Y-%m-%dT%H:%M')}
    )
    reason_for_borrowing = StringField('הסיבה להשאלה', validators=[DataRequired()])
    submit = SubmitField('שלח בקשה')


    def validate_borrowing_date(form, field):
        """Validate the borrowing date.

        This method checks that the borrowing date meets the required criteria.

        Args:
            form: The LoanRequestForm instance.
            field: The borrowing date field.

        Raises:
            ValidationError: If the borrowing date is not valid or does not meet the criteria.
        """
        israel_tz = pytz.timezone('Israel')
        current_time = datetime.now(israel_tz)
        borrowing_date = israel_tz.localize(field.data)
        if field.data.weekday() in [4, 5]:  # Friday or Saturday
            raise ValidationError('לא ניתן להשאיל פריטים בימי שישי ושבת')

        if not (field.data.time() >= datetime.strptime('08:00', '%H:%M').time()
                and field.data.time() <= datetime.strptime('16:00', '%H:%M').time()):
            raise ValidationError('תאריך ההשאלה חייב להיות בין בהשעות 08:00 ועד 16:00')

        if borrowing_date  < current_time:
            raise ValidationError("תאריך ההשאלה לא יכול להיות בעבר")
        min_borrowing_date = current_time + timedelta(hours=1)

        # Check if the borrowing date is at least 1 hour from now
        if borrowing_date < min_borrowing_date:
            raise ValidationError('לא ניתן להשאיל פריטים במרווח זמן הקטן משעה מעכשיו')
    def validate_return_date(form, field):
        """Validate the return date.

        This method checks that the return date meets the required criteria.

        Args:
            form: The LoanRequestForm instance.
            field: The return date field.

        Raises:
            ValidationError: If the return date is not valid or does not meet the criteria.
        """
        if field.data.weekday() in [4, 5]:  # Day: Friday or Saturday
            raise ValidationError('לא ניתן להחזיר פריטים בימי שישי ושבת')
        if not (field.data.time() >= datetime.strptime('08:00', '%H:%M').time()
                and field.data.time() <= datetime.strptime('16:00', '%H:%M').time()):
            raise ValidationError('תאריך ההחזרה חייב להיות בין בהשעות 08:00 ועד 16:00')
        if field.data < form.borrowing_date.data:
            raise ValidationError('תאריך ההחזרה לא יכול להיות לפני תאריך ההשאלה')
        if field.data > form.borrowing_date.data + timedelta(days=7):
            raise ValidationError('לא ניתן להשאיל פריט ליותר משבוע')


class recommendationForm(FlaskForm):
    """Form for submitting a recommendation.

    This form provides fields to input the item name, 
    reason for recommendation, and recommended amount.
    It also includes validation to ensure all fields are filled in.

    Attributes:
        item_name (StringField): Field for entering the item name. Required field.
        reason (StringField): 
            Field for entering the reason for the recommendation. Required field.
        amount (IntegerField): Field for entering the recommended amount. Required field.
        submit (SubmitField): Submit button for the form.

    """
    item_name = StringField('שם הפריט', validators=[DataRequired()])
    reason = StringField('סיבת המלצה', validators=[DataRequired()])
    amount = IntegerField('כמות', validators=[DataRequired()])
    submit = SubmitField('שלח')


class EditRequestForm(FlaskForm):
    """Form for editing a request.

    This form allows users to edit the borrowing date, 
    return date, and reason for borrowing of a request.
    It includes validation to ensure that the dates are within the allowed range and 
    that the return date is after the borrowing date.

    Attributes:
        borrowing_date (DateTimeField): Field for entering the borrowing date. Required field.
        return_date (DateTimeField): Field for entering the return date. Required field.
        reason_for_borrowing (StringField): 
            Field for entering the reason for borrowing. Required field.
        submit (SubmitField): Submit button for the form.

    Methods:
        validate_borrowing_date: 
            Custom validation method to check the validity of the borrowing date.
        validate_return_date: Custom validation method to check the validity of the return date.

    """
    borrowing_date = DateTimeField(
        'תאריך ההשאלה',
        format='%Y-%m-%dT%H:%M',
        validators=[DataRequired()]
    )
    return_date = DateTimeField(
        'תאריך ההחזרה',
        format='%Y-%m-%dT%H:%M',
        validators=[DataRequired()]
    )
    reason_for_borrowing = StringField('הסיבה להשאלה', validators=[DataRequired()])
    submit = SubmitField('עדכן בקשה')
    def validate_borrowing_date(form, field):
        """Validate the borrowing date.

        Checks if the borrowing date is within the allowed range 
        and meets other criteria such as not being in the past
        and being at least 1 hour from the current time.

        Args:
            form (EditRequestForm): The form object.
            field (DateTimeField): The borrowing date field.

        Raises:
            ValidationError: If the borrowing date is not valid according to the defined criteria.
        """
        israel_tz = pytz.timezone('Israel')
        current_time = datetime.now(israel_tz)
        borrowing_date = israel_tz.localize(field.data)
        if field.data.weekday() in [4, 5]:  # Friday or Saturday
            raise ValidationError('לא ניתן להשאיל פריטים בימי שישי ושבת')

        if not (field.data.time() >= datetime.strptime('08:00', '%H:%M').time()
                and field.data.time() <= datetime.strptime('16:00', '%H:%M').time()):
            raise ValidationError('תאריך ההשאלה חייב להיות בין בהשעות 08:00 ועד 16:00')

        if borrowing_date  < current_time:
            raise ValidationError("תאריך ההשאלה לא יכול להיות בעבר")
        min_borrowing_date = current_time + timedelta(hours=1)

        # Check if the borrowing date is at least 1 hour from now
        if borrowing_date < min_borrowing_date:
            raise ValueError("לא ניתן להשאיל פריטים במרווח זמן הקטן משעה מעכשיו")
    def validate_return_date(form, field):
        """Validate the return date.

        Checks if the return date is within the allowed range 
        and meets other criteria such as being after the borrowing date.

        Args:
            form (EditRequestForm): The form object.
            field (DateTimeField): The return date field.

        Raises:
            ValidationError: If the return date is not valid according to the defined criteria.
        """
        if field.data.weekday() in [4, 5]:  # Day: Friday or Saturday
            raise ValidationError('לא ניתן להחזיר פריטים בימי שישי ושבת')
        if not (field.data.time() >= datetime.strptime('08:00', '%H:%M').time()
                and field.data.time() <= datetime.strptime('16:00', '%H:%M').time()):
            raise ValidationError('תאריך ההחזרה חייב להיות בין בהשעות 08:00 ועד 16:00')
        if field.data < form.borrowing_date.data:
            raise ValidationError('תאריך ההחזרה לא יכול להיות לפני תאריך ההשאלה')
        if field.data > form.borrowing_date.data + timedelta(days=7):
            raise ValidationError('לא ניתן להשאיל פריט ליותר משבוע')
