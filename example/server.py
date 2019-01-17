from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from datetime import datetime
from emoji_feedback import EmojiFeedbackSensor

app = Flask(__name__)
CORS(app)

# faking actor, edApp, and session
actor = {
    'id': 'urn:uuid:1a02e4fc-24c1-11e9-ab14-d663bd873d93',
    'type': 'Person',
    'name': 'First Last',
    'dateCreated': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
}

edApp = {
    'id': "urn:uuid:3a02e4fc-24c1-11e9-ab14-d663bd873d93",
    'type': 'SoftwareApplication'
}

session = {
    'id': "urn:uuid:4a02e4fc-24c1-11e9-ab14-d663bd873d93",
    'type': 'Session'
}

@app.route('/')
def hello():
    return 'Hello, World!'

@app.route('/emoji', methods=['POST'])
def emoji():
  req_data = request.get_json()
  object = req_data.get('object')
  eventTime = req_data.get('eventTime')
  selections = req_data.get('selections')
  question = req_data.get('question')

  feedback_sensor = EmojiFeedbackSensor(debug=True)
  feedback_sensor.send_emoji_feedback(
    eventTime=eventTime,
    actor=actor,
    object=object,
    edApp=edApp,
    session=session,
    question=question,
    selections=selections
  )

  resp = jsonify(success=True)
  return resp

@app.route('/feedback', methods=['POST'])
def feedback():
  req_data = request.get_json()
  object = req_data.get('object')
  eventTime = req_data.get('eventTime')
  feedback = req_data.get('feedback')
  questionText = req_data.get('questionText')

  feedback_sensor = EmojiFeedbackSensor(debug=True)
  feedback_sensor.send_comment_feedback(
    eventTime=eventTime,
    actor=actor,
    object=object,
    edApp=edApp,
    session=session,
    questionText=questionText,
    commentText=feedback
  )

  resp = jsonify(success=True)
  return resp

# @app.route('/votes', methods=['GET'])
# def votes():
#   return jsonify({'votes': 2715})

if __name__ == "__main__":
    import sys
    import logging
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    app.run(host="0.0.0.0", debug=True)