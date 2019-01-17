# Emoji Feedback Python Backend

[![Build Status](https://travis-ci.org/ubc/emoji-feedback-py-backend.svg)](https://travis-ci.org/ubc/emoji-feedback-py-backend) [![Coverage Status](https://codecov.io/gh/ubc/emoji-feedback-py-backend/branch/master/graph/badge.svg)](https://codecov.io/gh/ubc/emoji-feedback-py-backend)

## Dependencies

* [emoji-feedback](https://github.com/ubc/emoji-feedback) (frontend component)

## Usage

The goal of this library is to provide an easy to use python Caliper sensor for the [emoji-feedback](https://github.com/ubc/emoji-feedback) library. When implementing this library with `emoji-feedback`, you will need endpoints for the `emoji` and `feedback` events. You can then provide Caliper `actor`, `session` and `edApp` context information to complete the event. You may also skip setting these to use anonymous entities.

### Setting Caliper host and api key

You can either set the caliper endpoint info when creating the object

```python
feedback_sensor = EmojiFeedbackSensor(
    caliper_host='https://example.caliper.host.com/',
    caliper_api_key='1234567890'
)
```

Or by environment variables:

`EMOJI_FEEDBACK_CALIPER_HOST`: Set the Caliper host.

`EMOJI_FEEDBACK_CALIPER_API_KEY`: Set the Caliper api key.


### Emoji Flask endpoint example

```python
from datetime import datetime
@app.route('/emoji', methods=['POST'])
def emoji():
    req_data = request.get_json()
    eventTime = req_data.get('eventTime')
    object = req_data.get('object') # Some Entity or entity id
    selections = req_data.get('selections') # Array of selections
    question = req_data.get('question') # RatingScaleQuestion entity or entity id

    # generate actor based on current user
    actor = {
        'id': ...,
        'type': 'Person',
        ...
    }

    # generate edApp based on
    edApp = {
        'id': ...,
        'type': 'SoftwareApplication',
        ...
    }

    # generate session based on current user session
    session = {
        'id': ...,
        'type': 'Session',
        ...
    }

    feedback_sensor = EmojiFeedbackSensor(
        caliper_host='https://example.caliper.host.com/',
        caliper_api_key='1234567890'
    )

    feedback_sensor.send_emoji_feedback(
        eventTime=eventTime,
        actor=actor,
        object=object,
        edApp=edApp,
        session=session,
        question=question,
        selections=selections
    )
```

If you would like to handle emitting the event yourself, you can instead generate the event for later use

```
    feedback_sensor = EmojiFeedbackSensor()

    event = feedback_sensor.generate_emoji_feedback_event(
        eventTime=eventTime,
        actor=actor,
        object=object,
        edApp=edApp,
        session=session,
        question=question,
        selections=selections
    )
```

## Running Unit Tests

    python setup.py test

or

    nosetests

## Changelog

### 0.1.0
1. Initial version
2. Must use `-e` to install package since `imsglobal-caliper` is not on PyPI
