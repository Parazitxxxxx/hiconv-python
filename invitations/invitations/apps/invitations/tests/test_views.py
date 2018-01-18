from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase
from invitations.apps.invitations.models import Invitation

User = get_user_model()


class SendInvitationViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username='admin@acme.test', email='admin@acme.test')
        user.set_password('123')
        user.save()
        cls.url = reverse('invitation:send')

    def test_send_invitation_success(self):
        self.client.login(username='admin@acme.test', password='123')
        mail.outbox = []
        self.assertFalse(Invitation.objects.exists())
        response = self.client.post(self.url, {'email': 'test@acme.test'}, follow=True)
        self.assertRedirects(response, '/invitation/send/success')

        self.assertEqual(Invitation.objects.count(), 1)
        invitation = Invitation.objects.last()
        self.assertEqual(invitation.email, 'test@acme.test')
        self.assertIsNone(invitation.user)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Invitation to ACME service')

        invitation_path = '/invitation/activate/{}'.format(invitation.uid)
        self.assertIn(invitation_path, mail.outbox[0].body)
        self.assertEqual(mail.outbox[0].to[0], invitation.email)
        self.assertEqual(mail.outbox[0].from_email, settings.DEFAULT_FROM_EMAIL)

    def test_send_anonymous_invitation_failed(self):
        response = self.client.post(self.url, {'email': 'test@acme.test'}, follow=True)
        self.assertRedirects(response, '/login/?next=/invitation/send/')

    def test_send_exists_invitation_failed(self):
        self.client.login(username='admin@acme.test', password='123')
        Invitation.objects.create(email='test@acme.test')
        response = self.client.post(self.url, {'email': 'test@acme.test'}, follow=True)

        self.assertFormError(
            response,
            form='form',
            field='email',
            errors=['Invitation for that email already sent.']
        )

    def test_send_activated_invitation_failed(self):
        self.client.login(username='admin@acme.test', password='123')
        user = User.objects.create(username='test@acme.test', email='test@acme.test')
        Invitation.objects.create(email='test@acme.test', user=user)
        response = self.client.post(self.url, {'email': 'test@acme.test'}, follow=True)

        self.assertFormError(
            response,
            form='form',
            field='email',
            errors=['Invitation for that email already sent.']
        )

    def test_send_exists_case_sensivity_invitation_failed(self):
        self.client.login(username='admin@acme.test', password='123')
        Invitation.objects.create(email='test@acme.test')
        response = self.client.post(self.url, {'email': 'TeSt@acme.test'}, follow=True)

        self.assertFormError(
            response,
            form='form',
            field='email',
            errors=['Invitation for that email already sent.']
        )


class ActivateInvitationViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.invitation = Invitation.objects.create(email='test@acme.test')
        cls.url = reverse('invitation:activate', args=[cls.invitation.uid])

    def test_activate_invitation_success(self):
        mail.outbox = []
        self.assertFalse(User.objects.exists())
        response = self.client.post(
            self.url,
            {
                'username': 'test@acme.test',
                'password_original': 'PassWord',
                'password_repeat': 'PassWord'
            },
            follow=True,
        )
        self.assertRedirects(response, '/invitation/send/')

        self.invitation.refresh_from_db()

        self.assertEqual(User.objects.count(), 1)
        user = User.objects.last()
        self.assertEqual(user.email, self.invitation.email)
        self.assertEqual(user, self.invitation.user)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Welcome to ACME service')
        self.assertIn('Welcome to ACME service.', mail.outbox[0].body)
        self.assertEqual(mail.outbox[0].to[0], user.email)
        self.assertEqual(mail.outbox[0].from_email, settings.DEFAULT_FROM_EMAIL)

    def test_activate_invitation_with_wrong_passwords_failed(self):
        response = self.client.post(
            self.url,
            {
                'username': 'test@acme.test',
                'password_original': 'PassWord',
                'password_repeat': 'wrong PassWord'
            },
            follow=True,
        )

        self.assertFormError(
            response,
            form='form',
            field=None,
            errors=['Passwords do not match.']
        )

    def test_activate_activated_invitation_failed(self):
        user = User.objects.create(username='test@acme.test', email='test@acme.test')
        self.invitation.user = user
        self.invitation.save()

        response = self.client.post(
            self.url,
            {
                'username': 'test@acme.test',
                'password_original': 'PassWord',
                'password_repeat': 'wrong PassWord'
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 404)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)
