from django.urls import path
from . import views
from . import leave_views

urlpatterns = [
    # Attendance URLs
    path('mark/', views.mark_attendance, name='mark_attendance'),
    path('records/', views.attendance_records, name='attendance_records'),
    path('dashboard/', views.attendance_dashboard, name='attendance_dashboard'),
    path('manual/', views.manual_attendance, name='manual_attendance'),
    path('register-face/', views.register_face, name='register_face'),
    path('face-registration-success/', views.face_registration_success, name='face_registration_success'),
    path('manage-faces/', views.manage_faces, name='manage_faces'),
    path('delete-face/<str:employee_id>/', views.delete_face, name='delete_face'),

    # Leave management URLs
    path('leave/submit/', leave_views.submit_leave, name='submit_leave'),
    path('leave/my-leaves/', leave_views.my_leaves, name='my_leaves'),
    path('leave/manage/', leave_views.manage_leaves, name='manage_leaves'),
    path('leave/approve/<int:leave_id>/', leave_views.approve_leave, name='approve_leave'),
    path('leave/reject/<int:leave_id>/', leave_views.reject_leave, name='reject_leave'),
]