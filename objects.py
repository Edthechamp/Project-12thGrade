from flask_login import UserMixin

class User(UserMixin):
    #defines the user, stored in database table users 
    def __init__(self,username,password):
        self.username=username
        self.__password=password

    def get_id(self):
        #flask_login parasti strada ar integer IDs, tpe overwritoju UserMixin class lai returno vnk username pagaidam
        return self.username


    
class Room():
    def __init__(self,roomid):
        self.__roomID = roomid
        self.messages = []
        self.usersON = []

    def userJoined(self,username):
        if username not in self.usersON:
            self.usersON.append(username)

    def userLeft(self,username):
        if username in self.usersON:
            self.usersON.remove(username)

    def addMessage(self,user,msg):
        self.messages.append([user,msg])

    def getMessages(self):
        return self.messages