from flask_login import UserMixin

class User(UserMixin):
    #defines the user, stored in database table users 
    def __init__(self,username,password):
        self.username=username
        self.__password=password

    def get_id(self):
        #flask_login parasti strada ar integer IDs, tpe overwritoju UserMixin class lai returno vnk username pagaidam
        return self.username

    def login(self, entered_username,entered_password):
        pass

    def getData(self):
        return self.username,self.__password