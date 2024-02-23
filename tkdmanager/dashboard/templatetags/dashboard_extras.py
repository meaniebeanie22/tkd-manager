from django import template
from django.contrib.auth.models import Group 

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name): 
    group = Group.objects.get(name=group_name) 
    return True if group in user.groups.all() else False

@register.simple_tag(name='callmethod')
def callmethod(obj, method_name, *args):
    method = getattr(obj, method_name)
    return method(*args)

@register.simple_tag(takes_context=True, name='callmethodcontext')
def callmethodcontext(context, obj, method_name, *args):
    method = getattr(obj, method_name)
    return method(context, *args)
