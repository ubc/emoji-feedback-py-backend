import uuid
import requests
from datetime import datetime
from os import environ

ANONYMOUS_ACTOR = {
    'id': 'http://purl.imsglobal.org/caliper/Person',
    'type': 'Person'
}

ANONYMOUS_EDAPP = {
    'id': 'http://purl.imsglobal.org/caliper/SoftwareApplication',
    'type': 'SoftwareApplication'
}

ANONYMOUS_SESSION = {
    'id': 'http://purl.imsglobal.org/caliper/Session',
    'type': 'Session'
}

class EmojiFeedbackSensor(object):
    SENSOR_ID = "https://emojifeedback.learninganalytics.ubc.ca/"
    CALIPER_VERSION = "http://purl.imsglobal.org/ctx/caliper/v1p2"

    def __init__(self, caliper_host=None, caliper_api_key=None, debug=False):
        self.caliper_host = caliper_host if caliper_host else environ.get('EMOJI_FEEDBACK_CALIPER_HOST', None)
        self.caliper_api_key = caliper_api_key if caliper_api_key else environ.get('EMOJI_FEEDBACK_CALIPER_API_KEY', None)
        self.debug = debug

    def generate_emoji_feedback_event(self, eventTime, object, question, selections,
            edApp=ANONYMOUS_EDAPP, session=ANONYMOUS_SESSION, actor=ANONYMOUS_ACTOR,
            **kwargs):
        generated = {
            'id': 'urn:uuid:' + str(uuid.uuid4()),
            'type': 'Rating',
            'rater': actor,
            'rated': object,
            'question': question,
            'selections': selections,
            'dateCreated': eventTime
        }
        event = {
            'id': 'urn:uuid:' + str(uuid.uuid4()),
            '@context': 'http://purl.imsglobal.org/ctx/caliper/v1p2',
            'type': 'FeedbackEvent',
            'actor': actor,
            'action': 'Ranked',
            'profile': 'FeedbackProfile',
            'object': object,
            'edApp': edApp,
            'session': session,
            'generated': generated,
            'eventTime': eventTime,
        }
        event.update(kwargs)

        return event

    def send_emoji_feedback(self, eventTime, object, question, selections,
            edApp=ANONYMOUS_EDAPP, session=ANONYMOUS_SESSION, actor=ANONYMOUS_ACTOR,
            **kwargs):
        event = self.generate_emoji_feedback_event(eventTime, object, question, selections,
            edApp, session, actor, **kwargs)
        self._emit_event(event)

    def generate_comment_feedback_event(self, eventTime, object, questionText, commentText,
            edApp=ANONYMOUS_EDAPP, session=ANONYMOUS_SESSION, actor=ANONYMOUS_ACTOR,
            **kwargs):
        generated = {
            'id': 'urn:uuid:' + str(uuid.uuid4()),
            'type': 'Comment',
            'commenter': actor,
            'commentedOn': object,
            'value': commentText,
            'dateCreated': eventTime,
            'extensions': {
                'question': questionText
            }
        }
        event = {
            'id': 'urn:uuid:' + str(uuid.uuid4()),
            '@context': 'http://purl.imsglobal.org/ctx/caliper/v1p2',
            'type': 'FeedbackEvent',
            'actor': actor,
            'action': 'Commented',
            'profile': 'FeedbackProfile',
            'object': object,
            'edApp': edApp,
            'session': session,
            'generated': generated,
            'eventTime': eventTime,
        }
        event.update(kwargs)

        return event

    def send_comment_feedback(self, eventTime, object, questionText, commentText,
            edApp=ANONYMOUS_EDAPP, session=ANONYMOUS_SESSION, actor=ANONYMOUS_ACTOR,
            **kwargs):
        event = self.generate_comment_feedback_event(eventTime, object, questionText, commentText,
            edApp, session, actor, **kwargs)
        self._emit_event(event)

    def _emit_event(self, event):
        if not self.caliper_host:
            raise Exception('Emoji Feedback Error: Caliper Host not set')

        if not self.caliper_api_key:
            raise Exception('Emoji Feedback Error: Caliper API Key not set')

        sendTime = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        envelope = {
            'sensor': EmojiFeedbackSensor.SENSOR_ID,
            'sendTime': sendTime,
            'dataVersion': EmojiFeedbackSensor.CALIPER_VERSION,
            'data': [ event ]
        }

        response = requests.post(
            self.caliper_host,
            json=envelope,
            headers={
                'Authorization': 'Bearer '+str(self.caliper_api_key),
                'Content-Type': 'application/json'
            }
        )
        response.raise_for_status()

        if self.debug:
            print(response.text)