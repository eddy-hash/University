from flask import Flask, request, session, render_template, redirect, url_for, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# -----------------------------
# MySQL Configuration
# -----------------------------
app.config['MYSQL_HOST'] = '127.0.0.1'      # Use 127.0.0.1 on Windows
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Eddy@2023'
app.config['MYSQL_DB'] = 'students'
app.config['MYSQL_PORT'] = 3307

mysql = MySQL(app)

# -----------------------------
# Routes
# -----------------------------

@app.route('/')
def home():
    if 'username' in session:
        # Fetch full user info from DB
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM students WHERE username=%s", (session['username'],))
        user = cur.fetchone()
        cur.close()
        return render_template('base.html', user=user)
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Logged-in user info
    cur.execute("SELECT * FROM students WHERE username=%s", (session['username'],))
    user = cur.fetchone()

    # Fetch all students for table
    cur.execute("SELECT * FROM students")
    students = cur.fetchall()

    cur.close()

    if request.method == 'POST':
        # Collect form data
        phone = request.form.get('phone')
        nida = request.form.get('nida')
        email = request.form.get('email')
        full_name = request.form.get('full_name')
        dob = request.form.get('dob')
        gender = request.form.get('gender')
        address = request.form.get('address')
        program = request.form.get('program')
        department = request.form.get('department')
        year = request.form.get('year')
        guardian_name = request.form.get('guardian_name')
        guardian_phone = request.form.get('guardian_phone')
        password = request.form.get('password')
        image = request.files.get('profile_image')

        # Build update query
        update_query = """
            UPDATE students SET full_name=%s, dob=%s, gender=%s, phone=%s, nida=%s,
                                email=%s, address=%s, program=%s, department=%s, year=%s,
                                guardian_name=%s, guardian_phone=%s
        """
        params = [full_name, dob, gender, phone, nida, email, address, program,
                  department, year, guardian_name, guardian_phone]

        if password:
            hashed = generate_password_hash(password)
            update_query += ", password=%s"
            params.append(hashed)

        if image and image.filename != '':
            os.makedirs("static/images", exist_ok=True)
            image_path = os.path.join("static/images", image.filename)
            image.save(image_path)
            update_query += ", profile_image=%s"
            params.append(image.filename)

        update_query += " WHERE username=%s"
        params.append(session['username'])

        # Execute update
        cur = mysql.connection.cursor()
        cur.execute(update_query, params)
        mysql.connection.commit()
        cur.close()

        flash("Profile updated successfully!", "success")
        return redirect(url_for('dashboard'))

    return render_template('dashboard.html', user=user, students=students)

@app.route('/update_account', methods=['POST'])
def update_account():
    if 'username' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM students WHERE username=%s", (session['username'],))
    user = cur.fetchone()
    cur.close()

    # Collect form data
    phone = request.form.get('phone')
    nida = request.form.get('nida')
    email = request.form.get('email')
    full_name = request.form.get('full_name')
    dob = request.form.get('dob')
    gender = request.form.get('gender')
    address = request.form.get('address')
    program = request.form.get('program')
    department = request.form.get('department')
    year = request.form.get('year')
    guardian_name = request.form.get('guardian_name')
    guardian_phone = request.form.get('guardian_phone')
    password = request.form.get('password')
    image = request.files.get('profile_image')

    # Build update query
    update_query = """
        UPDATE students SET full_name=%s, dob=%s, gender=%s, phone=%s, nida=%s,
                            email=%s, address=%s, program=%s, department=%s, year=%s,
                            guardian_name=%s, guardian_phone=%s
    """
    params = [full_name, dob, gender, phone, nida, email, address, program,
              department, year, guardian_name, guardian_phone]

    if password:
        hashed = generate_password_hash(password)
        update_query += ", password=%s"
        params.append(hashed)

    if image and image.filename != '':
        os.makedirs("static/images", exist_ok=True)
        image_path = os.path.join("static/images", image.filename)
        image.save(image_path)
        update_query += ", profile_image=%s"
        params.append(image.filename)

    update_query += " WHERE username=%s"
    params.append(session['username'])

    # Execute update
    cur = mysql.connection.cursor()
    cur.execute(update_query, params)
    mysql.connection.commit()
    cur.close()

    flash("Profile updated successfully!", "success")
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        pwd = request.form['password']

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT username, password FROM students WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()

        if not user:
            error = "Username does not exist"
        elif not check_password_hash(user['password'], pwd):
            error = "Incorrect password"
        else:
            session['username'] = user['username']
            return redirect(url_for('home'))

    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        pwd = request.form['password']
        hashed_pwd = generate_password_hash(pwd)

        cur = mysql.connection.cursor()
        try:
            cur.execute("INSERT INTO students (username, password) VALUES (%s, %s)", (username, hashed_pwd))
            mysql.connection.commit()
        except MySQLdb.IntegrityError:
            error = "Username already exists"
        cur.close()

        if not error:
            flash("Registration successful! Please login.", "success")
            return redirect(url_for('login'))

@app.route('/delete_permission/<int:request_id>', methods=['POST'])
def delete_permission(request_id):
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM permissions WHERE id = %s", (request_id,))
    mysql.connection.commit()
    cursor.close()

    flash("Permission request deleted successfully!", "success")
    return redirect(url_for('pex_requests'))


@app.route('/pex_requests', methods=['GET', 'POST'])
def pex_requests():
    if 'username' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    username = session['username']

    # Get student_id
    cur.execute("SELECT student_id FROM students WHERE username=%s", (username,))
    student = cur.fetchone()
    if not student:
        flash("Student not found", "error")
        return redirect(url_for('dashboard'))
    
    student_id = student['student_id']

    # Handle POST form (from statements.html)
    if request.method == 'POST':
        reason = request.form.get('reason')
        details = request.form.get('details')

        if reason and details:
            cur.execute(
                "INSERT INTO permission_requests (username, student_id, reason, details, status) "
                "VALUES (%s, %s, %s, %s, %s)",
                (username, student_id, reason, details, 'Pending')
            )
            mysql.connection.commit()
            flash("Permission request submitted successfully", "success")
        else:
            flash("Reason and details are required", "error")

    # Fetch permission requests for this student
    cur.execute(
        "SELECT * FROM permission_requests WHERE student_id=%s ORDER BY created_at DESC",
        (student_id,)
    )
    requests = cur.fetchall()
    cur.close()

    return render_template('permission.html', user_requests=requests, username=username)


@app.route('/statements')
def statements():
    return render_template('statements.html')

@app.route('/registration')
def registration():
    return render_template('registration.html')

@app.route('/my_room')
def my_room():
    return render_template('my_room.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT username FROM students WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()

        if not user:
            error = "Username does not exist."
        else:
            flash("User found! You can reset your password.", "success")
            return redirect(url_for('reset_password', username=username))

    return render_template('forgot_password.html', error=error)

@app.route('/reset_password/<username>', methods=['GET', 'POST'])
def reset_password(username):
    error = None
    if request.method == 'POST':
        new_password = request.form['password']
        hashed_pwd = generate_password_hash(new_password)

        cur = mysql.connection.cursor()
        cur.execute("UPDATE students SET password=%s WHERE username=%s", (hashed_pwd, username))
        mysql.connection.commit()
        cur.close()

        flash("Password updated successfully!", "success")
        return redirect(url_for('login'))

    return render_template('reset_password.html', username=username, error=error)

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("Logged out successfully!", "success")
    return redirect(url_for('login'))

if __name__ == "__main__":
    print("All registered endpoints:")
    for rule in app.url_map.iter_rules():
        print(rule.endpoint, "->", rule)
    app.run(debug=True)
