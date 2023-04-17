from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.translation import gettext_lazy as _

from .models import *

class AnswerInline(admin.TabularInline):
    model = Answer


class QuizAdminForm(forms.ModelForm):
    """
    below is from
    http://stackoverflow.com/questions/11657682/
    django-admin-interface-using-horizontal-filter-with-
    inline-manytomany-field
    """

    class Meta:
        model = Quiz
        exclude = []

    questions = forms.ModelMultipleChoiceField(
        queryset=Question.objects.all().select_subclasses(),
        required=False,
        label=_("Questions"),
        widget=FilteredSelectMultiple(
            verbose_name=_("Questions"),
            is_stacked=False))

    def __init__(self, *args, **kwargs):
        super(QuizAdminForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['questions'].initial =\
                self.instance.question_set.all().select_subclasses()

    def save(self, commit=True):
        quiz = super(QuizAdminForm, self).save(commit=False)
        quiz.save()
        quiz.question_set.set(self.cleaned_data['questions'])
        self.save_m2m()
        return quiz


class QuizAdmin(admin.ModelAdmin):
    form = QuizAdminForm

    list_display = ('title', 'category', )
    list_filter = ('category',)
    search_fields = ('description', 'category', )


class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('category', 'apparatus_type')


# class SubCategoryAdmin(admin.ModelAdmin):
#     # search_fields = ('sub_category', )
#     # list_display = ('sub_category', 'category',)
#     # # list_filter = ('category',)


class MCQuestionAdmin(admin.ModelAdmin):
    list_display = ('content', 'category', )
    list_filter = ('category',)
    fields = ('content', 'category', 'sub_category',
              'figure', 'quiz', 'explanation', 'priority', 'answer_order')

    search_fields = ('content', 'explanation')
    filter_horizontal = ('quiz',)

    inlines = [AnswerInline]


class ProgressAdmin(admin.ModelAdmin):
    """
    to do:
            create a user section
    """
    search_fields = ('user', 'score', )


class TFQuestionAdmin(admin.ModelAdmin):
    list_display = ('content', 'category', )
    list_filter = ('category',)
    fields = ('content', 'category', 'sub_category',
              'figure', 'quiz', 'explanation','priority', 'correct',)

    search_fields = ('content', 'explanation')
    filter_horizontal = ('quiz',)


class EssayQuestionAdmin(admin.ModelAdmin):
    list_display = ('content', 'category', )
    list_filter = ('category',)
    fields = ('content', 'category', 'sub_category', 'quiz', 'explanation', 'verif_function','priority','rounding')
    search_fields = ('content', 'explanation')
    filter_horizontal = ('quiz',)

class SittingAdmin(admin.ModelAdmin):
    list_display =('user','complete')

class montexxxAdminSite(admin.AdminSite):
    site_header = "montexxx Quiz admin"
    site_title = "montexxx Quiz Portal"

montexxx_admin_site = montexxxAdminSite(name='montexxxquiz_admin')

montexxx_admin_site.register(Quiz, QuizAdmin)
montexxx_admin_site.register(Category, CategoryAdmin)
# montexxx_admin_site.register(SubCategory, SubCategoryAdmin)
montexxx_admin_site.register(MCQuestion, MCQuestionAdmin)
montexxx_admin_site.register(Progress, ProgressAdmin)
montexxx_admin_site.register(TF_Question, TFQuestionAdmin)
montexxx_admin_site.register(Essay_Question, EssayQuestionAdmin)
montexxx_admin_site.register(Sitting, SittingAdmin)
