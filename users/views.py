from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Employee
from attendance.utils import FaceRecognition
from django.conf import settings


@login_required
def register_face(request):
    """
    View for registering employee face with facial recognition
    """
    if request.method == 'POST' and request.FILES.get('face_image'):
        try:
            face_image = request.FILES['face_image']
            employee_id = request.POST.get('employee_id')

            if not employee_id:
                messages.error(request, "❌ Employee ID is required!")
                return redirect('register_face')

            # Get employee
            try:
                employee = Employee.objects.get(employee_id=employee_id)
            except Employee.DoesNotExist:
                messages.error(request, "❌ Employee not found!")
                return redirect('register_face')

            # Check if face already registered
            if employee.face_encoding:
                messages.warning(request, f"⚠️ Face already registered for {employee.user.get_full_name()}")
                return redirect('register_face')

            # Verify single face in image
            is_valid, verify_message = FaceRecognition.verify_single_face(face_image)
            if not is_valid:
                messages.error(request, f"❌ {verify_message}")
                return redirect('register_face')

            # Encode face
            encoding, message = FaceRecognition.encode_face_from_image(face_image)

            if encoding is not None:
                # Save face encoding and image to employee
                employee.set_face_encoding(encoding)
                employee.face_image = face_image
                employee.save()

                messages.success(request, f"✅ Face registered successfully for {employee.user.get_full_name()}")
                if message:
                    messages.info(request, f"🔍 {message}")
                return redirect('employee_list')
            else:
                messages.error(request, f"❌ Face registration failed: {message}")
                return redirect('register_face')

        except Exception as e:
            messages.error(request, f"❌ Error registering face: {str(e)}")
            return redirect('register_face')

    # GET request - show registration form
    employees = Employee.objects.filter(is_active=True, face_encoding__isnull=True)

    # Check if face recognition is available
    face_recognition_available = getattr(settings, 'FACE_RECOGNITION_AVAILABLE', True)

    return render(request, 'users/register_face.html', {
        'employees': employees,
        'face_recognition_available': face_recognition_available
    })


@login_required
def employee_list(request):
    """
    View for displaying list of all employees
    """
    employees = Employee.objects.select_related('user', 'department').all()
    return render(request, 'users/employee_list.html', {'employees': employees})
