from django.contrib.auth.models import Group
from coursesapp.models import CourseRegistration, Lecturer, LevelAdviser, Student
from django.core import serializers
from django.shortcuts import render
from django.template.loader import render_to_string
from xhtml2pdf import pisa
# from weasyprint import HTML, CSS

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



def report(data):
    regs = CourseRegistration.objects.filter(form=data)
    name = f'coursesapp/staticfiles/coursesapp/reports/course_reg_{data.student.name}'
    context = {
    "regs": regs,
    "form": data
    }


    content = render_to_string('report.html', context )
    with open(f"{name}.pdf", "w+b") as f:
        pisa.CreatePDF(
            content,                # the HTML to convert
            dest=f)
            
    return f"{name}.pdf"

def eligible_report(data):
    name = f"coursesapp/static/coursesapp/reports/eligible_{data['lecturer'].name} -- {data['course'].course_code}"
    context = {
        "course": data["course"],
        "timeline": data['timeline'],
        "regs": data["regs"],
        "lecturer": data["lecturer"]
    }

    content = render_to_string('eligible_students.html', context)
    with open(f"{name}.pdf", "w+b") as f:
        pisa.CreatePDF(
            content,                # the HTML to convert
            dest=f)
            
    return f"{name}.pdf"