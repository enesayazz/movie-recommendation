from django import forms

class MyForm(forms.Form):
    my_field = forms.CharField(label='My Field', max_length=100)