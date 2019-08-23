from django.conf.urls import url, include
from .views import *

urlpatterns = [
    #url(r'^$', test),
    url(r'^like_change$',like_change,name='like_change')
]

