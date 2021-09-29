# Generated by Django 3.2.7 on 2021-09-03 11:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('coursesapp', '0002_portalopen'),
    ]

    operations = [
        migrations.CreateModel(
            name='AcademicTimeline',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('academic_semester', models.CharField(choices=[('FIR', 'First'), ('SEC', 'Second'), ('SUM', 'Summer')], default='FIR', max_length=3)),
                ('academic_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='coursesapp.academicyear')),
            ],
        ),
    ]