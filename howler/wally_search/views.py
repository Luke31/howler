from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from wally.elastic.search import Search
from datetime import datetime
from django.utils.translation import ugettext as _
from elasticsearch import Elasticsearch
from django.conf import settings as djsettings
from datetime import datetime


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
            return render(request, 'wally/results.html', {'error_message': _("Incorrent field format from-date")})

        try:
            request_to = request.GET.get('to', '')
            if request_to != '':
                kwargs['date_lte'] = datetime.strptime(request_to, web_datetime_format)
        except ValueError:
            # Translators: The user didn't submit the correct values in the form
            return render(request, 'wally/results.html', {'error_message': _("Incorrent field format to-date")})

        kwargs['date_sliding_value'] = request.GET.get('date_sliding_value', '')
        kwargs['date_sliding_type'] = request.GET.get('date_sliding_type', '')

        try:
            kwargs['use_sliding_value'] = bool(int(request.GET.get('use_sliding_value', True)))
        except ValueError:
            return render(request, 'wally/results.html', {'error_message': _("Incorrent use of date selection")})

        try:
            kwargs['number_results'] = int(request.GET.get('number_results', 10))
        except ValueError:
            return render(request, 'wally/results.html', {'error_message': _("Incorrent number of results")})

        try:
            kwargs['include_spam'] = bool(request.GET.get('include_spam'))
        except ValueError:
            return render(request, 'wally/results.html', {'error_message': _("Incorrent value for include spam")})

        try:
            kwargs['only_attachment'] = bool(request.GET.get('only_attachment'))
        except ValueError:
            return render(request, 'wally/results.html', {'error_message': _("Incorrent value for only attachment")})

        es = Elasticsearch(djsettings.ES_HOSTS, timeout=djsettings.ES_TIMEOUT, maxsize=djsettings.ES_MAXSIZE_CON)
        response = Search(es, es_index_prefix=djsettings.ES_INDEX_PREFIX, es_type_name=djsettings.ES_TYPE_NAME).search(
            query, **kwargs)

        # Convert sent date to nice string
        for hit in response:
            hit.date = datetime.strptime(hit.date, djsettings.ES_DATETIME_FORMAT)

    except KeyError as exc:
        # Redisplay the search form.
        # Translators: The user didn't submit a correct query, a value is missing
        return render(request, 'wally/results.html',
                      {'error_message': _("Incorrent query: {exception}").format(exception=exc)})
    else:
        context = {
            'query': query,
            'hit_list': response,
            'EMAIL_SHOW_MAX_CHARS':djsettings.EMAIL_SHOW_MAX_CHARS
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
