from django import forms
from .models import TopicRequest

class TopicRequestForm(forms.ModelForm):
    class Meta:
        model = TopicRequest
        fields = [
            'title',
            'explanation',
            'example_code',
            'exercise_render_code',
            'exercise_logic_code',
        ]
        widgets = {
            'explanation': forms.Textarea(attrs={'rows': 4}),
            'example_code': forms.Textarea(attrs={'rows': 6}),
            'exercise_render_code': forms.Textarea(attrs={'rows': 6}),
            'exercise_logic_code': forms.Textarea(attrs={'rows': 6}),
        }