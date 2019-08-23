from django.shortcuts import render, reverse, redirect
from .forms import *
from django.http import JsonResponse
from django.conf import settings
from read_statistic.utils import get_seven_days_read_data, get_today_hot_data, get_yesterday_hot_data
from django.core.cache import cache
from django.contrib import auth
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Sum
from django.core.mail import send_mail
from blog.models import *
from .models import *
import datetime
import string
import random

import time


def get_7_days_hot_blogs():
    today = timezone.now().date()
    date = today - datetime.timedelta(days=7)
    blogs = Blog.objects \
        .filter(read_details__date__lt=today, read_details__date__gte=date) \
        .values('id', 'title') \
        .annotate(read_num_sum=Sum('read_details__read_num')) \
        .order_by('-read_num_sum')
    return blogs[:7]


def home(request):
    blog_content_type = ContentType.objects.get_for_model(Blog)
    dates, read_nums = get_seven_days_read_data(content_type=blog_content_type)
    today_hot_data = get_today_hot_data(blog_content_type)
    yesterday_hot_data = get_yesterday_hot_data(blog_content_type)
    # seven_hot_data=get_7_days_hot_blogs()
    # 获取7天热门博客的缓存数据
    hot_blog_for_seven_days = cache.get('hot_blog_for_seven_days')
    if hot_blog_for_seven_days is None:
        hot_blog_for_seven_days = get_7_days_hot_blogs()
        cache.set('hot_blog_for_seven_days', hot_blog_for_seven_days, 3600)
    context = {'read_nums': read_nums, 'dates': dates,
               'today_hot_data': today_hot_data,
               'yesterday_hot_data': yesterday_hot_data,
               'seven_hot_data': hot_blog_for_seven_days
               }
    return render(request, 'blogger/home.html', context)


def login(request):
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            # clean函数在form中返回的是一个字典值含有user对象我们要用键取他的值
            user = login_form.clean()
            auth.login(request, user['user'])
            return redirect(request.GET.get('from', reverse("blooger:home")))
    else:
        login_form = LoginForm()
    context = {}
    context['login_form'] = login_form
    return render(request, 'blogger/login.html', context)


# 详情页登陆模块
def login_for_medal(request):
    login_form = LoginForm(request.POST)
    data = {}
    if login_form.is_valid():
        # clean函数在form中返回的是一个字典值含有user对象我们要用键取他的值
        user = login_form.clean()
        auth.login(request, user['user'])

        data['status'] = 'SUCCESS'
    else:
        data['status'] = 'ERROR'
    return JsonResponse(data)

# 注册
def register(request):
    if request.method == 'POST':
        reg_form = RegForm(request.POST,request=request)
        if reg_form.is_valid():
            username = reg_form.cleaned_data['username']
            email = reg_form.cleaned_data['email']
            password = reg_form.cleaned_data['password_again']
            # 创建用户
            user = User.objects.create_user(username, email, password)
            user.save()
            # 登录用户
            user = auth.authenticate(username=username, password=password)
            #清除session
            del request.session['register_code']
            auth.login(request, user)
            return redirect(request.GET.get('from', reverse("blooger:home")))
    else:
        reg_form = RegForm()
    context = {}
    context['reg_form'] = reg_form
    return render(request, 'blogger/register.html', context)


# 注销登陆
def logout(request):
    auth.logout(request)
    return redirect(request.GET.get('from', reverse("blooger:home")))


# 用户信息
def userinfo(request):
    context = {}
    return render(request, 'blogger/user_info.html', context)


# 修改用户昵称
def change_nickname(request):
    redirect_to = request.GET.get('from', reverse('blooger:home'))
    if request.method == 'POST':
        form = ChangeNicknameForm(request.POST, user=request.user)
        if form.is_valid():
            nickname_new = form.cleaned_data['nickname_new']
            print(nickname_new)
            profile, created = Profile.objects.get_or_create(user=request.user)
            profile.nickname = nickname_new
            profile.save()
            return redirect(redirect_to)
    else:
        form = ChangeNicknameForm()
    context = {}
    context['page_title'] = '修改昵称'
    context['form_title'] = '修改昵称'
    context['submit_text'] = '修改'
    context['form'] = form
    context['return_back_url'] = redirect_to
    return render(request, 'blogger/form.html', context)

#绑定邮箱
def bind_email(request):
    redirect_to = request.GET.get('from', reverse('blooger:home'))

    if request.method == 'POST':
        form = BindEmailForm(request.POST, request=request)
        if form.is_valid():
            email = form.cleaned_data['email']
            request.user.email = email
            request.user.save()
            #清除session
            del request.session['send_code_time']
            return redirect(redirect_to)
    else:
        form = BindEmailForm()
    context = {}
    context['page_title'] = '绑定邮箱'
    context['form_title'] = '绑定邮箱'
    context['submit_text'] = '绑定'
    context['form'] = form
    context['return_back_url'] = redirect_to
    return render(request, 'blogger/bind_email.html', context)

#发送邮箱验证
def send_verification_code(request):
    email = request.GET.get('email', '')
    send_for=request.GET.get('send_for','')
    data = {}
    if email != '':
        # 生成验证码
        code = ''.join(random.sample(string.ascii_letters + string.digits, 4))
        now = int(time.time())
        send_code_time = request.session.get('send_code_time', 0)
        if now - send_code_time < 30:
            data['status'] = 'ERROR'
        else:
            request.session[send_for] = code
            request.session['send_code_time'] = now
            # 发送邮件
            sender = settings.EMAIL_FROM
            send_mail(
                '绑定邮箱',  # 邮件主题
                '验证码：%s' % code,  # 邮件内容
                sender,  # 发送者信息
                [email],  # 接收者邮箱地址
                fail_silently=False,  # 是否报错误
                # (如果要发送html代码显示，则邮件地址要显示为空并且要代以下内容，则 #html_message='<h1>%s, 欢迎您成为天天生鲜注册会员</h1>请点击下面链接激活您的账户<br/>' \
                # '<a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>'\
                #  % (username, token, token)
                # html_message=html_message)

            )
            data['status'] = 'SUCCESS'
    else:
        data['status'] = 'ERROR'
    return JsonResponse(data)

#修改密码
def change_password(request):
    redirect_to=reverse('blooger:home')
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST, user=request.user)
        if form.is_valid():
            user = request.user
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()
            auth.logout(request)

            return redirect(redirect_to)
    else:
        form = ChangePasswordForm()
    context = {}
    context['page_title'] = '修改密码'
    context['form_title'] = '修改密码'
    context['submit_text'] = '修改'
    context['form'] = form
    context['return_back_url'] = redirect_to
    return render(request, 'blogger/form.html', context)

#重置密码
def forgot_password(request):
    redirect_to = reverse('blooger:login')
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST, request=request)
        if form.is_valid():
            email = form.cleaned_data['email']
            new_password = form.cleaned_data['new_password']
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            # 清除session
            del request.session['forgot_password_code']
            return redirect(redirect_to)
    else:
        form = ForgotPasswordForm()

    context = {}
    context['page_title'] = '重置密码'
    context['form_title'] = '重置密码'
    context['submit_text'] = '重置'
    context['form'] = form
    context['return_back_url'] = redirect_to
    return render(request, 'blogger/forgot_password.html', context)
