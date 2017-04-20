from django import template

register = template.Library()


@register.filter(name='field')
def get_verbose_field_name(instance, field_name):
    return instance._meta.get_field(field_name)


@register.filter(name='verbose_name')
def get_verbose_name(object):
    return object.verbose_name
