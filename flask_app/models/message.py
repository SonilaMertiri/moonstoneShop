from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash, request
class Message:
    DB = "myshop_schema"
    def __init__(self, data):
        self.id = data['id']
        self.full_name = data['full_name']
        self.message = data['message']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.user_id= data['user_id']


    @classmethod
    def create_message(cls,data):
        query="INSERT INTO messages (full_name, message, user_id) VALUES (%(full_name)s, %(message)s, %(user_id)s);"
        return connectToMySQL(cls.DB).query_db(query,data)
    

    @classmethod
    def get_all(cls):
        query= "SELECT * FROM messages;"
        results= connectToMySQL(cls.DB).query_db(query)
        messages=[]
        if results:
            for result in results:
                messages.append(result)
        return messages
    

    @staticmethod
    def validate_message(message):
        is_valid=True
        if len(message['full_name'])<2:
            flash("Please enter your name!" ,'full_nameRequired')
            is_valid=False
        if len(message['message'])<10:
            flash("Provide a valid message!" ,'messageRequired')
            is_valid=False
        return is_valid