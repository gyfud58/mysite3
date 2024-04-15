from django import forms
from sales.models import Question, Answer

class QuestionForm(forms.ModelForm):
    class Meta:
        model=Question
        fields=['wname','wplace','port','upload_imgfile']
        # widgets={
        #     'subject':forms.TextInput(attrs={'class':'form=control'}),
        #     'content':forms.Textarea(attrs={'class':'from-control','rows':10}),
        # }
        labels={
            'wname':'근무자명',
            'wplace' : '근무지역',
            'port' : '항구명',
            'upload_imgfile' : '이미지',
        }

class AnswerForm(forms.ModelForm):
    class Meta:
        model=Answer
        fields=['predicted_imgfile','damage_result']
        labels={
            'predicted_imgfile':'이미지',
            'damage_result':'손상 여부 결과'
        }