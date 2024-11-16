import uuid
from django.db import models
from homeApp.models import Test, Question


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
    question_id = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="question")
    correct_answer = models.JSONField(default=list)
    respondent_answer = models.JSONField(default=list)
    is_correct = models.BooleanField(default=False)
    points = models.IntegerField(default=0)
    time_taken = models.IntegerField(default=0)  # Time taken in seconds
    
    class Meta: 
        verbose_name_plural = "Respondent answers"
        verbose_name = "Respondent answer"

    def __str__(self):
        # String representation of the model in admin
        return f"{self.respondent_data.respondent_id}"
