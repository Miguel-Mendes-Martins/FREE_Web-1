from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from django.views.generic import TemplateView, TemplateView, DetailView
from free.views.api import ExecutionSerializer, ResultSerializer
from free.models import *
from django_tables2 import Table, TemplateColumn, Column
from django_tables2.views import SingleTableView
from django.views.generic.base import RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.http import Http404

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
        if (self.request.META.get('HTTP_REFERER') != None):
            context['source'] = self.request.META.get('HTTP_REFERER').split("/")[3]
            if self.request.META.get('HTTP_REFERER').split("/")[5] == "take":
                context['base'] = "free/base_stripped.html"
            else:
                context['base'] = "free/base.html"
        else: 
            context['base'] = "free/base.html"
        try:
            context['final_result'] = ResultSerializer(Result.objects.get(result_type='f', execution=self.execution)).data
        except:
            context['final_result'] = {}
        return context

    def get_template_names(self):
        return ['free/experiments/' + self.execution.apparatus.apparatus_type.slug + '.html']

class ApparatusVideoView(LoginRequiredMixin, DetailView):
    template_name = 'free/apparatus_video.html'
    def get_queryset(self):
        return Apparatus.objects.filter(id=self.kwargs['pk'])
        #.get(pk=self.kwargs['pk'])


class CreateExecutionView(LoginRequiredMixin, TemplateView):    
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        apparatus_id = kwargs['apparatus_id']
        protocol_id = kwargs['protocol_id']
        context['base'] = "free/base.html"

        self.apparatus = get_object_or_404(Apparatus, pk=apparatus_id)

        if not self.apparatus.protocols.filter(id=protocol_id).exists():
            raise Http404("Apparatus type does implement such protocol")

        context['execution_json'] = {}
        context['apparatus'] = self.apparatus
        context['protocol'] = Protocol.objects.get(pk=protocol_id)
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
    current_status = TemplateColumn(verbose_name=_('Current status'), template_name='free/current_status.html', order_by='last_online')

    class Meta:
        model = Apparatus
        fields = ['apparatus_type', 'location', 'apparatus_type__scientific_area', 'apparatus_type__lab_type', 'current_status', 'protocols']    
        
class ApparatusesView(LoginRequiredMixin,SingleTableView):
    template_name = 'free/apparatuses.html'
    table_class = ApparatusTable
    queryset = Apparatus.objects.all()

class ApparatusesRedirectNewExperiment(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        apparatus_id = kwargs['apparatus_id']
        protocol_id = kwargs['protocol_id']
        apparatus_type_slug = kwargs['apparatus_type_slug']

        obj = get_object_or_404(Apparatus, pk=apparatus_id)

        if obj.apparatus_type.slug != apparatus_type_slug:
            raise Http404("Apparatus type does not match")

        return reverse_lazy('free:execution-create', kwargs={'apparatus_id': apparatus_id, 'protocol_id': protocol_id})
