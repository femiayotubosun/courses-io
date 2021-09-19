from django.contrib.auth.models import Group
from coursesapp.models import Lecturer, LevelAdviser, Student


def make_user(user, role):
    dict_of_models = {"lecturer": Lecturer, "adviser": LevelAdviser, "student": Student}
    if dict_of_models[role] == Lecturer:
        g = Group.objects.get(name="lecturers")
        g.user_set.add(user)
    elif dict_of_models[role] == LevelAdviser:
        g = Group.objects.get(name="advisers")
        g.user_set.add(user)
    return dict_of_models[role].objects.create(user=user)
