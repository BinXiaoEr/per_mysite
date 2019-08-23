from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
import threading
from django.shortcuts import render
#多线程发送邮件
class SendMail(threading.Thread):
    def __init__(self, subject, text, email, fail_silently=False):
        self.subject = subject
        self.text = text
        self.email = email
        self.fail_silently = fail_silently
        threading.Thread.__init__(self)

    def run(self):
        send_mail(
            self.subject,
            '',
            settings.EMAIL_FROM,
            [self.email],
            fail_silently=self.fail_silently,
            html_message=self.text
        )

class Comment(models.Model):
    #contenttype可以关联任意字段
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    text=models.TextField()
    comment_time=models.DateTimeField(auto_now=True)
    user=models.ForeignKey(User,related_name='comments',on_delete=models.CASCADE)
    root=models.ForeignKey('self',related_name='root_comment',null=True,on_delete=models.CASCADE)
    parent=models.ForeignKey('self',null=True,related_name='parent_comment',on_delete=models.CASCADE)
    reply_to=models.ForeignKey(User,null=True,related_name='replies',on_delete=models.CASCADE)

    def send_mail(self):
        if self.parent is None:
            # 评论我的博客
            subject = '博客评论通知'
            email = self.content_object.get_email()
        else:
            # 评论回复
            subject = '有人回复你的评论'
            email = self.reply_to.email
        if email != "":
            context = {}
            context['comment_text'] = self.text
            context['url'] = self.content_object.get_url()
            text = render(None, 'blog/send_mail.html', context).content.decode('utf-8')
            send_mail = SendMail(subject, text, email)
            send_mail.start()

    def __str__(self):
        return self.text
    class Meta:
        ordering=['-comment_time']
