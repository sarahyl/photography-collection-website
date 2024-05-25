from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from .forms import ReportForm
from django.views.generic.edit import CreateView
from .forms import QuestionForm, ChoiceFormSet
from .models import Question, Choice, Report
from django.contrib.auth import logout
import datetime

#login view
def login(request):
    if request.user.is_authenticated:
        return redirect('website:index') #redirects to home page
    return render(request, "website/login.html",{})

#logout. returns users to login page
def logout_view(request):
    logout(request)
    return redirect(reverse('website:login'))
        
#home page. displays links to recent polls
def index(request):
    latest_question_list = Question.objects.filter(pub_date__lte = timezone.now()).order_by('-pub_date')[:5]
    context = {
        'latest_question_list': latest_question_list
    }
    return render(request, 'website/index.html', context)

#page to create a new poll
class PollCreateView(CreateView):
    form_class = QuestionForm
    template_name = "website/createpoll.html"

    #for the choice options for the created poll
    def get_context_data(self, **kwargs):
        context = super(PollCreateView, self).get_context_data(**kwargs)
        context['choice_formset'] = ChoiceFormSet() #template attached to this view now has a choice_formset availabed in the context
        return context
    
    #function to create a new poll 
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
        #check that choices are not empty
        for meta in choice_formset:
            choice_text = meta['choice_text'].value()
            if choice_text == "":
                return redirect(reverse("website:add"))
                #TODO: display an error message

        #creating and saving the poll    
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
    
#page to show poll question and choices, can vote in poll
class DetailView(generic.DetailView):
    model = Question
    template_name = 'website/details.html'

    def get_queryset(self):
        return Question.objects.filter(pub_date__lte=timezone.now())

#page to show results of a poll
class ResultsView(generic.DetailView):
    model = Question
    template_name = 'website/results.html'

#function to update results of a poll
def vote(request, question_id):
    #poll to update
    question = get_object_or_404(Question, pk=question_id)
    try:
        #get which choice to increment vote count for
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        #Redisplay the question voting form.
        return render(request, 'website/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        #increment vote count
        selected_choice.vote += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('website:results', args=(question.id,)))
    
#page to display all submitted feedback reports
class ReportListView(generic.ListView):
    template_name = 'website/report_list.html'
    context_object_name = 'report_list'
    def get_queryset(self):
        return Report.objects.all()

#page to submit a new feedback report
def new_report_form(request):
    form = ReportForm()

    report = Report.objects.all()

    context = {
        'form': form,
        'report': report,
    }
    
    return render(request, 'website/new_report_form.html', context)

#page to view the details of a feedback report
def report_details(request, pk):

    report = Report.objects.get(id=pk)

    context = {
        'report': report
    }
    
    return render(request, 'website/report_details.html', context)

#function to submit a report
def submit_report(request):
    #get report data
    form = ReportForm(request.POST, request.FILES)
    #save report
    if form.is_valid():
        report = form.save(commit=False)
        #print("type", request.FILES['document'].content_type)
        report.document_type = request.FILES['document'].content_type #save file's type 
        report.save()
    return HttpResponseRedirect(reverse('website:index'))

#function to delete report
def delete_report(request, pk):
    report = Report.objects.all().get(id=pk) #get report to delete
    report.document.delete(save=False) #deletes the file from s3 bucket
    report.delete() #deletes the report instance in your database
    return HttpResponseRedirect(reverse('website:index'))

"""
def map(request):
    key = settings.API_KEY
    context = {
        'key': key,
    }
    return render(request, 'website/map.html', context)
"""

