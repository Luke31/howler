from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from wally.elastic.search import Search
from datetime import datetime


def search(request):
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
            return render(request, 'wally/search.html', {'error_message': "Incorrent field format from-date"})

        try:
            request_to = request.GET.get('to', '')
            if request_to != '':
                kwargs['date_lte'] = datetime.strptime(request_to, web_datetime_format)
        except ValueError:
            return render(request, 'wally/search.html', {'error_message': "Incorrent field format to-date"})

        try:
            include_spam = request.GET['include_spam']
        except KeyError:
            include_spam = False

        response = Search().search(query, **kwargs)
    except KeyError:
        # Redisplay the wally form.
        return render(request, 'wally/search.html', {'error_message': "Incorrent query"})
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