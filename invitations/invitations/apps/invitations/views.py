from django.contrib.auth import authenticate, login
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.detail import BaseDetailView
from django.views.generic.edit import FormView

from .forms import InvitationActivationForm, InvitationSendForm
from .models import Invitation


class SendInvitationView(FormView):
    template_name = 'invitations/invitation_send_form.html'
    form_class = InvitationSendForm
    success_url = reverse_lazy('invitation:send_success')

    @transaction.atomic
    def form_valid(self, form):
        form.save()
        form.send_email(self.request.get_host())
        return super().form_valid(form)


class SendInvitationSuccessView(TemplateView):
    template_name = 'invitations/invitation_send_success.html'


class ActivateInvitationView(FormView, BaseDetailView):
    model = Invitation
    queryset = Invitation.objects.filter(user__isnull=True)
    slug_field = 'uid'
    slug_url_kwarg = 'uid'
    template_name = 'invitations/invitation_activation_form.html'
    form_class = InvitationActivationForm
    success_url = reverse_lazy('invitation:send')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    @transaction.atomic
    def form_valid(self, form):
        form.save(invitation=self.object)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password_original']
        user = authenticate(self.request, username=username, password=password)
        login(self.request, user)
        form.send_email(self.request.get_host())
        return HttpResponseRedirect(self.success_url)
