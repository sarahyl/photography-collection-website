from django.urls import path

from . import views

app_name = 'website'
urlpatterns = [
    path('', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('index', views.index, name='index'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    path('report/', views.new_report_form, name='new_report_form'),
    path('report/list/', views.ReportListView.as_view(), name='report_list'),
    path('report/submit/', views.submit_report, name='submit_report'),
    path('<int:question_id>/vote/', views.vote, name='vote'),
    path('createpoll/', views.PollCreateView.as_view(), name='createpoll'),
    #path('map/', views.map, name='map'),
    path('report/delete/<int:pk>', views.delete_report, name='delete_report'),
    path('report/<int:pk>/', views.report_details, name='report_details')

]