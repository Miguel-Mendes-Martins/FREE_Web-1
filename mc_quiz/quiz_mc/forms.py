from django import forms
from django.forms.widgets import RadioSelect, Textarea


class QuestionForm(forms.Form):
    def __init__(self, question, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        if question is not False:
            choice_list = [x for x in question.get_answers_list()]
            self.fields["answers"] = forms.ChoiceField(choices=choice_list,
                                                        widget=RadioSelect)


class EssayForm(forms.Form):
    def __init__(self, question, *args, **kwargs):
        super(EssayForm, self).__init__(*args, **kwargs)
        if question.sub_category != None:
            self.fields["answers"] = forms.FloatField(required=False)
        else:
            self.fields["answers"] = forms.FloatField()
        #self.fields["answers"] = forms.CharField(widget=Textarea(attrs={'style': 'width:100%'}))
