from django.template import Library

from django.utils.safestring import mark_safe
import markdown

# 创建一个library类的对象
register = Library()

@register.filter
def custom_markdown(obj):
    return mark_safe(markdown.markdown(obj,
                                       extensions=['markdown.extensions.fenced_code', 'markdown.extensions.codehilite'],
                                       safe_mode=True,
                                       enable_attributes=False))


@register.filter
def show_markdown(obj):
    from django.utils.html import strip_tags
    obj= strip_tags(markdown.markdown(obj))

    return obj
