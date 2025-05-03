from django.db import models
from django.contrib.auth.models import AbstractUser

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
    
    
class CourseFile(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='course_files/')
    description = models.CharField(max_length=255, blank=True)
    

class Task(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='tasks'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    min_words = models.PositiveIntegerField(default=100)
    expected_defense_time = models.PositiveIntegerField(default=10)

    def __str__(self):
        return f"{self.title} | {self.course.title}"


class TeacherSchedule(models.Model):
    teacher = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'teacher'},
        related_name='schedule'
    )
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





