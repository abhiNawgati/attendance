
#provode jwt token to flask app
#database queries 
# psql -h localhost postgres -U postgres
import datetime
from flask import Flask,request,jsonify
import jwt

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/postgres'
app.config['SECRET_KEY'] = 'secret_key'
db = SQLAlchemy(app)


class Users(db.Model):
    user_id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email_id = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    
    def __repr__(self):
        return '<User %r>' % self.name
    

@app.route('/user', methods=['POST'])
def add_user():
    name = request.json['name']
    email_id = request.json['email_id']
    password = request.json['password']
    
    new_user = Users(name=name, email_id=email_id, password=password)
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'New user created successfully!'})


def generate_jwt_token(email_id):
    payload = {
        'email_id': email_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
        'iat': datetime.datetime.utcnow()
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

@app.route("/signup", methods=['POST'])
def signup():
    name = request.json.get('name')
    email_id = request.json.get('email_id')
    password = request.json.get('password')

    user = Users.query.filter_by(email_id=email_id).first()
    if user:
        return jsonify({'error': 'Email already exists'}), 400
    
    new_user = Users(name=name, email_id=email_id, password=password)
    
    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    token = generate_jwt_token(email_id)
    return jsonify({'token': token}), 200


@app.route('/')
# ‘/’ URL is bound with hello_world() function.
def hello_world():
	return 'Hello World'

@app.errorhandler(404)
def page_not_found(e):
    return "404 not found error"

# main driver function
if __name__ == '__main__':

	# run() method of Flask class runs the application
	# on the local development server.
	
	print('db connected');
	app.run()
