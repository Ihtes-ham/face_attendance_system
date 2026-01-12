from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q, Count
import json

from .models import Attendance
from users.models import Employee

try:
    from .utils import FaceRecognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False


@login_required
def mark_attendance(request):
    """
    View to mark attendance using face recognition
    """
    if request.method == 'POST':
        try:
            # Check if face recognition is available
            if not FACE_RECOGNITION_AVAILABLE:
                messages.error(request, "❌ Face recognition system is not available!")
                return redirect('mark_attendance')

            # Get all employees with face encodings
            employees_with_faces = Employee.objects.filter(
                face_encoding__isnull=False,
                is_active=True
            )

            if not employees_with_faces.exists():
                messages.error(request, "❌ No employees with registered faces found! Please register faces first.")
                return redirect('mark_attendance')

            # Prepare known encodings dictionary
            known_encodings = {}
            for emp in employees_with_faces:
                encoding = emp.get_face_encoding_list()
                if encoding:
                    known_encodings[emp.employee_id] = encoding

            print(f"🎯 Starting face recognition with {len(known_encodings)} registered faces...")

            # REAL face recognition
            employee_id, message = FaceRecognition.recognize_face_from_camera(known_encodings)

            if employee_id:
                # Get employee
                employee = Employee.objects.get(employee_id=employee_id, is_active=True)
                today = timezone.now().date()
                current_time = timezone.now()

                # Check if already marked attendance today
                existing_attendance = Attendance.objects.filter(
                    employee=employee,
                    date=today
                ).first()

                if existing_attendance:
                    # Update time_out if marking departure
                    if not existing_attendance.time_out:
                        existing_attendance.time_out = current_time.time()
                        existing_attendance.save()
                        messages.success(request,
                                         f"✅ Departure recorded for {employee.user.get_full_name()} at {current_time.strftime('%H:%M:%S')}!")
                    else:
                        messages.warning(request,
                                         f"⏰ Attendance already completed for {employee.user.get_full_name()} today!")
                else:
                    # Create attendance record for arrival
                    Attendance.objects.create(
                        employee=employee,
                        status='present'
                    )
                    messages.success(request,
                                     f"✅ Attendance marked for {employee.user.get_full_name()} at {current_time.strftime('%H:%M:%S')}!")

                messages.info(request, f"🔍 {message}")
                return redirect('mark_attendance')

            else:
                messages.error(request, f"❌ Face recognition failed: {message}")
                return redirect('mark_attendance')

        except Employee.DoesNotExist:
            messages.error(request, "❌ Employee not found or inactive!")
        except Exception as e:
            messages.error(request, f"❌ Error marking attendance: {str(e)}")

    # Get today's attendance and stats for display
    today = timezone.now().date()
    today_attendance = Attendance.objects.filter(date=today).select_related('employee__user')
    total_employees = Employee.objects.filter(is_active=True).count()
    employees_with_faces = Employee.objects.filter(face_encoding__isnull=False, is_active=True).count()

    context = {
        'today_attendance': today_attendance,
        'employees_count': total_employees,
        'faces_count': employees_with_faces,
        'face_recognition_available': FACE_RECOGNITION_AVAILABLE,
    }

    return render(request, 'attendance/mark_attendance.html', context)


@login_required
def attendance_records(request):
    """
    View to display attendance records with filtering options
    """
    records = Attendance.objects.select_related('employee__user').all().order_by('-date', '-time_in')

    # Date filtering
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    employee_id = request.GET.get('employee_id')
    status_filter = request.GET.get('status')

    if start_date:
        records = records.filter(date__gte=start_date)
    if end_date:
        records = records.filter(date__lte=end_date)
    if employee_id:
        records = records.filter(employee__employee_id=employee_id)
    if status_filter:
        records = records.filter(status=status_filter)

    context = {
        'records': records,
        'employees': Employee.objects.filter(is_active=True),
        'status_choices': Attendance.ATTENDANCE_STATUS,
    }

    return render(request, 'attendance/records.html', context)


@login_required
def attendance_dashboard(request):
    """
    Dashboard view with attendance statistics
    """
    today = timezone.now().date()
    current_month = timezone.now().month
    current_year = timezone.now().year

    # Get statistics
    total_employees = Employee.objects.filter(is_active=True).count()
    present_today = Attendance.objects.filter(date=today).count()
    employees_with_faces = Employee.objects.filter(face_encoding__isnull=False, is_active=True).count()

    # Monthly statistics
    monthly_attendance = Attendance.objects.filter(
        date__year=current_year,
        date__month=current_month
    ).count()

    # Get recent attendance
    recent_attendance = Attendance.objects.select_related('employee__user').filter(
        date=today
    ).order_by('-time_in')[:10]

    # Get attendance by status for today
    today_status = Attendance.objects.filter(date=today).values('status').annotate(
        count=Count('status')
    )

    context = {
        'today': today,
        'total_employees': total_employees,
        'present_today': present_today,
        'employees_with_faces': employees_with_faces,
        'monthly_attendance': monthly_attendance,
        'recent_attendance': recent_attendance,
        'today_status': today_status,
        'face_recognition_available': FACE_RECOGNITION_AVAILABLE,
    }

    return render(request, 'attendance/dashboard.html', context)


@login_required
def manual_attendance(request):
    """
    Manual attendance marking for admin/staff
    """
    if not request.user.is_staff:
        messages.error(request, "❌ You don't have permission to access this page.")
        return redirect('dashboard')

    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        date = request.POST.get('date')
        status = request.POST.get('status')

        try:
            employee = Employee.objects.get(employee_id=employee_id, is_active=True)

            # Check if attendance already exists for this date
            existing = Attendance.objects.filter(employee=employee, date=date).first()
            if existing:
                messages.warning(request, f"Attendance already exists for {employee.user.get_full_name()} on {date}")
            else:
                Attendance.objects.create(
                    employee=employee,
                    date=date,
                    status=status
                )
                messages.success(request, f"✅ Manual attendance marked for {employee.user.get_full_name()}")
                return redirect('attendance_records')

        except Employee.DoesNotExist:
            messages.error(request, "❌ Employee not found!")
        except Exception as e:
            messages.error(request, f"❌ Error: {str(e)}")

    context = {
        'employees': Employee.objects.filter(is_active=True),
        'status_choices': Attendance.ATTENDANCE_STATUS,
    }

    return render(request, 'attendance/manual_attendance.html', context)


@login_required
def register_face(request):
    """
    View to register employee faces
    """
    if not request.user.is_staff:
        messages.error(request, "❌ You don't have permission to access this page.")
        return redirect('dashboard')

    if request.method == 'POST':
        try:
            employee_id = request.POST.get('employee_id')
            face_image = request.FILES.get('face_image')

            print(f"DEBUG: Starting face registration for employee: {employee_id}")

            if not employee_id or not face_image:
                messages.error(request, "❌ Please select employee and upload image")
                return redirect('register_face')

            # Get employee
            try:
                employee = Employee.objects.get(employee_id=employee_id, is_active=True)
                print(f"DEBUG: Found employee: {employee.user.get_full_name()}")
            except Employee.DoesNotExist:
                messages.error(request, f"❌ Employee with ID '{employee_id}' not found or inactive!")
                return redirect('register_face')

            # Check if face already registered
            if employee.face_encoding:
                messages.warning(request, f"⚠️ Face already registered for {employee.user.get_full_name()}")
                return redirect('register_face')

            # Verify single face
            print("DEBUG: Verifying single face...")
            is_valid, verify_message = FaceRecognition.verify_single_face(face_image)
            print(f"DEBUG: Face verification result: {is_valid}, message: {verify_message}")

            if not is_valid:
                messages.error(request, verify_message)
                return redirect('register_face')

            # Encode face
            print("DEBUG: Encoding face...")
            result = FaceRecognition.encode_face_from_image(face_image)
            print(f"DEBUG: Face encoding result: {result}")

            # Check if result is None or not a tuple
            if result is None:
                messages.error(request, "❌ Face encoding failed: No result returned")
                return redirect('register_face')

            if not isinstance(result, tuple) or len(result) != 2:
                messages.error(request, f"❌ Face encoding failed: Invalid result format: {result}")
                return redirect('register_face')

            encoding, message = result

            if encoding:
                # Save encoding to employee
                employee.face_encoding = json.dumps(encoding)
                employee.save()
                messages.success(request, f"✅ Face registered successfully for {employee.user.get_full_name()}")
                messages.info(request, f"🔍 {message}")
                return redirect('face_registration_success')
            else:
                messages.error(request, f"❌ {message}")

        except Employee.DoesNotExist:
            messages.error(request, "❌ Employee not found!")
        except Exception as e:
            messages.error(request, f"❌ Error registering face: {str(e)}")
            print(f"DEBUG: Exception in register_face: {str(e)}")

    # Get employees without face encodings
    employees_without_faces = Employee.objects.filter(
        is_active=True,
        face_encoding__isnull=True
    )

    context = {
        'employees': employees_without_faces,
        'face_recognition_available': FACE_RECOGNITION_AVAILABLE,
    }
    return render(request, 'attendance/register_face.html', context)


@login_required
def face_registration_success(request):
    """
    Success page after face registration
    """
    return render(request, 'attendance/face_registration_success.html')


@login_required
def manage_faces(request):
    """
    View to manage registered faces
    """
    if not request.user.is_staff:
        messages.error(request, "❌ You don't have permission to access this page.")
        return redirect('dashboard')

    # Get employees with and without face encodings
    employees_with_faces = Employee.objects.filter(
        face_encoding__isnull=False,
        is_active=True
    ).select_related('user')

    employees_without_faces = Employee.objects.filter(
        face_encoding__isnull=True,
        is_active=True
    ).select_related('user')

    context = {
        'employees_with_faces': employees_with_faces,
        'employees_without_faces': employees_without_faces,
        'face_recognition_available': FACE_RECOGNITION_AVAILABLE,
    }
    return render(request, 'attendance/manage_faces.html', context)


@login_required
def delete_face(request, employee_id):
    """
    View to delete face data for an employee
    """
    if not request.user.is_staff:
        messages.error(request, "❌ You don't have permission to access this page.")
        return redirect('dashboard')

    if request.method == 'POST':
        try:
            employee = Employee.objects.get(employee_id=employee_id, is_active=True)
            employee.face_encoding = None
            employee.save()
            messages.success(request, f"✅ Face data deleted for {employee.user.get_full_name()}")
        except Employee.DoesNotExist:
            messages.error(request, "❌ Employee not found!")
        except Exception as e:
            messages.error(request, f"❌ Error deleting face data: {str(e)}")

    return redirect('manage_faces')