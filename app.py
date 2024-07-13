from dotenv import load_dotenv
import os
import logging
from flask import Flask, request
from celery import Celery
from flask_mail import Mail, Message
from datetime import datetime

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)

# Configure Flask-Mail
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

# Configure Celery
app.config['CELERY_BROKER_URL'] = os.getenv('CELERY_BROKER_URL')
app.config['CELERY_RESULT_BACKEND'] = os.getenv('CELERY_RESULT_BACKEND')

mail = Mail(app)

# Create and configure Celery
celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# Logging configuration
logging.basicConfig(filename='/var/log/messaging_system.log', level=logging.INFO)

@celery.task
def send_email(recipient):
    msg = Message('Hello from HNG Intern in Stage 3', sender=app.config['MAIL_USERNAME'], recipients=[recipient])
    msg.body = 'This is a test email sent from a Flask application using Celery.'
    with app.app_context():
        mail.send(msg)

@app.route('/send-message')
def send_message():
    sendmail = request.args.get('sendmail')
    talktome = request.args.get('talktome')
    
    if sendmail:
        send_email.delay(sendmail)
        return f'Email queued to be sent to {sendmail}'
    
    if talktome:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logging.info(f'Talk to me called at {current_time}')
        return 'Logged current time'

    return 'No valid parameter provided'

if __name__ == '__main__':
    app.run(debug=True)