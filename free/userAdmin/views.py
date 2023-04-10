from django.views.generic import  View, TemplateView

from django.shortcuts import redirect
from free.models import *
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django_tables2.views import SingleTableView
from django_tables2 import Table, TemplateColumn, Column

from social_django.models import UserSocialAuth
from django.contrib.auth.models import User
from django.db.models import OuterRef, Subquery, Count

from django.urls import reverse

from django.utils import timezone


from django.db.models import Count, F, Value
from datetime import date

from django.core import serializers
from rest_framework.views import APIView
from rest_framework.response import Response

class ExecutionsDeleteOlder(PermissionRequiredMixin,APIView):
    permission_required = 'user.is_supersuser'
    def delete(self, *args, **kwargs):
            days_old = kwargs['days']
            if(days_old< 30):
                return Response({'error': 'You can only delete Executions older than 30 days.'}, status = 400)
            Execution.objects.filter(created_at__lte= (date.today()- timedelta(days=days_old))).delete()
            return Response(status = 200)




class ExperimentCleanUpView(LoginRequiredMixin, PermissionRequiredMixin,TemplateView ):

    template_name='experiments_cleanup.html'
    permission_required = 'user.is_supersuser'
    def get_context_data(self, **kwargs):          
        context = super().get_context_data(**kwargs)       
        experiment_dates = Execution.objects.annotate(time_dif=F('created_at')-date.today()).values('time_dif').annotate(total=Count('time_dif'))
        exec_creation_dates = []
        exec_creation_count = []
        
        for r in experiment_dates :
            if r['time_dif'].days<=0:
                exec_creation_dates.append(-r['time_dif'].days)
                exec_creation_count.append(r['total'])
        print(exec_creation_dates)
        print(exec_creation_count)

        context['executions_creation_dates'] =  exec_creation_dates
        context['executions_creation_count'] =  exec_creation_count

        return context



class UsersTable(Table):
    action = TemplateColumn(template_name='delete_user.html')

    class Meta:
        model = UserSocialAuth
        fields = ['user.id', 'user', 'provider', 'uid', 'user.first_name', 'user.last_name', 'user.last_login', 'total']


class UsersCleanUpListView(PermissionRequiredMixin,SingleTableView):
    permission_required = 'user.is_supersuser'
    template_name = 'users_cleanup_lists.html'
    table_class = UsersTable

    def get_queryset(self):
        experimet_count = Execution.objects.filter(user=OuterRef("user")).values('user').annotate(total=Count('user'))
        return UserSocialAuth.objects.select_related('user').annotate(total=Subquery(experimet_count.values('total')))


class UserDelete(PermissionRequiredMixin, View):
    permission_required = 'user.is_supersuser'
    def get(self, request, *args, **kwargs):
        user_id = kwargs['id']
        Execution.objects.filter(user_id =user_id).delete()
        UserSocialAuth.objects.filter(user_id =user_id).delete()
        User.objects.filter(id=user_id).delete()
        return redirect(reverse('users-cleanup-admin'))