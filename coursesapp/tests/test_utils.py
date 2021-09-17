# from django.test import TestCase
# from django.contrib.auth.models import User, Group
# from coursesapp.models import Lecturer, LevelAdviser, Student
# from coursesapp.utils import make_user

    
# class MakeUserTest(TestCase):
#     def setUp(self) -> None:
#         self.user = User.objects.create(
#             username="testuserA", email="testuser3@test.com", password="password1#q212P"
#         )

#     def test_utils(self):
#         data = make_user(self.user, "lecturer")
#         self.assertIsInstance(Lecturer, data)
