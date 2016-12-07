from django import forms
from django.forms import ModelForm
from .models import Synonym
from django.utils.translation import ugettext as _


class SynonymForm(ModelForm):
    class Meta:
        model = Synonym
        fields = ['synonym_term_a', 'synonym_term_b']

        # class SynonymForm(forms.Form):
        #     synonym_term_a = forms.CharField(label=_('Term A'), max_length=200)
        #     synonym_term_b = forms.CharField(label=_('Term B'), max_length=200)
