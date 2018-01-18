from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^send/$',
        views.SendInvitationView.as_view(),
        name='send'
        ),
    url(r'^send/success$',
        views.SendInvitationSuccessView.as_view(),
        name='send_success'
        ),
    url(r'^activate/(?P<uid>[\w]+)$',
        views.ActivateInvitationView.as_view(),
        name='activate'
        ),
]
