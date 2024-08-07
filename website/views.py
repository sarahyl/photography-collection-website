from django.http import HttpResponseRedirect
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from django.views.generic.edit import CreateView
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.conf import settings

from .forms import QuestionForm, ChoiceFormSet, PhotographForm, ContestForm
from .models import RegularUser, AdminUser, Question, Choice, Photograph, Contest, ContestSubmission

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

import datetime
import boto3


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
        if request.user.groups.filter(name='AdminUser').exists():
            try: #check if a regular user instance has been created for this user
                user = AdminUser.objects.get(user=request.user)
            except AdminUser.DoesNotExist: #if not then create an instance
                user = AdminUser.objects.create(user=request.user, name=request.user.get_full_name(), username=request.user.get_username(), email=request.user.email)
        else:
            try: #check if a regular user instance has been created for this user
                user = RegularUser.objects.get(user=request.user)
            except RegularUser.DoesNotExist: #if not then create an instance
                user = RegularUser.objects.create(user=request.user, name=request.user.get_full_name(), username=request.user.get_username(), email=request.user.email)
    else:
        base_template = "website/base_guest.html"
    #latest_question_list = Question.objects.filter(pub_date__lte = timezone.now()).order_by('-pub_date')[:5]
    
    photographs = Photograph.objects.order_by('-date_uploaded') #most recent photographs first

    #each column of photographs displayed on home page
    photographs_col1 = []
    photographs_col2 = []
    photographs_col3 = []

    #sort photographs into one of three columns
    for i in range(len(photographs)):
        if i % 3 == 0:
            photographs_col1.append(photographs[i])
        elif (i % 3) - 1 == 0:
            photographs_col2.append(photographs[i])
        else: 
            photographs_col3.append(photographs[i])

    context = {
        #'latest_question_list': latest_question_list,
        'base_template': base_template,
        'photographs_col1':photographs_col1,
        'photographs_col2': photographs_col2,
        'photographs_col3': photographs_col3
    }
    return render(request, 'website/index.html', context)

def profile(request, username):
    user = User.objects.get(username=username)
    photographs = Photograph.objects.filter(user=user) #get photos uploaded by the current user

    #get either the RegularUser or AdminUser instance
    try:
        user = RegularUser.objects.get(user=request.user)
    except RegularUser.DoesNotExist:
        user = AdminUser.objects.get(user=request.user)

    #each column of photographs displayed on home page
    photographs_col1 = []
    photographs_col2 = []
    photographs_col3 = []

    #sort photographs into one of three columns
    for i in range(len(photographs)):
        if i % 3 == 0:
            photographs_col1.append(photographs[i])
        elif (i % 3) - 1 == 0:
            photographs_col2.append(photographs[i])
        else: 
            photographs_col3.append(photographs[i])


    context = {
        'user': user,
        'photographs': photographs,
        'photographs_col1':photographs_col1,
        'photographs_col2': photographs_col2,
        'photographs_col3': photographs_col3
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
@login_required
def upload(request):
    form = PhotographForm()

    context = {
        'form': form
    }
    
    return render(request, 'website/upload.html', context)

#function to upload a photograph
@login_required
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
        photograph.user = request.user
        photograph.save()
        form.save_m2m()
        messages.success(request, "The photograph has been uploaded.")
    return HttpResponseRedirect(reverse('website:index'))

#page to view the details of a photograph
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
        'user': user,
    }
    
    return render(request, 'website/photograph_details.html', context)

#function to delete photograph
@login_required
def delete_photograph(request, pk):
    photograph = Photograph.objects.all().get(id=pk) #get report to delete
    s3_client = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    s3_client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=photograph.image.name) #deletes the file from s3 bucket
    photograph.delete() #deletes the report instance in your database
    messages.success(request, "The photograph has been deleted.")
    return HttpResponseRedirect(reverse('website:index'))

#page listing photography contests
@login_required
def contests(request):
    #ongoing contests
    contests = Contest.objects.filter(deadline__gt=timezone.now())

    #check if user is admin or regular user
    user = request.user
    if request.user.groups.filter(name='AdminUser').exists():
        admin_user = True 
    else:
        admin_user = False
    
    photographs = Photograph.objects.filter(user=user) #get photos uploaded by the current user

    #each column of photographs
    photographs_col1 = []
    photographs_col2 = []

    #sort photographs into one of three columns
    for i in range(len(photographs)):
        if i % 2 == 0:
            photographs_col1.append(photographs[i])
        else: 
            photographs_col2.append(photographs[i])

    context = {
        'contests': contests,
        'admin_user': admin_user,
        'photographs_col1': photographs_col1,
        'photographs_col2': photographs_col2
    }
    return render(request, 'website/contests.html', context)

#page to create contests - only accessible by admin users
@login_required
def create_contest(request):
    #checks if the user is an admin user
    if not request.user.groups.filter(name='AdminUser').exists():
        messages.error(request, "Not authorized to visit this page.")
        return redirect(reverse("website:index"))
    
    form = ContestForm()
    context = {
        'form': form
    }
    return render(request, "website/create_contest.html", context)

#function to create a contest
@login_required
def submit_contest_form(request):
    #get report data
    form = ContestForm(request.POST, request.FILES)
    #save report
    if form.is_valid():
        contest = form.save(commit=False)
        contest.user = request.user
        contest.save()
        messages.success(request, "The contest has been created.")
    return HttpResponseRedirect(reverse("website:contests"))

def tagged(request, tag):
    if request.user.is_authenticated:
        base_template = "website/base.html"
    else:
        base_template = "website/base_guest.html"

    photographs = Photograph.objects.filter(tags__name__in=[tag])
    #each column of photographs
    photographs_col1 = []
    photographs_col2 = []
    photographs_col3 = []

    #sort photographs into one of three columns
    for i in range(len(photographs)):
        if i % 3 == 0:
            photographs_col1.append(photographs[i])
        elif (i % 3) - 1 == 0:
            photographs_col2.append(photographs[i])
        else: 
            photographs_col3.append(photographs[i])
    
    context = {
        'photographs_col1':photographs_col1,
        'photographs_col2': photographs_col2,
        'photographs_col3': photographs_col3,
        'base_template': base_template,
        'tag': tag
    }

    return render(request, 'website/tagged.html', context)

    
#TODO: function that splits photographs in lists for displaying photographs in columns
#photographs is the photographs to be sorted into the lists
#col_num is number of columns in the photogrid
def photography_cols(photographs, col_num):
    pass
    #return photograph_cols