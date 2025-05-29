from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime
import logging

app = Flask(__name__)

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['github_events']
collection = db['events']

# Logging setup
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/events')
def get_events():
    events = list(collection.find({}, {'_id': 0}))
    logging.debug(f"Fetched events: {len(events)}")
    return jsonify(events)

@app.route('/webhook', methods=['POST'])
def webhook():
    event_type = request.headers.get('X-GitHub-Event')
    payload = request.get_json()
    logging.debug(f"Received webhook: {event_type} {payload}")

    # Handle ping event
    if event_type == 'ping':
        return jsonify({'message': 'Ping received'}), 200

    # Handle push and pull_request events
    if event_type not in ['push', 'pull_request']:
        logging.error(f"Invalid event type: {event_type}")
        return jsonify({'error': 'Invalid event type'}), 400

    try:
        event_data = {}
        if event_type == 'push':
            event_data = {
                'request_id': payload['head_commit']['id'],
                'author': payload['pusher']['name'],
                'action': 'PUSH',
                'from_branch': None,
                'to_branch': payload['ref'].split('/')[-1],
                'timestamp': payload['head_commit']['timestamp']
            }
        elif event_type == 'pull_request':
            action = payload['action']
            if action == 'opened':
                event_data = {
                    'request_id': str(payload['pull_request']['id']),
                    'author': payload['pull_request']['user']['login'],
                    'action': 'PULL_REQUEST',
                    'from_branch': payload['pull_request']['head']['ref'],
                    'to_branch': payload['pull_request']['base']['ref'],
                    'timestamp': payload['pull_request']['created_at']
                }
            elif action == 'closed' and payload['pull_request']['merged']:
                event_data = {
                    'request_id': str(payload['pull_request']['id']),
                    'author': payload['pull_request']['user']['login'],
                    'action': 'MERGE',
                    'from_branch': payload['pull_request']['head']['ref'],
                    'to_branch': payload['pull_request']['base']['ref'],
                    'timestamp': payload['pull_request']['merged_at']
                }

        if event_data:
            collection.insert_one(event_data)
            logging.debug(f"Stored event: {event_data}")
            return jsonify({'message': 'Event processed'}), 200
        else:
            logging.debug(f"Ignored event: {event_type} {action}")
            return jsonify({'message': 'Event ignored'}), 200

    except Exception as e:
        logging.error(f"Webhook error: {str(e)}")
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)