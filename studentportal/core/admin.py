from django.contrib import admin

from core.models import CustomUser, Course, Task, TeacherSchedule, Submission, DefenseQueue, Topic, Appointment

admin.site.register(CustomUser)
admin.site.register(Course)
admin.site.register(Task)
admin.site.register(TeacherSchedule)
admin.site.register(Submission)
admin.site.register(DefenseQueue)
admin.site.register(Topic)
admin.site.register(Appointment)
