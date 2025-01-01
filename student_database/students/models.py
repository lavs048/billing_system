from django.db import models

class Student(models.Model):
    student_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
    class_grade = models.CharField(max_length=50)
    birthday = models.DateField()
    age = models.IntegerField()
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    email = models.EmailField()

    def __str__(self):
        return self.name
