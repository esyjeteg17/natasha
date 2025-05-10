from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Course, Task, TeacherSchedule,
    Submission, DefenseQueue, Topic, Appointment
)
from datetime import datetime, date

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    teacher = UserSerializer(read_only=True)

    class Meta:
        model = Course
        fields = '__all__'


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

class AppointmentInfoSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='student.first_name', read_only=True)
    last_name  = serializers.CharField(source='student.last_name',  read_only=True)
    position   = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = ('id', 'first_name', 'last_name', 'created_at', 'position')

    def get_position(self, obj):
        # Берём свежий QuerySet из БД, чтобы в нём был и только что созданный апойнтмент
        qs = Appointment.objects.filter(schedule=obj.schedule).order_by('created_at')
        return list(qs).index(obj) + 1
    
class TeacherScheduleSerializer(serializers.ModelSerializer):
    teacher = UserSerializer(read_only=True)
    appointments_count  = serializers.SerializerMethodField()
    max_slots           = serializers.SerializerMethodField()
    available_slots     = serializers.SerializerMethodField()
    duration_minutes    = serializers.SerializerMethodField()
    # вот наше новое поле
    appointments        = AppointmentInfoSerializer(many=True, read_only=True)

    class Meta:
        model = TeacherSchedule
        fields = [
            'id', 'title', 'date', 'start_time', 'end_time',
            'duration_minutes', 'max_slots', 'appointments_count', 'available_slots', 'teacher', 
            'appointments',
        ]

    def get_duration_minutes(self, obj):
        start_dt = datetime.combine(date.today(), obj.start_time)
        end_dt   = datetime.combine(date.today(), obj.end_time)
        return int((end_dt - start_dt).total_seconds() // 60)

    def get_max_slots(self, obj):
        return self.get_duration_minutes(obj) // 15

    def get_appointments_count(self, obj):
        return obj.appointments.count()

    def get_available_slots(self, obj):
        return self.get_max_slots(obj) - self.get_appointments_count(obj)

class SubmissionSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)

    class Meta:
        model = Submission
        fields = '__all__'
        read_only_fields = ['student', 'ai_check_passed']


class DefenseQueueSerializer(serializers.ModelSerializer):
    class Meta:
        model = DefenseQueue
        fields = '__all__'
        

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'password', 
            'first_name', 'last_name', 
            'role',  'phone',
            'group',
            'course'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'role': {'required': False},
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        if not user.role:
            user.role = 'student'
        user.save()
        return user
    

    

class AppointmentSerializer(serializers.ModelSerializer):
    student = serializers.ReadOnlyField(source='student.username')
    position = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = ('id', 'student', 'created_at', 'position')

    def get_position(self, obj):
        qs = Appointment.objects.filter(schedule=obj.schedule).order_by('created_at')
        return list(qs).index(obj) + 1