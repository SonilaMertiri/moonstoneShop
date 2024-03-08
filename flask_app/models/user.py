from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
import re	# the regex module
# create a regular expression object that we'll use later   
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 

class User:
    DB = "myshop_schema"
    def __init__(self, data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.role = data['role']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']


    @classmethod
    def get_user_by_email(cls,data):
        query= 'SELECT * FROM users WHERE email= %(email)s;'
        result= connectToMySQL(cls.DB).query_db(query, data)
        if result:
            return result[0]
        return False
    
    @classmethod
    def get_user_by_id(cls,data):
        query= 'SELECT * FROM users WHERE id= %(id)s;'
        result= connectToMySQL(cls.DB).query_db(query, data)
        if result:
            return result[0]
        return False
    
    @classmethod
    def create(cls,data):
        query='INSERT INTO users (first_name, last_name, email, password) VALUES ( %(first_name)s, %(last_name)s, %(email)s, %(password)s);'
        return connectToMySQL(cls.DB).query_db(query, data)
    
    @classmethod
    def update(cls,data):
        query="UPDATE users SET first_name=%(first_name)s, last_name=%(last_name)s WHERE id=%(id)s;"
        return connectToMySQL(cls.DB).query_db(query, data)
    
    @classmethod
    def delete(cls,data):
        query="DELETE FROM users WHERE id=%(id)s;"
        return connectToMySQL(cls.DB).query_db(query, data)
    
    @staticmethod
    def validate_user(user):
        is_valid = True
        if not EMAIL_REGEX.match(user['email']): 
            flash("Invalid email address!", 'emailLogin')
            is_valid = False

        if len(user['password'])<3:
            flash("Password is required!", 'passwordLogin')
            is_valid = False
        return is_valid
    
    @staticmethod
    def validate_userRegister(user):
        is_valid = True
        if not EMAIL_REGEX.match(user['email']): 
            flash("Invalid email address!", 'emailRegister')
            is_valid = False

        if len(user['password'])<3:
            flash("Password is required!", 'passwordRegister')
            is_valid = False
        if len(user['first_name'])<1:
            flash("First name is required!", 'nameRegister')
            is_valid = False
        if len(user['last_name'])<1:
            flash("Last name is required!", 'lastNameRegister')
            is_valid = False
        return is_valid
    
    #do bejme validate user update
    
    @staticmethod
    def validate_user_update(user):
        is_valid = True
        if len(user['first_name'])<1:
            flash("First name is required!", 'nameRegister')
            is_valid = False
        if len(user['last_name'])<1:
            flash("Last name is required!", 'lastNameRegister')
            is_valid = False
        return is_valid
    


    # metodat per paypal
    @classmethod
    def createPayment(cls,data):
        query = "INSERT INTO payments (amount, paymentDate, status, user_id, item_id) VALUES (%(amount)s, NOW(), %(status)s, %(user_id)s, %(item_id)s);"
        return connectToMySQL(cls.DB).query_db(query, data)
    
    @classmethod
    def get_allUserPayments(cls, data):
        query = "SELECT * FROM payments where user_id = %(id)s;"
        results = connectToMySQL(cls.DB).query_db(query, data)
        payments = []
        if results:
            for pay in results:
                payments.append(pay)
        return payments