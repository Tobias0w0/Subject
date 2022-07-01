import uuid,os,hashlib,pymysql
#import
from flask import Flask,render_template,request,redirect,session,abort,flash,jsonify 
app = Flask(__name__)

# Register the setup page and import create_connection()
from utils import create_connection, setup
app.register_blueprint(setup)


@app.before_request
def restrict():
    restricted_pages=['list_user','view_user','edit_user','select_user', 'dashboard']
    if 'logged_in' not in session and request.endpoint in restricted_pages:
        return redirect('/register')
        
@app.route('/')
def home():
    return render_template("index.html")

# TODO: Add a '/register' (add_user) route that uses INSERT
@app.route('/register', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':

        password = request.form['password']
        encrypted_password = hashlib.sha256(password.encode()).hexdigest()

        avatar_image = request.files["avatar"]
        ext= os.path.splitext(avatar_image.filename) [1]
        avatar_filename = str(uuid.uuid4())[:8] + ext
        avatar_image.save("static/images/" + avatar_filename)

        with create_connection() as connection:
            with connection.cursor() as cursor:
                sql = """INSERT INTO users (first_name, last_name, email, password, avatar) VALUES (%s, %s, %s, %s, %s)"""

                vaules=(request.formjust['first_name'],
                        request.form['last_name'],
                        request.form['email'],
                        encrypted_password,
                        avatar_filename)

                try:
                    cursor.execute(sql, vaules)
                    connection.commit()
                except pymysql.err.IntergrityError:
                        flash('email has been taken')
                        return redirect('/register')
                return redirect('/')
    return render_template('users_add.html')

# TODO: Add a '/dashboard' (list_users) route that uses SELECT

@app.route('/dashboard')
def list_user():

    with create_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            result = cursor.fetchall()
    return render_template('user_list.html', result=result)


#TODO: Add a '/profile' (view_user) route that uses SELECT
@app.route('/view')

def view_user():
    with create_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM user")

            result = cursor.fetchall()
    return render_template('user_view.html', result=result)


# TODO: Add a '/select_user' route that uses DELETE

@app.route('/select')
def select_user():
    with create_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM user WHERE id=%s", request.args['id'])
            connection.commit()
            session['Yr11_Subjects'] = result['Yr11_Subjects']
            session['id'] = result['id']
            return redirect('/subject')



# TODO: Add an '/edit_user' route that uses UPDATE
@app.route('/edit', methods=['GET', 'POST'])

def edit_user():

    #admin users are allowed, users with the right id are allowed, everyone else sees error 404
    if session['role'] != 'admin' and str(session['id']) !=request.args['id']:
        return abort(404)

    if request.method == 'POST':

        if request.files['avatar'].filename:
            avatar_image = request.files["avatar"]
            ext= os.path.splitext(avatar_image.filename)[1]
            avatar_filename = str(uuid.uuid4())[:8] + ext
            avatar_image.save("static/images/" + avatar_filename)
        if request.form['old_avatar'] != 'None':
            os.remove("static/images/" + request.form['old_avatar'])
        else:
            avatar_filename = request.form['old_avatar']

        with create_connection() as connection:
            with connection.cursor() as cursor:
                sql = """INSERT INTO users (first_name, last_name, email, password, avatar) VALUES (%s, %s, %s, %s)"""


                vaules=(request.form['first_name'],
                        request.form['last_name'],
                        request.form['email'],
                        request.form['password'],
                        avatar_filename,
                        request.form['id']
                        )
                cursor.execute(sql,vaules)
                connection.commit()
        return redirect('/view?id=' + request.form['id'])
    else:
        with create_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE id = %s", request.args['id'])
                result = cursor.fetchone()
                return render_template('users_edit.html', result=result)


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST': #LOGIN

        #encrypt password
        password = request.form['password']
        encrypted_password = hashlib.sha256(password.encode()).hexdigest()
            

        with create_connection() as connection:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM users WHERE email=%s AND password=%s"
                values = (request.form["email"], encrypted_password)

                cursor.execute(sql,values)
                result = cursor.fetchone()

            if result:

                session['login'] = True
                return redirect('/subject')
                return "you are logged in as " + result['first_name']
            else:
                return redirect('/login')
    else:
        return render_template('users_login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

 # email taken
@app.route('/checkmail')
def check_email():
     with create_connection() as connection: 
        with connection.cursor() as cursor:
          sql = "SELECT * FROM users WHERE email=#s" 
          vaules = (request.args['email'])

          cusor.execute(sql,vaules)
          result = cursor.fecthtone()

@app.route('/movies')
def movies():
    if session['role'] !='admin':
        return redirect('/')
    with create_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            result = cursor.fetchall()
    return render_template('moviesID.html', result=result )

@app.route('/subject')
def subject():
    with create_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM tobheyes_databass.subject_selection")
            result = cursor.fetchall()
    return render_template('subject_selection.html', result=result )

if __name__ == '__main__':
    import os

    # This is required to allow flashing messages. We will cover this later.
    app.secret_key = os.urandom(32)

    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError: 
        PORT = 5555
    app.run(HOST, PORT, debug=True)