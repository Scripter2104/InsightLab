from django.shortcuts import render, redirect
from homeApp.models import Test, TestConfiguration
from .models import RespondentData


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

        print(form_data)

        respondent_data = RespondentData(**form_data)
        respondent_data.save()
        return redirect('question_page')

    return render(request, 'start_test.html', {"testConfig": testConfig, "fields": fields, "testName": testName})


def question_page_view(request, *args, **kwargs):
    return render(request, 'question_page.html', {})
