from datetime import datetime
from django.utils import timezone


def time_difference_in_seconds(time1, time2):
    # Convert time objects to timedelta
    delta = datetime.combine(timezone.now().date(), time2) - datetime.combine(
        timezone.now().date(), time1
    )
    # Calculate the time difference in seconds
    difference_seconds = delta.total_seconds()
    return difference_seconds
