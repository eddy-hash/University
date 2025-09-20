from flask import Flask, request, session, render_template, redirect, url_for
from flask_mysqldb import MySQL
import MySQLdb.cursors
from werkzeug.security import generate_password_hash, check_password_hash

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

@app.route('/')
def home():
    if 'username' in session:
        return render_template('base.html', username=session['username'])
    return redirect(url_for('login'))



@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM students WHERE username=%s", (session['username'],))
    user = cur.fetchone()
    cur.close()

    if request.method == 'POST':
        phone = request.form['phone']
        nida = request.form['nida']
        password = request.form['password']
        image = request.files.get('profile_image')

        update_query = "UPDATE students SET phone=%s, nida=%s"
        params = [phone, nida]

        
        if password:
            from werkzeug.security import generate_password_hash
            hashed = generate_password_hash(password)
            update_query += ", password=%s"
            params.append(hashed)

        if image and image.filename != '':
            image_path = "static/images/" + image.filename
            image.save(image_path)
            update_query += ", profile_image=%s"
            params.append(image.filename)

        update_query += " WHERE username=%s"
        params.append(session['username'])

        cur = mysql.connection.cursor()
        cur.execute(update_query, params)
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('dashboard'))

    return render_template('dashboard.html', user=user)


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
        hashed_pwd = generate_password_hash(pwd)  # 🔒 Hash password

        cur = mysql.connection.cursor()
        try:
            cur.execute(
                "INSERT INTO students (username, password) VALUES (%s, %s)",
                (username, hashed_pwd)
            )
            mysql.connection.commit()
        except MySQLdb.IntegrityError:
            error = "Username already exists"
        cur.close()

        if not error:
            return redirect(url_for('login'))

    return render_template('register.html', error=error)

@app.route('/pex_requests', methods=['GET', 'POST'])
@app.route('/pex_requests', methods=['GET', 'POST'])
def pex_requests():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == 'POST':
        username = request.form['username']
        student_id = request.form['student_id']
        reason = request.form['reason']
        details = request.form['details']

        cur.execute(
            "INSERT INTO permission_requests (username, student_id, reason, details, status) VALUES (%s, %s, %s, %s, %s)",
            (username, student_id, reason, details, 'Pending')
        )
        mysql.connection.commit()

   
    cur.execute("SELECT * FROM permission_requests")  
    requests = cur.fetchall()
    cur.close()

    return render_template('permission.html', requests=requests)


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
    message = None

    if request.method == 'POST':
        username = request.form['username']

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT username FROM students WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()

        if not user:
            error = "Username does not exist."
        else:
            message = "User found! You can reset your password."
            return redirect(url_for('reset_password', username=username))

    return render_template('forgot_password.html', error=error, message=message)


@app.route('/reset_password/<username>', methods=['GET', 'POST'])
def reset_password(username):
    error = None
    success = None

    if request.method == 'POST':
        new_password = request.form['password']
        hashed_pwd = generate_password_hash(new_password)

        cur = mysql.connection.cursor()
        cur.execute("UPDATE students SET password=%s WHERE username=%s", (hashed_pwd, username))
        mysql.connection.commit()
        cur.close()

        success = "Password updated successfully!"
        return redirect(url_for('login'))

    return render_template('reset_password.html', username=username, error=error, success=success)


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


if __name__ == "__main__":
    print("All registered endpoints:")
    for rule in app.url_map.iter_rules():
        print(rule.endpoint, "->", rule)
    app.run(debug=True)
