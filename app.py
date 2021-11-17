from flask import Flask, render_template, url_for, redirect, session, request, get_flashed_messages, flash
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime

'''
TODO:
show all charities on main page 
profile page 
log donation on profile page 
charity page for individual charities
'''

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super secret key' #this is for the sessions

bcrypt = Bcrypt(app)

client = MongoClient()
db = client.Charity_Tracker
users = db.users
charities = db.charities

@app.route('/')
def index():
    name = session.get("name")
    return render_template("index.html", name=name)

@app.route('/profile')
def profile():
    name = session.get("name")
    if name != None:
        return render_template("profile.html")
    else:
        return redirect(url_for("login"))

@app.route('/logout')
def logout():
    session["name"] = None
    session["username"] = None
    session["password"] = None
    return redirect(url_for("login"))

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/login', methods=['POST'])
def login_form():
    username = request.form.get("username")
    password = request.form.get("password")
    #password_hash = bcrypt.generate_password_hash(password)
    
    found_user = users.find_one({"username": username})
    if found_user:
        print("Found")
        if bcrypt.check_password_hash(found_user['password'], password):
            session["name"] = found_user['name']
            session["username"] = found_user['username']
            session["password"] = found_user['password']
            return redirect(url_for("index"))
        else:
            flash("Incorrect Password")
            return redirect(url_for("login")) 
    else:
        print("Not Found")
        flash("User Not Found")
        return redirect(url_for("login"))

@app.route('/signup')
def signup():
    return render_template("signup.html")

@app.route('/signup', methods=['POST'])
def signup_form():
    username = request.form.get("username")
    password = request.form.get("password")
    password_hash = bcrypt.generate_password_hash(password)
    name = request.form.get("name")

    found_user = users.find_one({'username':username})
    if found_user:
        flash("User already exists")
        return redirect(url_for('signup'))
    
    user = {
        'username':username,
        'password':password_hash,
        'name':name,
        'created':datetime.datetime.utcnow()
    }
    users.insert(user)

    session["name"] = user['name']
    session["username"] = user['username']
    session["password"] = user['password']

    return redirect(url_for("index"))

@app.route('/admin')
def admin():
    username = session.get('username')
    print(f'{username} tried to access admin...')
    if username != None:
        if username == 'admin':
            return render_template("admin.html", users=users.find(), charities=charities.find())
        else:
            return render_template("profile.html")
    else:
        return redirect(url_for("login"))

@app.route('/admin', methods=['POST'])
def admin_form():
    
    charity = {
        'name':request.form.get('name'),
        'description':request.form.get('description'),
        'created':datetime.datetime.utcnow()
    }
    print(charity)
    charities.insert_one(charity)

    return redirect(url_for('admin'))

if __name__ == "__main__":
    app.run(debug=True)