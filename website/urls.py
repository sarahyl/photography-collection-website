from django.urls import path

from . import views

app_name = 'website'
urlpatterns = [
    path('logout/', views.logout_view, name='logout'),
    path('', views.index, name='index'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    path('<int:question_id>/vote/', views.vote, name='vote'),
    path('createpoll/', views.PollCreateView.as_view(), name='createpoll'),
    path('upload/', views.upload, name='upload'),
    path('upload/submit/', views.submit_upload_form, name='submit_upload_form'),
    path('delete/<int:pk>', views.delete_photograph, name='delete_photograph'),
    path('photograph/<int:pk>/', views.photograph_details, name='photograph_details')
]