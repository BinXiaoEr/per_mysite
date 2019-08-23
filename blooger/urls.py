from django.conf.urls import url, include
from .views import *

urlpatterns = [
    url(r'^login$', login, name='login'),
    url(r'^logout$', logout, name='logout'),
    url(r'^userinfo$', userinfo, name='userinfo'),
    url(r'^change_nickname$', change_nickname, name='change_nickname'),
    url(r'^bind_email$', bind_email, name='bind_email'),
    url(r'^send_verification_code$', send_verification_code, name='send_verification_code'),
    url(r'^login_for_medal$', login_for_medal, name='login_for_medal'),
    url(r'^change_password$', change_password, name='change_password'),
    url(r'^forgot_password$', forgot_password, name='forgot_password'),
    url(r'^register$', register, name='register'),
    url(r'^$', home, name='home'),
]
