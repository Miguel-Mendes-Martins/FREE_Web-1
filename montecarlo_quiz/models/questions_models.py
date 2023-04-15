from __future__ import unicode_literals

from django.db import models
from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.core.validators import (
    MaxValueValidator, validate_comma_separated_integer_list,
)

from django.utils.translation import ugettext_lazy as _
from six import python_2_unicode_compatible
from django.conf import settings

from model_utils.managers import InheritanceManager

from .quiz_models import Question
from free.models import Result
from free.views.api import ResultSerializer

ANSWER_ORDER_OPTIONS = (
    ('content', _('Content')),
    ('random', _('Random')),
    ('none', _('None'))
)


@python_2_unicode_compatible
class Essay_Question(Question):

    verif_function = models.CharField(max_length=100,
                               blank=True,
                               help_text=_("Enter the name of the function"
                                           "that will correct the question"),
                               verbose_name=_('Function name'))

    outer_locals = locals()

    def check_if_correct(self, guess, execution,decimal):

        if guess is None:
            return False

        try:
            if_correct = self.outer_locals[self.verif_function](self,guess,
                                                            execution,decimal)
        except KeyError:
            if_correct = False
            print("Wrong verif_function name in question model")

        return if_correct

    def get_answers(self):
        return False

    def get_answers_list(self):
        return False

    def answer_choice_to_string(self, guess):
        return str(guess)

    def __str__(self):
        return self.content

    def area_approximation(self, guess, execution,decimal):
        if execution == None:
            return False
        else:
            queryset = ResultSerializer(
                Result.objects.get(result_type='f', execution=execution)).data

            points_in = len(
                [values for values in queryset["value"] if values['circ']=='1'])
            sq_area = (2*execution.config['R'])**2
            area_approx = round(sq_area * points_in/len(queryset["value"]),decimal)
            print("Right answer:",area_approx)
            self.explanation = f"The approximate area of the circle was: {area_approx}"
            self.save()
            
            return not bool(guess - area_approx)
        # if (guess - area_approx) == 0:
        #     return True
        # else:
        #     return False

    def number_points(self,guess,execution,decimal):
        if guess < 100:
            return False
        else:  
            return True

    class Meta:
        verbose_name = _("Open ended question")
        verbose_name_plural = _("Open ended questions")

class TF_Question(Question):
    correct = models.BooleanField(blank=False,
                                  default=False,
                                  help_text=_("Tick this if the question "
                                              "is true. Leave it blank for"
                                              " false."),
                                  verbose_name=_("Correct"))

    def check_if_correct(self, guess):
        if guess == "True":
            guess_bool = True
        elif guess == "False":
            guess_bool = False
        else:
            return False

        if guess_bool == self.correct:
            return True
        else:
            return False

    def get_answers(self):
        return [{'correct': self.check_if_correct("True"),
                 'content': 'True'},
                {'correct': self.check_if_correct("False"),
                 'content': 'False'}]

    def get_answers_list(self):
        return [(True, True), (False, False)]

    def answer_choice_to_string(self, guess):
        return str(guess)

    class Meta:
        verbose_name = _("True/False Question")
        verbose_name_plural = _("True/False Questions")
        ordering = ['category']

class MCQuestion(Question):

    answer_order = models.CharField(
        max_length=30, null=True, blank=True,
        choices=ANSWER_ORDER_OPTIONS,
        help_text=_("The order in which multichoice "
                    "answer options are displayed "
                    "to the user"),
        verbose_name=_("Answer Order"))

    def check_if_correct(self, guess):
        answer = Answer.objects.get(id=guess)

        if answer.correct is True:
            return True
        else:
            return False

    def order_answers(self, queryset):
        if self.answer_order == 'content':
            return queryset.order_by('content')
        if self.answer_order == 'random':
            return queryset.order_by('?')
        if self.answer_order == 'none':
            return queryset.order_by()
        return queryset

    def get_answers(self):
        return self.order_answers(Answer.objects.filter(question=self))

    def get_answers_list(self):
        return [(answer.id, answer.content) for answer in
                self.order_answers(Answer.objects.filter(question=self))]

    def answer_choice_to_string(self, guess):
        return Answer.objects.get(id=guess).content

    class Meta:
        verbose_name = _("Multiple Choice Question")
        verbose_name_plural = _("Multiple Choice Questions")


@python_2_unicode_compatible
class Answer(models.Model):
    question = models.ForeignKey(MCQuestion, 
                                 verbose_name=_("Question"), 
                                 related_name='%(app_label)s_%(class)s_question',
                                 on_delete=models.CASCADE)

    content = models.CharField(max_length=1000,
                               blank=False,
                               help_text=_("Enter the answer text that "
                                           "you want displayed"),
                               verbose_name=_("Content"))

    correct = models.BooleanField(blank=False,
                                  default=False,
                                  help_text=_("Is this a correct answer?"),
                                  verbose_name=_("Correct"))

    def __str__(self):
        return self.content

    class Meta:
        verbose_name = _("Answer")
        verbose_name_plural = _("Answers")
