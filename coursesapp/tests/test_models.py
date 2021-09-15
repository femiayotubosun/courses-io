from django.test import TestCase
from django.contrib.auth.models import User
from coursesapp.models import (
    AcademicTimeline,
    Course,
    CourseRegistration,
    Department,
    Lecturer,
    LevelAdviser,
    SemesterCourseAllocation,
    Student,
    StudentClass,
    AcademicYear,
    StudentGrade,
)


class DepartmentTest(TestCase):
    def create_dept(self, name="Test Department"):
        return Department.objects.create(department_name=name)

    def test_dept_creation(self):
        d = self.create_dept()
        self.assertTrue(isinstance(d, Department))
        self.assertEqual(d.__str__(), "<Department: Test Department>")


class StudentClassTest(TestCase):
    def setUp(self) -> None:
        self.d = Department.objects.create(department_name="Test Department")

    def create_student_class(self, level=None):
        return (
            StudentClass.objects.create(department=self.d)
            if level == None
            else StudentClass.objects.create(department=self.d, level=level)
        )

    def test_student_class_creation(self):
        sc = self.create_student_class()
        self.assertTrue(isinstance(sc, StudentClass))
        self.assertEqual(sc.__str__(), "<Student Class: Test Department 100 Level>")

    def test_set_differnt_levl(self):
        sc = self.create_student_class(level="2L")
        self.assertTrue(isinstance(sc, StudentClass))
        self.assertTrue(sc.__str__(), "<Student Class: Test Department 200 Level>")


class AcademicYearTest(TestCase):
    def test_create_manually(self):
        ay = AcademicYear.objects.create(year="2020/2021")
        self.assertTrue(isinstance(ay, AcademicYear))
        self.assertEqual(ay.__str__(), "<Academic Year: 2020/2021>")

    def test_create_first(self):
        ay = AcademicYear.create_first()
        self.assertTrue(isinstance(ay, AcademicYear))
        self.assertEqual(ay.__str__(), "<Academic Year: 2021/2022>")

    def test_create_next(self):
        ay = AcademicYear.create_first()
        self.assertTrue(ay.__str__(), "<Academic Year: 2021/2022>")
        next_ay = AcademicYear.create_next()
        self.assertTrue(next_ay.__str__(), "<Academic Year:2022/2023>")

    def test_make_session_with_string(self):
        test_year = AcademicYear.make_sesssion_from_year("2021")
        self.assertEqual("2021/2022", test_year)

    def test_make_session_exception(self):
        with self.assertRaises(Exception) as context:
            AcademicYear.make_sesssion_from_year("sdf")
            self.assertTrue(ValueError in context.exception)


class AcademicTimelineTestManual(TestCase):
    def setUp(self):
        pass
        self.year = AcademicYear.create_first()

    def test_create_manually(self):
        atl = AcademicTimeline.objects.create(academic_year=self.year)
        self.assertTrue(isinstance(atl, AcademicTimeline))
        self.assertEqual(atl.__str__(), "<Academic Timeline: 2021/2022 First Semester>")


class AcademicTimelineTestFunctions(TestCase):
    def setUp(self) -> None:
        pass

    def test_create_first(self):
        atl = AcademicTimeline.create_first()
        self.assertEqual(atl.__str__(), "<Academic Timeline: 2021/2022 First Semester>")

    def test_create_next(self):
        first_atl = AcademicTimeline.create_next()
        self.assertEqual(
            first_atl.__str__(), "<Academic Timeline: 2021/2022 First Semester>"
        )
        next_atl_second_sem = AcademicTimeline.create_next()
        self.assertEqual(
            next_atl_second_sem.__str__(),
            "<Academic Timeline: 2021/2022 Second Semester>",
        )
        current_atl = AcademicTimeline.get_current()
        self.assertEqual(current_atl, next_atl_second_sem)

    def test_creat_next_new_session(self):
        AcademicTimeline.create_first()
        AcademicTimeline.create_next()
        AcademicTimeline.create_next()
        new_atl = AcademicTimeline.create_next()
        self.assertEqual(
            new_atl.__str__(), "<Academic Timeline: 2022/2023 First Semester>"
        )
        new_atl_sem = AcademicTimeline.create_next()
        self.assertEqual(
            new_atl_sem.__str__(), "<Academic Timeline: 2022/2023 Second Semester>"
        )


class StudentTest(TestCase):
    def setUp(self):
        self.test_user = User.objects.create(
            username="testuser12", password="KLSDJN92&63)932"
        )
        d = Department.objects.create(department_name="Test Department")

        self.student_cls = StudentClass.objects.create(department=d)
        AcademicTimeline.create_first()

        test_user2 = User.objects.create(
            username="testuser", password="KLSDJN92&63)932"
        )
        self.lecturer = Lecturer.objects.create(
            user=test_user2, name="Test Lecturer", department=d
        )

        self.course1 = Course.objects.create(
            course_title="Test Course", course_code="TST111", lecturer=self.lecturer
        )
        self.course2 = Course.objects.create(
            course_title="Test Course 2", course_code="TST112", lecturer=self.lecturer
        )
        self.course3 = Course.objects.create(
            course_title="Test Course 3", course_code="TST113", lecturer=self.lecturer
        )
        self.course4 = Course.objects.create(
            course_title="Test Course 4", course_code="TST114", lecturer=self.lecturer
        )
        self.course5 = Course.objects.create(
            course_title="Test Course 5", course_code="TST115", lecturer=self.lecturer
        )

        test_sem_alloc = SemesterCourseAllocation.objects.create(
            student_class=self.student_cls
        )

        test_sem_alloc.course_list.add(self.course1)
        test_sem_alloc.course_list.add(self.course2)
        test_sem_alloc.course_list.add(self.course3)

    def test_creation(self):
        student = Student.objects.create(
            user=self.test_user, name="Test Name", student_class=self.student_cls
        )

        user = User.objects.create(username="testuserdfd", password="somethingnice")
        student2 = Student.objects.create(user=user, name="Test Name 2")
        self.assertEqual(student.__str__(), "<Student: testuser12>")
        self.assertEqual(student2.__str__(), "<Student: testuserdfd>")

    def test_get_course_allocation_no_carryovers(self):
        student = Student.objects.create(
            user=self.test_user, name="Test Name", student_class=self.student_cls
        )
        course_alloc = student.get_semester_allocation()
        self.assertEqual(course_alloc["default"].count(), 3)
        self.assertEqual(course_alloc["carryovers"].count(), 0)

    def test_get_course_allocation_with_carryovers(self):
        student = Student.objects.create(
            user=self.test_user, name="Test Name", student_class=self.student_cls
        )
        StudentGrade.objects.create(student=student, course=self.course4, score=20)
        StudentGrade.objects.create(student=student, course=self.course5, score=15)
        course_alloc = student.get_semester_allocation()
        self.assertEqual(course_alloc["default"].count(), 3)
        self.assertEqual(course_alloc["carryovers"].count(), 2)

    def test_init_course_reg(self):
        old_count = CourseRegistration.objects.all().count()
        student = Student.objects.create(
            user=self.test_user, name="Test Name", student_class=self.student_cls
        )
        StudentGrade.objects.create(student=student, course=self.course4, score=20)
        StudentGrade.objects.create(student=student, course=self.course5, score=15)

        course_regs = student.init_course_reg()

        self.assertEquals(type(course_regs), list)
        self.assertTrue(isinstance(course_regs[0][0], CourseRegistration))
        self.assertEqual(old_count + 5, len(course_regs))


class LecturerTest(TestCase):
    def setUp(self):
        self.test_user = User.objects.create(
            username="testuser", password="KLSDJN92&63)932"
        )
        self.test_department = Department.objects.create(
            department_name="Test Department"
        )

    def test_creation(self):
        lecturer = Lecturer.objects.create(
            user=self.test_user, name="Test Lecturer", department=self.test_department
        )

        self.assertEqual(lecturer.__str__(), "<Lecturer: Test Lecturer>")


class LevelAdviserTest(TestCase):
    def setUp(self) -> None:
        self.test_user = User.objects.create(
            username="testuser", password="KLSDJN92&63)932"
        )
        self.test_department = Department.objects.create(
            department_name="Test Department"
        )

    def test_creation(self):
        adviser = LevelAdviser.objects.create(
            user=self.test_user, department=self.test_department
        )
        self.assertEqual(adviser.__str__(), "<Level Adviser: testuser>")


class CourseTest(TestCase):
    def setUp(self):
        test_user = User.objects.create(username="testuser", password="KLSDJN92&63)932")
        test_department = Department.objects.create(department_name="Test Department")

        self.lecturer = Lecturer.objects.create(
            user=test_user, name="Test Lecturer", department=test_department
        )

    def test_creation(self):
        course = Course.objects.create(
            course_title="Test Course", course_code="TST111", lecturer=self.lecturer
        )
        self.assertEqual(course.__str__(), "<Course: TST111 Compulsory>")


class StudentGradeTest(TestCase):
    def setUp(self):
        test_user1 = User.objects.create(
            username="testuser1", password="KLSDJN92&63)932"
        )
        test_user2 = User.objects.create(
            username="testuser2", password="KLSDJN92&63)932"
        )

        test_department = Department.objects.create(department_name="Test Department")
        lecturer = Lecturer.objects.create(
            user=test_user1, name="Test Lecturer", department=test_department
        )

        self.test_course = Course.objects.create(
            course_title="Test Course", course_code="TST111", lecturer=lecturer
        )
        student_class = StudentClass.objects.create(department=test_department)

        self.test_student = Student.objects.create(
            name="Test Student", user=test_user2, student_class=student_class
        )

    def test_creation(self):
        test_student_grade = StudentGrade.objects.create(
            student=self.test_student, course=self.test_course, score=50
        )
        self.assertEqual(
            test_student_grade.__str__(), "<Student Grade: Test Student TST111 C>"
        )

    def test_getLetterGrade(self):
        pass


class CourseRegistrationTest(TestCase):
    def setUp(self):
        test_user1 = User.objects.create(
            username="testuser1", password="KLSDJN92&63)932"
        )
        test_user2 = User.objects.create(
            username="testuser2", password="KLSDJN92&63)932"
        )

        test_department = Department.objects.create(department_name="Test Department")
        lecturer = Lecturer.objects.create(
            user=test_user1, name="Test Lecturer", department=test_department
        )

        self.test_course = Course.objects.create(
            course_title="Test Course", course_code="TST111", lecturer=lecturer
        )
        student_class = StudentClass.objects.create(department=test_department)

        self.test_student = Student.objects.create(
            name="Test Student", user=test_user2, student_class=student_class
        )

    def test_creation(self):
        test_cr = CourseRegistration.objects.create(
            student=self.test_student, course=self.test_course
        )
        self.assertEqual(
            test_cr.__str__(), "<Course Registration: testuser2 TST111 Unapproved>"
        )

    def test_request_course_reg(self):
        test_cr = CourseRegistration.objects.create(
            student=self.test_student, course=self.test_course
        )
        test_cr.request_course_reg()
        self.assertEqual(
            test_cr.__str__(), "<Course Registration: testuser2 TST111 Pending>"
        )

    def test_approve_course_reg(self):
        test_cr = CourseRegistration.objects.create(
            student=self.test_student, course=self.test_course
        )
        test_cr.request_course_reg()
        test_cr.approve_course_reg()
        self.assertEqual(
            test_cr.__str__(), "<Course Registration: testuser2 TST111 Approved>"
        )

    def test_reject_course_reg(self):
        test_cr = CourseRegistration.objects.create(
            student=self.test_student, course=self.test_course
        )
        test_cr.request_course_reg()
        test_cr.reject_course_reg()
        self.assertEqual(
            test_cr.__str__(), "<Course Registration: testuser2 TST111 Unapproved>"
        )


class SemesterCourseAllocationTest(TestCase):
    def setUp(self):
        test_user = User.objects.create(username="testuser", password="KLSDJN92&63)932")
        test_department = Department.objects.create(department_name="Test Department")

        self.lecturer = Lecturer.objects.create(
            user=test_user, name="Test Lecturer", department=test_department
        )
        d = Department.objects.create(department_name="Test Department")
        self.test_student_class = StudentClass.objects.create(department=d)
        self.course1 = Course.objects.create(
            course_title="Test Course", course_code="TST111", lecturer=self.lecturer
        )
        self.course2 = Course.objects.create(
            course_title="Test Course 2",
            course_code="TST112",
            lecturer=self.lecturer,
        )

    def test_creation(self):
        test_sem_alloc = SemesterCourseAllocation.objects.create(
            student_class=self.test_student_class
        )
        self.assertEqual(
            test_sem_alloc.__str__(),
            "<Course Allocation: First Semester Test Department 100 Level 0>",
        )

    def test_add_courses(self):
        test_sem_alloc = SemesterCourseAllocation.objects.create(
            student_class=self.test_student_class
        )
        test_sem_alloc.course_list.add(self.course1)
        test_sem_alloc.course_list.add(self.course2)
        self.assertEqual(
            test_sem_alloc.__str__(),
            "<Course Allocation: First Semester Test Department 100 Level 2>",
        )

    # sca.course_list.add(c)


# TODO:
"""
Logic for Course Registration,
A list of courses are passed.
Sorted with a key such that
Carry overs come first.


This is for backend validation
Student.register_courses(
    []
)
"""
