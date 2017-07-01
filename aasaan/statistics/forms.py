from django import forms
from .MonthYearWidget import MonthYearWidget
from .models import OverseasEnrollement
from functools import partial

DateInput = partial(forms.DateInput, {'class': 'datepicker'})

class OverseasEnrollementForm(forms.ModelForm):
    program_month = forms.DateField(label = 'Month', widget=MonthYearWidget(years=range(2014, 2018)));
    program_start_date = forms.DateField(label='Program Date', widget=forms.SelectDateWidget(years=range(2014, 2018)));
    country = forms.CharField()
    state = forms.CharField(required=False)
    center_name = forms.CharField()
    program_name = forms.CharField()
    no_of_day = forms.IntegerField(required=False)
    total_participants = forms.IntegerField()
    teacher_name = forms.CharField(required=False)
    co_teacher = forms.CharField(required=False)

    class Meta:
        model = OverseasEnrollement
        exclude = ['co_teacher',]
