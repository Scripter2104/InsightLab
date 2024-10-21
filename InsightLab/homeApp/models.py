from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Test(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tests')
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name


class Questions(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    questions_text = models.TextField()
    marks = models.IntegerField()

    def __str__(self):
        return self.questions_text


class Answer(models.Model):
    question = models.ForeignKey(Questions, on_delete=models.CASCADE, related_name='amswers')
    user_answer = models.TextField()
    correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Answer to {self.question.questions_text} is {self.user_answer}"
