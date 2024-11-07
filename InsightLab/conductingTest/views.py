import uuid

from django.shortcuts import render, redirect, reverse
from homeApp.models import Test, TestConfiguration, Question
from .models import RespondentData
import math


# Create your views here.

def test_start_view(request, *ags, **kwargs):
    test = Test.objects.get(unique_id=kwargs['test_id'])
    testName = test.name
    testConfig = TestConfiguration.objects.get(test=test)
    fields = testConfig.additional_fields

    if request.method == 'POST':
        form_data = {
            'test_id': kwargs['test_id'],
            'first_name': request.POST.get('first-name'),
            'last_name': request.POST.get('last-name') if 'Last-Name' in fields else None,
            'age': request.POST.get('age') if 'Age' in fields else None,
            'city': request.POST.get('city') if 'City' in fields else None,
            'email': request.POST.get('email') if 'Email-Address' in fields else None,
            'id_number': request.POST.get('id') if 'ID' in fields else None,
            'gender': request.POST.get('gender') if 'Gender' in fields else None,
            'phone': request.POST.get('phone') if 'Phone' in fields else None,

        }

        respondent_data = RespondentData(**form_data)
        respondent_data.save()
        request.session['respondent_id'] = str(respondent_data.respondent_id)
        return redirect('question_page')

    return render(request, 'start_test.html', {"testConfig": testConfig, "fields": fields, "testName": testName})


def question_page_view(request, *args, **kwargs):
    # Get the respondent and associated test
    respondent = RespondentData.objects.get(respondent_id=request.session.get("respondent_id"))
    test_obj = Test.objects.get(unique_id=respondent.test_id)
    questions = list(Question.objects.filter(test=test_obj))
    question_count = len(questions)
    time_per_question = test_obj.time_per_question
    time_limit = test_obj.time_limit

    if 'current_question_index' not in request.session:
        request.session['current_question_index'] = 0

    current_index = request.session['current_question_index']

    if current_index >= question_count:
        request.session['current_question_index'] = 0
        return redirect('test_end_page')

    current_question_id = questions[current_index]
    current_question = Question.objects.get(unique_id=uuid.UUID(str(current_question_id)))

    if request.method == 'POST':
        request.session['current_question_index'] += 1
        return redirect('question_page')

    request.session["max_marks"] = test_obj.max_marks
    request.session["pass_marks"] = test_obj.pass_marks
    request.session["summary_message"] = test_obj.summary_message

    if time_per_question != 0:
        minutes = int(time_per_question / 60)
        seconds = int(((time_per_question / 60) % 1) * 60)
        return render(request, 'question_page.html', {
            'question': current_question.question_text,
            'question_number': current_index + 1,
            'total_questions': question_count,
            'test_name': test_obj.name,
            'time_per_question': [0, minutes, seconds],
        })
    else:
        print("in else")
        hour = int(time_limit / 60)
        minutes = int(((time_limit / 60) % 1) * 60)
        if minutes == 0:
            minutes = 60
            hour = hour - 1
        return render(request, 'question_page.html', {
            'question': current_question.question_text,
            'question_number': current_index + 1,
            'total_questions': question_count,
            'test_name': test_obj.name,
            'time_limit': [hour, minutes - 1, 59]
        })


def test_end_page_view(request, *args, **kwargs):
    summary_message = request.session['summary_message']
    return render(request, 'test_end_page.html', {'summary_message': summary_message})
