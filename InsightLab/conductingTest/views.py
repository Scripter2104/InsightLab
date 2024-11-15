from django.shortcuts import render, redirect
from django.http import HttpResponse
from homeApp.models import Test, TestConfiguration, Question, Option
from .models import RespondentData, RespondentAnswers
from django.utils import timezone


# Create your views here.

def test_start_view(request, *ags, **kwargs):
    test = Test.objects.get(unique_id=kwargs['test_id'])
    testName = test.name
    testConfig = TestConfiguration.objects.get(test=test)
    fields = testConfig.additional_fields

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
        request.session['respondent_id'] = str(respondent_data.respondent_id)  # Convert to string
        return redirect('question_page')

    return render(request, 'start_test.html', {"testConfig": testConfig, "fields": fields, "testName": testName})


def question_page_view(request, *args, **kwargs):
    respondent = RespondentData.objects.get(respondent_id=request.session.get("respondent_id"))
    test_obj = respondent.test_id
    # Store common test data in session
    if 'test_data' not in request.session:
        questions = list(Question.objects.filter(test=test_obj).values('unique_id', 'question_text', 'question_type',
                                                                       'correct_points', 'incorrect_points'))

        for question in questions:
            question['unique_id'] = str(question['unique_id'])

        request.session['test_data'] = {
            "respondent_id": str(respondent.respondent_id),  # Store respondent_id as string
            "test_id": str(test_obj.unique_id),  # Store test_id as string
            "questions": questions,  # Store question data as a list of dictionaries
            "question_count": len(questions),
            "time_per_question": test_obj.time_per_question,
            "time_limit": test_obj.time_limit,
            "current_question_index": 0,
            "start_time": timezone.now().timestamp(),
            "total_marks": 0
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
    total_marks = test_data['total_marks']

    # Get test object and validate if it's active
    test_obj = Test.objects.get(unique_id=test_id)
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
        request.session['total_marks'] = test_data['total_marks']
        request.session['max_marks'] = test_obj.max_marks
        request.session['pass_marks'] = test_obj.pass_marks
        request.session['test_name'] = test_obj.name
        request.session.pop('test_data', None)
        request.session['first_name'] = respondent.first_name.capitalize()
        request.session['initials'] = respondent.first_name.strip()[0].upper()
        request.session['summary_message'] = test_obj.summary_message

        return redirect('test_end_page')

    # Get current question data
    current_question = questions[current_index]
    current_question_obj = Question.objects.get(unique_id=current_question['unique_id'])
    options = Option.objects.filter(question=current_question_obj)

    # Calculate remaining time
    if time_per_question != 0:
        elapsed_time = int(timezone.now().timestamp() - test_data['start_time'])
        remaining_time = max(0, time_per_question - elapsed_time)
    else:
        elapsed_time = int(timezone.now().timestamp() - test_data['start_time'])
        remaining_time = max(0, time_limit - elapsed_time)

    # On POST method
    if request.method == 'POST':
        correct_answers = [opt.option_text for opt in options if opt.is_correct]

        if current_question['question_type'] == 'multiple-choice':
            respondent_answers = request.POST.getlist('answer')
        else:
            respondent_answers = [request.POST.get('answer')] if request.POST.get('answer') else []

        is_correct = sorted(respondent_answers) == sorted(correct_answers)
        points = current_question['correct_points'] if is_correct else current_question['incorrect_points']
        if is_correct:
            total_marks += int(points)
        time_taken = timezone.now().timestamp() - test_data['start_time']

        respondent_answers_data = {"respondent_data": respondent,
                                   "question_id": current_question_obj,
                                   "correct_answer": correct_answers,
                                   "respondent_answer": respondent_answers,
                                   "is_correct": is_correct,
                                   "points": points,
                                   "time_taken": time_taken}

        respondentAnswer = RespondentAnswers(**respondent_answers_data)
        respondentAnswer.save()

        # Update session and redirect
        if time_per_question != 0:
            test_data['start_time'] = timezone.now().timestamp()
        test_data['current_question_index'] += 1
        test_data['total_marks'] = total_marks
        request.session['test_data'] = test_data
        print(total_marks)
        return redirect('question_page')

    render_context = {
        'question': current_question['question_text'],
        'question_number': current_index + 1,
        'question_type': current_question['question_type'],
        'total_questions': question_count,
        'test_name': test_obj.name,
        'test_obj': test_obj,
        'options': options,
        'remaining_time': remaining_time
    }
    if time_per_question != 0:
        render_context['time_per_question'] = time_per_question
    else:
        render_context['time_limit'] = time_limit

    return render(request, 'question_page.html', render_context)


def test_end_page_view(request, *args, **kwargs):
    return render(request, 'test_end_page.html', {"summary_message": request.session['summary_message'],
                                                  "total_marks": request.session['total_marks'],
                                                  "max_marks": request.session['max_marks'],
                                                  "pass_marks": request.session['pass_marks'],
                                                  "test_name":request.session["test_name"],
                                                  "first_name":request.session["first_name"],
                                                  "initials":request.session["initials"]})
