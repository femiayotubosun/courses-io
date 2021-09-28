from django.contrib import admin
from coursesapp.models import (
    Course,
    CourseRegistration,
    Department,
    Lecturer,
    LevelAdviser,
    SemesterCourseAllocation,
    Student,
    StudentClass,
    AcademicTimeline,
    AcademicYear,
    StudentGrade,
    PortalOpen,
    CourseRegistrationForm
)

# Register your models here.
admin.site.register(
    [
        Department,
        StudentClass,
        AcademicYear,
        AcademicTimeline,
        CourseRegistration,
        Student,
        Lecturer,
        LevelAdviser,
        Course,
        StudentGrade,
        SemesterCourseAllocation,
        PortalOpen,
        CourseRegistrationForm
    ]
)
