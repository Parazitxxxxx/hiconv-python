from django.test import TestCase
from invitations.apps.mailing.exceptions import ContextException
from invitations.apps.mailing.messages import InvitationMessage


class InvitationMessageTest(TestCase):

    def test_prepare_context_failed(self):
        mixin = InvitationMessage(recipient='test@acme.test', site_domain='acme.test')
        with self.assertRaisesMessage(
                ContextException,
                'Please put this key to context: uid'
                ):
            mixin._prepare_context()

    def test_prepare_context_success(self):
        mixin = InvitationMessage(
            recipient='test@acme.test',
            site_domain='acme.test',
            context={'uid': 'dsada'},
            )
        mixin._prepare_context()
