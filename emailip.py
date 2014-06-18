#!/usr/bin/python
#
#   Copyright 2014 Zeth
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""
Send an email with the current public IP Address of the machine.
Fill in the required variables below.

This should work with Python 2 or 3.

E.g. on Linux one can put this into /etc/cron.daily folder.
"""


FROM_ADDRESS = "example@example.net"
TO_ADDRESS = "example@example.net"
SMTP_USERNAME = "example@example.net"
SMTP_PASSWORD = "example123"
SMTP_SERVER = 'smtp.example.net'
SMTP_PORT = 587
STARTTLS = False

# You don't actually need to change these
SUBJECT = "IP Address Notification from Cron"
SERVER_URL = 'http://checkip.dyndns.org/'


try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen
import xml.etree.ElementTree as ET
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib


class IPEmailer(object):
    """Emails the public IP of the local machine."""
    def __init__(self,
                 from_address=FROM_ADDRESS,
                 to_address=TO_ADDRESS,
                 smtp_username=SMTP_USERNAME,
                 smtp_password=SMTP_PASSWORD,
                 smtp_server=SMTP_SERVER,
                 smtp_port=SMTP_PORT,
                 starttls=STARTTLS,
                 subject=SUBJECT,
                 server_url=SERVER_URL):
        self.from_address = from_address
        self.to_address = to_address
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.starttls = starttls
        self.subject = subject
        self.server_url = server_url

    def get_body_text(self):
        """Finds the external ip address and uses it as the email body."""
        response = urlopen(self.server_url)
        html = response.read()
        htmlelement = ET.fromstring(html)
        body = htmlelement.find('body')
        return body.text

    def build_message(self):
        """Build the message."""
        msg = MIMEMultipart()
        msg['From'] = self.from_address
        msg['To'] = self.to_address
        msg['Subject'] = self.subject
        msg.attach(MIMEText(self.get_body_text(), 'plain'))
        return msg.as_string()

    def send_mail(self):
        """Send the mail."""
        server = smtplib.SMTP(self.smtp_server, self.smtp_port)
        server.ehlo()
        if self.starttls:
            server.starttls()
        server.ehlo()
        server.login(self.smtp_username, self.smtp_password)
        server.sendmail(self.from_address,
                        self.to_address,
                        self.build_message())

if __name__ == '__main__':
    EMAILER = IPEmailer()
    EMAILER.send_mail()
