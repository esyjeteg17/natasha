# yourapp/filters.py
import django_filters
from django.contrib.auth import get_user_model
from .models import Course

User = get_user_model()

class CourseFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    min_hours = django_filters.NumberFilter(field_name='hours', lookup_expr='gte')
    max_hours = django_filters.NumberFilter(field_name='hours', lookup_expr='lte')
    teacher = django_filters.ModelChoiceFilter(
        queryset=User.objects.filter(role='teacher')
    )

    class Meta:
        model = Course
        # сюда попадут все фильтры по полям модели + наши доп. min_hours/max_hours
        fields = ['title', 'description', 'hours', 'teacher']
