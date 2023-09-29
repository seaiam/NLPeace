# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

from django.db import models

# Models created, 

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

class User(models.Model):
    username = models.CharField(max_length = 20)
    password = models.CharField(max_length = 20)
    fname = models.CharField(max_length = 20)
    lname = models.CharField(max_length = 20)
    DOB = models.DateTimeField()

class post(models.Model):
    postID = models.IntegerField(default = 0)
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length = 20)
    content = models.CharField(max_length = 300)
    date = models.DateTimeField()

class comment(models.Model):
    commentID = models.IntegerField(default = 0)
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField()
    date = models.DateTimeField()

class reaction(models.Model):
    reactionID = models.IntegerField(default = 0)
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    reactionType = models.CharField()
    date = models.DateTimeField()

