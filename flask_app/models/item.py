from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash, request
class Item:
    DB = "myshop_schema"
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.description = data['description']
        self.image = data['image']
        self.price = data['price']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.user_id= data['user_id']


    @classmethod
    def create(cls,data):
        query="INSERT INTO items (name, description, image, price, user_id) VALUES (%(name)s, %(description)s, %(image)s, %(price)s, %(user_id)s);"
        return connectToMySQL(cls.DB).query_db(query,data)
    

    @classmethod
    def get_all(cls):
        query= "SELECT * FROM items;"
        results= connectToMySQL(cls.DB).query_db(query)
        items=[]
        if results:
            for result in results:
                items.append(result)
        return items
    
    #shikoje me kujdes kete ne kete menyre do shtojme comments/review
    @classmethod
    def get_item_by_id(cls, data):
        query = "SELECT * FROM items LEFT JOIN users on items.user_id = users.id WHERE items.id = %(id)s;"
        result = connectToMySQL(cls.DB).query_db(query, data)
        if result:
            comments = []

            query2 = "SELECT * FROM comments left join users on comments.user_id = users.id where comments.item_id = %(id)s;"
            result2 = connectToMySQL(cls.DB).query_db(query2, data)
            if result2:
                for comment in result2:
                    comments.append(comment)
            result[0]['comments'] = comments
            # query3 = "SELECT users.firstName, users.lastName FROM likes left join users on likes.user_id = users.id where likes.book_id = %(id)s;"
            # result3 = connectToMySQL(cls.DB).query_db(query3, data)
            # likes = []
            # if result3:
            #     for like in result3:
            #         likes.append(like)
            # result[0]['likes'] = likes
            return result[0]
        return False
    

    @classmethod
    def deleteItem(cls,data):
        query="DELETE FROM items WHERE id=%(id)s;"
        return connectToMySQL(cls.DB).query_db(query,data)
    
    @classmethod
    def update(cls,data):
        query="UPDATE items SET name= %(name)s, description= %(description)s, image= %(image)s, price= %(price)s WHERE items.id=%(id)s;"
        return connectToMySQL(cls.DB).query_db(query,data)
    


    @staticmethod
    def validate_Item(item):
        is_valid = True
        if len(item['name']) < 2:
            flash('Name should be more than two characters', 'nameItem')
            is_valid = False
        if len(item['description']) < 10:
            flash('Description should be more than 10 characters', 'descriptionItem')
            is_valid = False
        if not request.files.get('image'):
            flash('Your file is not uploaded', 'imageItem')
            is_valid = False
        if len(item['price']) < 1:
            flash('You should put a price for this item', 'priceItem')
            is_valid = False
        return is_valid

    
    @staticmethod
    def validate_item_update(item):
        is_valid= True
        if len(item['name'])<2:
            flash('Name should be more than two characters', 'nameItem')
            is_valid=False
        if len(item['description'])<10:
            flash('Description should be more than 10 characters', 'descriptionItem')
            is_valid=False
        if not request.files.get('image'):
            flash('Your file is not uploaded', 'imageItem')
            is_valid = False
        if len(item['price'])<1:
            flash('You should put a price for this item', 'priceItem')
            is_valid=False
        return is_valid
    


    # per Komentet ose review metodaaaaaaaaaaaaat
    @classmethod
    def create_comment(cls, data):
        query = "INSERT INTO comments (comment, comment_image, item_id, user_id) VALUES (%(comment)s, %(comment_image)s,  %(item_id)s, %(user_id)s);"
        return connectToMySQL(cls.DB).query_db(query, data)
    
    @classmethod
    def get_comment_by_id(cls, data):
        query = "SELECT * FROM comments WHERE comments.id = %(id)s;"
        result = connectToMySQL(cls.DB).query_db(query, data)
        if result:
            return result[0]  # Return the first row of the result
        return False
    
    @classmethod
    def update_comment(cls, data):
        query = "UPDATE comments SET comment = %(comment)s, comment_image = %(comment_image)s WHERE id = %(id)s;"
        return connectToMySQL(cls.DB).query_db(query, data)
    
    @classmethod
    def delete_comment(cls, data):
        query = "DELETE FROM comments WHERE id = %(id)s;"
        return connectToMySQL(cls.DB).query_db(query, data)
    
    @classmethod
    def delete_all_item_comments(cls, data):
        query ="DELETE FROM comments where comments.item_id = %(id)s;"
        return connectToMySQL(cls.DB).query_db(query, data)
    
    @staticmethod
    def validate_comment(comment):
        is_valid= True
        if len(comment['comment'])<2:
            flash('Enter your review above', 'commentReview')
            is_valid=False
        if not request.files.get('comment_image'):
            flash('Your file is not uploaded', 'imageReview')
            is_valid = False
        return is_valid
    
    @classmethod
    def best_seller(cls):
        query = "SELECT items.id, items.name, items.description, items.image, items.price, COUNT(*) AS total_sales FROM items INNER JOIN payments ON items.id = payments.item_id GROUP BY items.id HAVING total_sales > 4 ORDER BY total_sales DESC;"
        results = connectToMySQL(cls.DB).query_db(query)
        best_selling_items = []
        if results:
            for result in results:
                best_selling_items.append(result)
        return best_selling_items
