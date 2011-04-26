# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _


class SearchSupervisionForm(forms.Form):

    def __init__(self, request, groups, checks, *args, **kwargs):
        super(SearchSupervisionForm, self).__init__(*args, **kwargs)
        self.request = request
        self.fields['address']   = forms.CharField ( required=False )
        self.fields['status']    = forms.ChoiceField( required=False, label = _("Status"), choices = [('ALL', 'All'), ('ERROR', 'Error'), ('FINISHED', 'Finished'), ('WARNING', 'Warning')])
        self.fields['group']     = forms.ChoiceField( required=False, label = _("Group"), choices = reduce(lambda all, id: all + ((id, groups[id]["name"]),), groups, (('ALL', 'All'),)))
        self.fields['check']     = forms.ChoiceField( required=False, label = _("Check"), choices = reduce(lambda all, id: all + ((id, "%s-%s" % (checks[id]["plugin"], checks[id]["plugin_check"])),), checks, (('ALL', 'All'),)))
        self.fields['display']   = forms.ChoiceField( required=False, label = _("Display"), choices = [('STATUS', 'Status'), ('HISTORY', 'History')])
        self.fields['refresh']   = forms.ChoiceField( required=False, label = _("Refresh"), choices = [('NONE', 'No refresh'), ('2', '2'), ('10', '10'), ('20', '20'), ('30', '30')])
