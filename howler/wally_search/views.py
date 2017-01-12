from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from wally.elastic.search import SearchMail, SearchIrc
from datetime import datetime
from django.utils.translation import ugettext as _
from elasticsearch import Elasticsearch
from django.conf import settings as djsettings
from datetime import datetime
import dateutil.parser
import pytz


def searchmail(request):
    """
    Get search-form for email search
    """
    user_language = 'ja'
    # translation.activate(user_language)
    # request.session[translation.LANGUAGE_SESSION_KEY] = user_language
    context = {
        'sort_field': request.session.get('mail_sort_field', '_score'),
        'sort_dir': request.session.get('mail_sort_dir', '-'),
        'show_hits': request.session.get('mail_show_hits', False),
    }
    return render(request, 'wally/searchmail.html', context)


def searchirc(request):
    """
    Get search-form for irc search
    """
    context = {
        'sort_field': request.session.get('irc_sort_field', '_score'),
        'sort_dir': request.session.get('irc_sort_dir', '-'),
    }
    return render(request, 'wally/searchirc.html', context)

web_datetime_format = '%Y/%m/%d %H:%M'


def find(request):
    """
    Find email or irc entries by provided search-arguments
    :param request: Request with all search-arguments (incl query)
    :return: Result-page (either IRC or email search result)
    """
    try:
        query = request.GET['query']
        search_type = request.GET['search_type']
        if search_type == 'email':
            result_template = 'wally/resultsmail.html'
        elif search_type == 'irc':
            result_template = 'wally/resultsirc.html'

        kwargs = {}
        try:
            request_from = request.GET.get('from', '')
            if request_from != '':
                naive_date_input = dateutil.parser.parse(request_from)
                kwargs['date_gte'] = pytz.timezone(djsettings.TIME_ZONE).localize(naive_date_input,
                                                                                  is_dst=None)  # datetime.strptime(request_from, web_datetime_format)
        except ValueError:
            # Translators: The user didn't submit the correct values in the form
            return render(request, result_template, {'error_message': _("Incorrent field format from-date")})

        try:
            request_to = request.GET.get('to', '')
            if request_to != '':
                naive_date_input = dateutil.parser.parse(request_to)
                kwargs['date_lte'] = pytz.timezone(djsettings.TIME_ZONE).localize(naive_date_input,
                                                                                  is_dst=None)  # datetime.strptime(request_to, web_datetime_format)
        except ValueError:
            # Translators: The user didn't submit the correct values in the form
            return render(request, result_template, {'error_message': _("Incorrent field format to-date")})

        kwargs['date_sliding_value'] = request.GET.get('date_sliding_value', '')
        kwargs['date_sliding_type'] = request.GET.get('date_sliding_type', '')

        try:
            kwargs['use_sliding_value'] = bool(int(request.GET.get('use_sliding_value', True)))
        except ValueError:
            return render(request, result_template, {'error_message': _("Incorrent use of date selection")})

        try:
            kwargs['number_results'] = int(request.GET.get('number_results', 10))
        except ValueError:
            return render(request, result_template, {'error_message': _("Incorrent number of results")})

        try:
            sort_field = request.GET.get('sort_field')
            kwargs['sort_field'] = sort_field
        except ValueError:
            return render(request, result_template, {'error_message': _("Incorrent value for sort field")})

        try:
            sort_dir = request.GET.get('sort_dir')
            kwargs['sort_dir'] = sort_dir
        except ValueError:
            return render(request, result_template, {'error_message': _("Incorrent value for sort direction")})

        try:
            show_hits = bool(request.GET.get('show_hits', False))
        except ValueError:
            return render(request, result_template, {'error_message': _("Incorrent value for show hits body")})

        # E-mail only values
        try:
            kwargs['include_spam'] = bool(request.GET.get('include_spam'))
        except ValueError:
            return render(request, result_template, {'error_message': _("Incorrent value for include spam")})

        try:
            kwargs['only_attachment'] = bool(request.GET.get('only_attachment'))
        except ValueError:
            return render(request, result_template, {'error_message': _("Incorrent value for only attachment")})

        # IRC only values
        # - none yet -

        # Search
        es_index_prefix = djsettings.ES_SUPPORTED_INDEX_PREFIX[search_type]
        es_type_name = djsettings.ES_SUPPORTED_TYPE_NAMES[search_type]
        es = Elasticsearch(djsettings.ES_HOSTS, timeout=djsettings.ES_TIMEOUT, maxsize=djsettings.ES_MAXSIZE_CON)
        if search_type == 'email':
            # Save search-fields in session
            request.session['mail_sort_field'] = sort_field
            request.session['mail_sort_dir'] = sort_dir
            request.session['mail_show_hits'] = show_hits

            response = SearchMail(es, es_index_prefix=es_index_prefix, es_type_name=es_type_name).search(
                query, **kwargs)
            # Convert sent date to nice string
            for hit in response:
                hit.date = dateutil.parser.parse(
                    hit.date)  # datetime.strptime(hit.date, djsettings.ES_DATETIME_FORMAT_MAIL)  #   #
        elif search_type == 'irc':
            # Save search-fields in session
            request.session['irc_sort_field'] = sort_field
            request.session['irc_sort_dir'] = sort_dir
            response = SearchIrc(es, es_index_prefix=es_index_prefix, es_type_name=es_type_name).search(
                query, **kwargs)
            # Convert sent date to nice string
            for hit in response:
                hit.sent = dateutil.parser.parse(
                    hit['@timestamp'])  # datetime.strptime(hit['@timestamp'], djsettings.ES_DATETIME_FORMAT_IRC)
                hit.timestamp_raw = hit['@timestamp']

    except KeyError as exc:
        # Translators: The user didn't submit a correct query, a value is missing
        return render(request, result_template,
                      {'error_message': _("Incorrent query: {exception}").format(exception=exc)})
    else:
        context = {
            'query': query,
            'hit_list': response,
        }
        return render(request, result_template, context)


def detail_irc(request):
    result_template = 'wally/resultsircdetail.html'
    try:
        origin_timestamp = request.GET.get('origin_timestamp')
    except ValueError:
        return render(request, result_template, {'error_message': _("Incorrent value for desired date timestamp")})
    try:
        channel = request.GET.get('channel')
    except ValueError:
        return render(request, result_template, {'error_message': _("Incorrent value for desired channel")})

    es_index_prefix = djsettings.ES_SUPPORTED_INDEX_PREFIX['irc']
    es_type_name = djsettings.ES_SUPPORTED_TYPE_NAMES['irc']
    es = Elasticsearch(djsettings.ES_HOSTS, timeout=djsettings.ES_TIMEOUT, maxsize=djsettings.ES_MAXSIZE_CON)
    response = SearchIrc(es, es_index_prefix=es_index_prefix, es_type_name=es_type_name).search_close(origin_timestamp,
                                                                                                      channel)
    # Convert sent date to nice string
    for hit in response:
        hit.sent = dateutil.parser.parse(
            hit['@timestamp'])  # datetime.strptime(hit['@timestamp'], djsettings.ES_DATETIME_FORMAT_IRC)
        hit.is_origin_entry = hit['@timestamp'] == origin_timestamp

    context = {
        'hit_list': response,
    }


    return render(request, result_template, context)
