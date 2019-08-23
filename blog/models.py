from django.db import models
from django.contrib.auth.models import User
from mdeditor.fields import MDTextField
from django.contrib.contenttypes.models import ContentType
from read_statistic.models import *
from django.contrib.contenttypes.fields import GenericRelation
from django.shortcuts import  reverse
class BlogType(models.Model):
    type_name = models.CharField(max_length=20)

    def __str__(self):
        return self.type_name

def get_default_user():

    user=User.objects.get(is_superuser=1)
    return user.id

class Blog(models.Model,ReadNumExpand):
    title = models.CharField(max_length=50)
    blog_type = models.ForeignKey(BlogType, on_delete=models.CASCADE)
    content = MDTextField()
    read_details=GenericRelation(ReadDetail)
    author = models.ForeignKey(User, on_delete=models.CASCADE,default=get_default_user)
    create_time = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def get_url(self):
        return reverse('blog:detail',args=[self.pk])

    def get_email(self):
        return self.author.email
    def __str__(self):
        return self.title
    class Meta:
        ordering = ['-create_time']
