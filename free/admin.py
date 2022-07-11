from django.contrib import admin
from django.forms import ModelForm
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from modeltranslation.admin import TabbedTranslationAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django_summernote.admin import SummernoteModelAdmin

from free.models import *

admin.site.site_title = _('FREE Administration')
admin.site.site_header = _('FREE Administration')
admin.site.index_title = _('FREE Administration')

class ApparatusTypeAdmin(SummernoteModelAdmin):
    prepopulated_fields = {"slug": ("name_en",)}
    exclude = ['description', 'scientific_area', 'lab_type', 'name']
    
    def __init__(self, *args, **kwargs):
        self.summernote_fields = [f'description_{lang[0]}' for lang in settings.LANGUAGES]
        super().__init__(*args, **kwargs)
        
admin.site.register(ApparatusType, ApparatusTypeAdmin)

class ApparatusAdminForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'instance' in kwargs and kwargs['instance']:
            self.fields['protocols'].queryset = Protocol.objects.filter(apparatus_type=kwargs['instance'].apparatus_type)
        else:
            self.fields['protocols'].widget = self.fields['protocols'].hidden_widget()

class ApparatusAdmin(SummernoteModelAdmin):
    form = ApparatusAdminForm
    list_filter = ['apparatus_type']
    readonly_fields = ('last_online', )
    exclude = ['description', 'location']
    
    def __init__(self, *args, **kwargs):
        
        self.summernote_fields = [f'description_{lang[0]}' for lang in settings.LANGUAGES]
        super().__init__(*args, **kwargs)

admin.site.register(Apparatus, ApparatusAdmin)

class ProtocolAdmin(SummernoteModelAdmin):
    list_display = ['__str__', 'apparatus_type']
    
    exclude = ['description', 'name']
    
    def __init__(self, *args, **kwargs):
        self.summernote_fields = [f'description_{lang[0]}' for lang in settings.LANGUAGES]
        super().__init__(*args, **kwargs)
        
admin.site.register(Protocol, ProtocolAdmin)

class ExecutionAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'apparatus', 'start', 'end']
    list_filter = ['apparatus', 'apparatus__apparatus_type']
admin.site.register(Execution, ExecutionAdmin)

class ResultAdmin(admin.ModelAdmin):
    list_display = ['value','result_type', 'time']
    list_filter = ['execution__apparatus', 'time']
admin.site.register(Result, ResultAdmin)

class UserProfileInline(admin.StackedInline):
    model=UserProfile
    can_delete=False

class UserAdmin(BaseUserAdmin):
    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.inlines = (UserProfileInline,)
        else:
            self.inlines = ()
        return super().get_form(request, obj, **kwargs)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)


