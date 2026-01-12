from django.db import models
from django.conf import settings
from users.models import Employee


class Attendance(models.Model):
    ATTENDANCE_STATUS = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('half_day', 'Half Day'),
    )

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    time_in = models.TimeField(auto_now_add=True)
    time_out = models.TimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=ATTENDANCE_STATUS, default='present')

    class Meta:
        unique_together = ['employee', 'date']
        ordering = ['-date', 'employee']

    def __str__(self):
        return f"{self.employee} - {self.date}"

    def working_hours(self):
        """Calculate working hours if time_out is recorded"""
        if self.time_out:
            from datetime import datetime, date
            # Combine date with time_in and time_out
            datetime_in = datetime.combine(self.date, self.time_in)
            datetime_out = datetime.combine(self.date, self.time_out)
            duration = datetime_out - datetime_in
            hours = duration.total_seconds() / 3600
            return round(hours, 2)
        return None


class LeaveRequest(models.Model):
    LEAVE_TYPES = (
        ('sick', 'Sick Leave'),
        ('casual', 'Casual Leave'),
        ('emergency', 'Emergency Leave'),
        ('vacation', 'Vacation'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES, default='casual')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_on = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_leaves'
    )
    reviewed_on = models.DateTimeField(null=True, blank=True)
    admin_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-applied_on']

    def __str__(self):
        return f"{self.employee} - {self.start_date} to {self.end_date} ({self.status})"

    def duration(self):
        """Calculate leave duration in days"""
        return (self.end_date - self.start_date).days + 1

    def is_approved(self):
        return self.status == 'approved'

    def is_pending(self):
        return self.status == 'pending'