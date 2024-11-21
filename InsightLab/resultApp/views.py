from django.shortcuts import render, get_object_or_404
from homeApp.models import Test, Question
from conductingTest.models import RespondentData, RespondentAnswers
from django.db.models import Sum


def respondent_list(request, test_id):
    test = get_object_or_404(Test, unique_id=test_id)
    respondents = RespondentData.objects.filter(test_id=test)
    total_questions = test.questions.count()

    respondent_data = []
    for respondent in respondents:
        answers = RespondentAnswers.objects.filter(respondent_data=respondent)
        total_score = answers.aggregate(Sum('points'))['points__sum'] or 0
        total_questions = answers.count()
        total_time = answers.aggregate(Sum('time_taken'))['time_taken__sum'] or 0

        # Calculate score based on correct/incorrect points and equal weighting
        correct_points = answers.filter(is_correct=True).aggregate(Sum('question_id__correct_points'))[
                             'question_id__correct_points__sum'] or 0
        incorrect_points = answers.filter(is_correct=False).aggregate(Sum('question_id__incorrect_points'))[
                               'question_id__incorrect_points__sum'] or 0

        if total_questions > 0:  # Avoid division by zero
            percentage = (correct_points - incorrect_points) * 100 / (
                        test.questions.count() * (test.questions.first().correct_points))
        else:
            percentage = 0

        respondent_data.append({
            'respondent': respondent,
            'total_score': total_score,
            'total_questions': total_questions,
            'total_time': total_time,
            'percentage': percentage
        })

    context = {
        'test': test,
        'respondent_data': respondent_data,
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
