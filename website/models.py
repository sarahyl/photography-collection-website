import datetime
from django.db import models
from django.utils import timezone
from django.contrib import admin
from django.contrib.auth.models import User

class RegularUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    username = models.CharField(max_length=400)
    name = models.CharField(max_length=400)
    email = models.CharField(max_length=100)
    def __str__(self):
        return self.name
    
class AdminUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    username = models.CharField(max_length=400)
    name = models.CharField(max_length=400)
    email = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.question_text

    @admin.display(
        boolean=True,
        ordering='pub_date',
        description='Published recently?',
    )    
    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    vote = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text
    
class Photograph(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=150)
    description = models.CharField(max_length=255)
    date_uploaded = models.DateTimeField(default=timezone.now)
    image_type = models.CharField(max_length=255, null=True)
    image = models.FileField()

class Contest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=255)
    description = models.TextField(default="")
    date_created = models.DateTimeField(default=timezone.now)

class ContestSubmission(models.Model):
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, null=True)
    photograph = models.ForeignKey(Photograph, on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=50)
