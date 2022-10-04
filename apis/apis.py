from logging import exception
from flask import Flask,request,jsonify,make_response
from flask_pymongo import PyMongo
from bson import json_util
from bson.objectid import ObjectId
import json
import datetime

app = Flask(__name__)
app.config['MONGO_DBNAME'] = "quizApp"
app.config['MONGO_URI'] = "mongodb://localhost:27017/quizApp"
mongo = PyMongo(app)


@app.route("/studentRegister",methods=["POST"])
def studentRegister():
    students = mongo.db.students
    req_data = request.get_json()
    objects = students.find()
    if "username" in req_data and "email" in req_data and "password" in req_data:
        for obj in objects:
            if req_data["username"] == obj["username"] and req_data["email"] in obj["email"]:
                return make_response({"error":"username and email is already in use"}, 409)
            if req_data["username"] == obj["username"]:
                return make_response({"error":"username is already in use"}, 409)
            if req_data["email"] == obj["email"]:
                return make_response({"error":"email is already in use"}, 409)

        students.insert_one(req_data)
        return make_response(json.dumps(req_data,indent=4,default=json_util.default), 200)
    else:
        return make_response({"error":"Missing one attribute"}, 400)

@app.route("/studentLogin",methods=["POST"])
def studentLogin():
    students = mongo.db.students.find()
    req_data = request.get_json()
    for obj in students:
        if ( ("username" in req_data and obj["username"] == req_data["username"]) or ("email" in req_data and obj["email"] == req_data["email"]) ) and ("password" in req_data and obj["password"] == req_data["password"]):
            req_data["username"]= obj["username"]
            return make_response(req_data, 200)
    return make_response({"error":"Invalid Credentials!!!"}, 401)

@app.route("/getStudent",methods=["GET"])
def getStudent():
    try:
        students = mongo.db.students.find()
        result = []
        for obj in students:
            result.append(obj)
        print(students)
        return make_response(json.dumps(result,indent=4,default=json_util.default), 200)
    except:
        return make_response({"error":"Invalid Credentials!!!"}, 401)


#.........................quiz.....................................
@app.route("/addQuiz",methods=["POST"])
def addQuiz():
    quiz = mongo.db.quiz
    quizObjects = mongo.db.quiz.find()
    req_data = request.get_json()
    for obj in quizObjects:
        if req_data["quizName"] == obj["quizName"]:
            return make_response({"error":"Quiz Name is already in use"}, 409)
    quiz.insert_one(req_data)
    return make_response("Quiz Created",200)

@app.route("/getQuiz",methods=["GET"])
def getQuiz():
    quiz = mongo.db.quiz
    quizObjects = mongo.db.quiz.find()
    result = []
    for obj in quizObjects:
        result.append(obj)
    return make_response(json.dumps(result,indent=4,default=json_util.default),200)

@app.route("/getQuizById/<id>",methods=["GET"])
def getQuizById(id):
    quiz = mongo.db.quiz
    try:
        obj = mongo.db.quiz.find_one({"_id":ObjectId(id)})
        return make_response(json.dumps(obj,indent=4,default=json_util.default),200)
    except:
        return make_response({"error":"Something Went Wrong!!!"},400)



#......................report...............................
@app.route("/addReport/<username>/<quizId>",methods=["POST"])
def addReport(username,quizId):
    try:
        report = mongo.db.report
        obj =  report.find_one({"username":username})
        x = datetime.datetime.now()
        dateTime = x.strftime('%Y/%m/%d %I:%M:%S')
        req_data = request.get_json()
        req_data["dateTime"] = dateTime
        if obj is None:
            obj = {}
            obj["username"] = username
            obj["response"] = {quizId:[req_data]}
            report.insert_one(obj)
        else:
            if quizId in obj["response"]:
                (obj["response"][quizId]).append(req_data)
            else:
                obj["response"][quizId] = [req_data]
                obj["response"]
            object = report.update_one(
            {"_id" : ObjectId(obj["_id"])},
            {"$set":
                {"response":obj["response"]}
            },upsert=True
        )
        return make_response(json.dumps(obj,indent=4,default=json_util.default),200)
    except:
        return make_response({"error":"Something Went Wrong!!!"},400)

@app.route("/getReport",methods=["GET"])
def getReport():
    try:
        report = mongo.db.report
        reports =  report.find()
        result = []
        for obj in reports:
            result.append(obj) 
        return make_response(json.dumps(result,indent=4,default=json_util.default),200)
    except:
        return make_response({"error":"Something Went Wrong!!!"},400)

@app.route("/getReportByusername/<username>",methods=["GET"])
def getReportByusername(username):
    try:
        report = mongo.db.report
        obj =  report.find_one({"username":username})
        if obj == None:
            obj = {}
        return make_response(json.dumps(obj,indent=4,default=json_util.default),200)
    except:
        return make_response({"error":"Something Went Wrong!!!"},400)

@app.route("/getReportByusernameQuizId/<username>/<quizId>",methods=["GET"])
def getReportByUsernameQuizId(username,quizId):
    try:
        report = mongo.db.report
        obj =  report.find_one({"username":username})
        if obj == None:
            obj = {}
        else:
            obj = obj["response"][quizId]
        
        return make_response(json.dumps(obj,indent=4,default=json_util.default),200)
    except:
        return make_response({"error":"Something Went Wrong!!!"},400)


if __name__ == "__main__":
    app.run(debug=True)