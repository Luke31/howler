from django.contrib import admin
from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _


class Synonym(models.Model):
    synonym_term_a = models.CharField(max_length=200, verbose_name=_('Synonym Term A'))
    synonym_term_b = models.CharField(max_length=200, verbose_name=_('Synonym Term B (shortcut)'))
    synonym_term_b_katakana = models.CharField(max_length=200, verbose_name=_('Synonym Term B Katakana'), default='')

    def synonyms_combo(self):
        return ', '.join((self.synonym_term_a, self.synonym_term_b))

    def __str__(self):
        return self.synonyms_combo()

    def get_absolute_url(self):
        return reverse('settings:synonym_edit', kwargs={'pk': self.pk})


admin.site.register(Synonym)
