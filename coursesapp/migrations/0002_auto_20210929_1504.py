# Generated by Django 3.2.7 on 2021-09-29 14:04

from django.db import migrations
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from coursesapp.models import AcademicTimeline




def create_group_permissions(apps, schema_editor):
    lecturers, _ = Group.objects.get_or_create(name='lecturers')
    students, _ = Group.objects.get_or_create(name='students')
    advisers, _ = Group.objects.get_or_create(name='advisers')

    LevelAdviser = apps.get_model("coursesapp", "LevelAdviser")
    content_type = ContentType.objects.get_for_model(LevelAdviser)
    permission, _ = Permission.objects.get_or_create(
            codename="is_adviser", name="User is an adviser", content_type=content_type
        )
    advisers.permissions.add(permission)

    Student = apps.get_model("coursesapp", "Student")
    content_type = ContentType.objects.get_for_model(Student)
    permission, _ = Permission.objects.get_or_create(
            codename="is_student", name="User is a student", content_type=content_type
        )
    students.permissions.add(permission)

    Lecturer = apps.get_model("coursesapp", "Lecturer")
    content_type = ContentType.objects.get_for_model(Lecturer)
    permission, _ = Permission.objects.get_or_create(
            codename="is_lecturer", name="user is a lecturer", content_type=content_type
        )
    lecturers.permissions.add(permission)

def create_app_settings(apps, schema_editor):
    PortalOpen = apps.get_model("coursesapp", 'PortalOpen')

    AcademicTimeline.create_first()
    p = PortalOpen.objects.create()
    p.save()
class Migration(migrations.Migration):

    dependencies = [
        ('coursesapp', '0001_initial'),
    ]

    operations = [
            migrations.RunPython(create_group_permissions),
            migrations.RunPython(create_app_settings)
    ]
