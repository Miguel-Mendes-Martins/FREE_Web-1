from __future__ import unicode_literals
from six import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from mc_quiz.quiz_mc.models import *
from free.models import *
from free.views.api import ResultSerializer


@python_2_unicode_compatible
class Essay_Question(Question):

    def check_if_correct(self, guess,execution):
        if guess == None:
            return False
        queryset = ResultSerializer(Result.objects.get(result_type='f', execution=execution)).data
        #aux_list = [values for values in queryset["value"] if values['circ']=='1']
        points_in = len([values for values in queryset["value"] if values['circ']=='1'])
        print("points in:",points_in)
        print("points out:",len(queryset["value"]))
        area = 16.0 * points_in/len(queryset["value"]) 
        round_area = round(16.0 * points_in/len(queryset["value"]),5)
        print("Right answer:",round_area)
        self.explanation = f"The variance was: {round_area}"
        self.save()
        if( (guess - round_area) == 0):
            return True
        else:
            return False

    def get_answers(self):
        return False

    def get_answers_list(self):
        return False

    def answer_choice_to_string(self, guess):
        return str(guess)

    def __str__(self):
        return self.content

    class Meta:
        verbose_name = _("Essay style question")
        verbose_name_plural = _("Essay style questions")

