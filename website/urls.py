from django.urls import path

from . import views

app_name = 'website'
urlpatterns = [
    path('', views.login, name='login'),
    path('index', views.index, name='index'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    path('comments/', views.comments_view, name='comments'),
    path('comments/list/', views.CommentsListView.as_view(), name='commentslist'),
    path('comments/submitcomment/', views.submit_comment, name='submit_comment'),
    path('<int:question_id>/vote/', views.vote, name='vote'),
    path('map/', views.map, name='map'),
]