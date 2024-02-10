from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.conf import settings

from .models import Question, Choice, Comment

class IndexView(generic.ListView):
    template_name = 'website/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.filter(
            pub_date__lte = timezone.now()
        ).order_by('-pub_date')[:5]

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

def comments_view(request):
    return render(request, 'website/comments.html')

class CommentsListView(generic.ListView):
    template_name = 'website/commentslist.html'
    context_object_name = 'comments_list'
    def get_queryset(self):
        return Comment.objects.all()

def submit_comment(request):
    title_text = request.POST['title_text']
    comment_text = request.POST['comment_text']
    if (title_text != "") and (comment_text != ""):
        comment = Comment(title_text = title_text, comment_text=comment_text)
        comment.save()
        return HttpResponseRedirect(reverse('website:comments'))

    else:
        return render(request, 'website/comments.html', {
            'error_message': "Title and comment are required.",
        })

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
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('website:results', args=(question.id,)))
    
def map(request):
    key = settings.API_KEY
    context = {
        'key': key,
    }
    return render(request, 'website/map.html', context)

