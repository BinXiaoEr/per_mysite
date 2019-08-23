import datetime
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Sum
from .models import ReadNum, ReadDetail
from django.db.models import Sum
from .models import IpDeatil


def read_statistics_once_read(request, obj):
    ct = ContentType.objects.get_for_model(obj)
    key = "%s_%s_read" % (ct.model, obj.pk)

    if not request.COOKIES.get(key):
        # 总阅读数 +1
        # 创建或者获取的操作省略了很多 如果有对应字段就获取，没有对应查询就创建
        readnum, created = ReadNum.objects.get_or_create(
            content_type=ct, object_id=obj.pk)
        readnum.read_num += 1
        readnum.save()
        # 当天阅读数 +1
        date = timezone.now().date()
        readDetail, created = ReadDetail.objects.get_or_create(
            content_type=ct, object_id=obj.pk, date=date)
        readDetail.read_num += 1
        readDetail.save()
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            ip = request.META['HTTP_X_FORWARDED_FOR']
        else:
            ip = request.META['REMOTE_ADDR']
        if IpDeatil.objects.filter(ip=ip):
            ipdeatil = IpDeatil.objects.get(ip=ip)
            ipdeatil.id_blog += str(obj.id)+','
            ipdeatil.ip_count += 1
            ipdeatil.save()
        else:
            today = timezone.now().date()
            ipdeatil = IpDeatil(date=today, ip=ip,id_blog=str(obj.pk), ip_count=1)
            ipdeatil.save()
    return key


def get_seven_days_read_data(content_type):
    today = timezone.now().date()
    read_nums = []
    dates = []
    for i in range(6, -1, -1):
        date = today-datetime.timedelta(days=i)
        dates.append(date.strftime("%m/%d"))
        read_detail = ReadDetail.objects.filter(
            content_type=content_type, date=date)
        result = read_detail.aggregate(read_num_sum=Sum('read_num'))
        read_nums.append(result['read_num_sum']or 0)
    return dates, read_nums


def get_today_hot_data(content_type):
    today = timezone.now().date()
    read_detail = ReadDetail.objects.filter(
        content_type=content_type, date=today).order_by('-read_num')
    return read_detail[:4]


def get_yesterday_hot_data(content_type):
    today = timezone.now().date()
    yes = today-datetime.timedelta(days=1)
    read_detail = ReadDetail.objects.filter(
        content_type=content_type, date=yes).order_by('-read_num')
    return read_detail[:4]
