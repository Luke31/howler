from django.views import generic
from .models import Synonym
from wally.elastic.index import Index
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.conf import settings as djsettings
from elasticsearch import Elasticsearch


class SynonymIndex(generic.ListView):
    template_name = 'settings/synonym_index.html'
    context_object_name = 'synonym_list'

    def get_queryset(self):
        """Return all synonyms."""
        return Synonym.objects.order_by('synonym_term_a')


class SynonymCreate(generic.CreateView):
    model = Synonym
    success_url = reverse_lazy('settings:synonym')
    fields = ['synonym_term_a', 'synonym_term_b']


class SynonymUpdate(generic.UpdateView):
    model = Synonym
    success_url = reverse_lazy('settings:synonym')
    fields = ['synonym_term_a', 'synonym_term_b']


def synonym_delete(request, pk):
    if request.method == 'GET':
        synonym = Synonym.objects.get(pk=int(pk))
        synonym.delete()
        return HttpResponseRedirect(reverse('settings:synonym'))  # Redirect to synonyms


class SynonymDelete(generic.DeleteView):
    model = Synonym
    success_url = reverse_lazy('settings:synonym')


# def synonym_detail(request, synonym_id=0):
#     """Load (GET) or save (POST) synonym"""
#
#     # Save synonym
#     if request.method == 'POST':
#         # create a form instance and populate it with data from the request:
#         form = SynonymForm(request.POST)
#         # check whether it's valid:
#         if form.is_valid():
#             new_synonym = form.save()
#             # process the data in form.cleaned_data as required
#             # ...
#             # redirect to a new URL:
#             return HttpResponseRedirect('/thanks/')
#
#     # if a GET (or any other method) we'll create a blank form
#     elif synonym_id != 0:
#         synonym = Synonym.objects.get(pk=synonym_id)
#         f = Synonym(request.POST, instance=synonym)
#         form = SynonymForm()
#     else:
#         form = SynonymForm()
#
#     # Invalid?
#     return render(request, 'settings/synonym_detail.html', {'form': form})


# def synonynm_save(request, synonym_id):
#     question = get_object_or_404(Synonym, pk=synonym_id)
#     try:
#         selected_choice = question.choice_set.get(pk=request.POST['choice'])
#     except (KeyError, Choice.DoesNotExist):
#         # Redisplay the question voting form.
#         return render(request, 'polls/detail.html', {
#             'question': question,
#             'error_message': "You didn't select a choice.",
#         })
#     else:
#         selected_choice.votes += 1
#         selected_choice.save()
#         # Always return an HttpResponseRedirect after successfully dealing
#         # with POST data. This prevents data from being posted twice if a
#         # user hits the Back button.
#         return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))


def synonym_import(request):
    obj_list = Synonym.objects.order_by('synonym_term_a')
    kuromoji_synonyms = [x.synonyms_combo() for x in obj_list]
    es = Elasticsearch(djsettings.ES_HOSTS, timeout=djsettings.ES_TIMEOUT, maxsize=djsettings.ES_MAXSIZE_CON)
    index = Index(es, es_index_prefix=djsettings.ES_INDEX_PREFIX, es_type_name=djsettings.ES_TYPE_NAME,
                  user_dictionary_file=djsettings.JA_USER_DICT)
    index.add_mapping_to_index_multi(delete_old_indices=False, kuromoji_synonyms=kuromoji_synonyms)  # Update index
    # return HttpResponse()
    return HttpResponseRedirect(reverse('settings:synonym'))  # Redirect to synonyms
