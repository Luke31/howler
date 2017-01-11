from django.views import generic
from .models import Synonym
from wally.elastic.index import IndexMail
from wally.elastic.userdict import Userdict
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.conf import settings as djsettings
from elasticsearch import Elasticsearch
import os


class SynonymIndex(generic.ListView):
    template_name = 'settings/synonym_index.html'
    context_object_name = 'synonym_list'

    def get_queryset(self):
        """Return all synonyms."""
        return Synonym.objects.order_by('synonym_term_a')


class SynonymCreate(generic.CreateView):
    model = Synonym
    success_url = reverse_lazy('settings:synonym')
    fields = ['synonym_term_a', 'synonym_term_b', 'synonym_term_b_katakana']


class SynonymUpdate(generic.UpdateView):
    model = Synonym
    success_url = reverse_lazy('settings:synonym')
    fields = ['synonym_term_a', 'synonym_term_b', 'synonym_term_b_katakana']


def synonym_delete(request, pk):
    if request.method == 'GET':
        synonym = Synonym.objects.get(pk=int(pk))
        synonym.delete()
        return HttpResponseRedirect(reverse('settings:synonym'))  # Redirect to synonyms


def synonym_import(request):
    obj_list = Synonym.objects.order_by('synonym_term_a')

    # Add terms to userdict
    if os.path.exists(djsettings.ES_CONFIG_ROOT):
        for x in obj_list:
            ud = Userdict(es_conf_root=djsettings.ES_CONFIG_ROOT)
            ud.update_term_to_userdict(x.synonym_term_b, x.synonym_term_b_katakana)

    # Update index
    kuromoji_synonyms = [x.synonyms_combo() for x in obj_list]
    es = Elasticsearch(djsettings.ES_HOSTS, timeout=djsettings.ES_TIMEOUT, maxsize=djsettings.ES_MAXSIZE_CON)
    index = IndexMail(es, es_index_prefix=djsettings.ES_SUPPORTED_INDEX_PREFIX['email'], es_type_name=djsettings.ES_SUPPORTED_TYPE_NAMES['email'],
                  user_dictionary_file=djsettings.JA_USER_DICT)
    index.add_mapping_to_index_multi(delete_old_indices=False, kuromoji_synonyms=kuromoji_synonyms)  # Update index

    # return HttpResponse()
    return HttpResponseRedirect(reverse('settings:synonym'))  # Redirect to synonyms
