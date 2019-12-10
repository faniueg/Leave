import uuid
from django.core.cache import cache
from rest_framework.exceptions import ValidationError
from staff.models import Staff

def generate_token():
    token = uuid.uuid4().hex
    return token

def is_login(request):
    try:
        token = request.query_params.get('token')
        staff_id = cache.get(token)
        staff = Staff.objects.get(pk=staff_id)
    except Exception as e:
        raise ValidationError(detail="请先登录")
    return staff

def is_leader(request):
    try:
        token = request.query_params.get('token')
        staff_id = cache.get(token)
        staff = Staff.objects.get(pk=staff_id)
    except Exception as e:
        raise ValidationError(detail="请先登录")
    if not staff.is_leader:
        raise ValidationError(detail="抱歉，您没有权限执行此操作")
    return staff

