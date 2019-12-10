from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from django.db import models


# 部门表
class Department(models.Model):
    # 部门名称
    dp_name = models.CharField(max_length=64,null=False)

    def __str__(self):
        return self.dp_name

    class Meta:
        db_table = 'department'
        app_label = 'leave'


# 员工表
class Staff(models.Model):
    # 员工名字  密码  邮箱  性别  部门  是否领导  是否删除
    staff_name = models.CharField(max_length=16)
    _password = models.CharField(max_length=256, null=False)
    email = models.CharField(max_length=64, null=False)
    gender = models.CharField(choices=(('girl','女'),('boy','男')),max_length=5,default='boy')
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    is_leader = models.BooleanField(default=0)
    is_delete = models.BooleanField(default=0)

    def __str__(self):
        return self.staff_name

    @property
    def password(self):
        return Exception("can't get password")

    @password.setter
    def password(self, password):
        self._password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self._password, password)

    class Meta:
        db_table = 'staff'
        app_label = 'leave'


# 请假表
class LeaveTable(models.Model):
    # 请假员工  请假员工部门  请假日期  请假时长  是否审批
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    leave_start_datetime = models.DateTimeField(default=datetime.now)
    leave_days = models.IntegerField(default=1)
    is_approval = models.BooleanField(default=0)

    def __str__(self):
        return self.staff.staff_name+'请假了'+str(self.leave_days)+'天'

    class Meta:
        db_table = 'leave_table'
        app_label = 'leave'
