from sqlite3 import IntegrityError
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import and_, exc, func, or_
from flask_login import login_user, login_required, current_user, logout_user
from flask import abort, make_response, render_template, redirect, url_for, flash, request, Blueprint
from . import app, db
from .models import recommend_file_detail, Repair_Table, Notification, User, Item, LoanRequest
from .forms import add_users_manually_form, recommendationForm, upload_csv_form, EditRequestForm, LoanRequestForm, LoginForm, UpdateUserForm, ItemForm
bp = Blueprint('main', __name__)

@app.route('/dashboard')
@login_required
def home_page():
    """
    Displays the user dashboard page.

    This function returns a Flask response object
    that renders the 'dashboard.html' template with the
    current user's information.
    The response headers are set to disable caching to ensure that the
    page is always up-to-date.

    Returns:
        A Flask response object that renders the 
        'dashboard.html' template with the current user's information.
    
    backup code:
    if current_user.is_warehouse_manager:
        current_datetime = datetime.now()

        passed_requests = LoanRequest.query.filter(
            LoanRequest.return_date <= current_datetime,
            LoanRequest.status == 'Activated'
        ).all()
        two_days_from_now = current_datetime + timedelta(days=2)
        upcoming_requests = LoanRequest.query.filter(
            LoanRequest.return_date <= two_days_from_now,
            LoanRequest.return_date > current_datetime,
            LoanRequest.status == 'Activated'
        ).all()
        context = {'passed_requests': passed_requests, 'upcoming_requests': upcoming_requests}
        return render_template('manager_dashboard.html', context=context, date=datetime.now())
    """
    template = render_template('dashboard.html', user=current_user, date = datetime.now())
    response = make_response(template)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/')
def index():
    """
    Renders the application's main page.

    This function checks if the user is authenticated,
    and if not, redirects to the login page.
    If the user is authenticated,
    it redirects to the home page.

    Returns:
        A Flask redirect response to either the login page or the home page.
    """
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return redirect(url_for('home_page'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """ Renders the login page and handles user login requests.

    This function displays a login form to the user
    and handles user login requests. If the user
    submits a valid login form,
    the function checks if the email and password match a user in the
    database. If there is a match,
    the user is logged in and redirected to the home page. If not,
    an error message is displayed.

    Returns:
    If the HTTP method is GET, a Flask response
    object that renders the 'login.html' template.
    If the HTTP method is POST and the login form is valid:
    Flask redirect response to the home page.
    If the HTTP method is POST and the login form is invalid,
    a Flask response object that renders
    the 'login.html' template with error messages.
    """
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email_address=form.email.data).first()
        if user and user.check_password_correction(form.password.data):
            login_user(user)
            flash(f'התחברת בהצלחה כ- {user.first_name} {user.last_name}.',category='success')
            today = datetime.now()
            if not user.is_warehouse_manager:
                requests = LoanRequest.query.filter_by(user_id=user.id).all()
                for req in requests:
                    if req.status != 'Activated':
                        continue

                    if (req.return_date - today) < timedelta(days=1) and (req.return_date - today) > timedelta(days=0,hours=23,minutes=59):
                        msg = "לבקשה " + str(req.id) + " נשאר פחות מיום אחד להחזרת הציוד. "
                        today_ = datetime.today().date()
                        notific = Notification(user_id=user.id, message=msg, msg_date=today_, flag=1)
                        db.session.add(notific)
                        db.session.commit()
                    elif (req.return_date - today) < timedelta(days=3) and (req.return_date - today) > timedelta(days=0,hours=23,minutes=59):
                        msg = "לבקשה " + str(req.id) + " נשארו יומיים להחזרת הציוד. "
                        today_ = datetime.today().date()
                        notific = Notification(user_id=user.id, message=msg, msg_date=today_,flag=2)
                        db.session.add(notific)
                        db.session.commit()
                    elif (req.return_date - today) < timedelta(days=0,hours=0,minutes=0):
                        msg = "בקשה מס': " + str(req.id) + "לפריט: " + str(req.item_id) + " פגת תוקף, אנא החזר את הפריט באופן מיידי. "
                        today_ = datetime.today().date()
                        notific = Notification(user_id=user.id, message=msg, msg_date=today_,flag=0)
                        db.session.add(notific)
                        db.session.commit()
            else:
                requests = LoanRequest.query.all()
                for req in requests:
                    if req.status != 'Activated':
                        continue

                    if (req.return_date - today) < timedelta(days=0,hours=0,minutes=0):
                        temp_user = User.query.get(req.user_id)
                        msg = "בקשה מס' " + str(req.id) + " של המשתמש " + temp_user.email_address + " פגת תוקף מבלי שהפריט הוחזר. מספר טל- " + temp_user.phone_number
                        today_ = datetime.today().date()
                        notific = Notification(user_id=user.id, message=msg, msg_date=today_,flag=0)
                        db.session.add(notific)
                        db.session.commit()
            return redirect(url_for('home_page'))
        flash('שם המשתמש והסיסמה אינם תואמים.', category='danger')
    return render_template('login.html', form=form)

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    """
    Logs out the current user.

    This function logs out the current user,
    flashes a message to notify the user that they have been logged
    out, and redirects them to the login page.
    It also adds headers to the response to ensure that the page
    is not cached by the browser.

    Returns:
        A Flask redirect response to the login page.
    """
    logout_user()
    flash("התנתקת מהמערכת בהצלחה.", category='success')
    response = make_response(redirect(url_for('login')))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response



@app.route('/add_user', methods=['GET'])
@login_required
def add_user():
    """
    Renders the add user form.

    This function renders the add user form, 
    but only if the current user is a warehouse manager. 
    If the user is not a warehouse manager, 
    the function flashes an error message and
    redirects them to the home page.

    Returns:
        If the user is a warehouse manager, returns a
        Flask template rendering the add user form. Otherwise,
        redirects the user to the home page.
    """
    if not current_user.is_warehouse_manager:
        flash('אינך מורשה לבצע פעולה זאת', category='danger')
        return redirect(url_for('home_page'))
    return render_template('add_user.html')

@app.route('/add_manually', methods=['GET', 'POST'])
@login_required
def add_manually():
    """
    Renders a form to add users manually.

    This function renders a form that allows the
    warehouse manager to add users manually. 
    If the user is not a warehouse manager, 
    the function flashes an error message and redirects them to the home page.
    The form allows the warehouse manager to enter
    the user's first name, last name, email address,
    phone number, and role. 
    The function adds the user to the database
    if they do not already exist.

    Returns:
        If the user is a warehouse manager,
        renders a Flask template rendering the form to
        add users manually.
        If the user successfully adds a user,
        redirects the user to the add user page. Otherwise, renders the same
        form with error messages indicating what went wrong.
    """
    if not current_user.is_warehouse_manager:
        flash('אינך מורשה לבצע פעולה זאת', category='danger')
        return redirect(url_for('home_page'))
    form = add_users_manually_form()
    if form.validate_on_submit():
        user = User.query.filter_by(email_address=form.email.data).first()
        if user is not None:
            flash(f'A user with email {form.email.data} already exists', 'danger')
        else:
            is_student = form.select_field.data == 'Student'
            is_teacher = form.select_field.data == 'Teacher'
            user = User()
            user.first_name=form.first_name.data
            user.last_name=form.last_name.data
            user.email_address=form.email.data
            user.password = '12345'
            user.is_warehouse_manager = not is_student and not is_teacher
            user.is_teaching_staff_member=not is_student
            user.phone_number = form.phone_number.data
            try:
                db.session.add(user)
                db.session.commit()
                flash(f'A user with email {form.email.data} added successfully!', 'success')
            except IntegrityError as error:
                db.session.rollback()
                flash(str(error), 'danger')
            return redirect(url_for('add_user'))
    return render_template('manually.html', form=form)

@app.route('/upload_page', methods=['GET', 'POST'])
@login_required
def upload_page():
    """
    Renders the upload CSV page and allows a warehouse manager to add users to the system
    by uploading a CSV file.
    Validates the CSV file format and required columns, 
    and adds new users to the system by iterating over the rows in the uploaded CSV file.
    If a user already exists in the system, 
    returns a message indicating that a user with the same email already exists.
    If the CSV file is not in the correct format or some of the required columns are missing, 
    an error message is returned.

    Returns:
        A rendered HTML template with an upload CSV form.
    """
    if not current_user.is_warehouse_manager:
        flash('אינך מורשה לבצע פעולה זאת', category='danger')
        return redirect(url_for('home_page'))
    form = upload_csv_form()
    if form.validate_on_submit():
        file = form.csv_file.data
        if not file:
            flash('לא נבחר קובץ להעלאה', category='danger')
            return render_template('upload_csv.html', form=form)
        # Check if file is a CSV file
        if file.filename.split('.')[-1].lower() != 'csv':
            flash('הקובץ שהועלה אינו קובץ CSV', category='danger')
        else:
            data_file = pd.read_csv(file)
            if data_file.isnull().values.any():
                flash('הקובץ לא מלא, יש תאים רקים, נא מלא אותם והכנס את הקובץ שנית',category='danger')
                return redirect(url_for('add_user'))
            required_cols = {'first name', 'last name', 'email', 'type'}
            if set(required_cols).issubset(set(data_file.columns)):
                # Iterate over the rows in the DataFrame
                for i, row in data_file.iterrows():
                    # Check if user already exists in the database
                    user = User.query.filter_by(email_address=row['email']).first()
                    if user is not None:
                        flash(f'A user with email {row["email"]} already exists', 'danger')
                    else:
                        is_student = row['type'] =='student'
                        is_teacher = row['type']=='teacher'
                        user = User()
                        user.first_name=row['first name']
                        user.last_name=row['last name']
                        user.email_address=row['email']
                        user.password = '12345'
                        user.is_warehouse_manager = not row['type'] =='student' and not row['type']=='teacher'
                        user.is_teaching_staff_member=not row['type'] =='student'
                        user.phone_number = row['phone_number']
                        try:
                            db.session.add(user)
                            db.session.commit()
                            flash(f'A user with email {row["email"]} added successfully!', 'success')
                        except IntegrityError as error:
                            db.session.rollback()
                            flash(str(error), 'danger')
                return redirect(url_for('add_user'))
            print('The CSV file is missing one or more required columns')
    return render_template('upload_csv.html', form=form)

@app.route('/add_item', methods=['POST','GET'])
@login_required
def add_item():
    """
    Render the 'add_item' template and handle
    adding new items to the warehouse inventory.
    Only warehouse managers are authorized to access this route.

    Methods:
    POST: If the form data is valid, add a new item to the inventory.
    GET: Render the 'add_item' template with the
    ItemForm instance and all the items in the database.
    Returns:
    Render the 'add_item' template with the
    ItemForm instance and all the items in the database.
    """
    if not current_user.is_warehouse_manager:
        return redirect(url_for('index'))
    items_ = Item.query.all()   #load all items in warehouse (database)
    form = ItemForm()
    if form.validate_on_submit():
        print("success")
        item_id = form.item_id.data
        item_name = form.item_name.data
        item_type = form.item_type.data
        item_desc = form.item_desc.data
        #itemBio = form.item_bio.data

        try:    # try add the item into database. (check if there is any item with same id)
            new_item = Item(item_ID=item_id, item_name=item_name, item_type=item_type,item_desc=item_desc)
            db.session.add(new_item)
            db.session.commit()
            flash('הפריט נוסף בהצלחה', category='success')
        except exc.SQLAlchemyError:
            flash("פריט כבק קיים במערכת.", category="info")
        return redirect(url_for('add_item'))
    return render_template("add_item.html", form= form, items= items_)


# Eva's code ---------------------------------------------------------------------------------

@app.route('/update_user', methods=['GET', 'POST'])
@login_required
def update_user():
    """
    Route that allows users to update their account information.
    If the user is not logged in, they will be redirected to the login page.
    If the form is submitted and validated, 
    the user's account information will be updated in the database.
    If the form is not validated, 
    the form will be rendered to allow the user to enter the correct information.
    """
    user = current_user
    form = UpdateUserForm()
    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.phone_number = form.phone_number.data

        if form.new_password.data:
            if not user.check_password_correction(form.current_password.data):
                flash('Incorrect current password. Please try again.', 'danger')
                return redirect(url_for('update_user'))
            user.password = form.new_password.data

        db.session.commit()
        flash('User account has been updated!', 'success')
        return redirect(url_for('home_page'))

    if request.method == 'GET':
        form.first_name.data = user.first_name
        form.last_name.data = user.last_name
        form.phone_number.data = user.phone_number

    return render_template('update_user.html', title='Update User', form=form)

@app.route('/recommend_item', methods=['POST','GET'])
@login_required
def recommend_item_page():
    """
    This route allows a teaching staff member to
    recommend an item for the warehouse. 
    If the user submits a recommendation form, the data is saved to the database 
    and a success message is displayed. 

    Returns:
    - GET: Renders the 'recommend_item.html'
    template with a recommendation form and all previously 
    submitted recommendations for the current user.
    - POST: If the form data is valid,
    saves the recommendation details to the database 
    and redirects to the 'recommend_item'
    route to display the success message.
    """
    if not current_user.is_teaching_staff_member:
        return redirect(url_for('index'))
    form = recommendationForm()
    if form.validate_on_submit():
        current_time = datetime.now().strftime('%H:%M:%S %d-%m-%y' )
        recommend_file = recommend_file_detail(user_id=current_user.id, user_first_name = current_user.first_name, user_last_name = current_user.last_name, user_phone_number = current_user.phone_number, item_name=form.item_name.data, reason=form.reason.data, amount=form.amount.data,status='To Do', date_submitted=current_time)
        db.session.add(recommend_file)
        db.session.commit()
        flash('טופס ההמלצה נשלח בהצלחה!', 'success')
        return redirect(url_for('recommend_item_page'))
    recommended_items = recommend_file_detail.query.filter_by(user_id=current_user.id).all()
    return render_template('recommend_item.html', form=form,recommended_items=recommended_items)



@app.route('/recommend_item_admin')
@login_required
def recommend_item_admin():
    """
    Renders the page to view recommended items for the warehouse manager.
    If the current user is a warehouse manager, fetches all the recommended items
    from the database and displays them on the page in a table. Otherwise, sets
    `recommended_items` to None.

    Returns:
        The rendered HTML template 'recommend_item_admin.html'
        with the `recommended_items`
        variable passed to it.
    """
    recommended_items = None
    if current_user.is_warehouse_manager:
        recommended_items = recommend_file_detail.query.all()
        print(recommended_items)
    return render_template('recommend_item_admin.html', recommended_items=recommended_items)

@app.route('/recommend_item_admin', methods=['POST'])
@login_required
def update_recommendations():
    """
    Updates the status of recommended items in the database
    based on the options selected by the warehouse manager in 
    the 'recommend_item_admin' view.
    If the current user is not a warehouse manager,
    redirects to the 'recommend_item' 
    page. 

    Returns:
        If the current user is a warehouse manager,
        redirects to the 'recommend_item_admin' page with the updated
        recommendation status options selected by the user.
        Otherwise, renders the 'recommend_item.html' page.
    """
    selected_options = {}
    if current_user.is_warehouse_manager:
        for key, value in request.form.items():
            if key.startswith('status-'):
                item_id = key.split('-')[1]
                selected_options[item_id] = value
                item = recommend_file_detail.query.get(item_id)
                item.status = value
                db.session.commit()
        return redirect(url_for('recommend_item_admin', **selected_options))
    return render_template('recommend_item.html')

@app.route('/my_orders')
@login_required
def my_orders():
    """
    Renders the "My Orders" page,
    which displays all the loan requests
    submitted by the currently logged-in user.
    Only users who are not warehouse managers are allowed to access this page.
    If a warehouse manager attempts to access this page,
    they will be redirected to the home page with an error message.

    Returns:
        A rendered HTML template,
        displaying a table of all the loan requests submitted by the current user.
        The table shows information about each request,
        such as the requested item, the quantity, the requested
        start and end dates,
        the current status of the request,
        and any notes or comments left by the user.
    """
    if current_user.is_warehouse_manager:
        flash('אינך מורשה לבצע פעולה זאת', category='danger')
        return redirect(url_for('home_page'))

    user_requests = (
        LoanRequest.query
        .filter_by(user_id=current_user.id)
        #.options(joinedload(LoanRequest.item))  # Eager load the related items
        .all()
    )
    return render_template('my_orders.html', requests=user_requests)


@app.route('/all-items', methods=['GET'])
@login_required
def all_items():
    """
    Render the page that displays all items in the inventory.

    If a search query is provided as a query parameter,
    filter the items that have names or descriptions containing the
    search query.

    Returns:
        The rendered template for the all items page with a list of items to display.
    """
    search_query = request.args.get('search_query')
    if search_query:
        items = Item.query.filter(or_(
            Item.item_name.ilike(f'%{search_query}%'),
            Item.item_desc.ilike(f'%{search_query}%')
        )).all()
    else:
        items = Item.query.all()
    return render_template('all_items.html', items=items)


@app.route('/item/<int:item_id>',methods=['GET', 'POST'])
@login_required
def item_detail(item_id):
    """
    Renders the page for a single item's details and
    provides the user with the ability to request a loan for that item.

    Args:
    item_id (int): The ID of the item whose details are being displayed.

    Returns:
    GET: Renders the item detail page with a LoanRequestForm object.
    POST: If the user submits a valid loan request form,
    a new LoanRequest object is created and added to the database.
    On success, the user is redirected to the index page with a success message.
    On failure, the user is redirected to the index page with an error message.
    """
    item = Item.query.get(item_id)
    if item.status in ['Under Repair']:
        flash('לא ניתן להשאיל פריט זה')
    if item:
        form = LoanRequestForm()
        context = {'form': form, 'item':  item }
        if form.validate_on_submit():
            conflicting_request_AP = LoanRequest.query.filter_by(item_id=item.id, status = 'Approved').filter(or_(
            and_(LoanRequest.borrowing_date <= form.borrowing_date.data, LoanRequest.return_date > form.borrowing_date.data),
            and_(LoanRequest.borrowing_date >= form.borrowing_date.data, LoanRequest.borrowing_date < form.return_date.data)
            ))
            conflicting_request_AC = LoanRequest.query.filter_by(item_id=item.id, status = 'Activated').filter(or_(
            and_(LoanRequest.borrowing_date <= form.borrowing_date.data, LoanRequest.return_date > form.borrowing_date.data),
            and_(LoanRequest.borrowing_date >= form.borrowing_date.data, LoanRequest.borrowing_date < form.return_date.data)
            ))
            if conflicting_request_AP.first() or conflicting_request_AC.first():
                flash('הפריט המבוקש לא זמין בתאריך שנבחר', category='danger')
                return render_template('item_detail.html', context=context)
            user_request = LoanRequest()
            user_request.item_id = item.id
            user_request.user_id = current_user.id
            user_request.borrowing_date = form.borrowing_date.data
            user_request.return_date = form.return_date.data
            user_request.reason_for_borrowing = form.reason_for_borrowing.data
            user_request.opened_on = datetime.now()
            try:
                db.session.add(user_request)
                db.session.commit()
                flash('בקשתך נשלחה לאישור צוות המחסן', category='success')
                return redirect(url_for('index'))
            except exc.SQLAlchemyError:
                flash('שגיאה בעת יצירת הבקשה, אנא נסה בשנית', category="info")
                return redirect(url_for('index'))
        return render_template('item_detail.html', context=context)
    flash('תקלה בעת בחירת הפריט', category='info')
    return redirect(url_for('all_items'))


@app.route('/income_orders')
@login_required
def income_orders():
    """
    Displays a list of all pending loan requests that
    require approval by the warehouse manager.

    If the current user is not a warehouse manager,
    they are redirected to the home page with an error message.

    Returns:
        A rendered HTML template displaying a list of all pending
        loan requests for the warehouse manager to review.
    """
    if not current_user.is_warehouse_manager:
        flash('אינך מורשה לבצע פעולה זאת', category='danger')
        return redirect(url_for('home_page'))
    pending_requests = LoanRequest.query.all()
    return render_template('income_orders.html', pending_requests=pending_requests)

@app.route('/show_request/<int:request_id>',methods=['GET', 'POST'])
@login_required
def show_request(request_id):
    """
    Display the details of a specific loan request for a warehouse manager.

    Args:
        request_id (int): The ID of the loan request to display.

    Returns:
        A rendered HTML template displaying the loan request details and any
        conflicting requests.

        If the request ID is not valid, redirect to the `all_items` page.
        If the current user is not a warehouse manager,
        redirect to the `home_page`.
    """
    if not current_user.is_warehouse_manager:
        flash('אינך מורשה לבצע פעולה זאת', category='danger')
        return redirect(url_for('home_page'))
    user_request = LoanRequest.query.get(request_id)
    if user_request:
        is_live =  datetime.now() > user_request.borrowing_date
        context = {
            'user_request': user_request,
            'conflicting_request': user_request.check_for_conflicting_request(),
            "is_live":is_live
            }
        return render_template('show_request.html', context=context)
    flash('תקלה בעת בחירת הפריט', category='info')
    return redirect(url_for('all_items'))

@app.route('/approve_request/<int:request_id>',methods=['GET', 'POST'])
@login_required
def approve_request(request_id):
    """
    Approves the loan request with the given ID,
    updating its status to 'Approved' in the database.

    Arguments:
    - request_id: int, the ID of the loan request to be approved.

    Returns:
    - If the loan request is successfully approved,
    redirects to the 'income_orders' page with a success message.
    - If the loan request is not found, flashes an
    info message and redirects to the 'income_orders' page.
    - If the user is not a warehouse manager,
    flashes a danger message and redirects to the 'home_page'.
    """
    if not current_user.is_warehouse_manager:
        flash('אינך מורשה לבצע פעולה זאת', category='danger')
        return redirect(url_for('home_page'))
    user_request = LoanRequest.query.get(request_id)
    if user_request:
        user_request.status = 'Approved'
        msg = "בקשה מספר: " + str(user_request.id) + " אושרה. יש לאסוף את הפריט מהמחסן בתאריך שהוגדר."
        today_ = datetime.now()
        notific = Notification(user_id=user_request.user_id, message=msg, msg_date=today_, flag=3)
        db.session.add(notific)
        db.session.commit()
        flash('הבקשה אושרה', category='success')
        return redirect(url_for('income_orders'))
    flash('תקלה בעת מציאת הבקשה', category='info')
    return redirect(url_for('income_orders'))


@app.route('/complete_request/<int:request_id>',methods=['GET', 'POST'])
@login_required
def complete_request(request_id):
    """
    Completes a loan request.

    If the current user is not a warehouse manager,
    it displays an error message and redirects to the home page.

    Retrieves the loan request with the given request_id
    from the database.
    If the loan request exists, it changes the status to
    'Completed', updates the status of the associated item
    to 'Available',
    sets the return date to the current date and time,
    and sends a notification to the user.

    Returns:
    If the loan request is successfully completed,
    it redirects to the 'income_orders' page with a success flash message.
    If there is an error finding the loan request,
    it redirects to the 'income_orders' page with an info flash message.
    """
    if not current_user.is_warehouse_manager:
        flash('אינך מורשה לבצע פעולה זאת', category='danger')
        return redirect(url_for('home_page'))
    user_request = LoanRequest.query.get(request_id)
    item_ = Item.query.get(user_request.item_id)
    if user_request:
        user_request.status = 'Completed'
        item_.status = 'Available'
        user_request.return_date = datetime.now()
        msg = "בקשה מספר: " + str(user_request.id) + " הסתיימה בהצלחה."
        today_ = datetime.today().date()
        notific = Notification(user_id=user_request.user_id, message=msg, msg_date=today_)
        db.session.add(notific)
        db.session.commit()
        flash('השאלת הציוד הסתיימה', category='success')
        return redirect(url_for('income_orders'))
    flash('תקלה בעת מציאת הבקשה', category='info')
    return redirect(url_for('income_orders'))

@app.route('/activate_request/<int:request_id>',methods=['GET', 'POST'])
@login_required
def activate_request(request_id):
    """
    Activates a loan request.

    If the current user is not a warehouse manager,
    it displays an error message and redirects to the home page.

    Retrieves the loan request with the given request_id
    from the database and checks if its status is 'Approved'.
    If the loan request exists and its status is 'Approved',
    it changes the status to 'Activated', updates the status
    of the associated item to 'Loan',
    sets the borrowing date to the current date and time, and sends a notification
    to the user.

    Returns:
    If the loan request is successfully activated,
    it redirects to the 'income_orders' page with a success flash message.
    If there is an error finding the loan request,
    it redirects to the 'income_orders' page with an info flash message.
    """
    if not current_user.is_warehouse_manager:
        flash('אינך מורשה לבצע פעולה זאת', category='danger')
        return redirect(url_for('home_page'))
    user_request = LoanRequest.query.get(request_id)
    item_ = Item.query.get(user_request.item_id)
    if user_request and user_request.status == "Approved":
        user_request.status = 'Activated'
        item_.status = 'Loan'
        user_request.borrowing_date = datetime.now()
        msg = "בקשה מספר: " + str(user_request.id) + " התחילה להיספר."
        today_ = datetime.today().date()
        notific = Notification(user_id=user_request.user_id, message=msg, msg_date=today_, flag=3)
        db.session.add(notific)
        db.session.commit()
        flash('ההשאלה החלה', category='success')
        return redirect(url_for('income_orders'))
    flash('תקלה בעת מציאת הבקשה', category='info')
    return redirect(url_for('income_orders'))

@app.route('/cancel_request/<int:request_id>', methods=['GET', 'POST'])
@login_required
def cancel_request(request_id):
    """
    Endpoint to cancel a loan request made by the current user.

    Parameters:
    request_id (int): The ID of the loan request to cancel.

    Returns:
    redirect: Redirects the user to the 'my_orders' page.

    Behavior:
    - If the loan request is found and belongs to the current user, the request is canceled and deleted from the database.
    - If the loan request is not found, or does not belong to the current user, an error message is flashed and the user is redirected to the 'home_page'.
    """
    user_request = LoanRequest.query.filter_by(id=request_id).first()

    # Check that the request belongs to the current user
    if user_request.user_id != current_user.id and not current_user.is_warehouse_manager:
        flash('You are not authorized to cancel this request.', category='danger')
        return redirect(url_for('home_page'))

    user_request.status = "Canceled"
    db.session.delete(user_request)
    db.session.commit()

    flash('The request has been canceled.', category='success')
    if current_user.is_warehouse_manager:
        return redirect(url_for('income_orders'))
    return redirect(url_for('my_orders'))




@app.route('/requests/<int:request_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_request(request_id):
    '''
    This route function allows users to edit their loan requests.

    Args:

    request_id (int): The id of the loan request to be edited.
    Returns:

    GET: Renders the edit_request.html template,
    showing the form to edit the request.
    POST: If the form data is valid,
    edits the request with the new information and redirects to
    the my_orders page. Otherwise, shows an error message on the form.
    '''
    user_request = LoanRequest.query.filter_by(id=request_id).first_or_404()

    if user_request.user_id != current_user.id:
        abort(403)

    if user_request.status != "נשלח לאישור":
        flash("Only requests in 'נשלח לאישור' status can be edited.", "error")
        return redirect(url_for('my_orders'))

    if user_request.check_for_conflicting_request():
        flash("There is a conflicting request for the same item during the selected dates.", "error")
        return redirect(url_for('my_orders'))

    form = EditRequestForm()
    print(form.borrowing_date,form.return_date,form.reason_for_borrowing)
    if form.validate_on_submit():
        success, message = user_request.edit_request(
            form.borrowing_date.data, form.return_date.data, form.reason_for_borrowing.data
            )
        if success:
            flash(message, "success")
            return redirect(url_for('my_orders'))
        flash(message, "error")
    return render_template('edit_request.html', request=user_request, form=form)

@app.route('/new_report_admin')
def new_report_admin():
    """
    Generates and renders a report for the administrator.

    Retrieves all recommended items with the status 'ordered'
    or 'in_the_wh' from the database and sorts them by the
    date submitted in descending order. It also calculates the
      status counts for the recommended items.

    Returns:
    The 'new_report_admin.html' template is rendered with the recommended items and their corresponding status counts.
    """
    # Get all recommended items with status 'ordered' or 'in_the_wh' and sort by date submitted
    items = recommend_file_detail.query.filter(
        recommend_file_detail.status.in_(['ordered', 'in_the_wh'])
        ).order_by(
        recommend_file_detail.date_submitted.desc()
        ).all()
    # Calculate the status counts
    status_counts = db.session.query(
        recommend_file_detail.status, func.count(recommend_file_detail.id)
        ).group_by(
        recommend_file_detail.status
        ).all()
    return render_template('new_report_admin.html', items=items, status_counts=status_counts)

@app.route('/last_orders_report', methods=['GET', 'POST'])
def last_orders_report():
    """
    Generates and renders a report of last orders.

    If the request method is POST, it retrieves
    the search start date parameter from the form
    and performs a search query
    using the start date to filter the orders.
    The filtered orders are passed as context to
    the 'last_orders_report.html'
    template and rendered.

    If the request method is not POST,
    all orders are retrieved from the database and
    passed as context to the
    'last_orders_report.html' template and rendered.

    Returns:
    If the request method is POST, the 'last_orders_report.html'
    template is rendered with the filtered orders.
    If the request method is not POST,
    the 'last_orders_report.html' template is rendered with all orders.
    """
    orders = None
    if request.method=="POST":
        date = request.form.get("search_start_date")
        if date:
            date_type = datetime.strptime(date, '%Y-%m-%d')
            date_time_start = date_type.replace(hour = 0,minute = 0, second = 0)
            date_time_end = datetime.today()
            orders = LoanRequest.query.join(User).filter(
                LoanRequest.opened_on >= date_time_start,
                LoanRequest.opened_on <= date_time_end
                ).all()
            print(orders)
        else:
            orders = LoanRequest.query.all()
        return render_template('last_orders_report.html', orders=orders)
    return render_template('last_orders_report.html', orders=orders)

@app.route('/stud_req_report')
@login_required
def stud_req_report():
    """
    Generates and renders a report of student loan requests.

    If the current user is a teaching staff member,
    it retrieves all loan requests made by students from the database
    and counts the number of requests for each unique item.
    The list of unique items and their corresponding request counts
    are passed as context to the 'stud_req_report.html'
    template for rendering.

    Returns:
    The 'stud_req_report.html'
    template is rendered with the list of unique items,
    loan requests made by students,
    and the corresponding request counts.
    """
    requests = None
    items = []
    request_counts = []
    if current_user.is_teaching_staff_member:
        requests = LoanRequest.query.join(User).filter(User.is_teaching_staff_member is False).all()
        for req in requests:
            item_name = req.loan_request_item.item_name
            if item_name not in items:
                items.append(item_name)
                request_counts.append(1)
            else:
                item_index = items.index(item_name)
                request_counts[item_index] += 1
    return render_template('stud_req_report.html',items=items, requests=requests,request_counts=request_counts)

@app.route('/item_status_report')
def item_status_report():
    """
    Generates and renders a report of item statuses.

    Retrieves all items from the database and
    passes them as context to the 'item_status_report.html' template
    for rendering.

    Returns:
    The 'item_status_report.html'
    template is rendered with all items.
    """
    items = Item.query.all()
    return render_template('item_status_report.html', items=items)

@app.route('/reports/returned_orders', methods=['GET', 'POST'])
def generate_returned_orders_report():
    """
    Generates and renders a report of returned orders.

    If the request method is POST,
    it retrieves the return date parameter from the form and performs a search query
    using the return date to filter the returned orders.
    The filtered orders are passed as context to the
    'returned_orders_report.html' template and rendered.

    If the request method is not POST,
    it retrieves all completed loan requests and their
    associated items
    from the database and passes them as context to
    the 'returned_orders_report.html' template and renders it.

    Returns:
    If the request method is POST, the
    'returned_orders_report.html' template is rendered with
    the filtered orders.
    If the request method is not POST,
    the 'returned_orders_report.html' template is rendered with all completed
    loan requests.
    """
    if request.method == 'POST':
        return_date = request.form.get('return-date')
        # Perform the search query using the return_date parameter
        if return_date:
            return_date_type = datetime.strptime(return_date, '%Y-%m-%d')
            start_of_day = return_date_type.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = (start_of_day + timedelta(days=1)) - timedelta(seconds=1)
            returned_orders = (
                db.session.query(LoanRequest, Item)
                .join(Item).filter(
                        LoanRequest.status == 'Completed',
                        LoanRequest.return_date >= start_of_day,
                        LoanRequest.return_date <= end_of_day
                ).all()
            )
        else:
            returned_orders = db.session.query(
                LoanRequest, Item
                ).join(Item).filter(
                LoanRequest.status == 'Completed'
                ).all()
        # Render the template with the filtered orders
        return render_template('returned_orders_report.html', orders=returned_orders)
    returned_orders = db.session.query(
        LoanRequest, Item
        ).join(Item).filter(
        LoanRequest.status == 'Completed'
        ).all()
    return render_template('returned_orders_report.html', orders=returned_orders)

@app.route('/repairs', methods=['GET','POST'])
@login_required
def repairs():
    """
    Renders the page displaying the list of repairs and items.

    Checks if the current user is a warehouse manager.
    If not, a danger flash message is displayed,
    and the user is redirected to the 'home_page'.
    Retrieves all items and repair records from the database.
    Renders the 'repairs.html'
    template with the repair records and items passed as context.

    Returns:
    The repairs page is rendered with
    the repair records and items passed as context.
    """
    if not current_user.is_warehouse_manager:
        flash('אינך מורשה לבצע פעולה זאת', category='danger')
        return redirect(url_for('home_page'))
    items_ = Item.query.all()
    repairs_tbl = Repair_Table.query.all()

    return render_template('repairs.html', reps=repairs_tbl, items=items_)



@app.route('/show_item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def show_item(item_id):
    """
    Renders the page displaying details of a specific item.

    Checks if the current user is a warehouse manager.
    If not, a danger flash message is displayed,
    and the user is redirected to the 'home_page'.
    Retrieves the item with the specified
    ID from the database.
    If the item exists,
    the item detail page is rendered with the
    item object passed as context.
    If the item does not exist,
    an info flash message is displayed,
    and the user is redirected to the 'repairs' page.

    Args:
    item_id (int): The ID of the item being displayed.

    Returns:
    If the item exists,
    the item detail page is rendered with the
    item object passed as context.
    If the item does not exist,
    the user is redirected to the 'repairs' page with an info flash message.
    """
    if not current_user.is_warehouse_manager:
        flash('אינך מורשה לבצע פעולה זאת', category='danger')
        return redirect(url_for('home_page'))
    item_ = Item.query.get(item_id)
    if item_:
        return render_template('show_item.html', item=item_)
    flash('תקלה בעת בחירת הפריט', category='info')
    return redirect(url_for('repairs'))

@app.route('/repair_item/<int:item_id>', methods=['POST','GET'])
@login_required
def repair_item(item_id):
    """
    Handles the repair of an item.

    Checks if the current user is a warehouse manager.
    If not, a danger flash message is displayed,
    and the user is redirected to the 'home_page'.
    Retrieves the item with the specified ID
    from the database.
    If the item exists,
    a new repair request is created with the item's details.
    All loan requests associated with the item are
    canceled, and corresponding notifications are sent to the users.
    The item's status is updated to "Under Repair".
    The repair request is added to the database.
    A success flash message is displayed,
    and the user is redirected to the 'repairs' page.
    If the item does not exist,
    an info flash message is displayed,
    and the user is redirected to the 'repairs' page.

    Args:
    item_id (int): The ID of the item being repaired.

    Returns:
    If the item exists, the user is redirected to the
    'repairs' page with a success flash message.
    If the item does not exist, the user is redirected to the
    'repairs' page with an info flash message.
    """
    if not current_user.is_warehouse_manager:
        flash('אינך מורשה לבצע פעולה זאת', category='danger')
        return redirect(url_for('home_page'))
    item_ = Item.query.get(item_id)
    if item_:
        repair_ = Repair_Table(
            item_id=item_.id,
            item_name=item_.item_name,
            repair_date=datetime.now(),
            status="Under repair")
        requests_ = LoanRequest.query.filter_by(item_id=item_.id).all()
        item_.status = "Under Repair"
        for req in requests_:
            req.status = "Canceled"
            msg = "פריט: " + item_.item_ID + " נשלח לתיקון ולכן בקשת ההשאלה שלך לפריט זה בוטלה."
            today_ = datetime.today().date()
            notific = Notification(user_id=req.user_id, message=msg, msg_date=today_, flag=0)
            db.session.add(notific)
            db.session.commit()

        db.session.add(repair_)
        db.session.commit()
        flash('הבקשה אושרה', category='success')
        return redirect(url_for('repairs'))
    flash('תקלה בעת מציאת הבקשה', category='info')
    return redirect(url_for('repairs'))


@app.route('/return_item/<int:rep_id>', methods=['POST','GET'])
@login_required
def return_item(rep_id):
    """
    Handles the return of an item.

    Checks if the current user is a warehouse manager.
    If not, a danger flash message is displayed,
    and the user is redirected to the 'home_page'.
    Retrieves the repair request with the specified ID
    from the database.
    Retrieves the item associated with the repair
    request from the database.
    If the item exists, its status is updated to "Available"
    and the repair request's status is updated to "Returned".
    The changes are then committed to the database.
    A success flash message is displayed, and the user is
    redirected to the 'repairs' page.
    If the item or repair request does not exist, an info
    flash message is displayed,
    and the user is redirected to the 'repairs' page.

    Args:
    rep_id (int): The ID of the repair request for the item being returned.

    Returns:
    If the item exists,
    the user is redirected to the 'repairs'
    page with a success flash message.
    If the item does not exist,
    the user is redirected to the 'repairs'
    page with an info flash message.
    """
    if not current_user.is_warehouse_manager:
        flash('אינך מורשה לבצע פעולה זאת', category='danger')
        return redirect(url_for('home_page'))
    repair_ = Repair_Table.query.get(rep_id)
    item_ = Item.query.get(repair_.item_id)
    if item_:
        item_.status = "Available"
        repair_.status = "Returned"
        db.session.commit()
        flash('הבקשה אושרה', category='success')
        return redirect(url_for('repairs'))
    flash('תקלה בעת מציאת הבקשה', category='info')
    return redirect(url_for('repairs'))


@app.route('/read_msg_d/<int:msg_id>', methods=['POST','GET'])
@login_required
def read_msg_d(msg_id):
    """
    Marks a notification message as read.

    Retrieves the notification message with the
    specified ID from the database.
    If the message exists, its status is updated to
    "Read" and its flag is set to 4.
    The changes are then committed to the database.
    A success flash message is displayed,
    and the user is redirected to the 'home_page'.
    If the message does not exist, an info flash message
    is displayed, and the user is redirected to the 'home_page'.

    Args:
    msg_id (int): The ID of the notification message to be marked as read.

    Returns:
    If the message exists,
    the user is redirected to the 'home_page' with
    a success flash message.
    If the message does not exist,
    the user is redirected to the 'home_page' with
    an info flash message.
    """
    msg = Notification.query.get(msg_id)
    if msg:
        msg.status = "Read"
        msg.flag=4
        db.session.commit()
        flash('הודעה סומנה כנקראה', category='success')
        return redirect(url_for('home_page'))
    flash('תקלה בעת מציאת הבקשה', category='info')
    return redirect(url_for('home_page'))


@app.route('/del_msg_d/<int:msg_id>', methods=['POST','GET'])
@login_required
def del_msg_d(msg_id):
    """
    Deletes a notification message.

    Retrieves the notification message with the
    specified ID from the database.
    If the message exists, it is deleted from the database,
    and a success flash message is displayed.
    Finally, the user is redirected to the 'home_page'.
    If the message does not exist,
    an info flash message is displayed,
    and the user is redirected to the 'home_page'.

    Args:
    msg_id (int): The ID of the notification message to be deleted.

    Returns:
    If the message exists,
    the user is redirected to the 'home_page' with a success flash message.
    If the message does not exist,
    the user is redirected to the 'home_page' with an info flash message.
    """
    msg = Notification.query.get(msg_id)
    if msg:
        db.session.delete(msg)
        db.session.commit()
        flash('הודעה נמחקה', category='success')
        return redirect(url_for('home_page'))


    flash('תקלה בעת מציאת הבקשה', category='info')
    return redirect(url_for('home_page'))



@app.route('/read_msg_m/<int:msg_id>', methods=['POST','GET'])
@login_required
def read_msg_m(msg_id):
    """
    Marks a notification message as read.

    Retrieves the notification message with the
    specified ID from the database.
    If the message exists, its status is updated to
    "Read" in the database, and a success flash message is displayed.
    Finally, the user is redirected to the 'my_notifications' page.
    If the message does not exist, an info flash message is displayed,
    and the user is redirected to the 'home_page'.

    Args:
    msg_id (int): The ID of the notification message to be marked as read.

    Returns:
    If the message exists, the user is redirected to the
    'my_notifications' page with a success flash message.
    If the message does not exist,
    the user is redirected to the 'home_page' with an info flash message.
    """
    msg = Notification.query.get(msg_id)
    if msg:
        msg.status = "Read"
        db.session.commit()
        flash('הודעה סומנה כנקראה', category='success')
        return redirect(url_for('my_notifications'))
    flash('תקלה בעת מציאת הבקשה', category='info')
    return redirect(url_for('home_page'))


@app.route('/del_msg_m/<int:msg_id>', methods=['POST','GET'])
@login_required
def del_msg_m(msg_id):
    """
    Deletes a notification message.

    Retrieves the notification message with the specified
    ID from the database.
    If the message exists,
    it is deleted from the database and a success flash message is displayed.
    Finally, the user is redirected to the 'my_notifications' page.
    If the message does not exist,
    an info flash message is displayed and the user is
    redirected to the 'home_page'.

    Args:
    msg_id (int): The ID of the notification message to be deleted.

    Returns:
    If the message exists,
    the user is redirected to the 'my_notifications'
    page with a success flash message.
    If the message does not exist, the user is redirected to the
    'home_page' with an info flash message.
    """
    msg = Notification.query.get(msg_id)
    if msg:
        db.session.delete(msg)
        db.session.commit()
        flash('הודעה נמחקה', category='success')
        return redirect(url_for('my_notifications'))
    flash('תקלה בעת מציאת הבקשה', category='info')
    return redirect(url_for('home_page'))



@app.route('/messages', methods=['POST','GET'])
@login_required
def my_notifications():
    """
    Renders the notifications page for the current user.

    Retrieves all notifications associated with the
    current user from the database and renders the
    "my_notifications.html" template with the user
    object and the list of notifications.

    Returns:
    The rendered notifications page with the user
    object and the list of notifications.
    """
    notifications = Notification.query.filter_by(user_id = current_user.id).all()
    return render_template('my_notifications.html',user=current_user, notifications = notifications)



@app.route('/repair_status_report')
@login_required
def repair_status_report():
    """
    Renders the repair status report page.

    If the current user is a warehouse manager,
    the route retrieves a list of all repair
    records from the database and renders the
    "repair_status_report.html" template with
    the list of repairs.
    Otherwise, it flashes an error message and redirects to the home page.

    Returns:
    If the current user is a warehouse manager,
    the rendered repair status report page.
    Otherwise, a redirect to the home page.
    """
    if current_user.is_warehouse_manager:
        #repairs = Repair_Table.query.filter_by(status="Under Repair").all()
        repairs_tbl = Repair_Table.query.all()
        return render_template('repair_status_report.html', reps=repairs_tbl)
    flash('אין לך הרשאות לגשת לעמוד זה', category='info')
    return redirect(url_for('home_page'))


@app.route('/contact_teachers', methods=['GET'])
@login_required
def contact_teaching_staff():
    """
    Renders the contact page for teaching staff members.

    If the current user is a warehouse manager,
    the route retrieves a list of teaching staff members from the database
    and renders the "contact_teachers.html" template with the list of users.
    Otherwise, it flashes an error message and redirects to the home page.

    Returns:
    If the current user is a warehouse manager,
    the rendered contact page for teaching staff members.
    Otherwise, a redirect to the home page.
    """
    if current_user.is_warehouse_manager:
        users_ = User.query.filter_by(is_teaching_staff_member=True).all()
        return render_template("contact_teachers.html", users=users_)
    flash('אין לך הרשאות לגשת לדף זה')
    return redirect(url_for("home_page"))


@app.route('/about')
def about():
    """
    Renders the About page.

    Returns:
    A Flask response object with the rendered About page.
    """
    response = make_response(render_template('about.html'))
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    return response
