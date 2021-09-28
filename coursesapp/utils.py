from django.contrib.auth.models import Group
from coursesapp.models import CourseRegistration, Lecturer, LevelAdviser, Student
from django.core import serializers

def make_user(user, role):
    dict_of_models = {"lecturer": Lecturer, "adviser": LevelAdviser, "student": Student}
    if dict_of_models[role] == Lecturer:
        g = Group.objects.get(name="lecturers")
        g.user_set.add(user)
    elif dict_of_models[role] == LevelAdviser:
        g = Group.objects.get(name="advisers")
        g.user_set.add(user)
    else:
        g = Group.objects.get(name="students")
        g.user_set.add(user)
        return Student.objects.create(user=user)
    return dict_of_models[role].objects.create(user=user)



def serializer(model_instance, multiple=False):
    if multiple:
        data = serializers.serialize("json", model_instance, ensure_ascii=False)
        return data
    else:
        data = serializers.serialize("json", [model_instance], ensure_ascii=False)
        return data[1:-1]

