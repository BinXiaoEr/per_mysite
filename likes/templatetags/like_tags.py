from django.template import Library

from django.contrib.contenttypes.models import ContentType
from ..models import LikeCount,LikeRecord
#创建一个library类的对象
register=Library()
@register.simple_tag
def get_like_count(obj):
    content_type=ContentType.objects.get_for_model(obj)
    like_count, crea = LikeCount.objects.get_or_create(content_type=content_type, object_id=obj.id)
    return like_count.like_num
@register.simple_tag(takes_context=True)
def get_like_status(context,obj):
    content_type = ContentType.objects.get_for_model(obj)
    user = context['user']
    if not user.is_authenticated:
        return ''
    if LikeRecord.objects.filter(content_type=content_type, object_id=obj.pk, user=user).exists():
        return 'active'
    else:
        return ''

@register.simple_tag
def get_content_type(obj):
    content_type = ContentType.objects.get_for_model(obj)
    return content_type.model