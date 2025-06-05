from django import forms
from .models import TopicRequest

class TopicRequestForm(forms.ModelForm):
    explanation_file = forms.FileField(required=True, label='Файл с объяснением (.docx)')
    example_code_file = forms.FileField(required=True, label='Файл с примером кода (.docx)')
    class Meta:
        model = TopicRequest
        fields = [
            'title',
            'explanation_file',
            'example_code_file',
            'exercise_render_code',
            'exercise_logic_code',
        ]
        widgets = {
            'exercise_render_code': forms.Textarea(attrs={'rows': 6}),
            'exercise_logic_code': forms.Textarea(attrs={'rows': 6}),
        }