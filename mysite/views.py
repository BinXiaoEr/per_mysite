from haystack.views import SearchView
from django.db.models import Count
from blog.models import BlogType, Blog
from django.core.paginator import *  # 导入分页功能
each_page_blogs_number=6

class MySearchView(SearchView):
    def extra_context(self):
        context = super(MySearchView, self).extra_context()
        blog_type_list = BlogType.objects.annotate(blog_count=Count('blog'))
        paginator = Paginator(self.results, each_page_blogs_number)
        page_num = self.request.GET.get('page', 1)
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
        blog_date_dict = {}
        blog_dates = Blog.objects.dates('create_time', 'month', order='ASC')
        for blog_date in blog_dates:
            blog_count = Blog.objects.filter(create_time__year=blog_date.year,
                                             create_time__month=blog_date.month).count()
            blog_date_dict[blog_date] = blog_count
        context['blog_types'] = blog_type_list
        context['blog_dates'] = blog_date_dict
        context['page_range'] = page_range
        return context

