from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied
from .filters import CourseFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import PermissionDenied, ValidationError
from datetime import datetime, date
from .models import Appointment
from .serializers import AppointmentSerializer, AppointmentInfoSerializer
from .models import (
    Course, Task, TeacherSchedule,
    Submission, DefenseQueue, Topic
)
from .serializers import (
    UserSerializer, CourseSerializer, TaskSerializer,
    TeacherScheduleSerializer, SubmissionSerializer, DefenseQueueSerializer, RegisterSerializer, TopicSerializer
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
    """
    GET    /api/courses/          — общая страница всех курсов (любой автентифицированный увидит всё)
    GET    /api/courses/me/       — личный кабинет преподавателя: только его курсы
    POST   /api/courses/          — создать курс (только teacher)
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = CourseFilter
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'hours', 'date']
    ordering = ['-date']

    def perform_create(self, serializer):
        if self.request.user.role != 'teacher':
            raise PermissionDenied("Только преподаватель может создавать курсы.")
        serializer.save(teacher=self.request.user)

    @action(detail=False, methods=['get'], url_path='me')
    def my_courses(self, request):
        """
        /api/courses/me/ — возвращает только курсы, где teacher == request.user.
        Применяет фильтры / поиск / пагинацию так же, как и обычный list.
        """
        if request.user.role != 'teacher':
            # можно возвращать пустой список или 403, на ваше усмотрение
            return Response([], status=200)

        qs = self.get_queryset().filter(teacher=request.user)
        qs = self.filter_queryset(qs)

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class TeacherScheduleViewSet(viewsets.ModelViewSet):
    queryset = (
        TeacherSchedule.objects
        .all()
        .prefetch_related('appointments__student')  # чтобы избежать N+1 на вложенных студентах
    )
    serializer_class = TeacherScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.role == 'teacher':
            return qs.filter(teacher=self.request.user)
        return qs

    def perform_create(self, serializer):
        if self.request.user.role != 'teacher':
            raise PermissionError("Только преподаватель может создать расписание.")
        serializer.save(teacher=self.request.user)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def appointments(self, request, pk=None):
        """
        Список всех записей (очереди) для конкретного окна.
        """
        schedule = self.get_object()
        qs = schedule.appointments.select_related('student')
        serializer = AppointmentSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def signup(self, request, pk=None):
        """
        Записаться на это окно (текущий пользователь).
        """
        if request.user.role != 'student':
            raise PermissionDenied("Только студент может записаться.")
        schedule = self.get_object()
        # проверка наличия свободных мест
        slot_minutes = 15
        start_dt = datetime.combine(date.today(), schedule.start_time)
        end_dt   = datetime.combine(date.today(), schedule.end_time)
        total_min = (end_dt - start_dt).total_seconds() / 60
        max_slots = int(total_min // slot_minutes)
        if schedule.appointments.count() >= max_slots:
            raise ValidationError("В этом окне нет свободных мест.")
        # создаём запись (или возвращаем ошибку, если уже есть)
        appt, created = Appointment.objects.get_or_create(
            schedule=schedule,
            student=request.user
        )
        if not created:
            return Response(
                {"detail": "Вы уже записаны на это окно."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            AppointmentSerializer(appt).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['delete'], permission_classes=[permissions.IsAuthenticated])
    def cancel_signup(self, request, pk=None):
        """
        Отменить свою запись на это окно.
        """
        schedule = self.get_object()
        try:
            appt = Appointment.objects.get(schedule=schedule, student=request.user)
        except Appointment.DoesNotExist:
            return Response(
                {"detail": "Вы не записаны на это окно."},
                status=status.HTTP_404_NOT_FOUND
            )
        appt.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return super().get_queryset()

    def perform_create(self, serializer):
        topic = serializer.validated_data['topic']
        # проверяем, что тема принадлежит курсу текущего преподавателя
        if topic.course.teacher != self.request.user:
            raise PermissionDenied("Нельзя создавать задачи не в своих темах.")
        serializer.save()


class TopicViewSet(viewsets.ModelViewSet):
    queryset = Topic.objects.all()        
    serializer_class = TopicSerializer

    def get_queryset(self):
        return super().get_queryset()

    def perform_create(self, serializer):
        course = serializer.validated_data['course']
        # проверяем, что текущий юзер — владелец курса
        if course.teacher != self.request.user:
            raise PermissionDenied("Нельзя создавать темы не в своих курсах.")
        serializer.save()


class SubmissionViewSet(viewsets.ModelViewSet):
    """
    - Студенты могут создавать свои Submission (файл) — при создании автоматически ставится статус 'waiting_for_check'.
    - Студенты видят только свои Submission.
    - Преподаватели видят все Submission по курсам, которые они ведут, со статусом 'waiting_for_check'.
    - Преподаватели могут обновлять статус (например, на 'approved' или 'rejected').
    """
    serializer_class = SubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Submission.objects.all()

        # если передан ?task=ID — сразу отфильтруем по нему
        task_id = self.request.query_params.get('task')
        if task_id is not None:
            qs = qs.filter(task_id=task_id)

        # студент видит только свои сабмишны (вне зависимости от task-параметра)
        if user.role == 'student':
            return qs.filter(student=user)

        # преподаватель видит только сабмишны к своим курсам
        if user.role == 'teacher':
            return qs.filter(task__topic__course__teacher=user)

        # остальные не видят ничего
        return Submission.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != 'student':
            raise PermissionDenied("Только студенты могут отправлять Submission.")
        serializer.save(student=user, status='waiting_for_check')


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


class AppointmentViewSet(viewsets.ModelViewSet):
    """
    CRUD для записей студентов в очередь на защиту.
    """
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            # студент видит только свою очередь
            return user.appointments.select_related('schedule')
        if user.role == 'teacher':
            # преподаватель — всех, кто записался на его расписания
            return Appointment.objects.filter(schedule__teacher=user)
        # остальным (напр. админам) — всё
        return super().get_queryset()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != 'student':
            raise PermissionDenied("Только студент может записаться в очередь.")
        schedule_id = self.request.data.get('schedule')
        schedule = get_object_or_404(TeacherSchedule, id=schedule_id)
        # проверка на свободные места (валидируется ещё в clean(), но лучше заранее)
        slot_minutes = 15
        duration = (
            datetime.combine(date.today(), schedule.end_time)
            - datetime.combine(date.today(), schedule.start_time)
        ).total_seconds() / 60
        max_slots = int(duration // slot_minutes)
        if schedule.appointments.count() >= max_slots:
            raise ValidationError("В очереди нет свободных мест.")
        # сохраняем, привязывая текущего пользователя
        serializer.save(student=user)

    def perform_destroy(self, instance):
        # студент может выйти только из своей очереди
        if instance.student != self.request.user:
            raise PermissionDenied("Нельзя убрать чужую запись.")
        instance.delete()