from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from jinja2 import Template

from ..main import config

class EmailAgent():

    def __init__(self):
        self.sg = SendGridAPIClient(config().SENDGRID_API_KEY)
        self.fromEmail = config().ADMIN_EMAIL

    def send_verification(self,toEmail,public_uid):
        verification_link = config().ENDPOINT+'/account/verification/' + public_uid
        with open('app/templates/Welcome.html') as file_:
            template = Template(file_.read())
        content = template.render(
            email=toEmail,
            link=verification_link
        )
        message = Mail(
            from_email='chaoslies.andwar@gmail.com',
            to_emails=toEmail,
            subject='Account verification',
            html_content=content)
        response = self.sg.send(message)