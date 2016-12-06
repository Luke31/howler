from django.contrib import admin

from django.db import models


class Synonym(models.Model):
    synonym_term_a = models.CharField(max_length=200)
    synonym_term_b = models.CharField(max_length=200)

    def synonyms_combo(self):
        return ', '.join((self.synonym_term_a, self.synonym_term_b))

    def __str__(self):
        return self.synonyms_combo()

admin.site.register(Synonym)
