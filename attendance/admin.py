from django.contrib import admin
from django.utils import timezone
from .models import Attendance, LeaveRequest


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'time_in', 'time_out', 'status']
    list_filter = ['date', 'status']
    search_fields = ['employee__user__first_name', 'employee__user__last_name', 'employee__employee_id']
    list_editable = ['status']
    date_hierarchy = 'date'


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'start_date', 'end_date', 'status', 'applied_on', 'duration_days']
    list_filter = ['status', 'leave_type', 'applied_on']
    list_editable = ['status']
    search_fields = ['employee__user__first_name', 'employee__user__last_name', 'employee__employee_id']
    date_hierarchy = 'applied_on'
    readonly_fields = ['applied_on', 'duration_days']
    actions = ['approve_leaves', 'reject_leaves']

    def duration_days(self, obj):
        return obj.duration()
    duration_days.short_description = 'Duration (Days)'

    def approve_leaves(self, request, queryset):
        updated = queryset.update(status='approved', reviewed_by=request.user, reviewed_on=timezone.now())
        self.message_user(request, f'{updated} leave requests approved.')

    approve_leaves.short_description = "Approve selected leaves"

    def reject_leaves(self, request, queryset):
        updated = queryset.update(status='rejected', reviewed_by=request.user, reviewed_on=timezone.now())
        self.message_user(request, f'{updated} leave requests rejected.')

    reject_leaves.short_description = "Reject selected leaves"