from flask import Flask, render_template, url_for, redirect, session, request, get_flashed_messages, flash
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime

import pymongo

'''
TODO:
charity page for individual charities

'''

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super secret key' #this is for the sessions

bcrypt = Bcrypt(app)

client = MongoClient()
db = client.Charity_Tracker
users = db.users
charities = db.charities
donations = db.donations

@app.route('/')
def index():
    return render_template("index.html", charities=charities.find())


@app.route('/profile')
def profile():
    username = session.get("username")
    if username != None:
        user = users.find_one({'username':session.get('username')})
        charities_list = charities.find().sort('name', pymongo.ASCENDING)
        print(user)
        user_donations = donations.find({'donator_id':user['_id']})
        return render_template("profile.html", user=user, charities=charities_list, donations=user_donations)
    else:
        return redirect(url_for("login"))

@app.route('/profile', methods=['POST'])
def profile_form():
    charity_id = request.form.get('chosen-charity')
    money = request.form.get('money')
    user = users.find_one({'username':session.get('username')})

    donation = {
        'amount':float(money),
        'donator_id':user['_id'],
        'charity_id':charity_id,
        'created':datetime.datetime.utcnow()
    }
    donations.insert_one(donation)

    return redirect(url_for('profile'))


@app.route('/logout')
def logout():
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
        print("Found user")
        print(found_user)


        if bcrypt.check_password_hash(found_user['password'], password):
            print("Logged in")
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

    session["username"] = user['username']
    session["password"] = user['password']

    return redirect(url_for("index"))


@app.route('/admin')
def admin():
    username = session.get('username')
    print(f'{username} tried to access admin...')
    if username != None:
        if username == 'admin':
            return render_template("admin.html", users=users.find(), charities=charities.find(), donations=donations.find())
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


@app.route('/charity/<id>')
def charity(id):
    charity = charities.find_one({'_id':ObjectId(id)})
    if charity:
        found_donations = donations.find({'charity_id':charity['_id']})
        print(found_donations)
        return render_template('charity.html', charity=charity, donations=found_donations)
    else:
        return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)