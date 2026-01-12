from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import send_mail
from django.conf import settings
from .models import CustomUser, Employee, Department
import re


def register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        try:
            # Get form data
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            username = request.POST.get('username', '').strip()
            email = request.POST.get('email', '').strip().lower()
            phone = request.POST.get('phone', '').strip()
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')

            # Validation
            errors = []

            if not all([first_name, last_name, username, email, password1, password2]):
                errors.append("All fields except phone are required!")

            if password1 != password2:
                errors.append("Passwords do not match!")

            if len(password1) < 8:
                errors.append("Password must be at least 8 characters long!")

            # Check username
            if CustomUser.objects.filter(username=username).exists():
                errors.append("Username already exists!")

            # Check email
            if CustomUser.objects.filter(email=email).exists():
                errors.append("Email already registered!")

            # Validate email format
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                errors.append("Invalid email format!")

            if errors:
                for error in errors:
                    messages.error(request, error)
                return redirect('users:register')

            # Create user
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                user_type='employee'
            )

            # Generate employee ID
            employee_count = Employee.objects.count()
            employee_id = f"EMP{str(employee_count + 1).zfill(4)}"

            # Create employee profile
            Employee.objects.create(
                user=user,
                employee_id=employee_id,
                is_active=True
            )

            # Send welcome email
            try:
                send_mail(
                    'Welcome to Face Attendance System',
                    f'Hello {first_name},\n\nYour account has been created successfully!\n\n'
                    f'Username: {username}\n'
                    f'Employee ID: {employee_id}\n\n'
                    f'Please login and register your face to start marking attendance.\n\n'
                    f'Best regards,\nAttendance System Team',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=True
                )
            except:
                pass

            messages.success(request, f"✅ Account created successfully! Your Employee ID is {employee_id}")
            messages.info(request, "Please login with your credentials")

            return redirect('login')

        except Exception as e:
            messages.error(request, f"❌ Error creating account: {str(e)}")
            return redirect('users:register')

    return render(request, 'registration/register.html')


@login_required
def profile(request):
    """User profile view"""
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        messages.error(request, "Employee profile not found!")
        return redirect('dashboard')

    if request.method == 'POST':
        try:
            # Update user information
            request.user.first_name = request.POST.get('first_name', '').strip()
            request.user.last_name = request.POST.get('last_name', '').strip()
            request.user.email = request.POST.get('email', '').strip()
            request.user.phone = request.POST.get('phone', '').strip()
            request.user.save()

            messages.success(request, "✅ Profile updated successfully!")
            return redirect('profile')

        except Exception as e:
            messages.error(request, f"❌ Error updating profile: {str(e)}")

    # Get attendance statistics
    from attendance.models import Attendance, LeaveRequest
    from django.utils import timezone
    from datetime import timedelta

    today = timezone.now().date()
    current_month = timezone.now().month
    current_year = timezone.now().year

    # Monthly attendance
    monthly_attendance = Attendance.objects.filter(
        employee=employee,
        date__year=current_year,
        date__month=current_month
    ).count()

    # Total attendance
    total_attendance = Attendance.objects.filter(employee=employee).count()

    # Pending leaves
    pending_leaves = LeaveRequest.objects.filter(
        employee=employee,
        status='pending'
    ).count()

    # Approved leaves this year
    approved_leaves = LeaveRequest.objects.filter(
        employee=employee,
        status='approved',
        start_date__year=current_year
    ).count()

    context = {
        'employee': employee,
        'monthly_attendance': monthly_attendance,
        'total_attendance': total_attendance,
        'pending_leaves': pending_leaves,
        'approved_leaves': approved_leaves,
    }

    return render(request, 'users/profile.html', context)


@login_required
def change_password(request):
    """Change password view"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "✅ Password changed successfully!")
            return redirect('profile')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'users/change_password.html', {'form': form})


@login_required
def employee_list(request):
    """View for displaying list of all employees"""
    if not request.user.is_staff:
        messages.error(request, "❌ Access denied! Admin only.")
        return redirect('dashboard')

    employees = Employee.objects.select_related('user', 'department').filter(
        is_active=True
    ).order_by('employee_id')

    # Filter by department if provided
    department_id = request.GET.get('department')
    if department_id:
        employees = employees.filter(department_id=department_id)

    # Filter by face registration status
    has_face = request.GET.get('has_face')
    if has_face == 'yes':
        employees = employees.filter(face_encoding__isnull=False)
    elif has_face == 'no':
        employees = employees.filter(face_encoding__isnull=True)

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        employees = employees.filter(
            user__first_name__icontains=search_query
        ) | employees.filter(
            user__last_name__icontains=search_query
        ) | employees.filter(
            employee_id__icontains=search_query
        )

    # Get all departments for filter
    departments = Department.objects.all()

    # Statistics
    total_employees = Employee.objects.filter(is_active=True).count()
    with_faces = Employee.objects.filter(is_active=True, face_encoding__isnull=False).count()
    without_faces = total_employees - with_faces

    context = {
        'employees': employees,
        'departments': departments,
        'total_employees': total_employees,
        'with_faces': with_faces,
        'without_faces': without_faces,
    }

    return render(request, 'users/employee_list.html', context)


def password_reset_request(request):
    """Password reset request view"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()

        try:
            user = CustomUser.objects.get(email=email)

            # In a real application, you would:
            # 1. Generate a password reset token
            # 2. Send email with reset link
            # 3. Create a password reset confirmation page

            messages.success(request, "✅ Password reset instructions have been sent to your email!")
            return redirect('login')

        except CustomUser.DoesNotExist:
            # Don't reveal if email exists or not (security)
            messages.success(request,
                             "✅ If an account exists with this email, password reset instructions have been sent!")
            return redirect('login')

    return render(request, 'registration/password_reset.html')