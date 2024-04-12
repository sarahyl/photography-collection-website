from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.conf import settings
from .forms import ReportForm
from django.views.generic.edit import CreateView
from .forms import QuestionForm, ChoiceFormSet
from .models import Question, Choice, Report
from django.contrib.auth import logout
import datetime

def login(request):
    if request.user.is_authenticated:
        return redirect('website:index')
    return render(request, "website/login.html",{})

def logout_view(request):
    logout(request)
    return redirect(reverse('website:login'))
        
def index(request):
    latest_question_list = Question.objects.filter(pub_date__lte = timezone.now()).order_by('-pub_date')[:5]
    context = {
        'latest_question_list': latest_question_list
    }
    return render(request, 'website/index.html', context)

class PollCreateView(CreateView):
    form_class = QuestionForm
    template_name = "website/createpoll.html"

    def get_context_data(self, **kwargs):
        context = super(PollCreateView, self).get_context_data(**kwargs)
        context['choice_formset'] = ChoiceFormSet() #template attached to this view now has a choice_formset availabed in the context
        return context
    
    def post(self, request, *args, **kwargs):
        
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        choice_formset = ChoiceFormSet(self.request.POST)
        if form.is_valid() and choice_formset.is_valid():
            return self.form_valid(form, choice_formset)
        else:
            return self.form_invalid(form, choice_formset)
    
    def form_valid(self, form, choice_formset):
        #checking if choices are empty or not
        for meta in choice_formset:
            choice_text = meta['choice_text'].value()
            if choice_text == "":
                return redirect(reverse("website:add"))
            #probably add an error message here too 
            
        self.object = form.save(commit=False)
        self.object.pub_date = datetime.datetime.now()
        self.object.save() #save question
        choices = choice_formset.save(commit=False)
        for meta in choices:
            meta.question = self.object
            meta.save() #save choices
        return redirect(reverse("website:index"))
    
    def form_invalid(self, form, choice_formset):

        return redirect(reverse("website:createpoll"))
    
class DetailView(generic.DetailView):
    model = Question
    template_name = 'website/details.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

class ResultsView(generic.DetailView):
    model = Question
    template_name = 'website/results.html'

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        #Redisplay the question voting form.
        return render(request, 'website/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.vote += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('website:results', args=(question.id,)))
    
class ReportListView(generic.ListView):
    template_name = 'website/report_list.html'
    context_object_name = 'report_list'
    def get_queryset(self):
        return Report.objects.all()

def new_report_form(request):
    form = ReportForm()

    report = Report.objects.all()

    context = {
        'form': form,
        'report': report,
    }
    
    return render(request, 'website/new_report_form.html', context)

def report_details(request, pk):

    report = Report.objects.get(id=pk)

    context = {
        'report': report
    }
    
    return render(request, 'website/report_details.html', context)

def submit_report(request):
    form = ReportForm(request.POST, request.FILES)
    if form.is_valid():
        report = form.save(commit=False)
        print("type", request.FILES['document'].content_type)
        report.document_type = request.FILES['document'].content_type #save file's type 
        report.save()
    return HttpResponseRedirect(reverse('website:index'))

def delete_report(request, pk):
    report = Report.objects.all().get(id=pk)
    report.document.delete(save=False) #deletes the file in s3
    report.delete() #deletes the Report instance your database
    return HttpResponseRedirect(reverse('website:index'))

"""
def map(request):
    key = settings.API_KEY
    context = {
        'key': key,
    }
    return render(request, 'website/map.html', context)
"""

