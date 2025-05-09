from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime, date
from django.core.exceptions import ValidationError

class StudentGroup(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='student'
    )

    phone = models.CharField(max_length=20, blank=True, null=True)
    group = models.ForeignKey(
        'core.StudentGroup', 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )

    course = models.ForeignKey(
        'core.Course',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )

    def __str__(self):
        return f"{self.username} ({self.role})"
    
    

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    hours = models.PositiveIntegerField(default=0)
    img = models.ImageField(upload_to='courses/', blank=True, null=True)
    teacher = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'teacher'},
        related_name='courses'
    )
    date = models.DateField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.title
    
    

    


class Topic(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='topics'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(
        blank=True,
        help_text="Общее описание темы (необязательно)"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Порядок темы внутри курса"
    )

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} → {self.title}"


class Task(models.Model):
    # Теперь связь идёт не напрямую с Course, а через Topic
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    min_words = models.PositiveIntegerField(default=100)
    expected_defense_time = models.PositiveIntegerField(default=10)
    file = models.FileField(upload_to='tasks/')
    class Meta:
        ordering = ['id']  # или по своему полю order, если добавите

    def __str__(self):
        return f"{self.title} | {self.topic.title}"

class TeacherSchedule(models.Model):
    teacher = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'teacher'},
        related_name='schedule'
    )
    title = models.CharField(max_length=255, blank=True)
    date = models.DateField() 
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"Schedule {self.teacher.username} on {self.date}"


class Submission(models.Model):
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name='submissions'
    )
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'},
        related_name='submissions'
    )
    file = models.FileField(upload_to='submissions/')
    created_at = models.DateTimeField(auto_now_add=True)

    ai_check_passed = models.BooleanField(default=False)
    status = models.CharField(max_length=20, default='pending')  

    def __str__(self):
        return f"Submission #{self.id} by {self.student.username}"


class DefenseQueue(models.Model):
    submission = models.OneToOneField(
        Submission, on_delete=models.CASCADE, related_name='defense_slot'
    )
    teacher = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'teacher'},
        related_name='defense_slots'
    )
    defense_date = models.DateField()
    defense_time = models.TimeField()

    is_occupied = models.BooleanField(default=True)

    def __str__(self):
        return f"Defense slot for submission {self.submission.id}"



class Appointment(models.Model):
    """
    Запись студента на конкретное расписание.
    Позиция рассчитывается по created_at.
    """
    schedule = models.ForeignKey(
        TeacherSchedule,
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'},
        related_name='appointments'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # нельзя дважды записаться на одно и то же окно
        unique_together = ('schedule', 'student')
        ordering = ['created_at']

    def clean(self):
        # проверяем, что не превысили число слотов
        slot_minutes = 15
        start_dt = datetime.combine(date.today(), self.schedule.start_time)
        end_dt = datetime.combine(date.today(), self.schedule.end_time)
        total_min = (end_dt - start_dt).total_seconds() / 60
        max_slots = int(total_min // slot_minutes)
        if self.schedule.appointments.count() >= max_slots:
            raise ValidationError("В этом окне нет свободных мест.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)