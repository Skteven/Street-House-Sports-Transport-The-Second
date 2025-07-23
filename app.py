from flask import Flask, request, render_template, redirect, url_for, session
from sqlalchemy import create_engine, text
from datetime import date, timedelta, datetime
import sqlite3
import calendar
import re

app = Flask(__name__)
app.secret_key = 'isasecret'


def get_db_connection():
    conn = sqlite3.connect('transport.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def home():
    return render_template('Home.html', username=session.get('username'), userrole=session.get('userrole'))


def get_upcoming_weekend_dates():
    today = date.today()
    weekend_dates = []

    # Find the next Saturday (weekday 5) and Sunday (weekday 6)
    for target_weekday in [5, 6]:
        days_until = (target_weekday - today.weekday()) % 7
        next_day = today + timedelta(days=days_until)
        iso = next_day.strftime('%Y-%m-%d')  # For the value
        label = f"{calendar.day_name[next_day.weekday()]} {next_day.day} {next_day.strftime('%B %Y')}"
        weekend_dates.append((iso, label))

    return weekend_dates


@app.route('/Form', methods=['POST', 'GET'])
def form():
    weekend_dates = get_upcoming_weekend_dates()
    use_previous = request.args.get('use_previous')
    prefill = {}
    field_errors = {}
    previous_entries = []

    loc_map = {
    "1": "Other",
    "2": "Cranbrook Junior School",
    "3": "Lyne Park Tennis Courts",
    "4": "Knox Grammar School",
    "5": "Trinity Grammar School",
    "6": "Barker College",
    "7": "St Aloysius",
    "8": "Waverly College"
    }

    if not session.get('username') or not session.get('userrole'):
        return render_template('Form.html',
                               error="Please sign in or sign up before submitting the form.",
                               username=session.get('username'), userrole=session.get('userrole'),
                               weekend_dates=weekend_dates,
                               latest_entry=None,
                               previous_entries=[],
                               prefill={},
                               loc_map=loc_map, 
                               field_errors=field_errors,
                               user_phone=None)

    conn = get_db_connection()
    user_info = conn.execute('SELECT * FROM User WHERE Username = ?', (session.get('username'),)).fetchone()
    if user_info is None:
        return redirect(url_for('Logout'))
    previous_entries = conn.execute(
        "SELECT * FROM Timetable WHERE SubmittedBy = ? ORDER BY TimetableID DESC LIMIT 2",
        (session.get('username'),)).fetchall()
    conn.close()

    if use_previous:
        try:
            index = int(use_previous) - 1
            selected_entry = previous_entries[index]
            prefill = {
                'FullName': selected_entry['FullName'],
                'PNumber': selected_entry['PNumber'],
                'Location': str(selected_entry['Location']),
                'Other': selected_entry['Other'],
                'DropOff': selected_entry['DropOff'],
                'PickUp': selected_entry['PickUp'],
                'AddInfo': selected_entry['AddInfo']
            }
        except (IndexError, ValueError):
            pass

    if request.method == 'POST':
        FullName = user_info['Username']
        PNumber = user_info['PNumber']
        Location = request.form.get('Location')
        Other = request.form.get('Other')
        DropOff = request.form.get('DropOff')
        PickUp = request.form.get('PickUp')
        AddInfo = request.form.get('AddInfo')
        SelectedDate = request.form.get('Date')

        field_errors={}

        if not DropOff:
            field_errors['DropOff'] = "Please select a Drop Off time or choose 'No need'."
        if not PickUp:
            field_errors['PickUp'] = "Please select a Pick Up time or choose 'No need'."
        if not Location:
            field_errors['Location'] = "Location is required."
        elif Location == '1':
            if not Other or not Other.strip():
                field_errors['Other'] = "Please specify your location if you selected 'Other'."

        if not SelectedDate:
            field_errors['Date'] = "Please select a date."

        if DropOff and PickUp and DropOff.strip().lower() == "no need" and PickUp.strip().lower() == "no need":
            field_errors['DropOff'] = "You cannot select 'No need' for both Drop Off and Pick Up."
            field_errors['PickUp'] = "You cannot select 'No need' for both Drop Off and Pick Up."

        fmt = "%I:%M %p"
        try:
            drop_time = None
            pick_time = None

            if DropOff and DropOff.strip().lower() != "no need":
                drop_time = datetime.strptime(DropOff.strip(), fmt)
            if PickUp and PickUp.strip().lower() != "no need":
                pick_time = datetime.strptime(PickUp.strip(), fmt)

            if drop_time and pick_time and drop_time >= pick_time:
                field_errors['DropOff'] = "Drop Off time must be earlier than Pick Up time."
                field_errors['PickUp'] = "Pick Up time must be later than Drop Off time."

        except ValueError:
            if DropOff and DropOff.strip().lower() != "no need":
                field_errors['DropOff'] = "Invalid time format."
            if PickUp and PickUp.strip().lower() != "no need":
                field_errors['PickUp'] = "Invalid time format."


        prefill = {
            'Location': Location,
            'Other': Other,
            'DropOff': DropOff,
            'PickUp': PickUp,
            'AddInfo': AddInfo,
            'Date': SelectedDate}

        if field_errors:
            return render_template('Form.html',
                username=session.get('username'), userrole=session.get('userrole'),
                weekend_dates=weekend_dates,
                previous_entries=previous_entries,
                prefill=prefill,
                loc_map=loc_map,
                field_errors=field_errors,
                user_phone=user_info['PNumber'])

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO Timetable (FullName,PNumber,Date,Location,Other,DropOff,PickUp,AddInfo, SubmittedBy) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (FullName, PNumber, SelectedDate, Location, Other, DropOff, PickUp, AddInfo, session.get('username'))
        )
        conn.commit()
        conn.close()

        return redirect(url_for('form', submitted='1'))

    success = request.args.get('submitted') == '1'

    return render_template('Form.html',
                           username=session.get('username'), userrole=session.get('userrole'),
                           weekend_dates=weekend_dates,
                           success="Form submitted successfully!" if success else None,
                           latest_entry=previous_entries[0] if previous_entries else None,
                           previous_entries=previous_entries,
                           prefill=prefill,
                           loc_map=loc_map,
                           field_errors=field_errors,
                           user_phone=user_info['PNumber'])


@app.route('/Our_Team')
def team():
    return render_template('Our_Team.html', username=session.get('username'), userrole=session.get('userrole'))


@app.route('/NewAcc', methods=['POST', 'GET'])
def NewAcc():
    global SEmail
    field_errors = {}
    prefill_email = request.args.get('prefill_email', '')
    
    if request.method == 'POST':
        Email = request.form['Email'].strip().lower()
        Username = request.form['Username']
        Role = request.form['Role']
        Password = request.form['Password']
        FName = request.form['FName']
        SName = request.form['SName']
        PNumber = request.form['PNumber']
        prefill_email = request.args.get('prefill_email', '')
        email_lower = Email.strip().lower()
        

        conn = get_db_connection()
        existing = conn.execute('SELECT * FROM User WHERE LOWER(TRIM(Email)) = ?', (Email,)).fetchone()
        if existing:
            conn.close()
            return "An account with that email already exists. Please go back and try again."

        if not re.fullmatch(r"^[\w\.-]+@(student\.)?cranbrook\.nsw\.edu\.au$", email_lower):
            conn.close()
            return render_template('NewAcc.html', error="Email must be a valid Cranbrook address.")

        elif Role == "3" and not email_lower.endswith("@student.cranbrook.nsw.edu.au"):
            conn.close()
            return render_template('NewAcc.html', error="Student email must end with '@student.cranbrook.nsw.edu.au'.")
        elif Role in ["1", "2"] and not email_lower.endswith("@cranbrook.nsw.edu.au"):
            conn.close()
            return render_template('NewAcc.html', error="Staff email must end with '@cranbrook.nsw.edu.au'.")
        elif Role in ["1", "2"] and "@student.cranbrook.nsw.edu.au" in email_lower:
            conn.close()
            return render_template('NewAcc.html', error="Staff email must not include '@student.cranbrook.nsw.edu.au'.")

        conn.execute('INSERT INTO User (Email, FName, SName, PNumber, Username, Role, Password) VALUES (?, ?, ?, ?, ?, ?, ?)',
                     (Email, FName, SName, PNumber, Username, Role, Password))
        conn.commit()
        conn.close()

        return redirect(url_for('password'))

    return render_template('NewAcc.html', prefill_email=request.args.get('prefill_email', ''))

@app.route('/Contact_us')
def contact():
    return render_template('Contact_us.html', username=session.get('username'), userrole=session.get('userrole'))


@app.route('/Login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        session['SEmail'] = request.form['SEmail'].strip().lower()
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM User WHERE LOWER(Email) = LOWER(?)', (session['SEmail'],)).fetchone()
        conn.close()

        if user is None:
            return redirect(url_for('NewAcc', prefill_email=session['SEmail']))
        return redirect(url_for('password'))
    return render_template('login.html')

@app.route('/Password', methods=['POST', 'GET'])
def password():
    if request.method == 'POST':
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM User WHERE password=? AND LOWER(Email)=?', (password, session.get('SEmail'))).fetchone()
        conn.close()
        if user is None:
            return render_template('password.html', error="Incorrect password.")
        session['username'] = user['Username']
        session['userrole'] = user['Role']
        return redirect(url_for('home'))
    return render_template('password.html')


@app.route('/Timetable')
def timetable():
    archive_old_entries() 

    conn = get_db_connection()
    if session.get('userrole') == 1:
        submissions = conn.execute(
            'SELECT * FROM Timetable JOIN Location ON Timetable.Location = Location.LocationID ORDER BY TimetableID DESC'
        ).fetchall()
    else:
        submissions = conn.execute(
            'SELECT * FROM Timetable JOIN Location ON Timetable.Location = Location.LocationID WHERE SubmittedBy = ? ORDER BY TimetableID DESC',
            (session.get('username'),)
        ).fetchall()

    conn.close()
    return render_template('Timetable.html', submissions=submissions,username=session.get('username'), userrole=session.get('userrole'))



@app.route('/Logout', methods=['POST', 'GET'])
def Logout():
    session.clear()
    return render_template('Home.html', username=None, userrole=None)

@app.route('/Settings', methods=['GET', 'POST'])
def settings():
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM User WHERE Username = ?', (session.get('username'),)).fetchone()
    field_errors = {}
    user_role= user['Role']

    if request.method == 'POST':
        if request.form.get('cancel') == '1':
            conn.close()
            return redirect(url_for('settings'))

        new_username = request.form.get('Username')
        new_email = request.form.get('Email')
        new_phone = request.form.get('PNumber')
        new_password = request.form.get('Password')
        confirm_password = request.form.get('ConfirmPassword')

        original_username = request.form.get('OriginalUsername')
        original_email = request.form.get('OriginalEmail')
        original_phone = request.form.get('OriginalPNumber')
        original_password = request.form.get('OriginalPassword')

        email_lower = new_email.strip().lower()
        role_str = str(user_role)

        if not re.fullmatch(r"^[\w\.-]+@(student\.)?cranbrook\.nsw\.edu\.au$", email_lower):
            field_errors['Email'] = "Email must be a valid Cranbrook address."
        elif role_str == "3" and not email_lower.endswith("@student.cranbrook.nsw.edu.au"):
            field_errors['Email'] = "Student email must end with '@student.cranbrook.nsw.edu.au'."
        elif role_str in ["1", "2"] and not email_lower.endswith("@cranbrook.nsw.edu.au"):
            field_errors['Email'] = "Staff email must end with '@cranbrook.nsw.edu.au'."
        elif role_str in ["1", "2"] and "@student.cranbrook.nsw.edu.au" in email_lower:
            field_errors['Email'] = "Staff email must not include '@student.cranbrook.nsw.edu.au'."


        if not new_phone or not new_phone.isdigit() or not new_phone.startswith("0") or len(new_phone) != 10:
            field_errors['PNumber'] = "Invalid Number."

        if new_password != original_password:
            if not new_password or len(new_password) < 6:
                field_errors['Password'] = "Password must be at least 6 characters long."
            if not confirm_password:
                field_errors['ConfirmPassword'] = "Please confirm your password."
            elif new_password != confirm_password:
                field_errors['ConfirmPassword'] = "Passwords do not match."
        else:
            if confirm_password and new_password != confirm_password:
                field_errors['ConfirmPassword'] = "Passwords do not match."

        if field_errors:
            first_error = next(iter(field_errors))
            error_message = f"{field_errors[first_error]} Changes not saved."

            conn.close()
            user = {
                'Username': new_username,
                'Email': new_email,
                'PNumber': new_phone,
                'Password': new_password
            }
            return render_template(
                'Settings.html',
                user=user,
                username=session.get('username'),
                userrole=session.get('userrole'),
                field_errors=field_errors,
                save_error=error_message
            )

        conn.execute('''
            UPDATE User 
            SET Username = ?, Email = ?, PNumber = ?, Password = ?
            WHERE Username = ?
        ''', (new_username, new_email, new_phone, new_password, session.get('username')))
        conn.commit()
        conn.close()

        session['username'] = new_username
        return redirect(url_for('settings', saved='1'))

    saved = request.args.get('saved') == '1'
    conn.close()
    return render_template('Settings.html', user=user, username=session.get('username'), userrole=session.get('userrole'), field_errors={}, saved=saved)

@app.route('/Admin')
def admin():
    if session.get('userrole') != 1:
        return redirect(url_for('home'))

    conn = get_db_connection()
    users = conn.execute('SELECT * FROM User').fetchall()
    conn.close()

    return render_template('Admin.html', users=users, username=session.get('username'), userrole=session.get('userrole'))

@app.route('/DeleteUser', methods=['POST'])
def delete_user():
    if session.get('userrole') != 1:
        return redirect(url_for('home'))

    username_to_delete = request.form.get('username')

    conn = get_db_connection()
    conn.execute('DELETE FROM User WHERE Username = ?', (username_to_delete,))
    conn.commit()
    conn.close()

    return redirect(url_for('admin'))

def archive_old_entries():
    conn = get_db_connection()
    today = date.today().isoformat()

    past_entries = conn.execute('SELECT * FROM Timetable WHERE Date < ?', (today,)).fetchall()

    for entry in past_entries:
        conn.execute('''
            INSERT INTO ArchivedTimetable 
            (TimetableID, FullName, PNumber, Date, Location, Other, DropOff, PickUp, AddInfo, SubmittedBy)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            entry['TimetableID'], entry['FullName'], entry['PNumber'], entry['Date'],
            entry['Location'], entry['Other'], entry['DropOff'], entry['PickUp'],
            entry['AddInfo'], entry['SubmittedBy']
        ))

    conn.execute('DELETE FROM Timetable WHERE Date < ?', (today,))
    conn.commit()
    conn.close()


@app.route('/Archived')
def archived():
    selected_date = request.args.get('date')

    conn = get_db_connection()
    archived_dates = conn.execute(
        'SELECT DISTINCT Date FROM ArchivedTimetable ORDER BY Date DESC'
    ).fetchall()
    # No commit or save needed here since we are only reading from the database.
    filtered_entries = []
    if selected_date:
        filtered_entries = conn.execute(
            '''
            SELECT a.*, l.LocationName 
            FROM ArchivedTimetable a
            LEFT JOIN Location l ON a.Location = l.LocationID
            WHERE a.Date = ?
            ORDER BY a.TimetableID DESC
            ''',
            (selected_date,)
        ).fetchall()

    conn.close()
    return render_template(
        'ArchivedTable.html',
        archived_dates=archived_dates,
        filtered_entries=filtered_entries,
        selected_date=selected_date,
        username=session.get('username'),
        userrole=session.get('userrole')
    )


app.run(debug=True, reloader_type='stat', port=5000)

