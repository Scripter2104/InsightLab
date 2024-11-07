import uuid
from django.db import models
from homeApp.models import Test


# Create your models here.

class RespondentData(models.Model):
    test_id = models.ForeignKey(Test, on_delete=models.CASCADE)
    respondent_id = models.UUIDField(default=uuid.uuid1, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    id_number = models.CharField(max_length=50, blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return str(self.respondent_id)


class RespondentAnswers(models.Model):
    respondent_data = models.ForeignKey(RespondentData, on_delete=models.CASCADE, related_name="respondent")
    question = models.TextField()
    correct_answer = models.JSONField(default=list)
    respondent_answer = models.JSONField(default=list)
    is_correct = models.BooleanField(default=False)
    points = models.IntegerField(default=0)
