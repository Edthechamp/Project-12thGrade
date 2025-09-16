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
    return "home, no login"


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
    #TODO maybe someday add email verification if easy api available

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
def chatCreate():
    randomID = str(uuid.uuid4())[:6]

    while randomID in openRooms.keys(): 
        randomID=str(uuid.uuid4())[:6]
    
    openRooms[randomID] = Room(randomID)

    #redirect, lai user kurs creato room ari tiek ielikts jaunaja room
    return redirect(url_for("joinRoom",roomID=randomID))

@app.route("/Room/join",  methods=["POST"])
def passToJoin():
    roomID = request.form.get("roomID")
    return redirect(url_for("joinRoom",roomID=roomID))

@app.route("/Room/join/<roomID>")
def joinRoom(roomID):
    username=current_user.get_id()
    openRooms[roomID].userJoined(username)
    return render_template("chat.html",roomid=roomID,username=username)

##socket io functions:

@socketio.on("join")
def socketInit(data):
    join_room(data['room'])
    print(current_user.get_id(), "has joined the room: ", data['room'])
    emit("new_message", {"user": current_user.get_id(), "text": "has joined the room"}, room=data["room"])

@socketio.on("send_message")
def transferMsg(data):
    emit("new_message",{"user":current_user.get_id(),"text":data["text"]},room=data['room'])
    

@socketio.on("leave")
def userLeave(room):
    emit("new_message",{"user":current_user.get_id(),"text":"left the chat"},room=room)

socketio.run(app, host="0.0.0.0", port=5000, debug=True)
