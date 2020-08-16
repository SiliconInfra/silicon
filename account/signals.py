import django.dispatch

email_confirmed = django.dispatch.Signal(providing_args=["email"])
email_confirmation_sent = django.dispatch.Signal(providing_args=["confirmation"])
