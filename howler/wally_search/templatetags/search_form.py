from django import template


register = template.Library()


@register.filter
def addstr(arg1, arg2):
    """concatenate arg1 & arg2"""
    return str(arg1) + str(arg2)

# @register.inclusion_tag('common/search_form.html', takes_context=True)
# def search_form(context):
#     # choices = poll.choice_set.all()
#     form_type = context['form_type'];
#
#     return {
#         'show_hits': context['show_hits'],
#         'sort_field': context['sort_field'],
#         'sort_dir': context['sort_dir'],
#
#     }
