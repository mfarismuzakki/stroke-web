from django import template
from datetime import timedelta
register = template.Library()

@register.filter()
def time_normalization(date):
    try:
        hour = str(date.hour) if len(str(date.hour)) > 1 else '0' + str(date.hour)
        minute = str(date.minute) if len(str(date.minute)) > 1 else '0' + str(date.minute)
        day = str(date.day) if len(str(date.day)) > 1 else '0' + str(date.day)
        month = str(date.month) if len(str(date.month)) > 1 else '0' + str(date.month)
        year = str(date.year)

        return day + '/' + month + '/' + year + ' ' + hour + ':' + minute
    except:

        return date