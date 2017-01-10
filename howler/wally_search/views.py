from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from wally.elastic.search import SearchMail
from datetime import datetime
from django.utils.translation import ugettext as _
from elasticsearch import Elasticsearch
from django.conf import settings as djsettings
from datetime import datetime


def _get_search_context(request):
    context = {
        'sort_field': request.session.get('sort_field', '_score'),
        'sort_dir': request.session.get('sort_dir', '-'),
        'show_hits': request.session.get('show_hits', False),
    }
    return context


def searchmail(request):
    user_language = 'ja'
    # translation.activate(user_language)
    # request.session[translation.LANGUAGE_SESSION_KEY] = user_language
    context = _get_search_context(request)
    return render(request, 'wally/searchmail.html', context)


def searchirc(request):
    context = _get_search_context(request)
    return render(request, 'wally/searchirc.html', context)


web_datetime_format = '%Y/%m/%d %H:%M'


def find(request):
    try:
        query = request.GET['query']
        search_type = request.GET['search_type']

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
            sort_field = request.GET.get('sort_field')
            kwargs['sort_field'] = sort_field
        except ValueError:
            return render(request, 'wally/results.html', {'error_message': _("Incorrent value for sort field")})

        try:
            sort_dir = request.GET.get('sort_dir')
            kwargs['sort_dir'] = sort_dir
        except ValueError:
            return render(request, 'wally/results.html', {'error_message': _("Incorrent value for sort direction")})

        try:
            show_hits = bool(request.GET.get('show_hits', False))
        except ValueError:
            return render(request, 'wally/results.html', {'error_message': _("Incorrent value for show hits body")})

        # E-mail only values
        try:
            kwargs['include_spam'] = bool(request.GET.get('include_spam'))
        except ValueError:
            return render(request, 'wally/results.html', {'error_message': _("Incorrent value for include spam")})

        try:
            kwargs['only_attachment'] = bool(request.GET.get('only_attachment'))
        except ValueError:
            return render(request, 'wally/results.html', {'error_message': _("Incorrent value for only attachment")})

        # IRC only values
        # - none yet -

        # Save search-fields in session
        request.session['sort_field'] = sort_field
        request.session['sort_dir'] = sort_dir
        request.session['show_hits'] = show_hits

        es_index_prefix = djsettings.ES_SUPPORTED_INDEX_PREFIX[search_type]
        es_type_name = djsettings.ES_SUPPORTED_TYPE_NAMES[search_type]
        es = Elasticsearch(djsettings.ES_HOSTS, timeout=djsettings.ES_TIMEOUT, maxsize=djsettings.ES_MAXSIZE_CON)
        response = SearchMail(es, es_index_prefix=es_index_prefix, es_type_name=es_type_name).search(
            query, **kwargs)

        # Convert sent date to nice string
        for hit in response:
            hit.date = datetime.strptime(hit.date, djsettings.ES_DATETIME_FORMAT)

    except KeyError as exc:
        # Translators: The user didn't submit a correct query, a value is missing
        return render(request, 'wally/results.html',
                      {'error_message': _("Incorrent query: {exception}").format(exception=exc)})
    else:
        context = {
            'query': query,
            'hit_list': response,
            'EMAIL_SHOW_MAX_CHARS': djsettings.EMAIL_SHOW_MAX_CHARS
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
