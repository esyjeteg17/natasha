"""
URL configuration for studentportal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
    
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from core.views import (
    UserViewSet, CourseViewSet, TaskViewSet,
    TeacherScheduleViewSet, SubmissionViewSet, DefenseQueueViewSet, TopicViewSet, AppointmentViewSet
)
from neurocheck.views import DocumentReviewViewSet
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'tasks', TaskViewSet)
router.register(r'teacher-schedules', TeacherScheduleViewSet, basename='teacher-schedule')
router.register(r'submissions', SubmissionViewSet, basename='submission')
router.register(r'defense', DefenseQueueViewSet)
router.register(r'topics', TopicViewSet)
router.register(r'doc-review', DocumentReviewViewSet, basename='doc-review')
router.register(r'appointments', AppointmentViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    path('api/', include(router.urls)),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)