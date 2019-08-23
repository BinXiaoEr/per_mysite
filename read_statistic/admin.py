from django.contrib import admin
from .models import *
#Register your models here.
@admin.register(ReadNum)
class BlogRead(admin.ModelAdmin):
    list_display = ('read_num','content_object')

@admin.register(ReadDetail)
class ReadDetailAdmin(admin.ModelAdmin):
    list_display = ('date','read_num','content_object')

@admin.register(IpDeatil)
class ReadDetailAdmin(admin.ModelAdmin):
    list_display = ('date','ip','id_blog','ip_count')
