from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse, FileResponse
from django.urls import reverse
from django.contrib import messages

from coursesapp.models import (
    AcademicTimeline,
    CourseRegistrationForm,
    Lecturer,
    LevelAdviser,
    PortalOpen,
    Student,
)
from coursesapp import utils


@login_required
def index(request):
    user = request.user

    try:
        Student.objects.get(user=user)
        return redirect(reverse("student_dashboard"))
    except Student.DoesNotExist:
        try:
            Lecturer.objects.get(user=user)
            return redirect(reverse("lecturer_dashboard"))
        except Lecturer.DoesNotExist:
            try:
                LevelAdviser.objects.get(user=user)
                return redirect(reverse("adviser_dashboard"))
            except:
                return redirect(reverse("login"))


def signup(request):
    if request.method == "POST":
        if not (request.POST["password"] == request.POST["re-password"]) or not (
            request.POST["username"]
        ):
            messages.error(request, "Passwords don't match")
            return redirect(reverse("signup"))
            
        try:
            user = User.objects.get(username=request.POST["username"])

            messages.error(request, "Username already exist")
            return redirect(reverse("signup"))
            # Modal user already exists
        except User.DoesNotExist:
            user = User.objects.create_user(
                username=request.POST["username"],
                password=request.POST["password"],
                email=request.POST["email"] if request.POST["email"] else None,
            )
            try:
                utils.make_user(user, request.POST["registeras"])
                messages.success(request, "Registrations successful, please login")
                return redirect(reverse("login"))
            except Exception as e:
                return redirect(reverse("signup"))
    return render(request, template_name="signup.html")


@login_required
@permission_required("coursesapp.can_create_tl")
def create_next_tl(request):
    AcademicTimeline.create_next()
    return HttpResponse("New Tl Created")


@login_required
@permission_required("coursesapp.can_modify_portal")
def open_portal(request):

    if PortalOpen.objects.all().count() == 0:
        p = PortalOpen.objects.create()
        p.save()
    else:
        p = PortalOpen.objects.all().last()
        p.course_registration_open = True
        p.save()
    return HttpResponse("Portal is open")


@login_required
@permission_required("coursesapp.can_modify_portal")
def close_portal(request):
    if PortalOpen.objects.all().count() == 0:
        p = PortalOpen.objects.create()
        p.course_registration_open = False
        p.save()
    else:
        p = PortalOpen.objects.all().last()
        p.course_registration_open = False
        p.save()
    return HttpResponse("Portal is open")



# DOWNLOAD DATA
@login_required
def print_form(request, reg_id):
    form = CourseRegistrationForm.objects.get(pk=reg_id)
    data = utils.report(form)
    data = open(data, 'rb')
    response = FileResponse(data, as_attachment=True)
    return response
