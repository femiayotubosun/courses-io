from django.db.models import fields
from rest_framework import serializers
from rest_framework.fields import CharField, ChoiceField
from coursesapp.models import Course, CourseRegistration

class CourseSerializer(serializers.ModelSerializer):

    course_type = CharField(source='get_course_type_display')
    class Meta:
        model = Course
        fields = '__all__'

class CourseRegSerializer(serializers.ModelSerializer):
    
    status = CharField(source='get_status_display')
    course = CourseSerializer(many=False, read_only=True)
    class Meta:
        model = CourseRegistration
        fields = '__all__'