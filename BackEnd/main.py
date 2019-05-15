from flask import Flask, request, jsonify, render_template, make_response, Response 
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from slackclient import SlackClient
import json
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Pavan123@localhost:5432/Sample'
USER   = 'root'
PASS   = 'dhihub123'
HOST   = '35.244.127.254'
DBNAME = 'sample'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://{}:{}@{}/{}'.format(USER,PASS,HOST,DBNAME)
slack_token = 'xoxb-575060474148-600534221555-p4pSLvMQO4ZdbognZ9Z9PiFu'
SLACK_VERIFICATION_TOKEN = 'QKeDPPoqJ4PfNm99ch0v1SUc'
sc = SlackClient(slack_token)
db = SQLAlchemy(app)
ma = Marshmallow(app)


#Helper for verifying that requests came from Slack
def verify_slack_token(request_token):
    if SLACK_VERIFICATION_TOKEN != request_token:
        print("Error: invalid verification token!")
        print("Received {} but was expecting {}".format(request_token, SLACK_VERIFICATION_TOKEN))
        return make_response("Request contains invalid Slack verification token", 403)

class Survey(db.Model):
    SurveyID = db.Column(db.Integer, primary_key=True)
    Survey_Title = db.Column(db.String(200), unique=False, nullable =False )
    
    def __init__(self,SurveyID,Survey_Title):
        self.SurveyID = SurveyID
        self.Survey_Title = Survey_Title

class UserSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('SurveyID','Survey_Title')
user_schema = UserSchema()
users_schema = UserSchema(many=True)


class Question(db.Model):
    que_id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    SurveyID = db.Column(db.Integer, db.ForeignKey('survey.SurveyID'),primary_key=True,autoincrement = False)
    question_type = db.Column(db.String(100),nullable=False)
    question = db.Column(db.String(300),nullable=False)
    optionA = db.Column(db.String(100))
    optionB = db.Column(db.String(100))
    optionC = db.Column(db.String(100))
    optionD = db.Column(db.String(100))
    
    def __init__(self,SurveyID,question_type,question,optionA,optionB,optionC,optionD):
        self.question_type = question_type
        self.SurveyID = SurveyID
        self.question = question
        self.optionA = optionA
        self.optionB = optionB
        self.optionC = optionC
        self.optionD = optionD

class UserSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('que_id','SurveyID','question_type','question','optionA','optionB','optionC','optionD')

user_schema1 = UserSchema()
users_schema1 = UserSchema(many=True)

class User_info(db.Model):
    UID = db.Column(db.String(50), primary_key=True)
    Name = db.Column(db.String(300))

    def __init__(self, UID,Name):
        self.UID = UID
        self.Name = Name
class UserSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('UID','Name')
user_schema2 = UserSchema()
users_schema2 = UserSchema(many=True)


class Answer(db.Model):
    UID = db.Column(db.String(50), db.ForeignKey('user_info.UID'),primary_key=True)
    que_id = db.Column(db.Integer, db.ForeignKey('question.que_id'),primary_key=True)
    SurveyID = db.Column(db.Integer, db.ForeignKey('survey.SurveyID'),primary_key=True)
    answer = db.Column(db.String(50), nullable=False)

    def __init__(self, UID,que_id,SurveyID,answer):
        self.UID = UID
        self.que_id = que_id
        self.SurveyID = SurveyID
        self.answer = answer

class UserSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('UID','que_id','SurveyID','answer')

user_schema3 = UserSchema()
users_schema3 = UserSchema(many=True)



@app.route("/user", methods=["POST","GET"])
def add_user():
    question1 = request.json['question']
    op_a = request.json['optionA']
    op_b = request.json['optionB']
    op_c = request.json['optionC']
    op_d = request.json['optionD']
    questType = request.json['questionType']
    
    print(question1,op_a,op_b,op_c,op_d)
    
    new_question = Question(1,questType,question1,op_a,op_b,op_c,op_d)
    db.session.add(new_question)
    db.session.commit()
    
    last_que = Question.query.order_by(Question.que_id.desc()).first()
    from_que_get_id = user_schema1.dump(last_que)
    question_id = from_que_get_id.data['que_id']
    survey_id = from_que_get_id.data['SurveyID']
    # op_a_value = "Value: "+op_a + " qid: "+str(question_id) + " sid: "+str(survey_id)
    # op_b_value = "Value: "+op_b + " qid: "+str(question_id) + " sid: "+str(survey_id)
    # op_c_value = "Value: "+op_c + " qid: "+str(question_id) + " sid: "+str(survey_id)
    # op_d_value = "Value: "+op_d + " qid: "+str(question_id) + " sid: "+str(survey_id)
    
    if questType == 4:
    
        op_a_value = json.dumps({
            "value" : op_a,
            "qid" : question_id,
            "surveyid" : survey_id
        })
        op_b_value = json.dumps({
            "value" : op_b,
            "qid" : question_id,
            "surveyid" : survey_id
        })
        op_c_value = json.dumps({
            "value" : op_c,
            "qid" : question_id,
            "surveyid" : survey_id
        })
        op_d_value = json.dumps({
            "value" : op_d,
            "qid" : question_id,
            "surveyid" : survey_id
        })

        print(op_a_value)
    
        attachments_json = [
        {
            "fallback": "Upgrade your Slack client to use messages like these.",
            "color": "#3AA3E3",
            "attachment_type": "default",
            "callback_id": "menu_options_2319",
            "actions": [
                {
                    "name": "low",
                    "text": op_a,
                    "type": "button",
                    "value": op_a_value
                },
                {
                    "name": "high",
                    "text": op_b,
                    "type": "button",
                    "value": op_b_value
                },
                {
                    "name": "high",
                    "text": op_c,
                    "type": "button",
                    "value": op_c_value
                },
                {
                    "name": "high",
                    "text": op_d,
                    "type": "button",
                    "value": op_d_value
                }
            ]
        }
        ]

    elif questType == 3 :
        op_a_value = json.dumps({
            "value" : op_a,
            "qid" : question_id,
            "surveyid" : survey_id
        })
        op_b_value = json.dumps({
            "value" : op_b,
            "qid" : question_id,
            "surveyid" : survey_id
        })
        op_c_value = json.dumps({
            "value" : op_c,
            "qid" : question_id,
            "surveyid" : survey_id
        })

        print(op_a_value)
    
        attachments_json = [
        {
            "fallback": "Upgrade your Slack client to use messages like these.",
            "color": "#3AA3E3",
            "attachment_type": "default",
            "callback_id": "menu_options_2319",
            "actions": [
                {
                    "name": "low",
                    "text": op_a,
                    "type": "button",
                    "value": op_a_value
                },
                {
                    "name": "high",
                    "text": op_b,
                    "type": "button",
                    "value": op_b_value
                },
                {
                    "name": "high",
                    "text": op_c,
                    "type": "button",
                    "value": op_c_value
                }
            ]
        }
        ]

    elif questType == 2:
        op_a_value = json.dumps({
            "value" : op_a,
            "qid" : question_id,
            "surveyid" : survey_id
        })
        op_b_value = json.dumps({
            "value" : op_b,
            "qid" : question_id,
            "surveyid" : survey_id
        })

        print(op_a_value)
    
        attachments_json = [
        {
            "fallback": "Upgrade your Slack client to use messages like these.",
            "color": "#3AA3E3",
            "attachment_type": "default",
            "callback_id": "menu_options_2319",
            "actions": [
                {
                    "name": "low",
                    "text": op_a,
                    "type": "button",
                    "value": op_a_value
                },
                {
                    "name": "high",
                    "text": op_b,
                    "type": "button",
                    "value": op_b_value
                }
            ]
        }
        ]

    # Send a message with the above attachment, asking the user if they want coffee
    sc.api_call(
    "chat.postMessage",
    channel="UGX2TGTFU",
    text = question1,
    as_user = True,
    attachments=attachments_json
    )


    
    # print(sc.api_call
    # (
    #     "chat.postMessage",
    #     channel = "#random",
    #     text = question,
    #     as_user = False 	
    # )
    # )

    return jsonify(new_question)

@app.route("/slack/message_actions", methods=["POST"])
def message_actions():

    # Parse the request payload
    form_json = json.loads(request.form["payload"])
    print(form_json)

    # Verify that the request came from Slack
    verify_slack_token(form_json["token"])

    # Check to see what the user's selection was and update the message accordingly
    selection = form_json["actions"][0]["value"]
    abc = json.loads(selection)
    answer_value = abc["value"]
    answer_que = abc["qid"]
    answer_survey = abc["surveyid"]
    u_id = form_json['user']['id']
    name = form_json['user']['name']
    
    print("Value is: ",answer_value)
    print("QID is:", answer_que)
    print("surveyid is : ", answer_survey)
    print("This is the ID:   ",id)
    print("Name:  ",name)
    
    new_answer = Answer(u_id,answer_que,answer_survey,answer_value)
    db.session.add(new_answer)
    db.session.commit()


    response = sc.api_call(
      "chat.update",
      channel=form_json["channel"]["id"],
      ts=form_json["message_ts"],
      text="Thank you! :smile:",
      attachments=[] # empty `attachments` to clear the existing massage attachments
    )

    # Send an HTTP 200 response with empty body so Slack knows we're done here
    return make_response("", 200)

@app.route("/user/data", methods=["GET"])
def get_user():
    all_questions = Question.query.all()
    result = users_schema1.dump(all_questions)
    return jsonify(result.data)

@app.route("/user/answer/data", methods=["GET"])
def get_answer():
    all_answer = Answer.query.all()
    ans=users_schema3.dump(all_answer)
    return jsonify(ans.data)

if __name__ == '__main__':
    app.debug = True
    app.run()




