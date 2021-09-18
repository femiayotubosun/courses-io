from coursesapp import forms
from coursesapp.forms import TimelineForm
from coursesapp.views.adviser import course_reg_edit_one_student, lecturers, student
from coursesapp.models import (
    AcademicTimeline,
    AcademicYear,
    Course,
    CourseRegistration,
    Lecturer,
    LevelAdviser,
)
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import permission_required, login_required
from django.urls import reverse


@login_required
@permission_required("coursesapp.is_lecturer")
def dashboard(request):
    lecturer = Lecturer.objects.get(user=request.user)
    courses = Course.objects.filter(lecturer=lecturer)

    # Data

    # Students

    # Course Regs

    return render(
        request,
        "lecturer/dashboard.html",
        {
            "lecturer": lecturer,
            "courses": courses,
            "title": "Lecturer Dashboard",
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
        form = TimelineForm(request.POST)

        if form.is_valid():

            year = form.cleaned_data["academic_year"]
            year = AcademicYear.objects.get(year=year)
            sem = form.cleaned_data["academic_semester"]

            try:
                tl = AcademicTimeline.objects.get(
                    academic_year=year, academic_semester=sem
                )

                # TODO: Check if this is the current timeline. Tell it is not yet archived.
            except AcademicTimeline.DoesNotExist:
                return redirect(
                    reverse("lecturer_course_archives", kwargs={"course_id": course_id})
                )
                # TODO: Modal for not found

            regs = CourseRegistration.objects.filter(
                academic_timeline=tl, course=course
            )

            form = TimelineForm(instance=tl)

            return render(
                request,
                "lecturer/dashboard_archives.html",
                {"form": form, "header": "Archives", "course": course, "regs": regs},
            )

    # :TODO
    return render(
        request,
        "lecturer/dashboard_archives.html",
        {"form": form, "header": "Archives", "course": course},
    )

    pass


@login_required
@permission_required("coursesapp.is_lecturer")
def approve_course_reg(request, course_id, student_id):
    course_reg = CourseRegistration.objects.get(
        course__id=course_id, student__id=student_id
    )
    course_reg.approve_course_reg()
    # :TODO Modal for approve successful
    return redirect(reverse("lecturer_one_course", kwargs={"course_id": course_id}))


@login_required
@permission_required("coursesapp.is_lecturer")
def reject_course_reg(request, course_id, student_id):
    course_reg = CourseRegistration.objects.get(
        course__id=course_id, student__id=student_id
    )
    course_reg.reject_course_reg()
    # :TODO Modal for reject successful
    return redirect(reverse("lecturer_one_course", kwargs={"course_id": course_id}))
