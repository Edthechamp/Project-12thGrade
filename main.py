from flask import Flask, jsonify, request, redirect, url_for, render_template
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import sqlite3
import uuid
from flask_socketio import SocketIO, emit, join_room, leave_room, send

from objects import User, Room

app = Flask(__name__)
socketio=SocketIO(app)
app.secret_key="verysecret"

login_manager = LoginManager()
login_manager.init_app(app)

conn=sqlite3.connect("database.db")
c=conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
)
"""
)

c.execute("""
CREATE TABLE IF NOT EXISTS rooms (
            roomID TEXT UNIQUE NOT NULL
)
""")
c.execute("""
CREATE TABLE IF NOT EXISTS messages (
            roomID TEXT NOT NULL,
            username TEXT NOT NULL,
            message TEXT NOT NULL,
            FOREIGN KEY(roomID) REFERENCES rooms(roomID)
)
""")


conn.close()

###!! SIGNUP AND LOGIN SYSTEM !!###

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT username, password FROM users WHERE username=?",(user_id,))
    row = c.fetchone()
    conn.close()

    if row:
        return User(row[0],row[1])
    return None

@app.route("/")
def home():
    if current_user.is_authenticated:
        return render_template("home.html", user=current_user.get_id())
    return redirect("/signup")


@app.route("/signup")
def signup():
    #display signup window, where username and password must be entered, with button "signup"
    return open("templates/signup.html").read()

@app.route("/signup/entered",methods=["POST"])
def createAccount():
    username = request.form.get("username")
    password = request.form.get("password")

    newUser = User(username,password)

    #TODO: add to databse for permanent storage

    conn=sqlite3.connect("database.db")
    c= conn.cursor()
    try:
        c.execute("INSERT INTO users (username,password) VALUES (?,?)",(username,password))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return "username not available",400
    conn.close()

    #TODO maybe sometime add email verification if easy api available

    login_user(newUser)
    return redirect("/")

@app.route("/login")
def tryLogin():
    return open("templates/login.html").read()

@app.route("/login/entered",methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    print("attempting login with: ", username,password)

    conn = sqlite3.connect("database.db")
    c= conn.cursor()
    print("database opem")
    c.execute("SELECT * FROM users WHERE username=? AND password=?",(username,password))
    row = c.fetchone()
    conn.close()
    if not row:
        print("user ", username, " does not exist")
        return "Invalid Username or Password",401


    print("got: ", row)

    user = User(username,password)
    print("created user object")
    login_user(user)
    print("user logged in with flask_login")

    return redirect("/")


###!! CHAT ROOM FUNCTIONALLITY !!###
openRooms = {}


@app.route("/Room/create")
def roomCreate():
    randomID = str(uuid.uuid4())[:6]
    while randomID in openRooms.keys(): 
        randomID=str(uuid.uuid4())[:6]
    openRooms[randomID] = Room(randomID)

    #add to db
    conn = sqlite3.connect('database.db')
    c=conn.cursor()
    c.execute(" INSERT INTO rooms (roomID) VALUES (?)",(randomID,))
    conn.commit()
    conn.close()

    #redirect, lai user kurs creato room ari tiek ielikts jaunaja room
    return redirect(url_for("joinRoom",roomID=randomID))


@app.route("/Room/join",  methods=["POST"])
def passToJoin():
    roomID = request.form.get("roomID")
    return redirect(url_for("joinRoom",roomID=roomID))



@app.route("/Room/join/<roomID>")
def joinRoom(roomID):
    if not current_user.is_authenticated:
        return redirect("/signup")
    
    username=current_user.get_id()

    if roomID in openRooms.keys():
        openRooms[roomID].userJoined(username)
        return render_template("chat.html",roomid=roomID,username=username)
    
    #ja tiek seit tad room obj nav in memory, pachekojam vai ir database
    conn = sqlite3.connect("database.db")
    c=conn.cursor()

    c.execute("SELECT * FROM rooms WHERE roomID=?",(roomID,))
    row=c.fetchone()
    conn.close()

    if not row:
        #nav ari database
        return redirect("/")
    
    openRooms[roomID] = Room(roomID)
    openRooms[roomID].userJoined(username)

    #load previous messages vel
    return render_template("chat.html",roomid=roomID,username=username)




##socket io functions:

@socketio.on("join")
def socketInit(data):
    if not current_user.is_authenticated:
        emit("unauthorized", {"msg": "You must log in first"})
        return
    
    join_room(data['room'])
    print(current_user.get_id(), "has joined the room: ", data['room'])

    with sqlite3.connect("database.db") as conn:
        c = conn.cursor()
        c.execute("SELECT username, message FROM messages WHERE roomID=? ORDER BY rowid ASC", (data['room'],))
        past_messages = c.fetchall()

    for user, text in past_messages:
        emit("new_message", {"user": user, "text": text})



    emit("new_message", {"user": current_user.get_id(), "text": "has joined the room"}, room=data["room"])



@socketio.on("send_message")
def transferMsg(data):

    conn = sqlite3.connect('database.db')
    c=conn.cursor()
    c.execute("INSERT INTO messages (roomID,username,message) VALUES (?,?,?)",(data["room"],current_user.get_id(),data["text"]))
    conn.commit()
    conn.close()

    emit("new_message",{"user":current_user.get_id(),"text":data["text"]},room=data['room'])
    

@socketio.on("leave")
def userLeave(room):
    emit("new_message",{"user":current_user.get_id(),"text":"left the chat"},room=room)


### custom "/" commands


socketio.run(app, debug=True)
