from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.db.models.signals import pre_save

# Create your models here.
class Department(models.Model):
    department_name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"<Department: {self.department_name}>"


class StudentClass(models.Model):
    FIRST_YEAR = "1L"
    SECOND_YEAR = "2L"
    THIRD_YEAR = "3L"
    FOURTH_YEAR = "4L"
    FIFTH_YEAR = "5L"

    FIRST = "FIR"
    SECOND = "SEC"
    SUMMER = "SUM"

    YEAR_IN_SCHOOL_CHOICES = [
        (FIRST_YEAR, "100 Level"),
        (SECOND_YEAR, "200 Level"),
        (THIRD_YEAR, "300 Level"),
        (FOURTH_YEAR, "400 Level"),
        (FIFTH_YEAR, "500 Level"),
    ]

    level = models.CharField(
        max_length=2,
        choices=YEAR_IN_SCHOOL_CHOICES,
        default=FIRST_YEAR,
    )
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    max_units = models.IntegerField(default=24)

    def get_semester_allocation(self, semester=FIRST):
        return SemesterCourseAllocation.objects.get(
            student_class=self, semester=semester
        )

    def __str__(self) -> str:
        return f"<Student Class: {self.department.department_name} {self.get_level_display()}>"


class AcademicYear(models.Model):
    year = models.CharField(max_length=10)

    def make_sesssion_from_year(first_year: int) -> str:
        try:
            first_year = int(first_year)
        except ValueError:
            raise ValueError
        return f"{first_year}/{first_year + 1}"

    def create_first():
        year = AcademicYear.make_sesssion_from_year(date.today().year)
        return AcademicYear.objects.create(year=year)

    def get_current():
        return AcademicYear.objects.all().last()

    def create_next():
        current_year = AcademicYear.get_current()
        next_year = AcademicYear.make_sesssion_from_year(
            current_year.year.split("/")[1]
        )
        return AcademicYear.objects.create(year=next_year)

    def __str__(self) -> str:
        return f"<Academic Year: {self.year}>"


class AcademicTimeline(models.Model):
    """
    AcademicTimeline.get_current()
    AcademicTimeline.create_next()

    """

    FIRST = "FIR"
    SECOND = "SEC"
    SUMMER = "SUM"

    ACADEMIC_SEMESTER_CHOICES = [
        (FIRST, "First"),
        (SECOND, "Second"),
        (SUMMER, "Summer"),
    ]

    academic_semester = models.CharField(
        max_length=3,
        choices=ACADEMIC_SEMESTER_CHOICES,
        default=FIRST,
    )

    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)

    def get_next_semester(current_semseter):
        if current_semseter == AcademicTimeline.FIRST:
            return AcademicTimeline.SECOND
        if current_semseter == AcademicTimeline.SECOND:
            return AcademicTimeline.SUMMER
        if current_semseter == AcademicTimeline.SUMMER:
            return AcademicTimeline.FIRST

    def get_current():
        return AcademicTimeline.objects.all().last()

    def create_first():
        year = AcademicYear.create_first()
        return AcademicTimeline.objects.create(academic_year=year)

    def create_next():

        if AcademicTimeline.objects.all().count() == 0:
            return AcademicTimeline.create_first()
        curr_tl = AcademicTimeline.get_current()
        semester = AcademicTimeline.get_next_semester(curr_tl.academic_semester)

        return (
            AcademicTimeline.objects.create(
                academic_semester=semester, academic_year=curr_tl.academic_year
            )
            if not semester == AcademicTimeline.FIRST
            else AcademicTimeline.objects.create(
                academic_semester=semester,
                academic_year=AcademicYear.create_next(),
            )
        )

    def __str__(self) -> str:
        return f"<Academic Timeline: {self.academic_year.year} {self.get_academic_semester_display()} Semester>"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Student(Profile):

    name = models.CharField(max_length=200, blank=True, null=True)
    matric_no = models.CharField(
        max_length=200,
        unique=True,
        blank=True,
        null=True,
    )
    student_class = models.ForeignKey(
        StudentClass,
        models.SET_NULL,
        blank=True,
        null=True,
    )

    def __str__(self) -> str:
        return f"<Student: {self.user.username}>"

    #   TODO: aLlocation includes carryovers and semester allocation for his class
    def get_semester_allocation(self):
        course_alloc = {}
        if self.student_class:
            course_alloc[
                "default"
            ] = self.student_class.get_semester_allocation().course_list
            course_alloc["carryovers"] = Course.objects.filter(
                studentgrade__grade="F", studentgrade__student=self
            )
            return course_alloc
        else:
            return None

    def init_course_reg(self):
        tl = AcademicTimeline.get_current()
        alloc = self.get_semester_allocation()
        courses = alloc["default"].all()
        courses_2 = alloc["carryovers"].all()
        default = [
            CourseRegistration.objects.get_or_create(
                student=self, course=course, academic_timeline=tl
            )
            for course in courses
        ]
        carryovers = [
            CourseRegistration.objects.get_or_create(
                student=self, course=course, academic_timeline=tl
            )
            for course in courses_2
        ]

        return default + carryovers


class Lecturer(Profile):
    class Meta:
        permissions = [("is_lecturer", "User is a lecturer")]

    name = models.CharField(max_length=200, blank=True)
    department = models.OneToOneField(
        Department, models.SET_NULL, blank=True, null=True
    )

    def __str__(self) -> str:
        return f"<Lecturer: {self.name}>"


class LevelAdviser(Profile):
    class Meta:
        permissions = [
            ("is_adviser", "User is a level adviser"),
        ]

    department = models.ForeignKey(Department, models.SET_NULL, blank=True, null=True)

    def __str__(self) -> str:
        return f"<Level Adviser: {self.user.username}>"


class Course(models.Model):

    COMPULSORY = "COM"
    PREREQUISTE = "PRE"
    ELECTIVE = "ELE"
    REQUIRED = "REQ"

    COURSE_TYPE_CHOICES = [
        (COMPULSORY, "Compulsory"),
        (PREREQUISTE, "Prerequisite"),
        (ELECTIVE, "Elective"),
        (REQUIRED, "Required"),
    ]

    course_type = models.CharField(
        max_length=3,
        choices=COURSE_TYPE_CHOICES,
        default=COMPULSORY,
    )

    course_title = models.CharField(max_length=255)
    course_code = models.CharField(max_length=10)
    course_units = models.IntegerField(default=2)
    department = models.ForeignKey(Department, models.SET_NULL, blank=True, null=True)
    prerequisites = models.ManyToManyField(
        "Course", related_name="prequisites", blank=True
    )
    lecturer = models.ForeignKey(Lecturer, models.SET_NULL, blank=True, null=True)

    def __str__(self) -> str:
        return f"<Course: {self.course_code} {self.get_course_type_display()}>"


class StudentGrade(models.Model):
    class Meta:
        permissions = (
            ("can_set_grade", "Can Edit Course Grade"),
            ("can_view_grade", "Can View Course Grade"),
        )
        unique_together = (
            "student",
            "course",
        )

    student = models.ForeignKey(Student, models.SET_NULL, blank=True, null=True)
    course = models.ForeignKey(Course, models.SET_NULL, blank=True, null=True)
    score = models.IntegerField(default=0)
    grade = models.CharField(default="-", max_length=1)

    def __str__(self) -> str:
        return f"<Student Grade: {self.student.name} {self.course.course_code} {self.grade}>"

    def getLetterGrade(score):
        score = round(score)
        grades = [(70, "A"), (60, "B"), (50, "C"), (40, "D"), (0, "F")]
        for i in range(len(grades)):
            if score >= grades[i][0]:
                return grades[i][1]


class CourseRegistration(models.Model):

    APPROVED = "APR"
    PENDING = "PEN"
    UNAPPROVED = "UNA"

    COURSE_REG_STATUS_CHOICES = [
        (APPROVED, "Approved"),
        (PENDING, "Pending"),
        (UNAPPROVED, "Unapproved"),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=3, choices=COURSE_REG_STATUS_CHOICES, default=UNAPPROVED
    )
    academic_timeline = models.ForeignKey(
        AcademicTimeline, models.SET_NULL, blank=True, null=True
    )

    def __str__(self) -> str:
        return f"<Course Registration: {self.student.user.username} {self.course.course_code} {self.get_status_display()}>"

    def request_course_reg(self):
        self.status = CourseRegistration.PENDING
        self.save()

    def approve_course_reg(self):

        if self.status == CourseRegistration.PENDING:
            self.status = CourseRegistration.APPROVED
            self.save()
            return self
        else:
            return

    def reject_course_reg(self):
        self.status = CourseRegistration.UNAPPROVED
        self.save()
        return self


class SemesterCourseAllocation(models.Model):
    FIRST = "FIR"
    SECOND = "SEC"
    SUMMER = "SUM"

    SEMESTER_CHOICES = [
        (FIRST, "First"),
        (SECOND, "Second"),
        (SUMMER, "Summer"),
    ]
    semester = models.CharField(max_length=3, choices=SEMESTER_CHOICES, default=FIRST)

    student_class = models.ForeignKey(
        StudentClass,
        models.SET_NULL,
        blank=True,
        null=True,
    )
    course_list = models.ManyToManyField(
        "Course", related_name="semester_courses", blank=True
    )

    def __str__(self) -> str:
        return f"<Course Allocation: {self.get_semester_display()} Semester {self.student_class.department.department_name} {self.student_class.get_level_display()} {self.course_list.count()}>"


class PortalOpen(models.Model):
    course_registration_open = models.BooleanField(default=True)


def save_grade(sender, instance, **kwargs):
    instance.grade = StudentGrade.getLetterGrade(instance.score)


pre_save.connect(save_grade, sender=StudentGrade)
