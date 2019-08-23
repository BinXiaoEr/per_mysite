from django.template import Library
from comment.models import Comment
from django.contrib.contenttypes.models import ContentType
#创建一个library类的对象
register=Library()
@register.simple_tag
def get_comment_count(obj):
    content_type=ContentType.objects.get_for_model(obj)
    return Comment.objects.filter(content_type=content_type,object_id=obj.pk).count()