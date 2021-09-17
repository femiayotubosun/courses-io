from django.http import response
from coursesapp.views.base import signup
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Permission
from coursesapp.models import (
    AcademicTimeline,
    Course,
    Department,
    Lecturer,
    PortalOpen,
    SemesterCourseAllocation,
    Student,
    LevelAdviser,
    StudentClass,
)
from django.contrib.contenttypes.models import ContentType


class BaseTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.index_url = reverse("index")
        self.signup_url = reverse("signup")
        self.new_tl_url = reverse("create_next_tl")
        self.open_portal_url = reverse("open_portal")
        self.close_portal_url = reverse("close_portal")

    def test_signup_test_GET(self):

        response = self.client.get((reverse("signup")))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "signup.html")

    def test_signup_POST(self):

        response = self.client.post(
            self.signup_url,
            {
                "username": "testuser3",
                "email": "testuser3@test.com",
                "password": "password1#q212P",
                "re-password": "password1#q212P",
                "registeras": "student",
            },
        )
        self.assertEquals(response.status_code, 302)

        # Test user was created
        user = User.objects.filter(username="testuser3").first()
        self.assertEquals(User.objects.all().first().username, "testuser3")
        self.assertEquals(Student.objects.all().first().user, user)

    def test_signup_non_matching_passwords_and_missing_username(self):

        response = self.client.post(
            self.signup_url,
            {
                "password": "as;dfasdfo39A",
                "re-password": "asdfasd*3921",
                "email": "test@tes.com",
                "registeras": "student",
            },
        )
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, "/signup/")

    def test_existing_user(self):

        User.objects.create(
            username="testuserA", email="testuser3@test.com", password="password1#q212P"
        )

        response = self.client.post(
            self.signup_url,
            {
                "username": "testuserA",
                "email": "testuser3@test.com",
                "password": "password1#q212P",
                "re-password": "password1#q212P",
                "registeras": "student",
            },
        )
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, "/signup/")

    def test_exception_from_make_user(self):
        response = self.client.post(
            self.signup_url,
            {
                "username": "testuserA",
                "email": "testuser3@test.com",
                "password": "password1#q212P",
                "re-password": "password1#q212P",
                "registeras": "studsdent",
            },
        )
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, "/signup/")

    def test_index_GET(self):
        res = self.client.get(reverse("index"))
        # print(res.content)
        self.assertEqual(res.status_code, 200)

    def test_create_next_tl(self):
        old = AcademicTimeline.objects.all().count()

        # Create user, giver persmission

        content_type = ContentType.objects.get_for_model(AcademicTimeline)
        permission = Permission.objects.create(
            codename="can_create_tl",
            name="Can Modify Portal",
            content_type=content_type,
        )

        response = self.client.post(
            self.signup_url,
            {
                "username": "testuserA",
                "email": "testuser3@test.com",
                "password": "password1#q212P",
                "re-password": "password1#q212P",
                "registeras": "student",
            },
        )

        user = User.objects.get(username="testuserA")
        user.user_permissions.add(permission)
        self.assertEquals(response.status_code, 302)
        response = self.client.post(
            reverse("login"),
            {
                "username": "testuserA",
                "password": "password1#q212P",
            },
        )

        response = self.client.get(self.new_tl_url)
        self.assertEquals(200, response.status_code)
        self.assertEquals(old + 1, AcademicTimeline.objects.all().count())

    def test_open_open_tl(self):
        content_type = ContentType.objects.get_for_model(PortalOpen)
        permission = Permission.objects.create(
            codename="can_modify_portal",
            name="Can Modify Portal",
            content_type=content_type,
        )

        response = self.client.post(
            self.signup_url,
            {
                "username": "testuserA",
                "email": "testuser3@test.com",
                "password": "password1#q212P",
                "re-password": "password1#q212P",
                "registeras": "student",
            },
        )

        user = User.objects.get(username="testuserA")
        user.user_permissions.add(permission)
        self.assertEquals(response.status_code, 302)
        self.client.login(
            username="testuserA",
            password="password1#q212P",
        )
        response = self.client.get(self.open_portal_url)
        self.assertEquals(200, response.status_code)
        self.assertEquals(
            True, PortalOpen.objects.all().last().course_registration_open
        )

    def test_close_tl(self):
        content_type = ContentType.objects.get_for_model(PortalOpen)
        permission = Permission.objects.create(
            codename="can_modify_portal",
            name="Can Modify Portal",
            content_type=content_type,
        )

        response = self.client.post(
            self.signup_url,
            {
                "username": "testuserA",
                "email": "testuser3@test.com",
                "password": "password1#q212P",
                "re-password": "password1#q212P",
                "registeras": "student",
            },
        )

        user = User.objects.get(username="testuserA")
        user.user_permissions.add(permission)
        self.assertEquals(response.status_code, 302)
        self.client.login(
            username="testuserA",
            password="password1#q212P",
        )
        response = self.client.get(self.close_portal_url)
        self.assertEquals(200, response.status_code)
        self.assertEquals(
            False, PortalOpen.objects.all().last().course_registration_open
        )

    def test_multiple_open_portal(self):
        content_type = ContentType.objects.get_for_model(PortalOpen)
        permission = Permission.objects.create(
            codename="can_modify_portal",
            name="Can Modify Portal",
            content_type=content_type,
        )

        response = self.client.post(
            self.signup_url,
            {
                "username": "testuserA",
                "email": "testuser3@test.com",
                "password": "password1#q212P",
                "re-password": "password1#q212P",
                "registeras": "student",
            },
        )

        user = User.objects.get(username="testuserA")
        user.user_permissions.add(permission)
        self.assertEquals(response.status_code, 302)
        self.client.login(
            username="testuserA",
            password="password1#q212P",
        )
        response = self.client.get(self.open_portal_url)
        self.assertEquals(200, response.status_code)
        self.assertEquals(
            True, PortalOpen.objects.all().last().course_registration_open
        )
        response = self.client.get(self.open_portal_url)
        self.assertEquals(200, response.status_code)
        self.assertEquals(
            True, PortalOpen.objects.all().last().course_registration_open
        )

    def test_multiple_close_tl(self):
        content_type = ContentType.objects.get_for_model(PortalOpen)
        permission = Permission.objects.create(
            codename="can_modify_portal",
            name="Can Modify Portal",
            content_type=content_type,
        )

        response = self.client.post(
            self.signup_url,
            {
                "username": "testuserA",
                "email": "testuser3@test.com",
                "password": "password1#q212P",
                "re-password": "password1#q212P",
                "registeras": "student",
            },
        )

        user = User.objects.get(username="testuserA")
        user.user_permissions.add(permission)
        self.assertEquals(response.status_code, 302)
        self.client.login(
            username="testuserA",
            password="password1#q212P",
        )
        response = self.client.get(self.open_portal_url)
        self.assertEquals(200, response.status_code)
        self.assertEquals(
            True, PortalOpen.objects.all().last().course_registration_open
        )
        response = self.client.get(self.close_portal_url)
        self.assertEquals(200, response.status_code)
        self.assertEquals(
            False, PortalOpen.objects.all().last().course_registration_open
        )


class AdviserTest(TestCase):
    def setUp(self) -> None:
        content_type = ContentType.objects.get_for_model(LevelAdviser)
        permission = Permission.objects.get(
            codename="is_adviser",
        )

        self.client = Client()
        response = self.client.post(
            reverse("signup"),
            {
                "username": "testuser",
                "email": "testuser@test.com",
                "password": "password1#q212P",
                "re-password": "password1#q212P",
                "registeras": "adviser",
            },
        )

        self.assertEquals(response.status_code, 302)
        response = self.client.post(
            reverse("signup"),
            {
                "username": "testuser3",
                "email": "testuser3@test.com",
                "password": "password1#q212P",
                "re-password": "password1#q212P",
                "registeras": "student",
            },
        )
        response = self.client.post(
            reverse("signup"),
            {
                "username": "testuser4",
                "email": "testuser3@test.com",
                "password": "password1#q212P",
                "re-password": "password1#q212P",
                "registeras": "student",
            },
        )
        self.assertEquals(response.status_code, 302)
        self.d = Department.objects.create(department_name="Test Department")
        sc = StudentClass.objects.create(department=self.d)
        user1 = User.objects.filter(username="testuser4").first()
        s = Student.objects.get(user=user1)
        s.student_class = sc
        s.save()

        user = User.objects.filter(username="testuser").first()
        user.user_permissions.add(permission)
        # Create student
        course = Course.objects.create(course_title="Test Course", course_code="TST")
        # Create a course
        self.dashboard_url = reverse("adviser_dashboard")
        self.lecturers_url = reverse("adviser_lecturers")
        self.student_levels_url = reverse("adviser_students_levels")
        self.students_in_level_url = reverse(
            "adviser_students_in_level", kwargs={"level_name": "1L"}
        )
        self.one_student_url = reverse("adviser_one_student", kwargs={"student_id": 2})
        self.courses_url = reverse("adviser_courses")
        self.one_course_url = reverse("adviser_course", kwargs={"course_id": 1})
        self.one_course_data = reverse("adviser_course_data", kwargs={"course_id": 1})
        self.one_course_edit = reverse("adviser_edit_course", kwargs={"course_id": 1})

    def test_GET_dashboard(self):
        self.client.login(
            username="testuser",
            password="password1#q212P",
        )
        response = self.client.get(self.dashboard_url)
        self.assertEquals(200, response.status_code)
        self.assertTemplateUsed(response, "adviser/dashboard.html")
        self.assertTrue("department" in response.context)
        self.assertTrue("lecturers" in response.context)
        self.assertTrue("students" in response.context)
        self.assertTrue("courses" in response.context)
        self.assertTrue("all_course_regs" in response.context)
        self.assertTrue("approved_course_regs" in response.context)
        self.assertTrue("pending_course_regs" in response.context)
        self.assertTrue("unappr_course_regs" in response.context)
        self.assertTrue("title" in response.context)

    def test_GET_lecturers(self):
        self.client.login(
            username="testuser",
            password="password1#q212P",
        )
        response = self.client.get(self.lecturers_url)
        self.assertEquals(200, response.status_code)
        self.assertTemplateUsed("adviser/dashboard_lecturers.html")

    def test_GET_courses(self):
        self.client.login(username="testuser", password="password1#q212P")
        response = self.client.get(self.courses_url)
        self.assertEquals(200, response.status_code)
        self.assertTemplateUsed("adviser/dashboard_courses.html")

    def test_GET_one_course(self):
        self.client.login(username="testuser", password="password1#q212P")
        response = self.client.get(self.one_course_url)
        self.assertEquals(200, response.status_code)
        self.assertTemplateUsed("adviser/dashboard_course.html")

    def test_GET_one_course_data(self):
        self.client.login(username="testuser", password="password1#q212P")
        response = self.client.get(self.one_course_data)
        self.assertEquals(200, response.status_code)
        self.assertTemplateUsed("adviser/dashboard_course_data.html")

    def test_GET_course_edit(self):
        self.client.login(username="testuser", password="password1#q212P")
        response = self.client.get(self.one_course_edit)
        self.assertEquals(200, response.status_code)
        self.assertTemplateUsed("adviser/dashboard_course_edit.html")
        # self.assertTemplateUsed("adviser/dashboard_course.html")

    def test_GET_students_levels(self):
        self.client.login(username="testuser", password="password1#q212P")
        response = self.client.get(self.student_levels_url)
        self.assertEquals(200, response.status_code)
        self.assertTemplateUsed("adviser/dashboard_students_levels.html")

    def test_GET_students_in_level(self):
        self.client.login(username="testuser", password="password1#q212P")
        response = self.client.get(self.students_in_level_url)
        self.assertEquals(200, response.status_code)
        self.assertTemplateUsed("adviser/dashboard_students.html")

    def test_GET_one_student_no_stud_class(self):
        self.client.login(username="testuser", password="password1#q212P")
        response = self.client.get(self.one_student_url)
        self.assertEquals(200, response.status_code)
        self.assertTemplateUsed("adviser/dashboard_student.html")

    def test_GET_one_student_(self):
        self.client.login(username="testuser", password="password1#q212P")

        student = Student.objects.get(pk=2)

        test_user2 = User.objects.create(
            username="testuserwadf332", password="KLSDJN92&63)932"
        )

        d = Department.objects.create(department_name="Test")
        lecturer = Lecturer.objects.create(
            user=test_user2, name="Test Lecturer", department=d
        )

        course1 = Course.objects.create(
            course_title="Test Course", course_code="TST111", lecturer=lecturer
        )
        course2 = Course.objects.create(
            course_title="Test Course 2", course_code="TST112", lecturer=lecturer
        )
        course3 = Course.objects.create(
            course_title="Test Course 3", course_code="TST113", lecturer=lecturer
        )
        course4 = Course.objects.create(
            course_title="Test Course 4", course_code="TST114", lecturer=lecturer
        )
        course5 = Course.objects.create(
            course_title="Test Course 5", course_code="TST115", lecturer=lecturer
        )

        sm_a = SemesterCourseAllocation.objects.create(
            student_class=student.student_class
        )

        sm_a.course_list.add(course1, course2, course3, course4, course5)

        AcademicTimeline.create_first()
        response = self.client.get(
            reverse("adviser_one_student", kwargs={"student_id": 2})
        )
        self.assertEquals(200, response.status_code)
        self.assertTrue("courses_carry" in response.context)
        self.assertTrue("courses_default" in response.context)
        self.assertTemplateUsed("adviser/dashboard_student.html")
