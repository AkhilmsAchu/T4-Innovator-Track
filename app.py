from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import json
import jwt
from datetime import datetime, timedelta
from functools import wraps
from sqlalchemy.orm import relationship


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.sqlite3'
app.config['SECRET_KEY'] = "random string"

db = SQLAlchemy(app)

class officerModel(db.Model):
   
    id = db.Column(db.Integer, primary_key = True)
    officerid = db.Column(db.Integer)
    name = db.Column(db.String(100))
    password = db.Column(db.String(100))
    phone = db.Column(db.Integer)

    def __init__(self, officerid,name,password,phone):
        self.officerid=userid
        self.name=name
        self.password=password
        self.phone=phone

class userModel(db.Model):
   
    id = db.Column(db.Integer, primary_key = True)
    userid = db.Column(db.Integer)
    name = db.Column(db.String(100))
    password = db.Column(db.String(100))
    phone = db.Column(db.Integer)

    def __init__(self, userid,name,password,phone):
        self.userid=userid
        self.name=name
        self.password=password
        self.phone=phone

class complaintModel(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100))
    message = db.Column(db.String(500))
    date = db.Column(db.Date)
    status = db.Column(db.Boolean) 
    userid = db.Column(db.Integer, db.ForeignKey(userModel.id))

    def __init__(self, title,message,date,status,userid):
        self.title = title
        self.message = message
        self.date = date
        self.status = status
        self.userid=userid

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message' : 'Token is missing !!'}), 401
  
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'],algorithms=['HS256'])
            current_user = userModel.query\
                .filter_by(id = data['public_id'])\
                .first()
        except Exception as e:
            print(e)
            return jsonify({
                'message' : 'Token is invalid !!'
            }), 401
        # returns the current logged in users contex to the routes
        return  f(current_user,data['role'], *args, **kwargs)
  
    return decorated

def userrequired(f):
    def inner(*args, **kwargs):
        if args[1] == "user":
            return f(*args, **kwargs)
        else:
            return {'message':'user not authorised'},403
        
    return inner

@app.route('/ulogin',methods=['POST'])
def ulogin():
    data=json.loads(request.data)
    un=data['userid']
    pwd=data['password']
    rcd=userModel.query.filter_by(userid=un,password=pwd).first()
    if rcd:
        token = jwt.encode({
            'public_id': rcd.id,
            'role': 'user',
            'exp' : datetime.utcnow() + timedelta(days = 930)
        }, app.config['SECRET_KEY'])
        return {'token':token}
    else:
        return {'message':'user not found'},404

@app.route('/ologin',methods=['POST'])
def ologin():
    data=json.loads(request.data)
    un=data['userid']
    pwd=data['password']
    rcd=officerModel.query.filter_by(officerid=un,password=pwd).first()
    if rcd:
        token = jwt.encode({
            'public_id': rcd.id,
            'role': 'officer',
            'exp' : datetime.utcnow() + timedelta(days = 930)
        }, app.config['SECRET_KEY'])
        return {'token':token}
    else:
        return {'message':'user not found'},404



@app.route('/uhome')
@token_required
@userrequired
def uhome(user,role):
    stud=complaintModel.query\
            .filter_by(userid = user.id)\
            .all()

    data=[]
    for i in stud:
        data.append({k: v for k, v in i.__dict__.items() if not str(k).startswith("_")})

    return {'result':data}

@app.route('/<int:id>', methods=['GET'])
def getone(id):
   student = students.query.get(id)
   data={k: v for k, v in student.__dict__.items() if not str(k).startswith("_")}
   sub = Subj.query.get(student.Subj)
   data['sub']=sub.name


   return data

@app.route('/<int:id>', methods=['DELETE'])
def deleteone(id):
   student = students.query.get(id)
   data={k: v for k, v in student.__dict__.items() if not str(k).startswith("_")}

   db.session.delete(student)
   db.session.commit()

   return 'DELETED'

@app.route('/create', methods = [ 'POST'])
def create():
   data=json.loads(request.data )

   student = students(data['name'], data['city'],data['addr'], data['pin'],1)
   
   
   db.session.add(student)
   
   db.session.commit()

   db.session.refresh(student)

   data={k: v for k, v in student.__dict__.items() if not str(k).startswith("_")}

   return data
 
@app.route('/<int:id>', methods = [ 'PUT'])
def update(id):
   data=json.loads(request.data )

   student = students.query.get(id)
   student.name=data['name']
   student.city=data['city']
   student.addr=data['addr']
   student.pin=data['pin']

   db.session.commit()

   db.session.refresh(student)

   data={k: v for k, v in student.__dict__.items() if not str(k).startswith("_")}

   return data         

if __name__ == '__main__':
   with app.app_context():
    db.create_all()
   app.run(debug = True)