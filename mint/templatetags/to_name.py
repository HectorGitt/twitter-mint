from django import template

register = template.Library()

@register.filter(name='to_name')
def to_name(value, arg):
    try:
        #return the name variable for every {{name}}
        return value.replace('{{name}}', arg)
    except:
        return value