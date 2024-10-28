# models.py
from django.db import models
from django.contrib.auth.models import User
import uuid
from django.urls import reverse


class Test(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tests')
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    link = models.URLField(blank=True, null=True)
    time_limit = models.IntegerField(default=30)
    time_per_question = models.IntegerField(default=0)
    max_marks = models.IntegerField(default=0)
    pass_marks = models.IntegerField(default=0)
    summary_message = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.link:
            self.link = self.generate_test_link()
        super().save(*args, **kwargs)

    def generate_test_link(self):
        return reverse('InsightLab', kwargs={'test_id': str(self.unique_id)})




class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.TextField(default='single-choice')
    correct_points = models.IntegerField(default=0)
    incorrect_points = models.IntegerField(default=0)

    def __str__(self):
        return self.question_text


class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    option_text = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.option_text


class TestConfiguration(models.Model):  # New model for test configuration
    test = models.OneToOneField(Test, on_delete=models.CASCADE, related_name='configuration')
    require_name = models.BooleanField(default=True)
    additional_fields = models.JSONField(default=dict)


