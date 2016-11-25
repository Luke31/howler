from django.shortcuts import render
from django.http import HttpResponse
from wally.elastic.search import Search


def index(request):
    res_strings = ["<style>em{ background:yellow}</style>",
    "You're at the search index. Search by using the q-parameter: <a href='http://10.0.10.180/howler/search/?q=hello'>http://10.0.10.180/howler/search/?q=hello</a><br><br>"]

    q = request.GET['q']

    if len(q) > 0:
        query = q
    else:
        query = "何か調整が必要でしょうか?"

    res_strings.append("Search in e-mails for text: {0}<br><br>".format(query))
    response = Search().search(query)

    for hit in response:
        if hasattr(hit, 'buildNum'):
            continue
        res_strings.append('<br><br><hr>Search Score: {0}, Sent: {1}, Language: {2}({3}% of total content) <br> {4}<hr>'
                           .format(hit.meta.score, hit.date, hit.langCode, hit.langPercent, hit.subject))
        if hasattr(hit.meta.highlight, 'body'):
            for fragment in hit.meta.highlight.body:
                res_strings.append('{0}<br>'.format(fragment))
        if hasattr(hit.meta.highlight, 'subject'):
            for fragment in hit.meta.highlight.subject:
                res_strings.append('{0}<br>'.format(fragment))

    return HttpResponse(''.join(res_strings))