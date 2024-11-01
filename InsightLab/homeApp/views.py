from django.shortcuts import render, redirect, get_object_or_404
from .models import Test
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from django.conf import settings
from django.http import HttpResponse
from .models import Test, TestConfiguration, Option, Question



# Create your views here.

def home_view(request, *ags, **kwargs):
    return render(request, 'home_page.html', {})


def newtest_view(request, *args, **kwargs):
    return render(request, 'new_test.html', {})


def test_start_page_config(request, *args, **kwargs):
    return render(request, 'test_start_page.html', {})


def question_manager_view(request, *args, **kwargs):
    return render(request, 'question_manager.html', {})


def start_test(request, *args, **kwargs):
    return render(request, 'start_test.html', {})


def grading_summary_view(request, *args, **kwargs):
    return render(request, 'grading_summary.html', {})


def time_setting_view(request, *args, **kwargs):
    return render(request, 'time_setting.html', {})


def start_test_view(request, *ags, **kwargs):
    test = Test.objects.get(unique_id=kwargs['test_id'])
    testName = test.name
    testConfig = TestConfiguration.objects.get(test=test)
    print(testConfig)
    fields = testConfig.additional_fields
    return render(request, 'start_test.html', {"testConfig": testConfig, "fields": fields, "testName": testName})


@login_required
def activate_test(request):
    if request.method == 'POST':

        try:
            data = json.loads(request.body)
            test_name = data.get("testName")
            time_complete = data.get("timeComplete")
            time_per_question = data.get("timePerQuestion")
            questions = data.get("questions")
            pass_marks = data.get("passMarks")
            max_marks = data.get("maxMarks")
            selected_fields = json.loads(data.get("selectedFields"))
            summary_message = data.get("summaryMessage")

            if time_complete!=None:
                time=time_complete.split(":")
                time_complete=(int(time[0])*60)+(int(time[1]))*60

            if  time_per_question!=None:
                time=time_per_question.split(":")
                time_per_question=(int(time[0])*60)+(int(time[1]))


            # Validation
            if not test_name or not questions or not pass_marks or not max_marks:
                return JsonResponse({'error': 'Missing required fields.'}, status=400)
            if not time_complete and not time_per_question:
                return JsonResponse({'error': 'Please enter test time'}, status=400)

            # Create and save the Test instance
            test = Test(
                user=request.user,
                name=test_name,
                pass_marks=pass_marks,
                max_marks=max_marks
            )


            test.link=request.build_absolute_uri(test.generate_test_link())
            test.is_active = True
            test.time_limit = time_complete if time_complete!=None else time_per_question * len(questions)
            test.time_per_question = time_per_question if time_per_question!=None else 0
            test.summary_message = summary_message if summary_message!=None or summary_message!='' else "Thank you for taking the test!"
            test.save()


            for questions_data in questions:
                question_text=questions_data.get('question')
                question_type=questions_data.get('answerType')
                correct_point=questions_data.get('correctScore')
                incorrect_points=questions_data.get('incorrectScore')
                answers=questions_data.get('answers')
                correctAnswer=questions_data.get('correctAnswers')

                question=Question(
                    test=test,
                    question_text=question_text,
                    question_type=question_type,
                    correct_points=correct_point,
                    incorrect_points=incorrect_points
                )
                question.save()

                print(correctAnswer,answers,end='\n')
                for index,option_text in enumerate(answers):
                        is_correct=index in correctAnswer
                        print(index,option_text,correctAnswer,is_correct,end='\n')
                        option=Option(
                            question=question,
                            option_text=option_text,
                            is_correct=is_correct
                        )
                        option.save()


            selected_fields=selected_fields[1:-1]
            selected_fields=selected_fields.split(",")
            selected_fields=[fields[1:-1] for fields in selected_fields]
            testConfiguration=TestConfiguration(
                test=test,
                additional_fields=selected_fields
            )
            testConfiguration.save()

            return JsonResponse({'message': 'Test activated successfully', 'test_id': test.id})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
