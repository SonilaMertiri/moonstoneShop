from flask_app import app
#here we import our controllers
from flask_app.controllers import items, users, messages

if __name__ == "__main__":
    app.run(debug=True)