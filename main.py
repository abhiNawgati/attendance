
#provode jwt token to flask app
#database queries 
# psql -h localhost postgres -U postgres
from sqlalchemy import text
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

@app.route("/signin", methods=['POST'])
def signin():
    print(0)
    email_id = request.json.get('email_id')
    password = request.json.get('password')
    user = Users.query.filter_by(email_id=email_id).first()

    # If the user exists, compare the password
    if user:
        if user.password == password:
            print('1')
            token = generate_jwt_token(email_id)
            
            return jsonify({"message": "Success","token":token}), 200
        else:
            print(2)
            # Return failure if the password does not match
            return jsonify({"message": "Failure"}), 401
    else:
        # Return failure if the user does not exist
        print(3)
        return jsonify({"message": "Failure"}), 401
     
@app.route('/')
# ‘/’ URL is bound with hello_world() function.
def hello_world():
	return 'Hello World'

@app.errorhandler(404)
def page_not_found(e):
    return "404 not found error"

@app.route('/createTable')
def createTable():
    req_data = request.get_json()
    table_name = req_data['table_name']
    roll_numbers = req_data['roll_numbers']
    print(roll_numbers)

    class Student(db.Model):
        __tablename__ = table_name
        id = db.Column(db.BigInteger, primary_key=True)
        roll_number = db.Column(db.String(255), nullable=False)

    db.create_all()

    


    for rn in roll_numbers:
        student = Student(roll_number=rn)
        print(student)
        db.session.add(student)

    db.session.commit()    

    

    return 'Table created successfully!'
     
@app.route('/attendance', methods=['POST'])
def mark_attendance():
    
    class Students(db.Model):
        
        id = db.Column(db.BigInteger, primary_key=True)
        roll_number = db.Column(db.String(255), nullable=False)
        __table_args__ = {'extend_existing': True}
    table_name = request.json.get('table_name')
    roll_numbers = request.json.get('roll_numbers')

    # create a new column with today's date and default value of 0
    today = datetime.datetime.now().strftime('attt%Y_%m_%d')
    table_name = request.json['table_name']
    if not isinstance(table_name, str):
        return jsonify({'error': 'Table name should be a string'}), 400
    sql = text("ALTER TABLE {} ADD COLUMN {} INTEGER DEFAULT 0".format(table_name, today))
    db.session.execute(sql)
    db.session.commit()

    sql_statement = text("UPDATE {} SET {}=1 WHERE roll_number IN {}".format(table_name,(today), tuple(roll_numbers)))
    db.session.execute(sql_statement, {'roll_numbers': roll_numbers})
    db.session.commit()

    return jsonify({'message': 'Column added and roll numbers marked successfully'}), 200
# main driver function
if __name__ == '__main__':

	# run() method of Flask class runs the application
	# on the local development server.
	
	print('db connected');
	app.run( port=8080)
