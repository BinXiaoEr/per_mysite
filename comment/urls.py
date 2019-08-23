from django.conf.urls import url, include
from .views import *

urlpatterns = [
    #url(r'^$', test),
    url(r'^update_comment$',update_comment,name='update_comment'),
]

