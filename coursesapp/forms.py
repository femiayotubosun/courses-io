from django.db.models import fields
from django.forms import ModelForm, SelectMultiple, TextInput, NumberInput
from django import forms
from django.forms import widgets
from django.forms.widgets import Select
from coursesapp.models import (
    AcademicTimeline,
    Course,
    CourseRegistration,
    Lecturer,
    SemesterCourseAllocation,
    Student,
    StudentClass,
)


class LecturerForm(ModelForm):
    class Meta:
        model = Lecturer
        fields = [
            "user",
            "name",
        ]


class CourseForm(ModelForm):
    class Meta:
        model = Course
        fields = [
            "course_title",
            "course_code",
            "course_units",
            "course_type",
            "prerequisites",
            "lecturer",
        ]

        widgets = {
            # "prerequisites": SelectMultiple(attrs={"multiple": ""}),
            "course_title": TextInput(
                attrs={
                    "class": " textinput rounded-lg border-gray-300 leading-normal py-2 w-full appearance-none px-4 border focus:outline-none text-gray-700 block bg-white"
                }
            ),
            "course_code": TextInput(
                attrs={
                    "class": " textinput rounded-lg border-gray-300 leading-normal py-2 w-full appearance-none px-4 border focus:outline-none text-gray-700 block bg-white"
                }
            ),
            "course_units": NumberInput(
                attrs={
                    "class": " numberinput rounded-lg border-gray-300 leading-normal py-2 w-full appearance-none px-4 border focus:outline-none text-gray-700 block bg-white"
                }
            ),
            "course_type": Select(
                attrs={
                    "class": " rounded-lg border-gray-300 leading-normal py-2 w-full appearance-none px-4 border focus:outline-none text-gray-700 block bg-white"
                }
            ),
            "prerequisites": SelectMultiple(
                attrs={
                    "multiple": "",
                    "class": " rounded-lg border-gray-300 leading-normal py-2 w-full appearance-none px-4 border focus:outline-none text-gray-700 block bg-white",
                }
            ),
            "lecturer": Select(
                attrs={
                    "class": " rounded-lg border-gray-300 leading-normal py-2 w-full appearance-none px-4 border focus:outline-none text-gray-700 block bg-white"
                }
            ),
        }


class SemAllocationFilterForm(forms.Form):

    FIRST = "FIR"
    SECOND = "SEC"
    SUMMER = "SUM"

    SEMESTER_CHOICES = [
        (FIRST, "First"),
        (SECOND, "Second"),
        (SUMMER, "Summer"),
    ]

    FIRST_YEAR = "1L"
    SECOND_YEAR = "2L"
    THIRD_YEAR = "3L"
    FOURTH_YEAR = "4L"
    FIFTH_YEAR = "5L"

    YEAR_IN_SCHOOL_CHOICES = [
        (FIRST_YEAR, "100 Level"),
        (SECOND_YEAR, "200 Level"),
        (THIRD_YEAR, "300 Level"),
        (FOURTH_YEAR, "400 Level"),
        (FIFTH_YEAR, "500 Level"),
    ]

    level = forms.ChoiceField(
        choices=YEAR_IN_SCHOOL_CHOICES,
        required=True,
        label="Level",
    )

    semester = forms.ChoiceField(
        label="Semester",
        choices=SEMESTER_CHOICES,
        required=True,
    )


class SemAllocationEditForm(ModelForm):
    class Meta:
        model = SemesterCourseAllocation
        fields = ["course_list"]

        widgets = {
            "course_list": SelectMultiple(
                attrs={
                    "multiple": "",
                    "class": " rounded-lg border-gray-300 leading-normal py-2 w-full appearance-none px-4 border focus:outline-none text-gray-700 block bg-white",
                }
            ),
        }


class StudentClassFilterForm(forms.Form):
    FIRST_YEAR = "1L"
    SECOND_YEAR = "2L"
    THIRD_YEAR = "3L"
    FOURTH_YEAR = "4L"
    FIFTH_YEAR = "5L"

    YEAR_IN_SCHOOL_CHOICES = [
        (FIRST_YEAR, "100 Level"),
        (SECOND_YEAR, "200 Level"),
        (THIRD_YEAR, "300 Level"),
        (FOURTH_YEAR, "400 Level"),
        (FIFTH_YEAR, "500 Level"),
    ]

    level = forms.ChoiceField(
        choices=YEAR_IN_SCHOOL_CHOICES,
        required=True,
        label="Level",
    )


class StudentClassEditForm(ModelForm):
    class Meta:
        model = StudentClass
        fields = ["max_units"]


class StudentForm(ModelForm):
    class Meta:
        model = Student
        fields = ["name", "matric_no", "student_class"]


class CourseRegEditForm(ModelForm):
    class Meta:
        model = CourseRegistration
        fields = ["status"]


class TimelineForm(ModelForm):
    class Meta:

        FIRST = "FIR"
        SECOND = "SEC"
        SUMMER = "SUM"

        SEMESTER_CHOICES = [
            (FIRST, "First"),
            (SECOND, "Second"),
            (SUMMER, "Summer"),
        ]
        model = AcademicTimeline
        fields = ["academic_year", "academic_semester"]
