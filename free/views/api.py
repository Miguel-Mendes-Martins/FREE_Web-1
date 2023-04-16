from rest_framework import generics, serializers, views
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from free.models import *
import json
import decimal
from jsonschema import validate, ValidationError as JSONValidationError
from freeweb import settings
from django.shortcuts import get_object_or_404
from django.apps import apps

from free.views.permissions import ApparatusOnlyAccess

# apparatus_type
class ApparatusTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApparatusType
        fields = ['name', 'description', 'scientific_area', 'lab_type']

class ApparatusTypeListAPI(generics.ListAPIView):
    """
    Returns a list of all ApparatusTypes.

    Returns a list of all ApparatusTypes.
    """
    queryset = ApparatusType.objects.all()
    serializer_class = ApparatusTypeSerializer

class ProtocolSerializer(serializers.ModelSerializer):
    read_only = True
    class Meta:
        model = Protocol
        fields = ['id', 'name', 'config']

class ApparatusSerializer(serializers.ModelSerializer):
    read_only = True
    protocols = ProtocolSerializer(many=True)
    apparatus_type = ApparatusTypeSerializer()
    
    class Meta:
        model = Apparatus
        fields = ['apparatus_type', 'protocols', 'location', 
                  'owner', 'video_config', 'config']

class ExecutionSerializer(serializers.ModelSerializer):
    protocol = ProtocolSerializer()

    class Meta:
        model = Execution
        fields = ['id','name', 'apparatus', 'protocol', 
                  'config', 'status', 'queue_time', 'start', 'end']
        read_only_fields = ('id', 'apparatus', 'protocol', 'status', 
                            'queue_time', 'start', 'end')

class ExecutionCreateSerializer(serializers.ModelSerializer):
    def validate(self, data):
        data = super().validate(data)
        adjusted_schema = json.loads(
            json.dumps(data['protocol'].config), 
            parse_float=decimal.Decimal)
        instance = data['config'] if 'config' in data else {}
        adjusted_instance = json.loads(
            json.dumps(instance), 
            parse_float=decimal.Decimal)
        
        try:
            validate(instance = adjusted_instance, schema = adjusted_schema)
        except JSONValidationError as e:
            raise serializers.ValidationError(e.message)
            
        return data  

    class Meta:
        model = Execution
        fields = ['id', 'name','apparatus', 'protocol', 'config']

class ExecutionUpdateSerializer(serializers.ModelSerializer):

    def validate(self, data):
        data = super().validate(data)
            
        if not self.instance.status in ['C','N']:
            raise serializers.ValidationError(
                "Can only update configuration of not enqueued executions.")
        
        try:
            validate(instance = data['config'] if 'config' in data else {}, 
                     schema = self.instance.protocol.config)
        except JSONValidationError as e:
            raise serializers.ValidationError(e.message)
            
        return data  

    class Meta:
        model = Execution
        fields = ['config']
        


class ExecutionConfigure(generics.CreateAPIView):
    """
    Configures an execution of experiment. 
    
    You must supply valid apparatus and protocol ids. 
    The config is validated against JSON schema of the protocol.
    """
    serializer_class = ExecutionCreateSerializer
    queryset = Execution.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, status = 'C')
        if(self.request.META.get('HTTP_REFERER') != None):
            if (self.request.META.get('HTTP_REFERER').split("/")[-4] 
                != "execution" ):
                exec_id = serializer['id'].value
                quiz_name = self.request.META.get('HTTP_REFERER').split("/")[4]
                #gets app name
                app = self.request.META.get('HTTP_REFERER').split("/")[3]
                #Imports sitting and quiz models from right app
                Sitting = apps.get_model(app,'Sitting')
                Quiz = apps.get_model(app,'Quiz')
                sitting = Sitting.objects.get(
                    quiz=Quiz.objects.get(url=quiz_name),
                    user=self.request.user, 
                    complete = False)
                sitting.execution = Execution.objects.get(pk=exec_id)
                sitting.save()

class ExecutionRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieves, updates or deletes a given execution. 
    
    The config is validated against JSON schema of the protocol.
    Update and delete are only possible for executions, 
    that have not been enqueued (are in configured state - C).
    It is only possble to update config of the execution.
    """
    queryset = Execution.objects.all()
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ExecutionSerializer
        return ExecutionUpdateSerializer

    def perform_update(self, serializer):
        serializer.save(status = 'C')
        
class ExecutionUpdateNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Execution
        fields = ['name']        
        
class ExecutionUpdateName(generics.UpdateAPIView):
    """
    Changes the name of the execution.

    It's possible to change the name of the execution in any state.
    """
    queryset = Execution.objects.all()
    lookup_field = 'id'
    serializer_class = ExecutionUpdateNameSerializer

class ExecutionStart(views.APIView):
    """
    Starts a configured execution. 
    
    Status is changed to Q - "Queued".
    """
    def put(self, *args, **kwargs):
        try:
            execution = Execution.objects.get(pk=kwargs['id'])
        except Execution.DoesNotExist:
            return Response({'error': 'Execution with given ID '
                             'does not exist!'}, status = 404)

        if execution.status != 'C':
            return Response({'error': 'You can only start executions with '
                             'Configured (C) state.'}, status = 400)

        execution.status = 'Q'
        execution.save()

        return Response(status = 200)
    
class Heartbeat(views.APIView):
    """
    Notifies the system that the Apparatus is alive


    """
    permission_classes = [ApparatusOnlyAccess]
    def put(self, *args, **kwargs):
        try:
            apparatus = Apparatus.objects.get(pk=kwargs['id'])
        except Apparatus.DoesNotExist:
            return Response({'error': 'Apparatus with this id does not exist!'}
            ,status=404)
        return Response(status=200)
    
class Version(views.APIView):
    """
    Returns the current version of the FREE server

    """
    def get(self, *args, **kwargs):
        return Response({'version': settings.FREE_VERSION})

class ApparatusView(generics.RetrieveAPIView):
    """
    Retrieves an information about a given apparatus.

    Retrieves an information about a given apparatus.
    """
    serializer_class = ApparatusSerializer
    queryset = Apparatus.objects.all()
    lookup_field = 'id'
    
class ApparatusListAPI(generics.ListAPIView):
    """
    Returns a list of all apparatuses.

    Returns a list of all apparatuses.
    """
    queryset = Apparatus.objects.all()
    serializer_class = ApparatusSerializer

class NextExecution(generics.RetrieveAPIView):
    """
    Returns the earliest started execution.

    This is supposed to be the next execution that the apparatus 
    should perform.

    **APPARATUS AUTHENTICATION REQUIRED**
    """
    permission_classes = [ApparatusOnlyAccess]
    serializer_class = ExecutionSerializer
    def get_object(self):
        apparatus = get_object_or_404(Apparatus, pk=self.kwargs['id'])
        self.check_object_permissions(self.request, apparatus)        
        obj = Execution.objects.filter(
            status='Q', 
            apparatus=apparatus).order_by('start').first()
        if obj:
            self.check_object_permissions(self.request, obj)
            obj.save()
        return obj   

class ResultSerializer(serializers.ModelSerializer):
    def validate(self, data):
        if data['execution'].status != 'R':
            raise ValidationError('Can only add results '
            'to a running execution!')
        if data['result_type'] == 'f':
            if Result.objects.filter(
                execution=data['execution'], 
                result_type='f').count()!=0:
                raise ValidationError('Cannot add more than one final result!')
            data['execution'].status = 'F'
            data['execution'].save()
        return data

    class Meta:
        model = Result
        fields = ['id', 'execution', 'value', 'result_type', 'time']

class AddResult(generics.CreateAPIView):
    """
    Adds a measurement result to a given execution.

    Adding a measurement with result_type "f" will 
    automatically stop the execution.

    **APPARATUS AUTHENTICATION REQUIRED**
    """
    permission_classes = [ApparatusOnlyAccess]
    serializer_class = ResultSerializer
    queryset = Result.objects.all()

    def create(self, request, *args, **kwargs):
        execution = Execution.objects.get(pk=request.data['execution'])
        self.check_object_permissions(request, execution)  
        return super().create(request, *args, **kwargs)


class ResultList(generics.ListAPIView):
    """
    Returns the final result for a given execution_id.

    Unpaginated, may be long.
    """
    serializer_class = ResultSerializer
    
    def get_queryset(self):
        return Result.objects.filter(
            execution_id=self.kwargs['id'], 
            result_type='f')

class ResultListFiltered(generics.ListAPIView):
    """
    Returns a list of all results for a given execution, 
    with id greater or equal to last_id.

    This allows you to limit the size of the 
    result list to only view most recent results.
    """
    serializer_class = ResultSerializer
    
    def get_queryset(self):
        return Result.objects.filter(
            execution_id=self.kwargs['id'], 
            pk__gte=self.kwargs['last_id']).order_by('time')

class ResultListFilteredLimited(generics.ListAPIView):
    """
    Returns a list of all results for a given execution, 
    with id greater or equal to last_id but at most limit items.

    This allows you to limit the size of the result list 
    to only view most recent results while limitng the size of the output.
    """
    
    serializer_class = ResultSerializer
    
    def get_queryset(self):
        return Result.objects.filter(
            execution_id=self.kwargs['id'], 
            pk__gte=self.kwargs['last_id']).\
            order_by('time')[:self.kwargs['limit']]

class ExecutionStatusSerializer(serializers.ModelSerializer):
    def validate(self, data):
        valid_transitions = {
            'Q': ['R'],
            'R': ['F', 'E']
        }

        if self.instance: # if updating
            if self.instance.status in valid_transitions:
                if (data['status'] not in 
                valid_transitions[self.instance.status]):
                    raise ValidationError('Execution in state ' 
                    + self.instance.status + 
                    ' can only change state to ' + 
                    ','.join(valid_transitions[self.instance.status]))
            else:
                raise ValidationError('Cannot change an execution ' 
                                      'with status ' + self.instance.status)

        return data
                
    class Meta:
        model = Execution
        fields = ['status']

class ChangeExecutionStatus(generics.RetrieveUpdateAPIView):
    """
    Changes or retrieves the status of a given execution.

    It is only possible to change state of running execution (R) 
    to either finished (F) or error (E).

    **APPARATUS AUTHENTICATION REQUIRED**
    """
    permission_classes = [ApparatusOnlyAccess]
    serializer_class = ExecutionStatusSerializer
    queryset = Execution.objects.all()
    lookup_field='id'

class ExecutionQueue(generics.ListAPIView):
    """
    Retrieves a current execution queue for the apparatus.

    **APPARATUS AUTHENTICATION REQUIRED**
    """
    permission_classes = [ApparatusOnlyAccess]
    serializer_class = ExecutionSerializer
    def get_queryset(self):
        return Execution.objects.filter(
            state='Q', 
            apparatus_id=self.kwargs['apparatus_id']).order_by('queue_time')