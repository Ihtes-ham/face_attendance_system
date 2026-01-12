from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .models import LeaveRequest
from users.models import Employee


@login_required
def submit_leave(request):
    """Employee submits leave request"""
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        messages.error(request, "Employee profile not found!")
        return redirect('dashboard')

    if request.method == 'POST':
        try:
            leave_type = request.POST.get('leave_type')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            reason = request.POST.get('reason')

            # Basic validation
            if not all([leave_type, start_date, end_date, reason]):
                messages.error(request, "All fields are required!")
                return redirect('submit_leave')

            # Create leave request
            leave_request = LeaveRequest.objects.create(
                employee=employee,
                leave_type=leave_type,
                start_date=start_date,
                end_date=end_date,
                reason=reason
            )

            # Send email notification to admin (if email configured)
            try:
                send_leave_notification(leave_request, 'submitted')
                messages.success(request, "✅ Leave request submitted successfully! Admin will be notified.")
            except:
                messages.success(request, "✅ Leave request submitted successfully!")

            return redirect('my_leaves')

        except Exception as e:
            messages.error(request, f"Error submitting leave request: {str(e)}")

    return render(request, 'attendance/submit_leave.html', {
        'leave_types': LeaveRequest.LEAVE_TYPES
    })


@login_required
def my_leaves(request):
    """Employee views their leave requests"""
    try:
        employee = Employee.objects.get(user=request.user)
        leaves = LeaveRequest.objects.filter(employee=employee).order_by('-applied_on')
    except Employee.DoesNotExist:
        messages.error(request, "Employee profile not found!")
        return redirect('dashboard')

    return render(request, 'attendance/my_leaves.html', {
        'leaves': leaves
    })


@login_required
def manage_leaves(request):
    """Admin manages all leave requests"""
    if not request.user.is_staff:
        messages.error(request, "Access denied!")
        return redirect('dashboard')

    leaves = LeaveRequest.objects.select_related('employee__user').all().order_by('-applied_on')

    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        leaves = leaves.filter(status=status_filter)

    return render(request, 'attendance/manage_leaves.html', {
        'leaves': leaves,
        'status_filter': status_filter
    })


@login_required
def approve_leave(request, leave_id):
    """Admin approves a leave request"""
    if not request.user.is_staff:
        messages.error(request, "Access denied!")
        return redirect('dashboard')

    leave = get_object_or_404(LeaveRequest, id=leave_id)
    leave.status = 'approved'
    leave.reviewed_by = request.user
    leave.reviewed_on = timezone.now()
    leave.save()

    # Send approval email
    try:
        send_leave_notification(leave, 'approved')
        messages.success(request, f"✅ Leave request approved! {leave.employee.user.get_full_name()} has been notified.")
    except:
        messages.success(request, f"✅ Leave request approved!")

    return redirect('manage_leaves')


@login_required
def reject_leave(request, leave_id):
    """Admin rejects a leave request"""
    if not request.user.is_staff:
        messages.error(request, "Access denied!")
        return redirect('dashboard')

    leave = get_object_or_404(LeaveRequest, id=leave_id)

    if request.method == 'POST':
        admin_notes = request.POST.get('admin_notes', '')
        leave.status = 'rejected'
        leave.reviewed_by = request.user
        leave.reviewed_on = timezone.now()
        leave.admin_notes = admin_notes
        leave.save()

        # Send rejection email
        try:
            send_leave_notification(leave, 'rejected')
            messages.success(request,
                             f"❌ Leave request rejected! {leave.employee.user.get_full_name()} has been notified.")
        except:
            messages.success(request, f"❌ Leave request rejected!")

        return redirect('manage_leaves')

    return render(request, 'attendance/reject_leave.html', {
        'leave': leave
    })


def send_leave_notification(leave_request, action):
    """Send email notification for leave actions"""
    if not settings.EMAIL_HOST_USER:  # Check if email is configured
        return

    subject = f"Leave Request {action.capitalize()} - {leave_request.employee.user.get_full_name()}"

    context = {
        'leave': leave_request,
        'action': action,
        'employee': leave_request.employee,
    }

    if action == 'submitted':
        # Send to admin
        recipient = 'admin@company.com'  # Replace with actual admin email
        template = 'emails/leave_submitted.html'
    else:
        # Send to employee
        recipient = leave_request.employee.user.email
        template = f'emails/leave_{action}.html'

    message = render_to_string(template, context)

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
            html_message=message,
            fail_silently=True
        )
    except Exception as e:
        print(f"Email sending failed: {e}")