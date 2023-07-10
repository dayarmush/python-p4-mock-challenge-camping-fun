#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return '<h1>Welcome Home</h1>'

@app.route('/campers', methods=['GET', 'POST'])
def get_campers():
    if request.method == 'GET':
        campers = Camper.query.all()

        camper_list = [camper.to_dict() for camper in campers ]
        for camper in camper_list:
            camper.pop('signups')

        return make_response(camper_list, 200)
    
    if request.method == 'POST':
        data = request.get_json()

        try:
            new_camper = Camper(name=data['name'], age=data['age'])

            db.session.add(new_camper)
            db.session.commit()

            return make_response(new_camper.to_dict(), 201)
        
        except ValueError as e:
            return make_response(jsonify({'errors': [str(e)]}), 400)
        
    
    return make_response(
        jsonify({'error': 'get failed'}),
        404
    )

@app.route('/campers/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def get_camper_by_id(id):
    camper = Camper.query.filter_by(id = id).first()

    if not camper:
        return make_response(jsonify({"error": 'Camper not found'}), 404)
    
    if request.method == 'GET':
        return make_response(camper.to_dict(), 200)
    
    if request.method == 'PATCH':
        data = request.get_json()
        
        try:
            for key in data:
                setattr(camper, key, data[key])

            db.session.add(camper)
            db.session.commit()

            return make_response(jsonify(camper.to_dict()), 202)
        
        except ValueError as e:
            return make_response({'errors': [str(e)]}, 400)

    
@app.get('/activities')
def get_activities():
    if request.method == 'GET':
        activities = []
        for activity in Activity.query.all():
            activity_dict = activity.to_dict()
            activity_dict.pop('signups')
            activities.append(activity_dict)

    return make_response(activities, 200)

@app.delete('/activities/<int:id>')
def get_activity_by_id(id):
    activity = Activity.query.filter_by(id=id).first()

    if not activity:
        return make_response({'error': 'Activity not found'}, 404)

    db.session.delete(activity)
    db.session.commit()

    return make_response({}, 204)

@app.post('/signups')
def signup():
    data = request.get_json()

    try:
        new_signup = Signup(camper_id=data['camper_id'], 
                            activity_id=data['activity_id'], 
                            time=data['time'])
        
        db.session.add(new_signup)
        db.session.commit()
        return make_response(new_signup.to_dict(), 201)
    
    except ValueError as e:
        return make_response({'errors': [str(e)]}, 400)

    

if __name__ == '__main__':
    app.run(port=5555, debug=True)
