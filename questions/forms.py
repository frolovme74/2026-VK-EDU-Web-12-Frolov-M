from django import forms
from questions.models import Question, Tag, Answer

class AskForm(forms.ModelForm):
    tags_str = forms.CharField(
        label="Теги",
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'python, django, web', 'class': 'form-control'})
    )

    class Meta:
        model = Question
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
        }

    def save_tags(self, question_instance):

        tags_data = self.cleaned_data.get('tags_str', '')
        if not tags_data:
            return

        tag_names = list(set([t.strip() for t in tags_data.split(',') if t.strip()]))
        
        for name in tag_names:

            tag, created = Tag.objects.get_or_create(
                name=name,
            )
            question_instance.tags.add(tag)

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Введите ваш ответ здесь...'
            }),
        }