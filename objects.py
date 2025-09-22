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
    

    
class ZooGame:
    def __init__(self):
        self.__players={} #username:[characterOBJ]

    def joined(self,player,character):
        self.__players[player]=character
        
    def players(self):
        return self.__players

    #define animal class
    class Animal:
        def __init__(self,animaltype):
            self.__type=animaltype
            self.__energy=10
            self.__age=1
            self.x=100
            self.y=100

            if self.__type=="cow":
                self.__speed=2
                self.__maxAge=20
                self.__maxEnergy=200
                
            elif self.__type=="pig":
                self.__speed=4
                self.__maxAge=15
                self.__maxEnergy=150
               
            elif self.__type=="horse":
                self.__speed=10
                self.__maxAge=25
                self.__maxEnergy=80
              
            else:
                return "no animal "+ animaltype
                
        def position(self,new_x,new_y):
            #var ielikt kk backend checks lai cheko ka nav mahinacijas
            self.x = new_x
            self.y = new_y