from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import (
    Course, Task, TeacherSchedule,
    Submission, DefenseQueue
)
from .serializers import (
    UserSerializer, CourseSerializer, TaskSerializer,
    TeacherScheduleSerializer, SubmissionSerializer, DefenseQueueSerializer, RegisterSerializer
)
from .services import (
    check_file_basic, find_nearest_defense_slot, calculate_max_students_per_day
)

User = get_user_model()


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_staff

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return RegisterSerializer
        return UserSerializer
    
    @action(detail=False, methods=['GET'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer): 
        if self.request.user.role != 'teacher':
            raise PermissionError("Только преподаватель может создавать курсы.")
        serializer.save(teacher=self.request.user)

    @action(detail=True, methods=['GET'], url_path='recommendation')
    def recommendation(self, request, pk=None):
        course = self.get_object()
        teacher = course.teacher
        today = request.query_params.get('date')
        if not today:
            today = str(course.teacher.schedule.first().date) \
                if course.teacher.schedule.exists() else None

        if not today:
            return Response({"error": "No schedule found"}, status=400)

        from datetime import datetime
        date_obj = datetime.strptime(today, '%Y-%m-%d').date()
        max_students = calculate_max_students_per_day(teacher, date_obj)
        return Response({"max_students": max_students})


class TeacherScheduleViewSet(viewsets.ModelViewSet):
    queryset = TeacherSchedule.objects.all()
    serializer_class = TeacherScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.role == 'teacher':
            return qs.filter(teacher=self.request.user)
        return qs

    def perform_create(self, serializer):
        if self.request.user.role != 'teacher':
            raise PermissionError("Только преподаватель может создавать расписание.")
        serializer.save(teacher=self.request.user)


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]


class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.role == 'student':
            return qs.filter(student=self.request.user)
        return qs

    def perform_create(self, serializer):
        submission = serializer.save(student=self.request.user)
        task = submission.task
        required_keywords = []
        if task.keywords:
            required_keywords = [k.strip() for k in task.keywords.split(',') if k.strip()]

        file_path = submission.file.path
        passed = check_file_basic(file_path, task.min_words, required_keywords)
        if passed:
            submission.ai_check_passed = True
            submission.status = 'in_queue'
        else:
            submission.ai_check_passed = False
            submission.status = 'rejected'
        submission.save()

        if submission.ai_check_passed:
            teacher = task.course.teacher
            slot = find_nearest_defense_slot(teacher, task.expected_defense_time)
            if slot is None:
                submission.status = 'rejected'
                submission.save()
            else:
                date, time = slot
                DefenseQueue.objects.create(
                    submission=submission,
                    teacher=teacher,
                    defense_date=date,
                    defense_time=time,
                    is_occupied=True
                )


class DefenseQueueViewSet(viewsets.ModelViewSet):
    queryset = DefenseQueue.objects.all()
    serializer_class = DefenseQueueSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.role == 'teacher':
            qs = qs.filter(teacher=self.request.user)
        elif self.request.user.role == 'student':
            qs = qs.filter(submission__student=self.request.user)
        return qs

    @action(detail=True, methods=['POST'], url_path='reschedule')
    def reschedule(self, request, pk=None):
        dq = self.get_object()
        if dq.submission.student != request.user and dq.teacher != request.user:
            return Response({"error": "Нет прав"}, status=403)

        task = dq.submission.task
        new_slot = find_nearest_defense_slot(dq.teacher, task.expected_defense_time)
        if new_slot is None:
            return Response({"error": "No free slots for reschedule"}, status=400)

        date, time = new_slot
        dq.defense_date = date
        dq.defense_time = time
        dq.save()
        return Response({"detail": "Rescheduled successfully"})

