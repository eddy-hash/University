from flask import Flask, request, session, render_template, redirect, url_for, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
from werkzeug.security import generate_password_hash, check_password_hash
import os
import uuid

app = Flask(__name__)
app.secret_key = "supersecretkey"

app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Eddy@2023'
app.config['MYSQL_DB'] = 'students'
app.config['MYSQL_PORT'] = 3307

mysql = MySQL(app)

def get_logged_in_user():
    if 'username' in session:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM students WHERE username=%s", (session['username'],))
        user = cur.fetchone()
        cur.close()
        return user
    return None

@app.route('/')
def home():
    user = get_logged_in_user()
    if user:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        pwd = request.form['password']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM students WHERE username=%s", (username,))
        user = cur.fetchone()
        cur.close()
        if not user:
            error = "Username does not exist"
        elif not check_password_hash(user['password'], pwd):
            error = "Incorrect password"
        else:
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("Logged out successfully!", "success")
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        pwd = request.form['password']
        email = request.form['email']
        hashed_pwd = generate_password_hash(pwd)
        cur = mysql.connection.cursor()
        try:
            cur.execute("INSERT INTO students (username, password, email) VALUES (%s, %s, %s)",
                        (username, hashed_pwd, email))
            mysql.connection.commit()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for('login'))
        except MySQLdb.IntegrityError:
            error = "Username already exists"
        cur.close()
    return render_template('register.html', error=error)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    user = get_logged_in_user()
    if not user:
        return redirect(url_for('login'))
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        dob = request.form.get('dob')
        gender = request.form.get('gender')
        phone = request.form.get('phone')
        nida = request.form.get('nida')
        email = request.form.get('email')
        address = request.form.get('address')
        program = request.form.get('program')
        department = request.form.get('department')
        year = request.form.get('year')
        guardian_name = request.form.get('guardian_name')
        guardian_phone = request.form.get('guardian_phone')
        password = request.form.get('password')
        image = request.files.get('profile_image')
        query = "UPDATE students SET full_name=%s, dob=%s, gender=%s, phone=%s, nida=%s, email=%s, address=%s, program=%s, department=%s, year=%s, guardian_name=%s, guardian_phone=%s"
        params = [full_name, dob, gender, phone, nida, email, address, program, department, year, guardian_name, guardian_phone]
        if password:
            hashed = generate_password_hash(password)
            query += ", password=%s"
            params.append(hashed)
        if image and image.filename != '':
            os.makedirs("static/images", exist_ok=True)
            filename = str(uuid.uuid4()) + "_" + image.filename
            image.save(os.path.join("static/images", filename))
            query += ", profile_image=%s"
            params.append(filename)
        query += " WHERE username=%s"
        params.append(user['username'])
        cur = mysql.connection.cursor()
        cur.execute(query, params)
        mysql.connection.commit()
        cur.close()
        flash("Profile updated successfully!", "success")
        return redirect(url_for('dashboard'))
    return render_template('dashboard.html', user=user)

@app.route('/update_account', methods=['GET', 'POST'])
def update_account():
    user = get_logged_in_user()
    if not user:
        flash("You must log in first.", "error")
        return redirect(url_for('login'))
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        new_username = request.form.get('username')
        email = request.form.get('email')
        phone = request.form.get('phone')
        program = request.form.get('program')
        department = request.form.get('department')
        password = request.form.get('password')
        profile_image = request.files.get('profile_image')
        UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'images')
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        image_filename = user['profile_image']
        if profile_image and profile_image.filename != '':
            filename = str(uuid.uuid4()) + "_" + profile_image.filename
            profile_image.save(os.path.join(UPLOAD_FOLDER, filename))
            image_filename = filename
        params = [full_name, new_username, email, phone, program, department, image_filename]
        query = "UPDATE students SET full_name=%s, username=%s, email=%s, phone=%s, program=%s, department=%s, profile_image=%s"
        if password:
            hashed_pwd = generate_password_hash(password)
            query += ", password=%s"
            params.append(hashed_pwd)
        query += " WHERE username=%s"
        params.append(user['username'])
        cur = mysql.connection.cursor()
        cur.execute(query, params)
        mysql.connection.commit()
        cur.close()
        session['username'] = new_username
        flash("Profile updated successfully!", "success")
        return redirect(url_for('update_account'))
    return render_template('registration.html', user=user)

@app.route('/pex_requests', methods=['GET', 'POST'])
def pex_requests():
    user = get_logged_in_user()
    if not user:
        return redirect(url_for('login'))
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        reason = request.form.get('reason')
        details = request.form.get('details')
        if reason and details:
            cur.execute("INSERT INTO permission_requests (username, student_id, reason, details, status) VALUES (%s,%s,%s,%s,%s)",
                        (user['username'], user['student_id'], reason, details, 'Pending'))
            mysql.connection.commit()
    cur.execute("SELECT * FROM permission_requests WHERE student_id=%s ORDER BY created_at DESC", (user['student_id'],))
    requests = cur.fetchall()
    cur.close()
    return render_template('permission.html', user=user, user_requests=requests)

@app.route('/delete_permission/<int:request_id>', methods=['POST'])
def delete_permission(request_id):
    user = get_logged_in_user()
    if not user:
        return redirect(url_for('login'))
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM permission_requests WHERE id=%s", (request_id,))
    mysql.connection.commit()
    cur.close()
    flash("Permission request deleted successfully!", "success")
    return redirect(url_for('pex_requests'))

@app.route('/select_courses', methods=['GET', 'POST'])
def select_courses():
    user = get_logged_in_user()
    if not user:
        flash("You must log in first.", "error")
        return redirect(url_for('login'))
    if request.method == 'POST':
        programming = request.form.get('programming')
        management = request.form.getlist('management')
        if not programming:
            flash("Please select 1 programming course.", "error")
            return redirect(url_for('select_courses'))
        if len(management) != 3:
            flash("Please select exactly 3 management courses.", "error")
            return redirect(url_for('select_courses'))
        selected_courses = programming + ", " + ", ".join(management)
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO student_courses (username, courses) VALUES (%s, %s)", (user['username'], selected_courses))
        mysql.connection.commit()
        cur.close()
        flash("Courses submitted successfully!", "success")
        return redirect(url_for('select_courses'))
    return render_template('course.html', user=user)

@app.route('/change_password', methods=['POST', 'GET'])
def change_password():
    user = get_logged_in_user()
    if not user:
        flash("You must log in first.", "error")
        return redirect(url_for('login'))
    error = None
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        if not check_password_hash(user['password'], old_password):
            error = "Old password is incorrect."
        elif new_password != confirm_password:
            error = "New passwords do not match."
        elif len(new_password) < 8:
            error = "Password must be at least 8 characters."
        else:
            hashed = generate_password_hash(new_password)
            cur = mysql.connection.cursor()
            cur.execute("UPDATE students SET password=%s WHERE username=%s", (hashed, user['username']))
            mysql.connection.commit()
            cur.close()
            flash("Password updated successfully!", "success")
            return redirect(url_for('change_password'))
    return render_template('change_password.html', user=user, error=error)

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT username FROM students WHERE username=%s", (username,))
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
        new_password = request.form.get['password']
        confirm_password = request.form.get['confirm_password']
        if new_password != confirm_password:
            error = "Passwords do not match."
        else:
            hashed = generate_password_hash(new_password)
            cur = mysql.connection.cursor()
            cur.execute("UPDATE students SET password=%s WHERE username=%s", (hashed, username))
            mysql.connection.commit()
            cur.close()
            flash("Password updated successfully!", "success")
            return redirect(url_for('login'))
    return render_template('reset_password.html', username=username, error=error)

@app.route('/statements')
def statements():
    user = get_logged_in_user()
    if not user:
        return redirect(url_for('login'))
    return render_template('statements.html', user=user)

if __name__ == "__main__":
    app.run(debug=True)
