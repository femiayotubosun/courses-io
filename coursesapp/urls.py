from coursesapp.views import adviser
from coursesapp.views.adviser import lecturers, students_levels
from coursesapp.views import base
from django.urls import path
from coursesapp import views

urlpatterns = [
    path("", views.base.index, name="index"),
    path("signup/", views.base.signup, name="signup"),
]


urlpatterns += [
    path("createNextTimeline/", views.base.create_next_tl, name="create_next_tl"),
    path("openCourseRegPortal/", views.base.open_portal, name="open_portal"),
    path("closeCourseRegPortal/", views.base.close_portal, name="close_portal"),
]


urlpatterns += [
    path("adviser/dashboard/", views.adviser.dashboard, name="adviser_dashboard"),
    path(
        "adviser/dashboard/lecturers/",
        views.adviser.lecturers,
        name="adviser_lecturers",
    ),
    path(
        "adviser/dashboard/students/levels/",
        views.adviser.students_levels,
        name="adviser_students_levels",
    ),
    path(
        "adviser/dashboard/students/levels/<str:level_name>/",
        views.adviser.students,
        name="adviser_students_in_level",
    ),
    path(
        "adviser/dashboard/students/<int:student_id>/",
        views.adviser.student,
        name="adviser_one_student",
    ),
    path(
        "adviser/dashboard/students/<int:student_id>/edit/",
        views.adviser.edit_student,
        name="adviser_edit_student",
    ),
    path("adviser/dashboard/courses/", views.adviser.courses, name="adviser_courses"),
    path(
        "adviser/dashboard/courses/<int:course_id>/",
        views.adviser.course,
        name="adviser_course",
    ),
    path(
        "adviser/dashboard/courses/<int:course_id>/data/",
        views.adviser.course_data,
        name="adviser_course_data",
    ),
    path(
        "adviser/dashboard/courses/<int:course_id>/edit/",
        views.adviser.course_edit,
        name="adviser_edit_course",
    ),
    path(
        "adviser/dashboard/allocations/",
        views.adviser.sem_allocation_filter_page,
        name="adviser_allocations_filter",
    ),
    path(
        "adviser/dashboard/allocations/<int:allocation_id>/",
        views.adviser.semester_allocation,
        name="adviser_semester_allocation",
    ),
    path(
        "adviser/dashboard/allocations/<int:allocation_id>/edit/",
        views.adviser.edit_sem_allocation,
        name="adviser_edit_semester_allocation",
    ),
    path(
        "adviser/dashboard/classes/",
        views.adviser.student_class,
        name="adviser_student_class",
    ),
    path(
        "adviser/dashboard/classes/<int:class_id>/edit/",
        views.adviser.edit_student_class,
        name="adviser_edit_student_class",
    ),
    path(
        "adviser/dashboard/courseregistration/",
        views.adviser.course_reg_students,
        name="adviser_course_reg",
    ),
    path(
        "adviser/dashboard/courseregistration/student/<int:student_id>/",
        views.adviser.course_reg_one_student,
        name="adviser_course_reg_one_student",
    ),
    path(
        "adviser/dashboard/courseregistration/<int:reg_id>/edit/",
        views.adviser.course_reg_edit_one_student,
        name="adviser_edit_course_reg",
    ),
    path(
        "adviser/dashboard/courseregistration/initialize/",
        views.adviser.initialize_course_reg,
        name="init_course_reg",
    ),
]


urlpatterns += [
    path("lecturer/dashboard/", views.lecturer.dashboard, name="lecturer_dashboard"),
    path(
        "lecturer/dashboard/courses/",
        views.lecturer.courses,
        name="lecturer_courses",
    ),
    path(
        "lecturer/dashboard/courses/<int:course_id>/",
        views.lecturer.one_course,
        name="lecturer_one_course",
    ),
    path(
        "lecturer/dashboard/courses/reg/approve/<int:course_id>/<int:student_id>/",
        views.lecturer.approve_course_reg,
        name="lecturer_approve_course_reg",
    ),
    path(
        "lecturer/dashboard/courses/reg/reject/<int:course_id>/<int:student_id>/",
        views.lecturer.one_course,
        name="lecturer_reject_course_reg",
    ),
]
