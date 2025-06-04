from pymongo import MongoClient
from datetime import datetime
from flask import request

def track_user_consent(consent_data):
    """Track consent for affiliate attribution analysis"""
    client = MongoClient(os.environ.get('MONGODB_URI'))
    db = client.gorillacamping
    
    consent_record = {
        'timestamp': datetime.utcnow(),
        'ip_hash': hash(request.remote_addr),  # Privacy-friendly
        'user_agent': request.headers.get('User-Agent'),
        'analytics_consent': consent_data.get('analytics', False),
        'marketing_consent': consent_data.get('advertisement', False),
        'country': get_country_from_ip(request.remote_addr),
        'referrer': request.referrer
    }
    
    db.consent_analytics.insert_one(consent_record)
    return consent_record

# Add this route to your Flask app
@app.route('/api/consent-update', methods=['POST'])
def consent_update():
    consent_data = request.json
    track_user_consent(consent_data)
    return {'status': 'success'}
