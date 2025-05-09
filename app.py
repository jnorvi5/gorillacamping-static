from flask import Flask, render_template, request
from pymongo import MongoClient
import os
from datetime import datetime

app = Flask(__name__)

MONGO_URI = os.environ.get("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.get_database("gorillacamping")
emails_collection = db.get_collection("subscribers")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email = request.form.get('email')
        if email:
            emails_collection.insert_one({
                "email": email,
                "source": "website-form",
                "timestamp": datetime.utcnow().isoformat(),
                "tags": ["user", "newsletter"]
            })
    return render_template('index.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/gear')
def gear():
    return render_template('gear.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True)