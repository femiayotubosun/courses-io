from datetime import time

from django.http.response import FileResponse
from coursesapp import forms, utils
from coursesapp.forms import LecturerForm, TimelineForm
from coursesapp.views.adviser import course_reg_edit_one_student, lecturers, student
from coursesapp.models import (
    AcademicTimeline,
    AcademicYear,
    Course,
    CourseRegistration,
    Lecturer,
    Student,
)
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import permission_required, login_required
from django.urls import reverse
from django.contrib import messages


@login_required
@permission_required("coursesapp.is_lecturer")
def dashboard(request):
    lecturer = Lecturer.objects.get(user=request.user)
    courses = Course.objects.filter(lecturer=lecturer)
    timeline = AcademicTimeline.get_current()

    students = Student.objects.filter(courseregistration__course__in=courses, courseregistration__academic_timeline=timeline)


    return render(
        request,
        "lecturer/dashboard.html",
        {
            "lecturer": lecturer,
            "courses": courses,
            "title": "Lecturer Dashboard",
            "students": students,
            "header": f"Welcome, {lecturer.name}",
        },
    )


@login_required
@permission_required("coursesapp.is_lecturer")
def courses(request):
    lecturer = Lecturer.objects.get(user=request.user)
    courses = Course.objects.filter(lecturer=lecturer).all()
    timeline = AcademicTimeline.get_current()

    for course in courses:
        course.students_count = CourseRegistration.objects.filter(
            course=course, academic_timeline=timeline
        ).count()

    return render(
        request,
        "lecturer/dashboard_all_courses.html",
        {
            "lecturer": lecturer,
            "courses": courses,
            "title": "Lecturer Dashboard",
            "header": "All Courses",
        },
    )


@login_required
@permission_required("coursesapp.is_lecturer")
def one_course(request, course_id):
    lecturer = Lecturer.objects.get(user=request.user)
    course = Course.objects.get(pk=course_id)
    timeline = AcademicTimeline.get_current()
    students = CourseRegistration.objects.filter(
        course=course, academic_timeline=timeline
    )
    appr = students.filter(status="APR")
    pen = students.filter(status="PEN")
    unappr = students.filter(status="UNA")

    return render(
        request,
        "lecturer/dashboard_one_course.html",
        {
            "lecturer": lecturer,
            "course": course,
            "students": students,
            "title": course.course_code,
            "header": course.course_title,
            "approved": appr,
            "pending": pen,
            "unapproved": unappr,
        },
    )


@login_required
@permission_required("coursesapp.is_lecturer")
def archives(request):
    lecturer = Lecturer.objects.get(user=request.user)
    courses = Course.objects.filter(lecturer=lecturer)

    return render(
        request,
        "lecturer/dashboard_archives_all_courses.html",
        {
            "lecturer": lecturer,
            "courses": courses,
            "title": "Lecturer Dashboard",
            "header": "Archives | All Courses",
        },
    )


@login_required
@permission_required("coursesapp.is_lecturer")
def course_archives(request, course_id):
    form = TimelineForm()
    course = Course.objects.get(pk=course_id)

    if request.method == "POST":
        try:
            yr = AcademicYear.objects.get(pk=request.POST['academic_year'])
            semester = request.POST['academic_semester']
            tl= AcademicTimeline.objects.get(academic_year=yr, academic_semester=semester)
            form = TimelineForm(request.POST, instance=tl)
            regs = CourseRegistration.objects.filter(
                academic_timeline=tl, course=course
            )

            form = TimelineForm(instance=tl)

            return render(
                request,
                "lecturer/dashboard_archives.html",
                {"form": form, "header": "Archives", "course": course, "regs": regs},
            )
        except:
            messages.error(request, "This Timeline is invalid or Data not found")
            return redirect(
                reverse("lecturer_course_archives", kwargs={"course_id": course_id})
            )
                # TODO: Modal for not found



    # :TODO
    return render(
        request,
        "lecturer/dashboard_archives.html",
        {"form": form, "header": "Archives", "course": course},
    )





@login_required
@permission_required("coursesapp.is_lecturer")
def profile(request):
    lecturer = Lecturer.objects.get(user=request.user)
    form = LecturerForm(instance=lecturer)

    if request.method == 'POST':
        form = LecturerForm(request.POST, instance=lecturer)
        if form.is_valid():
            form.save()
            return redirect(reverse('lecturer_profile'))
    
    return render(request, "lecturer/dashboard_profile.html", {"form": form, "title": "Dashboard", "header": "Dashboard | Lecturer"})

@login_required
@permission_required("coursesapp.is_lecturer")
def approve_course_reg(request, course_id, student_id):
    course_reg = CourseRegistration.objects.get(
        course__id=course_id, student__id=student_id
    )
    course_reg.approve_course_reg()
    messages.success(request, 'Approved successfully')
    return redirect(reverse("lecturer_one_course", kwargs={"course_id": course_id,}))


@login_required
@permission_required("coursesapp.is_lecturer")
def reject_course_reg(request, course_id, student_id):
    course_reg = CourseRegistration.objects.get(
        course__id=course_id, student__id=student_id
    )
    course_reg.reject_course_reg()
    messages.error(request, 'Rejected successfully')
    return redirect(reverse("lecturer_one_course", kwargs={"course_id": course_id}))


@login_required
@permission_required("coursesapp.is_lecturer")
def print_eligible(request, course_id):
    course = Course.objects.get(pk=course_id)
    timeline = AcademicTimeline.get_current()
    lecturer = Lecturer.objects.get(user=request.user)
    regs = CourseRegistration.objects.filter(course=course, academic_timeline=timeline, status="APR")

    context = {
        "timeline": timeline,
        "course": course,
        "lecturer": lecturer,
        "regs": regs
    }

    data = utils.eligible_report(context)
    data = open(data, 'rb')
    response = FileResponse(data, as_attachment=True)
    return response