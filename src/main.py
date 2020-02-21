"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os

from flask import Flask, request, jsonify, url_for, make_response
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from models import db
from models import User
from models import Todo
from functools import wraps
import jwt
import datetime
import uuid

from werkzeug.security import generate_password_hash, check_password_hash

#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if "x-access-token" in request.headers:
            token = request.headers["x-access-token"]

        if not token:
            return jsonify({'message' : "Token is missing!"}), 401

        try:
            data = jwt.decode(token, 'secret')
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message': "Token is invalid"}), 401
        return f(current_user, *args, **kwargs)
    return decorated


# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@app.route("/", methods=["GET"])
def get_sitemap():
    return generate_sitemap(app)

@app.route("/user", methods=["GET"])
@token_required
def get_all_users(current_user):

    if not current_user.admin:
        return jsonify({"message" : "Cannot perform that function!"})

    users = User.query.all()
    output = []
    for user in users:
        user_data = {}
        user_data["public_id"] = user.public_id
        user_data["name"] = user.name
        user_data["password"] = user.password
        user_data["admin"] = user.admin
        output.append(user_data)

    return jsonify({"users" : output})

@app.route("/user/<public_id>", methods=["GET"])
@token_required
def get_one_user(current_user, public_id):

    if not current_user.admin:
        return jsonify({"message" : "Cannot perform that function!"})

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({"message" : "No user found!"})
    
    user_data = {}
    user_data["public_id"] = user.public_id
    user_data["name"] = user.name
    user_data["password"] = user.password
    user_data["admin"] = user.admin

    return jsonify({"user" : user_data})

@app.route("/user", methods=["POST"])
@token_required
def create_user(current_user):

    if not current_user.admin:
        return jsonify({"message" : "Cannot perform that function!"})

    data = request.get_json()
    hashed_password = generate_password_hash(data["password"], method="sha256")
    new_user = User(public_id=str(uuid.uuid4()), name=data["name"], password=hashed_password, admin=False)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message":"New User Created!"})

@app.route("/user/<public_id>", methods=["PUT"])
@token_required
def promote_user(current_user, public_id):

    if not current_user.admin:
        return jsonify({"message" : "Cannot perform that function!"})

    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({"message" : "No user found!"})
    user.admin = True
    db.session.commit()
    return jsonify({"message" : "The User has been promoted to Admin!"})    

@app.route("/user/<public_id>", methods=["DELETE"])
@token_required
def delete_user(current_user, public_id):

    if not current_user.admin:
        return jsonify({"message" : "Cannot perform that function!"})

    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({"message" : "No user found!"})
    
    db.session.delete(user)
    db.session.commit()

    return jsonify({"message" : "The user has been Deleted forever!"})
@app.route("/login")
def login():
    
    auth = request.authorization
    if not auth or not auth.username or not auth.password:  
        return make_response("Could not verify", 401, {"WWW-Authenticate" : "Basic realm='Login required!'" })

    user = User.query.filter_by(name=auth.username).first()

    if not user:
        return make_response("Could not verify", 401, {"WWW-Authenticate" : "Basic realm='Login required!'" })
        
    if check_password_hash(user.password, auth.password):
        token = jwt.encode({"public_id" : user.public_id, "exp" : datetime.datetime.utcnow() + datetime.timedelta(minutes=15)},  'secret')
        return jsonify({"token": token.decode("UTF-8")})

    return make_response("Could not verify", 401, {"WWW-Authenticate" : "Basic realm='Login required!'" })

@app.route("/todo", methods=["GET"])
@token_required
def get_all_todos(current_user):
    todos = Todo.query.filter_by(user_id=current_user.id).all()
    output = []

    for todo in todos:
        todo_data = {}
        todo_data["id"] = todo.id
        todo_data["text"] = todo.text
        todo_data["complete"] = todo.complete
        output.append(todo_data)
    return jsonify({"todos": output})

@app.route("/todo/<todo_id>", methods=["GET"])
@token_required
def get_one_todo(current_user, todo_id):
    todo = Todo.query.filter_by(id=todo_id, user_id=current_user.id).first()

    if not todo:
        return jsonify({"message" : "No such Todo found"})
    
    todo_data = {}
    todo_data["id"] = todo.id
    todo_data["text"] = todo.text
    todo_data["complete"] = todo.complete

    return jsonify(todo_data)

@app.route("/todo", methods=["POST"])
@token_required
def create_todo(current_user):
    data = request.get_json()
    
    new_todo = Todo(text=data["text"], complete=False, user_id=current_user.id)
    db.session.add(new_todo)
    db.session.commit()

    return jsonify({"message" : "Todo created!"})

@app.route("/todo/<todo_id>", methods=["PUT"])
@token_required
def complete_todo(current_user, todo_id):
    todo = Todo.query.filter_by(id=todo_id, user_id=current_user.id).first()

    if not todo:
        return jsonify({"message" : "No such Todo found"})

    todo.complete = True
    db.session.commit()

    return jsonify({"message" : "Todo Marked completed =) Well done!"})

@app.route("/todo/<todo_id>", methods=["DELETE"])
@token_required
def delete_todo(current_user, todo_id):
    todo = Todo.query.filter_by(id=todo_id, user_id=current_user.id).first()

    if not todo:
        return jsonify({"message" : "No such Todo found"})

    db.session.delete(todo)
    db.session.commit()

    return jsonify ({"message" : "Successfully deleted the Todo item! Great!"})



# # generate sitemap with all your endpoints
# @app.route('/')
# def sitemap():
#     return generate_sitemap(app)

# @app.route('/hello', methods=['POST', 'GET'])
# def handle_hello():

#     response_body = {
#         "hello": "world"
#     }

#     return jsonify(response_body), 200

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
