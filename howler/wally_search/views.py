from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from wally.elastic.search import Search
from datetime import datetime
from django.utils.translation import ugettext as _
from django.utils import translation


def search(request):
    user_language = 'ja'
    # translation.activate(user_language)
    # request.session[translation.LANGUAGE_SESSION_KEY] = user_language
    return render(request, 'wally/search.html')


web_datetime_format = '%Y/%m/%d %H:%M'


def find(request):
    try:
        query = request.GET['query']
        kwargs = {}
        try:
            request_from = request.GET.get('from', '')
            if request_from != '':
                kwargs['date_gte'] = datetime.strptime(request_from, web_datetime_format)
        except ValueError:
            # Translators: The user didn't submit the correct values in the form
            return render(request, 'wally/search.html', {'error_message': _("Incorrent field format from-date")})

        try:
            request_to = request.GET.get('to', '')
            if request_to != '':
                kwargs['date_lte'] = datetime.strptime(request_to, web_datetime_format)
        except ValueError:
            # Translators: The user didn't submit the correct values in the form
            return render(request, 'wally/search.html', {'error_message': _("Incorrent field format to-date")})

        kwargs['date_sliding_value'] = request.GET.get('date_sliding_value', '')
        kwargs['date_sliding_type'] = request.GET.get('date_sliding_type', '')
        kwargs['use_sliding_value'] = request.GET.get('use_sliding_value', 1)
        try:
            include_spam = request.GET['include_spam']
        except KeyError:
            include_spam = False

        response = Search().search(query, **kwargs)
    except KeyError as exc:
        # Redisplay the search form.
        # Translators: The user didn't submit a correct query, a value is missing
        return render(request, 'wally/search.html',
                      {'error_message': _("Incorrent query: {exception}").format(exception=exc)})
    else:
        context = {
            'query': query,
            'hit_list': response,
        }
        return render(request, 'wally/results.html', context)


def detail(request, email_id):
    # For further development purposes
    # try:
    #     email = Search().wally(query)
    # except Question.DoesNotExist:
    #     raise Http404("Question does not exist")
    # return render(request, 'polls/detail.html', {'question': question})

    # question = get_object_or_404(Question, pk=question_id)
    return HttpResponse("You're looking at email %s." % email_id)

