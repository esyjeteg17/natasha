from django.contrib import admin

from core.models import CustomUser, Course, Task, TeacherSchedule, Submission, DefenseQueue

admin.site.register(CustomUser)
admin.site.register(Course)
admin.site.register(Task)
admin.site.register(TeacherSchedule)
admin.site.register(Submission)
admin.site.register(DefenseQueue)

# Register your models here.
