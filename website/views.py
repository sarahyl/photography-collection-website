from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from .forms import PhotographForm
from django.contrib import messages
from django.views.generic.edit import CreateView
from .forms import QuestionForm, ChoiceFormSet
from .models import RegularUser, AdminUser, Question, Choice, Photograph, Contest, ContestSubmission
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.conf import settings
import datetime


#logout. returns users to home page
def logout_view(request):
    logout(request)
    return redirect(reverse('website:index'))

#home page. displays recently uploaded photographs
def index(request):
    #base html template changes depending on if the user is logged in or a guest
    if request.user.is_authenticated:
        base_template = "website/base.html"
        #check if the user is a regular user
        if request.user.groups.filter(name='RegularUser').exists():
            try: #check if a regular user instance has been created for this user
                user = RegularUser.objects.get(user=request.user)
            except RegularUser.DoesNotExist: #if not then create an instance
                user = RegularUser.objects.create(user=request.user, name=request.user.get_full_name(), username=request.user.get_username(), email=request.user.email)
        if request.user.groups.filter(name='AdminUser').exists():
            try: #check if a regular user instance has been created for this user
                user = AdminUser.objects.get(user=request.user)
            except AdminUser.DoesNotExist: #if not then create an instance
                user = AdminUser.objects.create(user=request.user, name=request.user.get_full_name(), username=request.user.get_username(), email=request.user.email)
    else:
        base_template = "website/base_guest.html"
    #latest_question_list = Question.objects.filter(pub_date__lte = timezone.now()).order_by('-pub_date')[:5]
    
    photographs = Photograph.objects.order_by('-date_uploaded')

    context = {
        #'latest_question_list': latest_question_list,
        'base_template': base_template,
        'photographs':photographs
    }
    return render(request, 'website/index.html', context)

def profile(request, username):
    user = User.objects.get(username=username)
    photographs = Photograph.objects.filter(user=user)

    try:
        user = RegularUser.objects.get(user=request.user)
    except RegularUser.DoesNotExist:
        user = AdminUser.objects.get(user=request.user)

    context = {
        'user': user,
        'photographs': photographs
    }
    return render(request, 'website/profile.html', context)

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

#page to upload a new photograph
def upload(request):
    form = PhotographForm()

    context = {
        'form': form
    }
    
    return render(request, 'website/upload.html', context)

#function to submit a report
def submit_upload_form(request):
    #get report data
    form = PhotographForm(request.POST, request.FILES)
    #save report
    if form.is_valid():
        photograph = form.save(commit=False)
        if "image" not in request.FILES['image'].content_type:
            messages.error(request, "Attached file must be an image.")
            return HttpResponseRedirect(reverse('website:upload'))
        photograph.document_type = request.FILES['image'].content_type #save file's type 
        try:
            photograph.user = RegularUser.objects.get(user=request.user)
        except RegularUser.DoesNotExist:
            photograph.user = AdminUser.objects.get(user=request.user)
        photograph.save()
    return HttpResponseRedirect(reverse('website:index'))

#page to view the details of a feedback report
def photograph_details(request, pk):
    #base html template changes depending on if the user is logged in or a guest
    if request.user.is_authenticated:
        base_template = "website/base.html"
    else:
        base_template = "website/base_guest.html"
    
    user = request.user

    photograph = Photograph.objects.get(id=pk)

    context = {
        'base_template': base_template,
        'photograph': photograph,
        'user': user
    }
    
    return render(request, 'website/photograph_details.html', context)

#function to delete report
def delete_photograph(request, pk):
    photograph = Photograph.objects.all().get(id=pk) #get report to delete
    #photograph.image.delete(save=False) #deletes the file from s3 bucket
    photograph.delete() #deletes the report instance in your database
    messages.success(request, "The photograph has been deleted.")
    return HttpResponseRedirect(reverse('website:index'))

#page listing photography contests
def contests(request):
    contests = Contest.objects.all()
    context = {
        'contests': contests
    }
    return render(request, 'website/contests.html', context)