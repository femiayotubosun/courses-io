from typing import List
from django.forms.models import model_to_dict
from coursesapp.forms import ProfileForm, StudentClassForm, TimelineForm
from coursesapp.views.adviser import student
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import redirect, render
from django.urls import reverse
from coursesapp.models import AcademicTimeline, AcademicYear, CourseRegistration, CourseRegistrationForm, PortalOpen, Student, StudentClass
from django.contrib import messages

@login_required
@permission_required("coursesapp.is_student")
def dashboard(request):
    tl = AcademicTimeline.get_current()
    student = Student.objects.get(user=request.user)

    if not student.student_class:
        messages.error(request, "Please select your department and level")
        return redirect(reverse('student_my_data'))

    if not student.name:
        messages.error(request, "Please set your name")
        return redirect(reverse('student_my_data'))

    all_course_regs = CourseRegistration.objects.filter(academic_timeline=tl, student=student)
    approved_course_regs = all_course_regs.filter(status='APR')
    pending_course_regs = all_course_regs.filter(status='PEN')
    unappr_course_regs = all_course_regs.filter(status='UNA')

    header = "Welcome," + student.name if student.name else "student"
    return render(request, "student/dashboard.html", {
        "all_course_regs": all_course_regs,
        "approved_course_regs": approved_course_regs, 
        "pending_course_regs": pending_course_regs,
        "unappr_course_regs": unappr_course_regs,
        "title": "Dashboard | Student",
        "header": header
    })


@login_required
@permission_required("coursesapp.is_student")
def mydata(request):

    tl = AcademicTimeline.get_current()
    sc_form = StudentClassForm()
    student = Student.objects.get(user=request.user)

    pf_form = ProfileForm(instance=student)

    context = {'timeline': tl, 'student':student, "header": "Dashboard | Student", "title": "My Data", 'form': sc_form if student.student_class is None else pf_form}
    
    
    if request.method == 'POST':
        if 'department' in request.POST:
            form = StudentClassForm(request.POST)
            if form.is_valid():
                sc = StudentClass.objects.get(level=form.cleaned_data['level'], department=form.cleaned_data['department'])
                student.student_class = sc
                student.save()
                return redirect('student_my_data')
        else:
            form = ProfileForm(request.POST, instance=student)
            if form.is_valid():
                form.save()
                return redirect('student_my_data')
        
    
    return render(request, "student/dashboard_my_data.html", context)


@login_required
@permission_required("coursesapp.is_student")
def archives(request):
    form = TimelineForm()
    student = Student.objects.get(user=request.user)
    if not student.student_class:
        messages.error(request, "Please select your department and level")
        return redirect(reverse('student_my_data'))

    if not student.name:
        messages.error(request, "Please set your name")
        return redirect(reverse('student_my_data'))

    if request.method == 'POST':
        try:
            yr = AcademicYear.objects.get(pk=request.POST['academic_year'])
            semester = request.POST['academic_semester']
            tl= AcademicTimeline.objects.get(academic_year=yr, academic_semester=semester)
            form = TimelineForm(request.POST, instance=tl)
        except:
            messages.error(request, "Invalid timeline or No Data found!")
            return redirect(reverse('student_archives'))
        if form.is_valid():

            tl = form.instance
            form = TimelineForm(instance=form.instance)
            course_form, _ = CourseRegistrationForm.objects.get_or_create(timeline=tl, student=student)
            cf = course_form
            course_form = course_form.courses.all()
            return render(request, "student/dashboard_archive.html", { "cf": cf, "form": form, "header": "Dashboard | Student", "title": "Archives", "course_form": course_form })

    
    return render(request, "student/dashboard_archive.html", { "form": form, "header": "Dashboard | Student", "title": "Archives" })

@login_required
@permission_required("coursesapp.is_student")
def course_form(request, form_id):
    student = Student.objects.get(user=request.user)
    if not student.student_class:
        messages.error(request, "Please select your department and level")
        return redirect(reverse('student_my_data'))

    if not student.name:
        messages.error(request, "Please set your name")
        return redirect(reverse('student_my_data'))


    data = course_form.courses.all()
    student = course_form.student
    # if s == student:
    #     return redirect(reverse('student_dashboard'))
    return render(request, "student/dashboard_archived_form.html", {"data": data, "course_form": course_form, "student": student, "header": "Dashboard | Course Form", "title": "Archives" })




@login_required
@permission_required("coursesapp.is_student")
def course_reg(request):
    tl: AcademicTimeline = AcademicTimeline.get_current()
    portal_open: PortalOpen = PortalOpen.objects.get(pk=1).course_registration_open

    if not portal_open:
        messages.error(request, 'Course registration has closed')
        return render(request, "student/dashboard_course_registration.html", {"header": f"Course Regisration for {tl.academic_year.year} {tl.get_academic_semester_display()} semester has closed", "title": "Course Registration"} )
    
    try: 
        student: Student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, "You cannot view this page because you are not a student")
        return redirect(reverse('login'))

    if not student.student_class:
        messages.error(request, "Please select your department and level")
        return redirect(reverse('student_my_data'))

    if not student.name:
        messages.error(request, "Please set your name")
        return redirect(reverse('student_my_data'))

    try:
        course_form = CourseRegistrationForm.objects.get(student=student, timeline=tl)
    except CourseRegistration.DoesNotExist:
        messages.error("Your Course form has not been initialized. Wait for level adviser...")
        return redirect(reverse('student_dashboard'))

    
    sem_alloc = student.get_semester_allocation()
    default_courses = sem_alloc['default'].all()
    carryover_courses  = sem_alloc['carryovers'].all()

    carryovers = CourseRegistration.objects.filter(course__in=carryover_courses, student=student, form=course_form).all()
    default = CourseRegistration.objects.filter(course__in=default_courses, student=student, form=course_form).all()
    max_units: int = student.student_class.max_units

    registered_carryovers = True
    units_exceeded = True if course_form.total_current_units < max_units else False
    can_register = registered_carryovers and units_exceeded

    # Make carryovers compulsory and check if registering the course will exceed the maximum units allowed
    for reg in carryovers:
        units = reg.course.course_units

        if course_form.total_current_units + units > max_units:
            reg.can_register = False
        else:
            reg.can_register = True
        reg.course.course_type = "COM"

        # Check if all carryovers have been registered
        if reg.status == "UNA":
            registered_carryovers = False
    
    for reg in default:
        units = reg.course.course_units
        preq = reg.course.prerequisites.all()

        if any(c in carryover_courses for c in preq):
            reg.course.course_title += " - failed prerequisites!" 
            reg.can_register = False
            continue
        if course_form.total_current_units + units > max_units:
            reg.can_register = False
        else:
            reg.can_register = True
    
    return render(request, "student/dashboard_course_registration.html", {"can_register": can_register, "portal_open": portal_open, "carryovers": carryovers, "regular": default,
    "max_units": max_units, "course_form": course_form, "header": f"Your Course Regisration for {tl.academic_year.year} {tl.get_academic_semester_display()} semester", "title": "Course Registration"})
    

    # I need to check if all carry overs are registered


    # For each reg, check if they'll exceed max_units when registered




    
    #  TODO: Courses the student cannot register
    # TODO FUNCTION FOR REGISTERING STUDENTS
    # 
    # student = model_to_dict(student)
    # course_form = model_to_dict(course_form)

    # carryovers = [CourseRegSerializer(instance=c).data for c in carryovers[:]]
    # default = [CourseRegSerializer(instance=d).data for d in default[:]]

    # context = {
    #                             "student": student,
    #                             # "sem_alloc": sem_alloc,
    #                             "regular": default,
    #                             "carryovers": carryovers,
    #                             "max_units": max_units,
    #                             "course_form": course_form
    
    # }
    # return render(request, "student/dashboard_course_registration.html", {"context": context,
    # "header": f"Your Course Regisration for {tl.academic_year.year} {tl.get_academic_semester_display()} semester", "title": "Course Registration"})
    



@login_required
@permission_required("coursesapp.is_student")
def request_reg(request, reg_id):
    student: Student = Student.objects.get(user=request.user)
    reg: CourseRegistration = CourseRegistration.objects.get(pk=reg_id)

    if student.pk is not reg.student.pk:
        messages.success(request, "Request Successful.")
        return redirect(reverse('student_registration'))

    reg.request_course_reg()
    return redirect(reverse("student_registration"))