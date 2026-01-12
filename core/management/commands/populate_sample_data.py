from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import Department, Employee
from attendance.models import Attendance
from django.utils import timezone
from datetime import datetime, timedelta
import random
import json

CustomUser = get_user_model()


class Command(BaseCommand):
    help = 'Populate database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')

        # Create Departments
        departments_data = [
            {'name': 'IT Department', 'description': 'Information Technology Team'},
            {'name': 'HR Department', 'description': 'Human Resources Team'},
            {'name': 'Finance Department', 'description': 'Finance and Accounts Team'},
            {'name': 'Marketing Department', 'description': 'Marketing and Sales Team'},
        ]

        departments = {}
        for dept_data in departments_data:
            dept, created = Department.objects.get_or_create(
                name=dept_data['name'],
                defaults={'description': dept_data['description']}
            )
            departments[dept.name] = dept
            self.stdout.write(f'Created department: {dept.name}')

        # Create Employees
        employees_data = [
            {'username': 'ali.khan', 'first_name': 'Ali', 'last_name': 'Khan', 'email': 'ali.khan@company.com',
             'employee_id': 'EMP001', 'department': 'IT Department'},
            {'username': 'sara.ahmed', 'first_name': 'Sara', 'last_name': 'Ahmed', 'email': 'sara.ahmed@company.com',
             'employee_id': 'EMP002', 'department': 'HR Department'},
            {'username': 'ahmad.raza', 'first_name': 'Ahmad', 'last_name': 'Raza', 'email': 'ahmad.raza@company.com',
             'employee_id': 'EMP003', 'department': 'Finance Department'},
            {'username': 'fatima.zahra', 'first_name': 'Fatima', 'last_name': 'Zahra',
             'email': 'fatima.zahra@company.com', 'employee_id': 'EMP004', 'department': 'Marketing Department'},
            {'username': 'usman.ali', 'first_name': 'Usman', 'last_name': 'Ali', 'email': 'usman.ali@company.com',
             'employee_id': 'EMP005', 'department': 'IT Department'},
        ]

        for emp_data in employees_data:
            # Create User
            user, created = CustomUser.objects.get_or_create(
                username=emp_data['username'],
                defaults={
                    'first_name': emp_data['first_name'],
                    'last_name': emp_data['last_name'],
                    'email': emp_data['email'],
                    'user_type': 'employee'
                }
            )

            if created:
                user.set_password('password123')  # Default password
                user.save()
                self.stdout.write(f'Created user: {emp_data["username"]}')

            # Create Employee
            employee, emp_created = Employee.objects.get_or_create(
                user=user,
                defaults={
                    'employee_id': emp_data['employee_id'],
                    'department': departments[emp_data['department']],
                    'face_encoding': json.dumps([0.1] * 128),  # Dummy encoding for simulation
                }
            )

            if emp_created:
                self.stdout.write(f'Created employee: {emp_data["first_name"]} {emp_data["last_name"]}')

        # Create sample attendance records for last 7 days
        employees = Employee.objects.all()
        today = timezone.now().date()

        attendance_created_count = 0

        for i in range(7):
            date = today - timedelta(days=i)

            for employee in employees:
                # Skip if attendance already exists for this employee on this date
                if Attendance.objects.filter(employee=employee, date=date).exists():
                    continue

                # 80% chance of presence
                if random.random() < 0.8:
                    try:
                        # Create attendance record
                        attendance = Attendance.objects.create(
                            employee=employee,
                            date=date,
                            status='present',
                            time_in=timezone.now().replace(
                                hour=random.randint(8, 10),
                                minute=random.randint(0, 59),
                                second=0
                            ) - timedelta(days=i)
                        )
                        attendance_created_count += 1

                        if i == 0:  # Only show today's records
                            self.stdout.write(f'Created attendance for {employee.user.get_full_name()} on {date}')

                    except Exception as e:
                        self.stdout.write(f'Error creating attendance for {employee}: {e}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully populated sample data! Created {attendance_created_count} attendance records.')
        )
        self.stdout.write('Default password for all users: password123')
        self.stdout.write('You can login with: ali.khan / password123')