from django.contrib.auth.models import User
from django.conf import settings
from django.db import models
from django.utils import timezone

# Create your models here.
class Question(models.Model):
    hcode = models.CharField(max_length=10, unique=True)

    wname = models.TextField(max_length=20)
    wplace = models.TextField(max_length=20)
    port = models.TextField(max_length=20)

    author=models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='author_question')

    create_date = models.DateTimeField()
    modify_date = models.DateTimeField(null=True, blank=True)
    upload_imgfile = models.ImageField(upload_to="question/%Y%m%d", max_length=500,
                                       null=True, blank=True)

    def __str__(self):
        return self.wname+" "+self.wplace+" "+self.port+" "

    def publish(self):
        self.published_date=timezone.now()
        self.save()

class Answer(models.Model):
    damage_result=models.TextField()

    wname = models.TextField(max_length=20)
    wplace = models.TextField(max_length=20)
    port = models.TextField(max_length=20)

    author=models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='author_answer')

    create_date = models.DateTimeField()
    modify_date = models.DateTimeField(null=True, blank=True)
    predicted_imgfile = models.ImageField(upload_to="", max_length=500, 
                                null=True, blank=True)

    question=models.ForeignKey(Question,on_delete=models.CASCADE)

    def __str__(self):
        return self.wname+" "+self.wplace+" "+self.port+" "+self.damage_result+" "
# 이 코드는 상품 정보를 문자열 형식으로 반환합니다. 각 필드 값 사이에 공백(" ")을 추가하여 구분

    def publish(self):
        self.published_date=timezone.now()
        self.save()  # 현재 객체의 published_date 필드를 현재 시간으로 설정하고 객체를 저장