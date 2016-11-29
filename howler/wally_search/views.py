from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from wally.elastic.search import Search


def search(request):
    return render(request, 'wally/search.html')


def find(request):
    try:
        query = request.GET['query']
        try:
            from_datetime = request.GET['from']
            to_datetime = request.GET['to']
            include_spam = request.GET['include_spam']
        except KeyError:
            include_spam = False
        response = Search().search(query)
    except KeyError:
        # Redisplay the wally form.
        return render(request, 'wally/search.html', {'error_message': "Incorrent query.",})
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