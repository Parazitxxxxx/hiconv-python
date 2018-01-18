from django.conf import settings
from django.core.mail import send_mail
from django.template import Context, Template

from .exceptions import ContextException


class MessageMixin:
    """
    This mixin helps create simple Message objects with email send interface
    """
    message = ''
    subject = ''
    context_keys = []

    def __init__(self, recipient, site_domain, context={}):
        self.recipient = recipient
        self.site_domain = site_domain
        self.raw_context = context

    def send(self):
        rendered_message = self._render(self.message)
        send_mail(
            subject=self.subject,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.recipient],
            message=rendered_message,
            html_message=rendered_message,
        )

    def _render(self, message):
        template = Template(message)
        context = Context(self._prepare_context())
        return template.render(context)

    def _prepare_context(self):
        context = {'site_domain': self.site_domain}
        for key in self.context_keys:
            if key not in self.raw_context:
                raise ContextException('Please put this key to context: {}'.format(key))
            context[key] = self.raw_context[key]

        return context


class InvitationMessage(MessageMixin):
    """
    This message sends when user post new invitation
    """
    message = (
        'Please follow to this link to activate invitation:\n'
        '{{ site_domain }}/invitation/activate/{{ uid }}'
    )
    subject = 'Invitation to ACME service'
    context_keys = ['uid']


class WelcomeMessage(MessageMixin):
    """
    This message sends when user activate an invitation
    """
    message = (
        'Welcome to ACME service. You can follow to this url for invite another user:\n'
        '{{ site_domain }}'
    )
    subject = 'Welcome to ACME service'
