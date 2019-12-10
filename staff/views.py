from django.core.cache import cache

from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.generics import ListCreateAPIView, ListAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response

from staff.models import Staff, Department, LeaveTable
from staff.serializers import StaffSerializer, DepartmentSerializer, LeaveTableSerializer
from utils import generate_token, is_login, is_leader


# 员工登录注册
class StaffAPIView(ListCreateAPIView):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer

    def get(self, request, *args, **kwargs):
        staff_list = Staff.objects.all()
        data = {
            'status': 200,
            'msg': 'select staff success',
            'staff': []
        }
        for staff in staff_list:
            data['staff'].append({'id': staff.id,
                                   'staff_name': staff.staff_name,
                                   'email': staff.email,
                                   'department': staff.department.dp_name,
                                   'is_leader': staff.is_leader,
                                   'is_delete':staff.is_delete})
        return Response(data)

    def post(self, request, *args, **kwargs):
        action = request.query_params.get('action')
        if action == 'register':
            staff_name = request.data.get('staff_name')
            password = request.data.get('password')
            email = request.data.get('email')
            department = request.data.get('department')
            dp = Department.objects.get(pk=department)
            is_leader = request.data.get('is_leader')
            staff=Staff()
            staff.staff_name=staff_name
            staff.password=password
            staff.email=email
            staff.department=dp
            if is_leader:
                staff.is_leader = is_leader
            staff.save()

            data = {
                'status': 200,
                'msg': 'create staff success',
                'staff': {
                    'id': staff.id,
                    'staff_name': staff.staff_name,
                    'email': staff.email,
                    'department': staff.department.dp_name,
                    'is_leader': staff.is_leader,
                    'is_delete':staff.is_delete
                }
            }
            return Response(data)
        elif action == 'login':
            return self.login(request,*args,**kwargs)
        else:
            raise ValidationError(detail='请提供正确的请求动作')

    def login(self, request,*args, **kwargs):
        staff_name = request.data.get('staff_name')
        password = request.data.get('password')

        try:
            staff = Staff.objects.get(staff_name=staff_name)

        except Exception as e:
            raise ValidationError(detail="员工不存在")

        if staff.is_delete:
            raise PermissionDenied(detail="员工已离职")

        if not staff.check_password(password):
            raise ValidationError(detail='密码错误')

        token = generate_token()
        cache.set(token, staff.id, timeout=60*60*24)

        data = {
            'status': 200,
            'msg': '员工登陆成功',
            'token': token,
            'staff': {
                'id': staff.id,
                'staff_name': staff.staff_name,
                'department': staff.department.dp_name,
                'email': staff.email,
                'is_leader':staff.is_leader,
                'is_delete':staff.is_delete
            }
        }
        return Response(data)


# 部门创建查看
class DepartmentAPIView(ListCreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

    def post(self, request, *args, **kwargs):

        dp_name = request.data.get('dp_name')
        dp = Department()
        dp.dp_name=dp_name

        dp.save()
        data = {
            'status': 200,
            'msg': '部门创建成功',
            'department':{
                'id':dp.id,
                'dp_name':dp.dp_name
            }
        }
        return Response(data)

    def get(self, request, *args, **kwargs):
        dp_list = Department.objects.all()
        data = {
            'status':200,
            'msg': '查找成功',
            'dp_list': []
        }
        for dp in dp_list:
            data['dp_list'].append({'id':dp.id,'dp_name':dp.dp_name})
        return Response(data)


# 请假条创建查看
class LeaveAPIView(ListCreateAPIView):
    queryset = LeaveTable.objects.all()
    serializer_class = LeaveTableSerializer

    def get(self, request, *args, **kwargs):
        staff = is_login(request)
        leaves = LeaveTable.objects.filter(staff=staff)
        data = {
            'status': 200,
            'msg': '您的请假条如下所示：',
            'leave': []
        }
        for leave in leaves:
            data['leave'].append({'id': leave.id,
                                   'staff': leave.staff.staff_name,
                                   'department': leave.department.dp_name,
                                   'leave_start_datetime': leave.leave_start_datetime,
                                   'leave_days': leave.leave_days,
                                   'is_approval': leave.is_approval})
        return Response(data)

    def post(self, request, *args, **kwargs):

        staff = is_login(request)
        department = Department.objects.get(pk=staff.department.id)
        leave_start_datetime = request.data.get('leave_start_datetime', '')
        leave_days = request.data.get('leave_days', '')
        leave = LeaveTable()
        leave.staff=staff
        leave.department=department
        if leave_start_datetime:
            leave.leave_start_datetime=leave_start_datetime
        if leave_days:
            leave.leave_days = leave_days
        leave.save()
        data = {
            'status': 200,
            'msg': '请假条已创建，等待领导审批',
            'leave': {
                'id': leave.id,
                'staff': leave.staff.staff_name,
                'department':leave.department.dp_name,
                'leave_start_datetime': leave.leave_start_datetime,
                'leave_days': leave.leave_days,
                'is_approval': leave.is_approval
            }
        }
        return Response(data)


# 领导查看本部门请假条
class ApprovalListAPIView(ListAPIView):
    queryset = LeaveTable.objects.all()
    serializer_class = LeaveTableSerializer

    def get(self, request, *args, **kwargs):
        staff = is_leader(request)

        dp = staff.department
        leaves = LeaveTable.objects.filter(department=dp)
        data = {
            'status': 200,
            'msg': '您部门的请假条如下：',
            'leave': []
        }
        for leave in leaves:
            data['leave'].append({'id': leave.id,
                                   'staff': leave.staff.staff_name,
                                   'department': leave.department.dp_name,
                                   'leave_start_datetime': leave.leave_start_datetime,
                                   'leave_days': leave.leave_days,
                                   'is_approval': leave.is_approval})
        return Response(data)


# 请假条审批
class ApprovalAPIView(RetrieveUpdateAPIView):
    queryset = LeaveTable.objects.all()
    serializer_class = LeaveTableSerializer
    lookup_field = 'pk'

    def get(self, request, *args, **kwargs):
        staff = is_leader(request)
        leave_id = self.kwargs['pk']
        try:
            leave = LeaveTable.objects.get(pk=leave_id)
            data = {
                'status': 200,
                'msg': 'ok',
                'leave': {
                    'id': leave.id,
                    'staff': leave.staff.staff_name,
                    'department': leave.department.dp_name,
                    'leave_start_datetime': leave.leave_start_datetime,
                    'leave_days': leave.leave_days,
                    'is_approval': leave.is_approval
                }
            }
        except Exception as e:
            raise ValidationError(detail="cuowu")

        return Response(data)

    def put(self, request, *args, **kwargs):
        staff = is_leader(request)
        leave_id = self.kwargs['pk']
        leave = LeaveTable.objects.get(pk=leave_id)
        leave.is_approval = 1
        leave.save()
        data = {
            'status': 200,
            'msg': '假条审批成功',
            'leave': {
                'id': leave.id,
                'staff': leave.staff.staff_name,
                'department': leave.department.dp_name,
                'leave_start_datetime': leave.leave_start_datetime,
                'leave_days': leave.leave_days,
                'is_approval': leave.is_approval
            }
        }
        return Response(data)
