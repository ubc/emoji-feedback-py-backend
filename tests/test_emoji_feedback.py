import unittest
import os
from mock import Mock
from unittest.mock import patch
from datetime import datetime
import json

from emoji_feedback import EmojiFeedbackSensor

class TestEmojiFeedback(unittest.TestCase):
    def setUp(self):
        self.feedback_sensor = EmojiFeedbackSensor(
            caliper_host='http://test.com',
            caliper_api_key='123',
            debug=False
        )

        self.feedback_context = 'http://purl.imsglobal.org/ctx/caliper/v1p1/FeedbackProfile-extension'

        self.eventTime = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

        self.actor = {
            'id': 'urn:uuid:1a02e4fc-24c1-11e9-ab14-d663bd873d93',
            'type': 'Person',
            'name': 'First Last'
        }

        self.session = {
            'id': 'urn:uuid:4a02e4fc-24c1-11e9-ab14-d663bd873d93',
            'type': 'Session'
        }

        self.edApp = {
            'id': 'urn:uuid:3a02e4fc-24c1-11e9-ab14-d663bd873d93',
            'type': 'SoftwareApplication'
        }

        self.object = 'urn:uuid:3a02e4fc-24c1-11e9-ab14-d663bd873d11'

        self.selections = ['grinning face','disappointed face']
        self.scale = {
            'id': 'http://localhost:8080/',
            'type':'MultiselectScale',
            'scalePoints':5,
            'itemLabel':[
                '😁',
                '😀',
                '😐',
                '😕',
                '😞'
            ],
            'itemValues':[
                'beaming face with smiling eyes',
                'grinning face',
                'neutral face',
                'confused face',
                'disappointed face'
            ]
        }
        self.question = {
            'id': '',
            'type': 'RatingScaleQuestion',
            'questionPosed': 'How do you feel about this graph?',
            'scale': self.scale
        }
        self.rating = {
            'type': 'Rating',
            'rater': self.actor,
            'rated': self.object,
            'question': self.question,
            'selections': self.selections,
            'dateCreated': self.eventTime
        }
        self.questionText = 'How do you feel about this graph?'
        self.commentText = 'Alright'
        self.comment = {
            'type': 'Comment',
            'commenter': self.actor,
            'commentedOn': self.object,
            'value': self.commentText,
            'dateCreated': self.eventTime,
            'extensions': {
                 'question': self.questionText
            }
        }

        self.maxDiff = None

    def test_init(self):
        # no environ
        feedback_sensor = EmojiFeedbackSensor()
        self.assertIsNone(feedback_sensor.caliper_host)
        self.assertIsNone(feedback_sensor.caliper_api_key)
        self.assertFalse(feedback_sensor.debug)

        # with environ
        environ_overrides = {
            'EMOJI_FEEDBACK_CALIPER_HOST': 'http://test2.com',
            'EMOJI_FEEDBACK_CALIPER_API_KEY': '456'
        }
        with patch.dict('os.environ', environ_overrides):
            feedback_sensor = EmojiFeedbackSensor()
            self.assertEqual(feedback_sensor.caliper_host, 'http://test2.com')
            self.assertEqual(feedback_sensor.caliper_api_key, '456')
            self.assertFalse(feedback_sensor.debug)

        # with params
        feedback_sensor = EmojiFeedbackSensor(
            caliper_host='http://test3.com',
            caliper_api_key='789',
            debug=True
        )
        self.assertEqual(feedback_sensor.caliper_host, 'http://test3.com')
        self.assertEqual(feedback_sensor.caliper_api_key, '789')
        self.assertTrue(feedback_sensor.debug)


    def test_generate_emoji_feedback_event(self):
        # generate event
        event = self.feedback_sensor.generate_emoji_feedback_event(
            eventTime=self.eventTime,
            actor=self.actor,
            object=self.object,
            edApp=self.edApp,
            session=self.session,
            question=self.question,
            selections=self.selections
        )

        # convert to dict
        self.assertIsNotNone(event.get('generated'))
        self.assertIsNotNone(event['generated'].get('id'))
        del event['generated']['id']

        self.assertEqual(event, {
            '@context': self.feedback_context,
            'type': 'FeedbackEvent',
            'action': 'Ranked',
            'actor': self.actor,
            'object': self.object,
            'generated': self.rating,
            'edApp': self.edApp,
            'session': self.session,
            'eventTime': self.eventTime
        })

        # generate event with anonymous data
        event = self.feedback_sensor.generate_emoji_feedback_event(
            eventTime=self.eventTime,
            object=self.object,
            question=self.question,
            selections=self.selections
        )

        # convert to dict
        self.assertIsNotNone(event.get('generated'))
        self.assertIsNotNone(event['generated'].get('id'))
        del event['generated']['id']

        self.rating['rater'] = {
            'id': 'http://purl.imsglobal.org/caliper/Person',
            'type': 'Person'
        }

        self.assertEqual(event, {
            '@context': self.feedback_context,
            'type': 'FeedbackEvent',
            'action': 'Ranked',
            'actor': {
                'id': 'http://purl.imsglobal.org/caliper/Person',
                'type': 'Person'
            },
            'object': self.object,
            'generated': self.rating,
            'edApp': {
                'id': 'http://purl.imsglobal.org/caliper/SoftwareApplication',
                'type': 'SoftwareApplication'
            },
            'session': {
                'id': 'http://purl.imsglobal.org/caliper/Session',
                'type': 'Session'
            },
            'eventTime': self.eventTime,
        })

    def test_send_emoji_feedback(self):
        self.sent_caliper_event = None
        def send_event_override(event):
            self.sent_caliper_event = event
            return {}

        with patch('emoji_feedback.EmojiFeedbackSensor._emit_event') as mocked_send_event:
            mocked_send_event.side_effect = send_event_override

            self.feedback_sensor.send_emoji_feedback(
                eventTime=self.eventTime,
                actor=self.actor,
                object=self.object,
                edApp=self.edApp,
                session=self.session,
                question=self.question,
                selections=self.selections
            )

            self.assertIsNotNone(self.sent_caliper_event.get('generated'))
            self.assertIsNotNone(self.sent_caliper_event['generated'].get('id'))
            del self.sent_caliper_event['generated']['id']

            self.assertEqual(self.sent_caliper_event, {
                '@context': self.feedback_context,
                'type': 'FeedbackEvent',
                'action': 'Ranked',
                'actor': self.actor,
                'object': self.object,
                'generated': self.rating,
                'edApp': self.edApp,
                'session': self.session,
                'eventTime': self.eventTime
            })


    def test_generate_comment_feedback_event(self):
        # generate event
        event = self.feedback_sensor.generate_comment_feedback_event(
            eventTime=self.eventTime,
            actor=self.actor,
            object=self.object,
            edApp=self.edApp,
            session=self.session,
            questionText=self.questionText,
            commentText=self.commentText
        )

        # convert to dict
        self.assertIsNotNone(event.get('generated'))
        self.assertIsNotNone(event['generated'].get('id'))
        del event['generated']['id']

        self.assertEqual(event, {
            '@context': self.feedback_context,
            'type': 'FeedbackEvent',
            'action': 'Commented',
            'actor': self.actor,
            'object': self.object,
            'generated': self.comment,
            'edApp': self.edApp,
            'session': self.session,
            'eventTime': self.eventTime
        })

        # generate event with anonymous data
        event = self.feedback_sensor.generate_comment_feedback_event(
            eventTime=self.eventTime,
            object=self.object,
            questionText=self.questionText,
            commentText=self.commentText
        )

        # convert to dict
        self.assertIsNotNone(event.get('generated'))
        self.assertIsNotNone(event['generated'].get('id'))
        del event['generated']['id']

        self.comment['commenter'] = {
            'id': 'http://purl.imsglobal.org/caliper/Person',
            'type': 'Person'
        }

        self.assertEqual(event, {
            '@context': self.feedback_context,
            'type': 'FeedbackEvent',
            'action': 'Commented',
            'actor': {
                'id': 'http://purl.imsglobal.org/caliper/Person',
                'type': 'Person'
            },
            'object': self.object,
            'generated': self.comment,
            'edApp': {
                'id': 'http://purl.imsglobal.org/caliper/SoftwareApplication',
                'type': 'SoftwareApplication'
            },
            'session': {
                'id': 'http://purl.imsglobal.org/caliper/Session',
                'type': 'Session'
            },
            'eventTime': self.eventTime,
        })

    def test_send_comment_feedback(self):
        self.sent_caliper_event = None
        def send_event_override(event):
            self.sent_caliper_event = event
            return {}

        with patch('emoji_feedback.EmojiFeedbackSensor._emit_event') as mocked_send_event:
            mocked_send_event.side_effect = send_event_override

            self.feedback_sensor.send_comment_feedback(
                eventTime=self.eventTime,
                actor=self.actor,
                object=self.object,
                edApp=self.edApp,
                session=self.session,
                questionText=self.questionText,
                commentText=self.commentText
            )

            self.assertIsNotNone(self.sent_caliper_event.get('generated'))
            self.assertIsNotNone(self.sent_caliper_event['generated'].get('id'))
            del self.sent_caliper_event['generated']['id']

            self.assertEqual(self.sent_caliper_event, {
                '@context': self.feedback_context,
                'type': 'FeedbackEvent',
                'action': 'Commented',
                'actor': self.actor,
                'object': self.object,
                'generated': self.comment,
                'edApp': self.edApp,
                'session': self.session,
                'eventTime': self.eventTime
            })

    def test__emit_event(self):
        self.sent_host = None
        self.sent_evelope = None
        self.sent_headers = None
        def post_override(host, json, headers):
            self.sent_host = host
            self.sent_evelope = json
            self.sent_headers = headers

            mockresponse = Mock()
            mockresponse.raise_for_status = Mock()
            mockresponse.text = 'mock return'
            return mockresponse

        with patch('requests.post') as mocked_post:
            mocked_post.side_effect = post_override

            event = {
                '@context': self.feedback_context,
                'type': 'FeedbackEvent',
                'action': 'Commented',
                'actor': self.actor,
                'object': self.object,
                'generated': self.comment,
                'edApp': self.edApp,
                'session': self.session,
                'eventTime': self.eventTime
            }

            invalid_feedback_sensor = EmojiFeedbackSensor(
                caliper_host=None,
                caliper_api_key='123',
                debug=False
            )
            with self.assertRaises(Exception) as cm:
                invalid_feedback_sensor._emit_event(event)
            self.assertEqual('Emoji Feedback Error: Caliper Host not set', str(cm.exception))

            invalid_feedback_sensor = EmojiFeedbackSensor(
                caliper_host='http://test.com',
                caliper_api_key=None,
                debug=False
            )
            with self.assertRaises(Exception) as cm:
                invalid_feedback_sensor._emit_event(event)
            self.assertEqual('Emoji Feedback Error: Caliper API Key not set', str(cm.exception))

            self.feedback_sensor._emit_event(event)
            self.assertEqual(self.sent_host, 'http://test.com')
            self.assertEqual(self.sent_headers, {
                'Authorization': 'Bearer 123',
                'Content-Type': 'application/json'
            })

            self.assertEqual(self.sent_headers, {
                'Authorization': 'Bearer 123',
                'Content-Type': 'application/json'
            })
            self.assertIsNotNone(self.sent_evelope.get('sendTime'))
            del self.sent_evelope['sendTime']

            self.assertEqual(self.sent_evelope, {
                'sensor': 'https://emojifeedback.learninganalytics.ubc.ca/',
                'dataVersion': 'http://purl.imsglobal.org/ctx/caliper/v1p1',
                'data': [ event ]
            })