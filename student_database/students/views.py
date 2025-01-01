from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from .models import Student
import pandas as pd
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from .forms import StudentForm

# Sign Up View
def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'students/signup.html', {'form': form})

# Login View
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'students/login.html', {'form': form})

# Logout View
def logout_view(request):
    logout(request)
    return redirect('login')

# Dashboard View
def dashboard_view(request):
    # Get query parameters for filtering
    gender_filter = request.GET.get('gender', '')
    class_filter = request.GET.get('class_grade', '')

    # Filter students based on query parameters
    students = Student.objects.all()
    if gender_filter:
        students = students.filter(gender=gender_filter)
    if class_filter:
        students = students.filter(class_grade=class_filter)

    # Get distinct class list for filtering dropdown
    class_list = Student.objects.values_list('class_grade', flat=True).distinct()

    return render(request, 'students/dashboard.html', {
        'students': students,
        'class_list': class_list,
    })

def add_student(request):
    if request.method == "POST":
        # Process the form submission
        name = request.POST.get('name')
        gender = request.POST.get('gender')
        class_grade = request.POST.get('class_grade')
        birthday = request.POST.get('birthday')
        age = request.POST.get('age')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        student_id=request.POST.get('student_id')

        # Create a new student record and save it to the database
        student = Student(
            name=name,
            gender=gender,
            student_id=student_id,
            class_grade=class_grade,
            birthday=birthday,
            age=age,
            address=address,
            phone=phone,
            email=email
        )
        student.save()

        # Redirect to the dashboard after adding the student
        return redirect('dashboard')  # Redirect to the dashboard

    return render(request, 'students/add_student.html')

def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = StudentForm(instance=student)
    return render(request, 'students/edit_student.html', {'form': form})

def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == 'POST':
        student.delete()
        return redirect('dashboard')
    return render(request, 'students/delete_student.html', {'student': student})

def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    # Add logic to edit student details
    return render(request, 'students/edit_student.html', {'student': student})

def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    student.delete()
    return redirect('dashboard')

def export_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="students.pdf"'

    p = canvas.Canvas(response)
    p.drawString(100, 800, "Student Information")

    students = Student.objects.all()
    y = 750
    for student in students:
        line = f"{student.name}, {student.gender}, {student.class_grade}, {student.birthday}"
        p.drawString(100, y, line)
        y -= 20

    p.save()
    return response
import openpyxl
from django.http import HttpResponse
from .models import Student

def export_excel(request):
    # Create an in-memory Excel file
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Students Data"

    # Add header row
    headers = ["Name", "Student ID", "Gender", "Class", "Birthday", "Age", "Address", "Phone", "Email"]
    sheet.append(headers)

    # Add student data rows
    students = Student.objects.all()
    for student in students:
        sheet.append([
            student.name,
            student.student_id,
            student.gender,
            student.class_grade,
            student.birthday,
            student.age,
            student.address,
            student.phone,
            student.email,
        ])

    # Prepare the response
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="students_data.xlsx"'

    # Save the workbook to the response
    workbook.save(response)
    return response

# Add, Edit, and Delete Views
# Implement add, edit, and delete views for student records here
