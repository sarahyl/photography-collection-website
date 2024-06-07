from django import forms
from .models import Photograph, Question, Choice
from django.forms import inlineformset_factory, TextInput

class PhotographForm(forms.ModelForm):
    class Meta:
        model = Photograph
        fields = ('title', 'description', 'image', )
        widgets = {
            'title': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 40%;',
                'placeholder': 'Title'
                }),
            'description': TextInput(attrs={
                'class': "form-control", 
                'style': 'max-width: 100%;',
                'placeholder': 'Description'
                })
        }

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

