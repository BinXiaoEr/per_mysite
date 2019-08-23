from django.conf.urls import url, include
from .views import *

urlpatterns = [
    url(r'^show_list$', blog_list, name='show'),
    url(r'^detail/(\d+)$', blog_detail, name='detail'),
    url(r'^blog_type/(.+)$', blog_type, name='blog_type'),
    url(r'^date/(?P<year>(.+))/(?P<month>(.+))$',blog_with_date,name='blog_with_date'),

]
