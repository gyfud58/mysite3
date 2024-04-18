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
            'wname':'이용자',
            'wplace' : '지역',
            'port' : '건물',
            'upload_imgfile' : '이미지',
        }

class AnswerForm(forms.ModelForm):
    class Meta:
        model=Answer
        fields=['predicted_imgfile','damage_result']
        labels={
            'predicted_imgfile':'이미지',
            'damage_result':'인원 수'
        }