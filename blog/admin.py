from django.contrib import admin

# Register your models here.
from .models import *
@admin.register(Blog)
class BlogAdimn(admin.ModelAdmin):
    list_display = ('id','title','author','blog_type','create_time','last_update','get_read_num')
@admin.register(BlogType)
class BlogTypeAdmin(admin.ModelAdmin):
    list_display = ('id','type_name')

