import uuid

from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from homeApp.models import Test, TestConfiguration, Question, Option
from .models import RespondentData, RespondentAnswers
from django.utils import timezone
import math


# Create your views here.

def test_start_view(request, *ags, **kwargs):
    test = Test.objects.get(unique_id=kwargs['test_id'])
    testName = test.name
    testConfig = TestConfiguration.objects.get(test=test)
    fields = testConfig.additional_fields
    print(test)

    if request.method == 'POST':
        form_data = {
            'test_id': test,
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

    return render(request, 'start_test.html', {"fields": fields, "testName": testName})


def question_page_view(request, *args, **kwargs):
    # Store common test data in session
    if 'test_data' not in request.session:
        respondent = RespondentData.objects.get(respondent_id=request.session.get("respondent_id"))
        test_obj = respondent.test_id
        # List of dictionaries containing per-question data
        questions = list(Question.objects.filter(test=test_obj).values('id', 'question_text', 'question_type', 'correct_points', 'incorrect_points'))

        request.session['test_data'] = {
            "respondent_id": str(respondent.respondent_id),  # Store respondent_id instead of the full object
            "test_id": test_obj.id,  # Store test id only
            "questions": questions,  # Store question data as a list of dictionaries
            "question_count": len(questions),
            "time_per_question": test_obj.time_per_question,
            "time_limit": test_obj.time_limit,
            "current_question_index": 0,
            "start_time": timezone.now().timestamp()
        }

    # Get session data
    test_data = request.session['test_data']
    respondent_id = test_data['respondent_id']
    test_id = test_data['test_id']
    questions = test_data['questions']
    question_count = test_data['question_count']
    time_per_question = test_data['time_per_question']
    time_limit = test_data['time_limit']
    current_index = test_data['current_question_index']

    # Retrieve respondent and test objects
    respondent = RespondentData.objects.get(respondent_id=respondent_id)
    test_obj = Test.objects.get(id=test_id)

    # Check if test is active
    if not test_obj.is_active:
        return HttpResponse(
            """
            <div style="display: flex; justify-content: center; align-items: center; height: 100vh;">
                <h1 style="font-family: Arial, sans-serif; color: #16A34A; text-align: center;">
                    Test is not active
                </h1>
            </div>
            """
        )

    # Check if test is complete
    if current_index >= question_count:
        request.session.pop('test_data', None)
        return redirect('test_end_page')

    # Get current question data
    current_question = questions[current_index] # "current_question" is a dictionary
    options = list(Option.objects.filter(question_id=current_question['id']))

    # On POST method
    if request.method == 'POST':
        correct_answers = [opt.option_text for opt in options if opt.is_correct]

        if current_question['question_type'] == 'multiple-choice':
            respondent_answers = request.POST.getlist('answer')
        else:
            respondent_answers = [request.POST.get('answer')] if request.POST.get('answer') else []

        is_correct = sorted(respondent_answers) == sorted(correct_answers)
        points = current_question['correct_points'] if is_correct else current_question['incorrect_points']
        time_taken = timezone.now().timestamp() - test_data['start_time']

        # Create response record
        RespondentAnswers.objects.create(
            respondent_data=respondent,
            # "question_id=current_question['id']" works because Django interprets the _id suffix as an instruction to directly use the primary key (in this case, the id of the Question object)
            # "question=current_question['id']" fails because Django expects question to be a Question instance
            # to use "question" instead of "question_id", you would need to pass "question=Question.objects.get(id=current_question['id'])",
            question_id=current_question['id'],
            correct_answer=correct_answers,
            respondent_answer=respondent_answers,
            is_correct=is_correct,
            points=points,
            time_taken=int(time_taken)
        )

        # Update session and redirect
        test_data['current_question_index'] += 1
        test_data['start_time'] = timezone.now().timestamp()
        request.session['test_data'] = test_data
        return redirect('question_page')

    render_context = {
        'question': current_question['question_text'],
        'question_number': current_index + 1,
        'question_type': current_question['question_type'],
        'total_questions': question_count,
        'test_name': test_obj.name,
        'test_obj': test_obj,
        'options': options,
    }
    if time_per_question != 0:
        render_context['time_per_question'] = time_per_question
    else:
        render_context['time_limit'] = time_limit

    return render(request, 'question_page.html', render_context)


def test_end_page_view(request, *args, **kwargs):
    summary_message = "<h1>Thank you for taking the test<h1>"
    return render(request, 'test_end_page.html', {"summary_message": summary_message})
