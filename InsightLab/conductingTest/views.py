from django.shortcuts import render
from homeApp.models import Test, TestConfiguration


# Create your views here.

def test_start_view(request, *ags, **kwargs):
    test = Test.objects.get(unique_id=kwargs['test_id'])
    testName = test.name
    testConfig = TestConfiguration.objects.get(test=test)
    fields = testConfig.additional_fields
    return render(request, 'start_test.html', {"testConfig": testConfig, "fields": fields, "testName": testName})
