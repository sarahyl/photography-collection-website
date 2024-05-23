from django import forms
from .models import Report, Question, Choice
from django.forms import inlineformset_factory

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ('title', 'description', 'document', )

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text']


class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['choice_text']


ChoiceFormSet = inlineformset_factory(
    Question, Choice, form=ChoiceForm, extra=3, can_delete=False
)

