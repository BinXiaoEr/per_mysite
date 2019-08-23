from django.shortcuts import render
from .models import *
from django.core.paginator import Paginator
from django.db.models import Count
import markdown
from read_statistic.utils import *
from django.contrib.contenttypes.models import ContentType
from comment.models import Comment
from comment.forms import CommentForm
from blooger.forms import LoginForm
each_page_blogs_number = 12

# 获取分页信息
def get_blog_list_common_date(request, blogs_all_list):
    paginator = Paginator(blogs_all_list, each_page_blogs_number)
    # 获取页码参数get请求page=?,后面的1是默认
    page_num = request.GET.get('page', 1)
    # 具体页码的对应的model数
    page_of_blogs = paginator.get_page(page_num)
    #只显示当前页的周围4个,不显示所有标签
    page_range = [x for x in range(int(page_num) - 1, int(page_num) + 2) if 0 < x <= paginator.num_pages]
    # 加上省略页码范围 当距离第一和最后过多时省略中间 显示第一个页码标签和最后一个页码标签
    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')
    if page_range[0] != 1:
        page_range.insert(0, 1)
        # 加入第一页
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)
        # 加入最后一页
    # 获取博客分类的对应博客数量
    blog_type_list = BlogType.objects.annotate(blog_count=Count('blog'))
    # 获取日期归档对应的博客数量
    blog_dates = Blog.objects.dates('create_time', 'month', order='DESC')
    #存放按月统计的博客数量w
    blog_date_dict = {}

    for blog_date in blog_dates:
        blog_count = Blog.objects.filter(create_time__year=blog_date.year, create_time__month=blog_date.month).count()
        
        blog_date_dict[blog_date] = blog_count
        
    context = {}
    # 导航栏列表博客类型
    context['blog_types'] = blog_type_list
    # 分页后每页的博客
    context['page_of_blogs'] = page_of_blogs
    # 底部页码展示
    context['page_range'] = page_range
    #每月有多少篇博客
    context['blog_dates'] = blog_date_dict
    return context


# 获取博客页列表
def blog_list(request):
    blogs_all_list = Blog.objects.all()
    context = get_blog_list_common_date(request, blogs_all_list)

    return render(request, 'blog/blog_list.html', context)


# 按博客类型展示
def blog_type(request, type):
    blogtype = BlogType.objects.get(type_name=type)
    blogs_all_list = Blog.objects.filter(blog_type=blogtype)
    context = get_blog_list_common_date(request, blogs_all_list)
    context['blog_type'] = type  # 显示当前博客类型
    return render(request, 'blog/blog_with_type.html', context)


# 按博客日期展示
def blog_with_date(request, year, month):
    blogs_all_list = Blog.objects.filter(create_time__year=year, create_time__month=month)
    context = get_blog_list_common_date(request, blogs_all_list)
    context['blog_with_date'] = "%s年%s月" % (year, month)
    return render(request, 'blog/blog_with_date.html', context)


# 博客详情页
def blog_detail(request, pk):
    context = {}
    blog = Blog.objects.get(id=pk)
    blog.content = markdown.markdown(blog.content.replace("\r\n", ' \n'), extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        'markdown.extensions.toc'
    ])

    read_cookie_key = read_statistics_once_read(request, blog)
    # 自定义计数规则
    context['blog'] = blog
    context['previous_blog'] = Blog.objects.filter(create_time__gt=blog.create_time).last()  # 上一篇博客 因为排序是倒过来
    context['next_blog'] = Blog.objects.filter(create_time__lt=blog.create_time).first()
    #获取对应博客的评论内容
    blog_content_type=ContentType.objects.get_for_model(blog)
    comment=Comment.objects.filter(content_type=blog_content_type,object_id=pk,parent=None)
    context['comments']=comment
    #对form表单进行初始化
    data={}
    data['content_type']=blog_content_type.model
    data['object_id']=pk
    data['reply_comment_id']=0
    context['login_form']=LoginForm()
    context['comment_form']=CommentForm(initial=data)#传递一个form表单类
    response = render(request, 'blog/blog_detail.html', context)
    response.set_cookie(read_cookie_key, 'true')
    return response

