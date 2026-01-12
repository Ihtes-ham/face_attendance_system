from django.db import models
from django.contrib.auth.models import AbstractUser
import json


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('employee', 'Employee'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='employee')
    phone = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.username


class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Employee(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    employee_id = models.CharField(max_length=20, unique=True)
    face_encoding = models.TextField(blank=True, null=True)  # Store as JSON string
    face_image = models.ImageField(upload_to='face_images/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.employee_id})"

    def get_face_encoding_list(self):
        """Convert stored JSON encoding to list"""
        if self.face_encoding:
            try:
                return json.loads(self.face_encoding)
            except:
                return None
        return None

    def set_face_encoding(self, encoding_list):
        """Convert list to JSON string for storage"""
        if encoding_list:
            self.face_encoding = json.dumps(encoding_list)
        else:
            self.face_encoding = None