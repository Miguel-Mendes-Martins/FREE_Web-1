from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from django.views.generic import TemplateView, TemplateView
from free.views.api import ExecutionSerializer, ResultSerializer
from free.models import *
from django_tables2 import Table, TemplateColumn, Column
from django_tables2.views import SingleTableView

from django.contrib.auth.mixins import LoginRequiredMixin
class IndexView(TemplateView):
    template_name='free/index.html'

# EXPERIMENT CONTROL & EXECUTIONS

class ExecutionView(LoginRequiredMixin, TemplateView):
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.execution = Execution.objects.get(pk=kwargs['pk'])
        context['execution_json'] = ExecutionSerializer(self.execution).data
        context['apparatus'] = self.execution.apparatus
        context['protocol'] = self.execution.protocol
        try:
            context['final_result'] = ResultSerializer(Result.objects.get(result_type='f', execution=self.execution)).data
        except:
            context['final_result'] = {}
        return context

    def get_template_names(self):
        return ['free/experiments/' + self.execution.apparatus.apparatus_type.slug + '.html']

class CreateExecutionView(LoginRequiredMixin, TemplateView):    
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.apparatus = Apparatus.objects.get(pk=kwargs['apparatus_id'])
        
        context['execution_json'] = {}
        context['apparatus'] = self.apparatus
        context['protocol'] = Protocol.objects.get(pk=kwargs['protocol_id'])
        context['final_result'] = {}
        return context

    def get_template_names(self):
        return ['free/experiments/' + self.apparatus.apparatus_type.slug + '.html']


class ExecutionsTable(Table):
    action = TemplateColumn(template_name='free/execution_link.html')

    class Meta:
        model = Execution
        fields = ['apparatus', 'name', 'protocol', 'status', 'start', 'end']

class ExecutionsListView(LoginRequiredMixin,SingleTableView):
    template_name = 'free/executions.html'
    table_class = ExecutionsTable

    def get_queryset(self):
        return Execution.objects.filter(user=self.request.user, status__in =  self.status_filter)

class ExecutionsConfiguredListView(ExecutionsListView):
    status_filter = ['C','N', 'Q', 'R']

class ExecutionsFinishedListView(ExecutionsListView):
    status_filter = ['E',  'F', 'A', 'T']
        
# PROTOCOLS LIST

class ApparatusTable(Table):

    protocols = TemplateColumn(template_name='free/protocols.html')
    current_status = TemplateColumn(verbose_name=_('Current status'), template_name='free/current_status.html')

    class Meta:
        model = Apparatus
        fields = ['apparatus_type', 'location', 'apparatus_type__scientific_area', 'apparatus_type__lab_type', 'current_status', 'protocols']    
        
class ApparatusesView(LoginRequiredMixin,SingleTableView):
    template_name = 'free/apparatuses.html'
    table_class = ApparatusTable
    queryset = Apparatus.objects.all()