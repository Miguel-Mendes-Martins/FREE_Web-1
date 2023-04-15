from __future__ import unicode_literals
from six import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from quiz_pendulum.quiz_structure.models import *
from free.models import *
from free.views.api import ResultSerializer


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
        print(execution)
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
        verbose_name = _("Essay style question")
        verbose_name_plural = _("Essay style questions")
