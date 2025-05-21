import datetime
from datetime import timedelta
from django.db.models import Q
from .models import (
    TeacherSchedule, DefenseQueue, Submission
)

def check_file_basic(file_path, min_words, required_keywords):
    text = ""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except:
        pass  

    words = text.split()
    word_count = len(words)

    missing_keywords = []
    for kw in required_keywords:
        if kw.lower() not in text.lower():
            missing_keywords.append(kw)

    if word_count < min_words or missing_keywords:
        return False
    return True


def find_nearest_defense_slot(teacher, expected_time_minutes):

    now_date = datetime.date.today()

    schedules = TeacherSchedule.objects.filter(
        teacher=teacher,
        date__gte=now_date
    ).order_by('date', 'start_time')

    for sched in schedules:
        start = datetime.datetime.combine(sched.date, sched.start_time)
        end = datetime.datetime.combine(sched.date, sched.end_time)
        delta = timedelta(minutes=expected_time_minutes)

        current = start
        while current + delta <= end:
            candidate_time = current.time()
            busy = DefenseQueue.objects.filter(
                teacher=teacher,
                defense_date=sched.date,
                defense_time=candidate_time
            ).exists()
            if not busy:
                return (sched.date, candidate_time)

            current += delta

    return None


def calculate_max_students_per_day(teacher, date):
    schedule_qs = TeacherSchedule.objects.filter(
        teacher=teacher, date=date
    )
    if not schedule_qs.exists():
        return 0

    total_minutes = 0
    for sch in schedule_qs:
        start_dt = datetime.datetime.combine(date, sch.start_time)
        end_dt = datetime.datetime.combine(date, sch.end_time)
        diff = end_dt - start_dt
        total_minutes += int(diff.total_seconds() // 60)
        
    average_defense_time = 10
    max_students = total_minutes // average_defense_time
    return max_students
