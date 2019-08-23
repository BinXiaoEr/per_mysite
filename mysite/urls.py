from django.contrib import admin
from django.urls import path
from django.conf.urls import url,include
from django.conf import settings
from django.conf.urls.static import static
from haystack.views import SearchView
from .views import *
urlpatterns = [
    path('admin_manage/', admin.site.urls),
    url(r'^comment/', include(('comment.urls', 'comment'), namespace='comment')),
     url(r'^search/', MySearchView(), name='haystack_search'),  # 全文检索
    url(r'^blog/',include(('blog.urls','blog'),namespace='blog')),
    url(r'^likes/', include(('likes.urls', 'likes'), namespace='likes')),
    url(r'^', include(('blooger.urls', 'blooger'), namespace='blooger')),
    url(r'mdeditor/', include('mdeditor.urls')),
]

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
