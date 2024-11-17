from django.shortcuts import render, redirect
from django.http import HttpResponse
from homeApp.models import Test, TestConfiguration, Question, Option
from .models import RespondentData, RespondentAnswers
from django.utils import timezone
import time
import datetime
from django.views.decorators.cache import never_cache


# Create your views here.

@never_cache
def test_start_view(request, *ags, **kwargs):
    test = Test.objects.get(unique_id=kwargs['test_id'])
    testName = test.name
    testConfig = TestConfiguration.objects.get(test=test)
    fields = testConfig.additional_fields

    # handles back navigation from question_page if the test has started
    if 'test_is_present' in request.session:
        return redirect('question_page')
    # 'test_is_present' is not present but RespondentData for the test exists
    # handles back navigation from test_end_page after test has ended
    elif RespondentData.objects.filter(test_id=test, respondent_id=request.session.get("respondent_id")).exists():
        return redirect('test_end_page')

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
        request.session['test_is_present'] = True
        return redirect('question_page')

    return render(request, 'start_test.html', {"testConfig": testConfig, "fields": fields, "testName": testName})


@never_cache
def question_page_view(request, *args, **kwargs):
    # Handles back navigation from test_end_page
    if 'test_is_present' not in request.session:
        return redirect('test_end_page')

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
            "total_marks": 0,
            "total_time_taken": 0,
            "per_question_start_time": timezone.now().timestamp()
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

        if test_obj.time_per_question != 0:
            total_time = time_per_question * len(questions)
        else:
            total_time = test_obj.time_limit
        info = {
            "total_marks": test_data['total_marks'],
            "max_marks": test_obj.max_marks,
            "pass_marks": test_obj.pass_marks,
            "test_name": test_obj.name,
            "ending_time": str(time.localtime().tm_hour) + ":" + str(time.localtime().tm_min),
            "starting_time": str(time.localtime(test_data["start_time"]).tm_hour) + ":" + str(
                time.localtime(test_data["start_time"]).tm_min),
            "first_name": respondent.first_name.capitalize(),
            "initials": respondent.first_name.strip()[0].upper(),
            "summary_message": test_obj.summary_message,
            "date": str(datetime.date.today()),
            "total_time": str(datetime.timedelta(seconds=total_time)),
            "total_time_taken": str(datetime.timedelta(seconds=int(test_data["total_time_taken"])))
        }

        print(info["total_time_taken"])

        request.session.pop("test_data", None)
        request.session["info"] = info
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
        if time_per_question != 0:
            time_taken = timezone.now().timestamp() - test_data['start_time']
        else:
            time_taken = timezone.now().timestamp() - test_data["per_question_start_time"]

        respondent_answers_data = {"respondent_data": respondent,
                                   "question_id": current_question_obj,
                                   "correct_answer": correct_answers,
                                   "respondent_answer": respondent_answers,
                                   "is_correct": is_correct,
                                   "points": points,
                                   "time_taken": time_taken
                                   }

        test_data["total_time_taken"] += time_taken

        respondentAnswer = RespondentAnswers(**respondent_answers_data)
        respondentAnswer.save()

        # Update session and redirect
        if time_per_question != 0:
            test_data['start_time'] = timezone.now().timestamp()
        else:
            test_data["per_question_start_time"] = timezone.now().timestamp()
        test_data['current_question_index'] += 1
        test_data['total_marks'] = total_marks
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
        'remaining_time': remaining_time
    }
    if time_per_question != 0:
        render_context['time_per_question'] = time_per_question
    else:
        render_context['time_limit'] = time_limit

    return render(request, 'question_page.html', render_context)


@never_cache
def test_end_page_view(request, *args, **kwargs):
    # Clear session 'test_is_present' on first visit to end test
    # so back navigation to above (question_page_view) doesn't have it
    if 'test_is_present' in request.session:
        request.session.pop('test_is_present', None)

    info_from_session = request.session.get("info", {})
    test_end_info = {
        "summary_message": info_from_session.get("summary_message"),
        "total_marks": info_from_session.get("total_marks"),
        "max_marks": info_from_session.get("max_marks"),
        "pass_marks": info_from_session.get("pass_marks"),
        "test_name": info_from_session.get("test_name"),
        "first_name": info_from_session.get("first_name"),
        "initials": info_from_session.get("initials"),
        "end_time": info_from_session.get("ending_time"),
        "start_time": info_from_session.get("starting_time"),
        "date": info_from_session.get("date"),
        "total_time": info_from_session.get("total_time"),
        "total_time_taken": info_from_session.get("total_time_taken"),
        "result": "Pass" if info_from_session.get("total_marks") >= info_from_session.get("pass_marks") else "Fail"
    }

    return render(request, 'test_end_page.html', {**test_end_info})
