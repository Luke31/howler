# from django import template
#
# register = template.Library()
#
#
# @register.inclusion_tag('common/search_form.html', takes_context=True)
# def search_form(context):
#     # choices = poll.choice_set.all()
#     form_type = context['form_type'];
#
#     return {
#         'show_hits_body': context['show_hits_body'],
#         'sort_field': context['sort_field'],
#         'sort_dir': context['sort_dir'],
#
#     }
