from django.shortcuts import render, get_object_or_404 # type: ignore
from homeApp.models import Test, Question
from conductingTest.models import RespondentData, RespondentAnswers
from django.db.models import Sum # type: ignore

def respondent_list(request, test_id):
    test = get_object_or_404(Test, unique_id=test_id)
    respondents = RespondentData.objects.filter(test_id=test)
    total_respondents = respondents.count()
    total_questions = test.questions.count()

    lowest_score = 0
    highest_score = 0
    total_score = 0
    total_time_taken1 = 0

    respondent_data = []
    for respondent in respondents:
        total_time_taken = 0
        answers = RespondentAnswers.objects.filter(respondent_data=respondent)
        total_score += answers.aggregate(Sum('points'))['points__sum'] or 0
        total_time_taken += answers.aggregate(Sum('time_taken'))['time_taken__sum'] or 0

        correct_points = answers.filter(is_correct=True).aggregate(
            Sum('question_id__correct_points'))['question_id__correct_points__sum'] or 0
        incorrect_points = answers.filter(is_correct=False).aggregate(
            Sum('question_id__incorrect_points'))['question_id__incorrect_points__sum'] or 0

        if total_questions > 0:
            percentage = (correct_points - incorrect_points) * 100 / (
                    total_questions * (test.questions.first().correct_points))
        else:
            percentage = 0

        lowest_score = min(lowest_score, percentage)
        highest_score = max(highest_score, percentage)
        total_score += percentage
        total_time_taken1 += total_time_taken

        respondent_data.append({
            'respondent': respondent,
            'total_score': total_score,
            'total_questions': total_questions,
            'total_time': total_time_taken,
            'percentage': percentage
        })

    if test.time_limit!=None:
        time=test.time_limit
    if test.time_per_question!=None:
        time=test.time_per_question * total_questions

    print(time)

    context = {
    'test': test,
    'respondent_data': respondent_data,
    'lowest_score': lowest_score,
    'highest_score': highest_score,
    'average_score': round(total_score / total_respondents, 2) if total_respondents > 0 else 0,
    'average_time_taken': round(total_time_taken1 / total_respondents, 2) if total_respondents > 0 else 0,
    'total_time': time
    }


    return render(request, 'respondent_list.html', context)



def respondent_detail(request, respondent_id):
    respondent = get_object_or_404(RespondentData, respondent_id=respondent_id)
    answers = RespondentAnswers.objects.filter(respondent_data=respondent)

    detailed_answers = []
    for answer in answers:
        question = answer.question_id
        options = question.options.all()

        detailed_answers.append({
            'question': question,
            'options': options,
            'correct_answer': answer.correct_answer,
            'respondent_answer': answer.respondent_answer,
            'is_correct': answer.is_correct,
        })

    context = {
        'respondent': respondent,
        'detailed_answers': detailed_answers,
    }
    return render(request, 'respondent_detail.html', context)
