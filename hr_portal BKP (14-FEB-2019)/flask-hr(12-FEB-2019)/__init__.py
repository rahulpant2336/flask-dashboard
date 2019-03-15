from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import yaml
from flask_user import roles_required
import hashlib
import datetime

app = Flask(__name__)
db = yaml.load(open('db.yaml'))
app.secret_key = '3242353645646'

app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql = MySQL(app)



@app.route('/')
def Index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT  job_category FROM jobs")
    data = cur.fetchall()
    cur.close()
    return render_template('register.html', jobs=data)



@app.route('/register', methods = ['POST'])
def insert():

    if request.method == "POST":
        first_name = str(request.form['first_name'])
        middle_name = str(request.form['middle_name'])
        last_name = str(request.form['last_name'])
        email = str(request.form['email'])
        phone = request.form['phone']
        position_applied = str(request.form['position_applied'])
        password = hashlib.md5(request.form['password'].encode())
        password_save = password.hexdigest()
        role = 2
        confirm_password = hashlib.md5(request.form['confirm_password'].encode())
        confirm_password_save = confirm_password.hexdigest()
        cur = mysql.connection.cursor()
        params = [email]
        count = cur.execute('select * from students where email=%s', params)
        if count == 0:
            cur.execute("INSERT INTO students (first_name, middle_name, last_name, email, phone, position_applied, password, confirm_password, role) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (first_name, middle_name, last_name, email, phone, position_applied, password_save, confirm_password_save, role))
            mysql.connection.commit()
            flash("Registration success!!!")
            return render_template('register.html', success="success")
        else:
            flash("Email Already Registered!!!")
            return render_template('register.html', success="error")



@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    cur = mysql.connection.cursor()
    cur.execute("SELECT  * FROM students")
    data = cur.fetchall()
    cur.close()
    if 'username' in session:
        username = session['username']
        return render_template('evalution-form.html', now=datetime.datetime.now(), students=data)
    else:
        return redirect(url_for('login'))




def check_password(hashed_password, user_password):
    return hashed_password == hashlib.md5(user_password.encode()).hexdigest()

def validate(username, password):

    completion = False

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM students")
    data = cur.fetchall()
    for row in data:
        dbUser = row[4]
        dbPass = row[7]
        if dbUser==username:
            completion=check_password(dbPass, password)

    return completion





@app.route('/login-check', methods = ['POST'])
def checkLogin():
    error = None
    if request.method == 'POST':
        error = None
        email = str(request.form['email'])
        password = str(request.form['password'])
        completion = validate(email, password)
        if completion ==False:
            flash("Invalid Credentials. Please try again.")
            return render_template('login.html')
        else:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM students WHERE email ='"+email+"'")
            data = cur.fetchall()
            session['username'] = data
            return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))




@app.route('/update',methods=['POST','GET'])
def update():

    if request.method == 'POST':
        id_data = request.form['id']
        first_name = request.form['first_name']
        middle_name = request.form['middle_name']
        last_name = request.form['last_name']
        phone = request.form['phone']
        cur = mysql.connection.cursor()
        cur.execute("""
               UPDATE students
               SET first_name=%s, middle_name=%s, last_name=%s, phone=%s
               WHERE id=%s
            """, (first_name, middle_name, last_name, phone, id_data))
        flash("Record Updated Successfully")
        mysql.connection.commit()
        return redirect(url_for('dashboard'))


@app.route('/delete/<string:id_data>', methods = ['GET'])
def delete(id_data):
    flash("Record Has Been Deleted Successfully")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM students WHERE id=%s", (id_data,))
    mysql.connection.commit()
    return redirect(url_for('dashboard'))


@app.route('/my-profile')
def myProfile():
    return render_template("my-profile.html", now=datetime.datetime.now())


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")


@app.route('/questions-management')
def questionsManagement():
    return render_template("questions-management.html", now=datetime.datetime.now())

@app.route('/jobs-management')
def jobsManagement():
    cur = mysql.connection.cursor()
    cur.execute("SELECT  * FROM jobs")
    data = cur.fetchall()
    cur.close()
    if 'username' in session:
        username = session['username']
        return render_template('jobs-management.html', now=datetime.datetime.now(), students=data)
    else:
        return redirect(url_for('login'))

@app.route('/add-job')
def addJob():
    return render_template('add-job-form.html', now=datetime.datetime.now())

@app.route('/insert-job', methods = ['POST'])
def insertJob():

    if request.method == "POST":
        job_category = str(request.form['job_category'])
        status = str(request.form['status'])
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO jobs (job_category, status) VALUES (%s, %s)",
                        (job_category, status))
        mysql.connection.commit()
        flash("Job Added Successfully!!!")
        return redirect(url_for('addJob'))


@app.route('/update-job',methods=['POST'])
def updateJob():

    if request.method == 'POST':
        id_data = request.form['id']
        job_category = request.form['job_category']
        status = request.form['status']
        cur = mysql.connection.cursor()
        cur.execute("""
               UPDATE jobs
               SET job_category=%s, status=%s
               WHERE id=%s
            """, (job_category, status, id_data))
        flash("Job Updated Successfully")
        mysql.connection.commit()
        return redirect(url_for('jobsManagement'))


@app.route('/delete-job/<string:id_data>', methods = ['GET'])
def deleteJob(id_data):
    flash("Job Has Been Deleted Successfully")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM jobs WHERE id=%s", (id_data,))
    mysql.connection.commit()
    return redirect(url_for('jobsManagement'))




if __name__ == "__main__":
    app.run(debug=True)
