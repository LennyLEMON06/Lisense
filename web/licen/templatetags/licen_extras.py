# licen/templatetags/licen_extras.py

from django import template
from datetime import date

register = template.Library()

# @register.simple_tag
@register.filter(name='timesince_days')
def timesince_days(end_date):
    today = date.today()
    return (end_date - today).days
