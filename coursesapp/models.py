from typing import List
from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.db.models.signals import post_save, pre_save



class SingletonModel(models.Model):
    def save(*args, **kwargs):
        pass

# Create your models here.
class Department(models.Model):
    department_name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"{self.department_name.capitalize()}"


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
        alloc, _ = SemesterCourseAllocation.objects.get_or_create(
            student_class=self, semester=semester
        )

        return alloc

    def init_student_class(department: Department):
        for year in StudentClass.YEAR_IN_SCHOOL_CHOICES:
            StudentClass.objects.get_or_create(level=year[0], department=department)
        return

    def __str__(self) -> str:
        return f"<Student Class: {self.department.department_name} {self.get_level_display()}>"


class AcademicYear(models.Model):
    year = models.CharField(max_length=10, unique=True)

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
        return f"{self.year}"


class AcademicTimeline(models.Model):
    """
    AcademicTimeline.get_current()
    AcademicTimeline.create_next()
    """

    class Meta:
        
        unique_together = (
            'academic_semester', 'academic_year'
        )

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
        tl = AcademicTimeline.objects.all().last()
        return AcademicTimeline.create_first() if not tl else tl

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

    FIRST_YEAR = "1L"
    SECOND_YEAR = "2L"
    THIRD_YEAR = "3L"
    FOURTH_YEAR = "4L"
    FIFTH_YEAR = "5L"

    levels_list: List =[FIRST_YEAR, SECOND_YEAR, THIRD_YEAR, FOURTH_YEAR, FIFTH_YEAR]

    name = models.CharField(max_length=200, blank=True, null=True)
    matric_no = models.CharField(
        max_length=200,
        unique=True,
        blank=True,
        null=True,
    )
    student_class: StudentClass = models.ForeignKey(
        StudentClass,
        models.SET_NULL,
        blank=True,
        null=True,
    )
    promote_eligible = models.BooleanField(
        default=True
    )

    def __str__(self) -> str:
        return f"<Student: {self.user.username}>"

    def promote(self):
        if self.promote_eligible:
            index_old_level = Student.levels_list.index(self.student_class.level)
            if index_old_level == 4:
                return
            new_level = Student.levels_list[index_old_level + 1]
            dept = self.student_class.department
            student_class, _ = StudentClass.objects.get_or_create(level = new_level, department=dept)
            self.student_class = student_class
            self.save()
        return self

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
            raise Exception("No Student Class")

    def init_course_reg(self):
        tl = AcademicTimeline.get_current()
        alloc = self.get_semester_allocation()
        form, _ = CourseRegistrationForm.objects.get_or_create(student=self, timeline=tl)
        courses = alloc["default"].all()
        courses_2 = alloc["carryovers"].all()
        default = [
            CourseRegistration.objects.get_or_create(
                student=self, course=course, academic_timeline=tl, form=form
            )
            for course in courses
        ]
        carryovers = [
            CourseRegistration.objects.get_or_create(
                student=self, course=course, academic_timeline=tl, form=form
            )
            for course in courses_2
        ]
        course_alloc = {
            "default": default,
            "carryovers": carryovers
        }
        return course_alloc


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
    prerequisites = models.ManyToManyField("Course", blank=True)
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


class CourseRegistrationForm(models.Model):
    student = models.ForeignKey(Student, models.SET_NULL, blank=True, null=True)
    timeline = models.ForeignKey(AcademicTimeline, models.SET_NULL, blank=True, null=True)
    total_current_units = models.IntegerField(default=0)



class CourseRegistration(models.Model):

    APPROVED = "APR"
    PENDING = "PEN"
    UNAPPROVED = "UNA"

    COURSE_REG_STATUS_CHOICES = [
        (APPROVED, "Approved"),
        (PENDING, "Pending"),
        (UNAPPROVED, "Unapproved"),
    ]

    class Meta:
        unique_together = ("academic_timeline", "student", "course")

    student: Student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=3, choices=COURSE_REG_STATUS_CHOICES, default=UNAPPROVED
    )
    form = models.ForeignKey(
        CourseRegistrationForm,
        models.SET_NULL,
        blank=True,
        null=True,
        related_name="courses",
    )
    academic_timeline = models.ForeignKey(
        AcademicTimeline, models.SET_NULL, blank=True, null=True
    )

    def __str__(self) -> str:
        return f"<Course Registration: {self.student.user.username} {self.course.course_code} {self.get_status_display()}>"

    def request_course_reg(self):
        form = self.form
        course = self.course
        max_units = self.student.student_class.max_units

        if form.total_current_units + course.course_units <= max_units:
            self.status = CourseRegistration.PENDING
            self.save()

    def approve_course_reg(self):

        if self.status == CourseRegistration.PENDING:
            self.status = CourseRegistration.APPROVED
            self.save()
            return self

    def reject_course_reg(self):
        form = self.form
        course = self.course

        self.status = CourseRegistration.UNAPPROVED
        self.save()
        form.total_current_units -= course.course_units
        form.save()
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


def create_student_classes(sender, instance, **kwargs):
   levels = ["1L", "2L", "3L", "4L", "5L",]
   for level in levels:
       sc, _ = StudentClass.objects.get_or_create(level=level, department=instance)
    


def form_units(sender, instance, **kwargs):
    form = instance.form
    regs = CourseRegistration.objects.filter(form=form)
    regs = regs.filter(status="PEN")|regs.filter(status="APR")
    regs = regs.all()
    units = sum([reg.course.course_units for reg in regs])
    form.total_current_units = units
    form.save()



def save_grade(sender, instance, **kwargs):
    instance.grade = StudentGrade.getLetterGrade(instance.score)


pre_save.connect(save_grade, sender=StudentGrade)
post_save.connect(create_student_classes, sender=Department)
post_save.connect(form_units, sender=CourseRegistration)