from django.template.loader import render_to_string
from smtplib import SMTPAuthenticationError
import socket

from django.core.mail.message import EmailMessage as _


class EmailMessage:
	def send(self, subject_template, subject_context, to, message_template, message_context, cc=None, bcc=None,
	         reply_to=None, from_email=None):
		if isinstance(to, str):
			to = list(to)

		subject = render_to_string(subject_template, subject_context)
		message = render_to_string(message_template, message_context)
		email = _(subject=subject, body=message, from_email=from_email, to=to, bcc=bcc, cc=cc, reply_to=reply_to)
		email.content_subtype = 'html'
		try:
			return email.send()
		except SMTPAuthenticationError as e:
			# TODO: Add something here
			return False
		except socket.gaierror as e:
			# TODO: Add something here
			return False
