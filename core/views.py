from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from users.models import Employee, Department
from attendance.models import Attendance
from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta
import json


def home(request):
    return render(request, 'core/home.html')


@login_required
def dashboard(request):
    # Get statistics
    total_employees = Employee.objects.filter(is_active=True).count()
    total_departments = Department.objects.count()

    today = timezone.now().date()
    present_today = Attendance.objects.filter(date=today, status='present').count()

    employees_with_faces = Employee.objects.filter(face_encoding__isnull=False).count()

    # Recent attendance (last 10 records)
    recent_attendance = Attendance.objects.select_related(
        'employee__user', 'employee__department'
    ).order_by('-date', '-time_in')[:10]

    # Department-wise stats
    department_stats = Department.objects.annotate(
        employee_count=Count('employee'),
        present_today_count=Count(
            'employee__attendance',
            filter=Q(employee__attendance__date=today, employee__attendance__status='present')
        )
    )

    # Weekly attendance trend (last 7 days)
    dates = []
    present_counts = []

    for i in range(7):
        date = today - timedelta(days=i)
        dates.append(date.strftime('%a'))
        count = Attendance.objects.filter(date=date, status='present').count()
        present_counts.append(count)

    dates.reverse()
    present_counts.reverse()

    # For the weekly trend in the template (alternative format)
    weekly_trend = []
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        count = Attendance.objects.filter(date=date, status='present').count()
        weekly_trend.append((date.strftime("%Y-%m-%d"), count))

    context = {
        'total_employees': total_employees,
        'total_departments': total_departments,
        'present_today': present_today,
        'employees_with_faces': employees_with_faces,
        'recent_attendance': recent_attendance,
        'department_stats': department_stats,
        'today': today,
        'attendance_dates': json.dumps(dates),
        'attendance_counts': json.dumps(present_counts),
        'weekly_trend': weekly_trend,
    }

    # ✅ CORRECTED TEMPLATE PATH
    return render(request, 'attendance/dashboard.html', context)

