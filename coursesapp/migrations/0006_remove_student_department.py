# Generated by Django 3.2.7 on 2021-09-03 16:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coursesapp', '0005_course_lecturer_leveladviser_profile_student'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='department',
        ),
    ]