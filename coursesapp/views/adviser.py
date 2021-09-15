from django.forms.forms import Form
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import permission_required, login_required
from django.urls import reverse
from django.contrib.auth.models import User
from coursesapp import utils
from coursesapp import forms
from coursesapp.forms import (
    CourseForm,
    CourseRegEditForm,
    LecturerForm,
    SemAllocationEditForm,
    SemAllocationFilterForm,
    StudentClassEditForm,
    StudentClassFilterForm,
    StudentForm,
)
from coursesapp.models import (
    AcademicTimeline,
    LevelAdviser,
    Lecturer,
    Course,
    CourseRegistration,
    SemesterCourseAllocation,
    StudentClass,
    Student,
    Department,
    StudentGrade,
)


# Make views for adviser


@login_required
@permission_required("coursesapp.is_adviser")
def dashboard(request):

    department = Department.objects.filter(leveladviser__user=request.user).first()
    title = f"Dashboard | {department.department_name}" if department else None
    lecturers = Lecturer.objects.filter(department=department)
    students = Student.objects.filter(student_class__department=department)
    courses = Course.objects.filter(department=department)
    all_course_regs = CourseRegistration.objects.filter(
        student__student_class__department=department
    )
    approved_course_regs = all_course_regs.filter(status="APR")
    pending_course_regs = all_course_regs.filter(status="PEN")
    unappr_course_regs = all_course_regs.filter(status="UNA")

    return render(
        request,
        "adviser/dashboard.html",
        {
            "department": department,
            "lecturers": lecturers,
            "students": students,
            "courses": courses,
            "all_course_regs": all_course_regs,
            "approved_course_regs": approved_course_regs,
            "pending_course_regs": pending_course_regs,
            "unappr_course_regs": unappr_course_regs,
            "title": title,
        },
    )


# All Lecturers
@login_required
@permission_required("coursesapp.is_adviser")
def lecturers(request):
    department = Department.objects.filter(leveladviser__user=request.user).first()
    title = f"Dashboard | {department.department_name}" if department else None
    lecturers = Lecturer.objects.filter(department=department)

    return render(
        request,
        "adviser/dashboard_lecturers.html",
        {
            "department": department,
            "lecturers": lecturers,
            "title": "Lecturers",
        },
    )


# One lectuer editting and stuff

# All Courses
@login_required
@permission_required("coursesapp.is_adviser")
def courses(request):
    department = Department.objects.filter(leveladviser__user=request.user).first()
    courses = Course.objects.filter(department=department)

    return render(
        request,
        "adviser/dashboard_courses.html",
        {"department": department, "courses": courses, "title": "All Courses"},
    )


# One course edditing and stuff
@login_required
@permission_required("coursesapp.is_adviser")
def course(request, course_id):
    course = Course.objects.get(pk=course_id)
    prerequisites = course.prerequisites.all()
    # Number of students in this place

    student_count = CourseRegistration.objects.filter(course=course).count()
    return render(
        request,
        "adviser/dashboard_course.html",
        {
            "course": course,
            "student": student_count,
            "title": f"{course.course_title} | {course.course_code}",
            "prerequisites": prerequisites,
        },
    )


@login_required
@permission_required("coursesapp.is_adviser")
def course_data(request, course_id):
    # Filter by current timeline for coursereg
    course = Course.objects.get(pk=course_id)
    carryovers = Student.objects.filter(
        studentgrade__grade="F", studentgrade__course=course
    )
    students = Student.objects.filter(courseregistration__course=course)
    prerequisites = course.prerequisites

    return render(
        request,
        "adviser/dashboard_course_data.html",
        {
            "course": course,
            "carryovers": carryovers,
            "students": students,
            "title": f"{course.course_title} | {course.course_code}",
            "prerequisites": prerequisites,
        },
    )


@login_required
@permission_required("coursesapp.is_adviser")
def course_edit(request, course_id):
    course = Course.objects.get(pk=course_id)
    form = CourseForm(instance=course)

    if request.method == "POST":
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect(reverse("adviser_course", kwargs={"course_id": course_id}))
    return render(
        request, "adviser/dashboard_course_edit.html", {"course": course, "form": form}
    )


# ALl Students
@login_required
@permission_required("coursesapp.is_adviser")
def students_levels(request):

    return render(
        request, "adviser/dashboard_students_levels.html", {"title": "students"}
    )


@login_required
@permission_required("coursesapp.is_adviser")
def students(request, level_name):
    department = Department.objects.filter(leveladviser__user=request.user).first()
    students = Student.objects.filter(
        student_class__department=department, student_class__level=level_name
    )

    return render(
        request,
        "adviser/dashboard_students.html",
        {"title": "Students", "students": students},
    )


# One student, editting and stuff [carryovers, if sum of his outstanding is greater than available units]


@login_required
@permission_required("coursesapp.is_adviser")
def student(request, student_id):

    student = Student.objects.get(pk=student_id)

    if student.student_class == None:
        return redirect(reverse("adviser_students_levels"))

    sem_units = student.student_class.max_units

    try:
        courses_todo = student.get_semester_allocation()
        courses_carry = courses_todo["carryovers"].all()
        courses_default = courses_todo["default"].all()
        total_units = sum([course.course_units for course in courses_carry]) + sum(
            [course.course_units for course in courses_default]
        )
        return render(
            request,
            "adviser/dashboard_student.html",
            {
                "student": student,
                "default_units": sem_units,
                "courses_carry": courses_carry,
                "courses_default": courses_default,
                "total_units": total_units,
                "sem_units": sem_units,
            },
        )

    except SemesterCourseAllocation.DoesNotExist:
        return render(
            request,
            "adviser/dashboard_student.html",
            {
                "student": student,
                "default_units": sem_units,
            },
        )


@login_required
@permission_required("coursesapp.is_adviser")
def edit_student(request, student_id):
    student = Student.objects.get(pk=student_id)
    form = StudentForm(instance=student)

    if request.method == "POST":
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect(
                reverse("adviser_one_student", kwargs={"student_id": student_id})
            )

    return render(
        request,
        "adviser/dashboard_edit_student.html",
        {"form": form, "student": student, "title": "Edit Student"},
    )


# Semester ALlocations
@login_required
@permission_required("coursesapp.is_adviser")
def sem_allocation_filter_page(request):

    form = SemAllocationFilterForm()
    department = Department.objects.filter(leveladviser__user=request.user).first()
    if request.method == "POST":
        form = SemAllocationFilterForm(request.POST)
        if form.is_valid():
            level = form.cleaned_data["level"]
            semester = form.cleaned_data["semester"]

            student_class, _ = StudentClass.objects.get_or_create(
                level=level, department=department
            )

            sem_alloc, _ = SemesterCourseAllocation.objects.get_or_create(
                student_class=student_class,
                semester=semester,
            )

            # Exception for model does not exist

            return redirect(
                reverse(
                    "adviser_semester_allocation",
                    kwargs={"allocation_id": sem_alloc.id},
                )
            )

    return render(
        request,
        "adviser/dashboard_allocation_levels.html",
        {
            "form": form,
            "title": "Dashboard | Semester Allocation",
            "header": "Dashboard |Department",
        },
    )


@login_required
@permission_required("coursesapp.is_adviser")
def semester_allocation(request, allocation_id):
    department = Department.objects.filter(leveladviser__user=request.user).first()
    allocation = SemesterCourseAllocation.objects.get(pk=allocation_id)
    courses = allocation.course_list.all()

    return render(
        request,
        "adviser/dashboard_semester_allocation.html",
        {
            "allocation": allocation,
            "courses": courses,
            "department": department,
            "title": "Dashboard | Semester Allocation",
            "header": "Dashboard |Department",
        },
    )


@login_required
@permission_required("coursesapp.is_adviser")
def edit_sem_allocation(request, allocation_id):
    department = Department.objects.filter(leveladviser__user=request.user).first()
    allocation = SemesterCourseAllocation.objects.get(pk=allocation_id)
    form = SemAllocationEditForm(instance=allocation)

    if request.method == "POST":
        form = SemAllocationEditForm(request.POST, instance=allocation)
        if form.is_valid():
            form.save()
            return redirect(
                reverse(
                    "adviser_semester_allocation",
                    kwargs={"allocation_id": allocation_id},
                )
            )

    return render(
        request,
        "adviser/dashboard_allocation_edit.html",
        {
            "department": department,
            "allocation": allocation,
            "form": form,
            "title": "Dashboard | Semester Allocation",
            "header": f"Dashboard | {department.department_name}",
        },
    )


# Student_class datai
@login_required
@permission_required("coursesapp.is_adviser")
def student_class(request):
    department = Department.objects.filter(leveladviser__user=request.user).first()
    form = StudentClassFilterForm()
    if request.method == "POST":
        form = StudentClassFilterForm(request.POST)
        if form.is_valid():
            level = form.cleaned_data["level"]

            student_class, _ = StudentClass.objects.get_or_create(
                department=department, level=level
            )
            student_count = Student.objects.filter(student_class=student_class).count()
            return render(
                request,
                "adviser/dashboard_student_class.html",
                {
                    "form": form,
                    "title": "Classes",
                    "header": "Classes",
                    "student_class": student_class,
                    "student_count": student_count,
                },
            )

    return render(
        request,
        "adviser/dashboard_student_class.html",
        {"form": form, "title": "Classes", "header": "Classes"},
    )


@login_required
@permission_required("coursesapp.is_adviser")
def edit_student_class(request, class_id):
    student_class = StudentClass.objects.get(pk=class_id)
    form = StudentClassEditForm(instance=student_class)

    if request.method == "POST":
        form = StudentClassEditForm(request.POST, instance=student_class)
        if form.is_valid():
            form.save()
            return redirect(reverse("adviser_student_class"))

    return render(
        request,
        "adviser/dashboard_edit_student_class.html",
        {"form": form, "student_class": student_class},
    )


@login_required
@permission_required("coursesapp.is_adviser")
def course_reg_students(request):
    department = Department.objects.filter(leveladviser__user=request.user).first()
    tl = AcademicTimeline.get_current()
    form = StudentClassFilterForm()

    if request.method == "POST":
        form = StudentClassFilterForm(request.POST)
        if form.is_valid():
            level = form.cleaned_data["level"]
            student_class, _ = StudentClass.objects.get_or_create(
                department=department, level=level
            )
            students = Student.objects.filter(student_class=student_class)
            return render(
                request,
                "adviser/dashboard_course_reg_filter.html",
                {
                    "form": form,
                    "title": "Course Registrations",
                    "header": department.department_name,
                    "students": students,
                },
            )

    return render(
        request,
        "adviser/dashboard_course_reg_filter.html",
        {
            "form": form,
            "title": "Course Registrations",
            "header": department.department_name,
        },
    )


@login_required
@permission_required("coursesapp.is_adviser")
def course_reg_one_student(request, student_id):
    department = Department.objects.filter(leveladviser__user=request.user)
    tl = AcademicTimeline.get_current()
    student = Student.objects.get(pk=student_id)
    regs = CourseRegistration.objects.filter(student=student, academic_timeline=tl)

    return render(
        request,
        "adviser/dashboard_reg_one_student.html",
        {
            "department": department,
            "tl": tl,
            "student": student,
            "regs": regs,
            "title": "Course Registration",
            "header": student.name,
        },
    )


@login_required
@permission_required("coursesapp.is_adviser")
def course_reg_edit_one_student(request, reg_id):
    reg = CourseRegistration.objects.get(pk=reg_id)
    student = Student.objects.get(pk=reg.student.id)

    form = CourseRegEditForm(instance=reg)

    if request.method == "POST":
        form = CourseRegEditForm(request.POST, instance=reg)
        if form.is_valid():
            form.save()
            return redirect(
                reverse(
                    "adviser_course_reg_one_student", kwargs={"student_id": student.id}
                )
            )
    return render(
        request,
        "adviser/dashboard_edit_one_reg.html",
        {"reg": reg, "student": student, "form": form},
    )


@login_required
@permission_required("coursesapp.is_adviser")
def initialize_course_reg(request):
    department = Department.objects.filter(leveladviser__user=request.user).first()
    students = Student.objects.filter(student_class__department=department).all()
    try:
        [student.init_course_reg() for student in students]
        print("success")
        return redirect(reverse("adviser_course_reg"))
    except:
        print("failure")
        return redirect(reverse("adviser_course_reg"))


# Create if there's none

# Put warning if, max_units < sem_allocation


# Course Registrations
