from flask import Flask, render_template, url_for, redirect, session, request
from pymongo import MongoClient
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super secret key' #this is for the sessions

client = MongoClient()
db = client.Charity_Tracker
users = db.users

@app.route('/')
def index():
    name = session.get("name")
    if name == None:
        name = "[pls login]"
    return render_template("index.html", name=name)
    
@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/login', methods=['POST'])
def login_form():
    username = request.form.get("username")
    password = request.form.get("password")
    
    found_user = users.find_one({"username": username, "password": password})
    if found_user:
        print("Found")
        session["name"] = found_user['name']
        session["username"] = found_user['username']
        return redirect(url_for("index"))
    else:
        print("Not Found")
        return redirect(url_for("login"))

@app.route('/signup')
def signup():
    return render_template("signup.html")

@app.route('/signup', methods=['POST'])
def signup_form():
    username = request.form.get("username")
    password = request.form.get("password")
    name = request.form.get("name")

    session["name"] = name
    session["username"] = username

    user = {
        'username':username,
        'password':password,
        'name':name,
        'created':datetime.datetime.utcnow()
    }
    users.insert(user)

    return redirect(url_for("index"))

@app.route('/admin')
def admin():
    return render_template("admin.html", users=users.find())

if __name__ == "__main__":
    app.run(debug=True)