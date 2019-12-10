from rest_framework import serializers
from staff.models import Staff, Department, LeaveTable


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = ('id', 'staff_name', 'gender','is_leader','is_delete','department')


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ('id', 'dp_name')


class LeaveTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveTable
        fields = ('id', 'staff', 'department', 'leave_start_datetime', 'leave_days','is_approval')