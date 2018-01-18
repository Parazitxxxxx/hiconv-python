from django import forms
from django.contrib.auth import get_user_model
from django.core.validators import ValidationError
from django.utils.translation import ugettext_lazy as _
from invitations.apps.mailing.messages import InvitationMessage, WelcomeMessage

from .models import Invitation

User = get_user_model()


class InvitationSendForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if Invitation.objects.filter(email=email).exists():
            raise ValidationError(_('Invitation for that email already sent.'))

        if User.objects.filter(email=email).exists():
            raise ValidationError(_('User with this email already registered.'))
        return email

    def save(self):
        email = self.cleaned_data['email'].lower()
        self.invitation, created = Invitation.objects.get_or_create(email=email)

    def send_email(self, site_domain):
        email = self.cleaned_data['email'].lower()
        InvitationMessage(
            recipient=email,
            site_domain=site_domain,
            context={'uid': self.invitation.uid},
        ).send()


class InvitationActivationForm(forms.Form):
    username = forms.CharField()
    password_original = forms.CharField(
        max_length=32,
        widget=forms.PasswordInput,
        label=_('Password')
        )
    password_repeat = forms.CharField(
        max_length=32,
        widget=forms.PasswordInput,
        label=_('Repeat Password')
        )

    def clean(self):
        password_original = self.cleaned_data['password_original']
        password_repeat = self.cleaned_data['password_repeat']

        if password_original != password_repeat:
            raise ValidationError(_('Passwords do not match.'))

        return self.cleaned_data

    def save(self, invitation):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password_original']

        self.user, created = User.objects.get_or_create(
            username=username,
            email=invitation.email,
        )
        self.user.set_password(password)
        self.user.save()

        invitation.user = self.user
        invitation.save()

    def send_email(self, site_domain):
        WelcomeMessage(
            recipient=self.user.email,
            site_domain=site_domain,
        ).send()
