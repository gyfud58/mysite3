from django.contrib import messages # '수정권한이 없습니다' 오류 메세지 발생시키기 위해
from django.contrib.auth.decorators import login_required # @login_required 애더네이션 적용하기
from django.shortcuts import render, get_object_or_404, redirect 
from django.utils import timezone # 현재시간 timezone.now() 사용하기 위해

from ..models import Question
from ..forms import QuestionForm
from .answer_views import *

import os
import ultralytics # YOLO 라이브러리 import
from ultralytics import YOLO
import cv2
from PIL import Image, ImageFont, ImageDraw
import numpy as np
from datetime import datetime

# Create your views here.

# class별 건수 및 전체 건수 계산 함수
def count_objects(results, target_classes):

    total_counts = 0
    object_counts = {x: 0 for x in target_classes} # 0 으로 초기화

    for result in results: # predict() 결과가 저장된 results 변수 반복문
         for c in result.boxes.cls: # 예측결과에서 각 객체의 클래스ID
            c = int(c) # float타입 -> 정수형으로 변환
            '''
            target_classes : predict()에 넘겨준 관심 classes=[] 저장 리스트
            object_counts : 각 클래스별 객체 개수를 저장하는 딕셔너리
            '''
            if c in target_classes:
                object_counts[c] += 1
            elif c not in target_classes:
                object_counts[c] = 0

    for i in object_counts:
        if object_counts[i] >= 1 :
            total_counts += object_counts[i]

    return object_counts[3],total_counts # [halibut]마리, 전체 건수

# 이미지에 counter 넣기 함수
def plot_counter1(img, text1): # text 1 줄만 넣기
    font= cv2.FONT_HERSHEY_SIMPLEX
    fontScale = 1
    color = (0,255,0)
    thickness = 2

    h, w, c = img.shape # 이미지 크기(모양)를 읽어오자
    # c= img.shape

    # 문자 넣을 x,y 위치 정하기
    org1_x = org2_x = w - 330
    org1_y = h - 30
    org1 =  (org1_x, org1_y)

    # img 변수가 NumPy 배열인지 확인
    if not isinstance(img, np.ndarray):
        # img_nparray = np.array(img)
        # img_nparray = np.asarray(img)
        raise TypeError("img 변수가 NumPy 배열이 아닙니다.")

    cv2.putText(img,text1,org1,font,fontScale,color,thickness,cv2.LINE_AA)

    # 이미지 출력해보자
    # cv2.imshow('Image', img) # colab 이외 환경 (vscode, jupyter notebook 등)

# 추론/예측 함수
def yolo_predict(filename, user):

    source_path = './media/' + str(filename) # 경로 포함 파일이름
    predict_dir = './media/answer/'

    source_file = os.path.split(source_path)[1] # 순수 파일이름만
    predict_file = timezone.now().strftime("%Y%m%d") # %H%M
    
    out_file = predict_dir + predict_file + '/' + source_file
    # print
    predict_image_url = 'answer/' + predict_file + '/' + source_file
    # print(장고에는 answer부터 있어야 한다) * 미디어부터 있으면 장고가 인식을 못한다

    choice = False

    if choice : # YOLOv8 original 모델 그대로 사용
        yolo_model = YOLO('yolov8n.pt') 

    else : # 전이학습 : YOLOv8 pretrained 모델 지정
        # pretrained_model = 'C:/projects/crowds/YOLOv8/best.pt'
        pretrained_model = './media/weights/best_30.pt'
        yolo_model = YOLO(pretrained_model) # 전이학습용

    # predict 예측/추론하기
    results = yolo_model.predict(source=source_path, conf=0.30,save=True,
                                 project=predict_dir, name=predict_file, 
                                 exist_ok=True, seed=0, show_conf=False)

    # object detection 결과 : person, 전체 건수 계산
    halibut_count, total_counts = count_objects(results, yolo_model.names)

    # 이미지에 person 건수 쓰기
    cv2_image = cv2.imread(out_file)
    out_text1 = f'      [{halibut_count}] halibut' # 이미지에 출력
    plot_counter1(cv2_image, out_text1)
    cv2.imwrite(out_file, cv2_image)

    # result_mesg = f'YOLOv8 분석 내용 : [{halibut_count}] 명'
    result_mesg = f'[{halibut_count}] 명'
    return result_mesg, predict_image_url

@login_required(login_url='common:login')
def question_create(request):
    """
    sales 질문 등록
    """
    def _generate_next_hcode(last_hcode):
        """
        마지막 hcode로부터 다음 hcode를 생성
        """
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if not last_question:
            return 'H0001'

        last_hcode = last_question.hcode
        number = int(last_hcode[1:]) + 1
        next_hcode = f"H{number:04}"

        if number > len(alphabet):
            next_hcode = f"{alphabet[number // len(alphabet)]}{next_hcode}"
        return next_hcode

    if request.method == 'POST':
        form=QuestionForm(request.POST,request.FILES)
        if form.is_valid():
            question=form.save(commit=False)
            question.upload_imgfile = request.FILES['upload_imgfile']
            question.author=request.user # 추가한 속성 author 적용
            question.create_date=timezone.now()

            # hcode 생성
            # question.hcode = _generate_next_hcode()

            last_question = Question.objects.order_by('hcode').last()
            if last_question:
                question.hcode = _generate_next_hcode(last_question.hcode)  # last_hcode 인수 전달
            else:
                question.hcode = 'H0001'

            question.save()

            # ======= YOLOv8 predict() 후에 답변을 자동 생성할까? ========== 

        # if (question.upload_imgfile.size > 0) : # 파일이 정상적으로 업로드 되었는 지
            result_mesg, out_file = yolo_predict(question.upload_imgfile, request.user)
            # print(type(result_mesg))
            # print(type(out_file))
            # img=cv2.imread('example.jpg', cv2.IMREAD_COLOR)
            # print("이미지의 데이터 타입:", img.dtype)
            # print("이미지의 형태:", img.shape)

            answer_create(request, question.id, result_mesg, out_file) ### result_mesg, predict_image_url 반환 지점

            return redirect('sales:index')

    else:
        form=QuestionForm()
    context={'form':form}
    return render(request,'sales/question_form.html',context)

@login_required(login_url='common:login')
def question_modify(request, question_id):
    """
    sales 질문 수정
    """
    question=get_object_or_404(Question,pk=question_id)
    if request.user != question.author:
        messages.error(request,'수정권한이 없습니다')
        return redirect('sales:detail',question_id=question.id)

    if request.method == "POST":
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            question=form.save(commit=False)
            question.author=request.user
            question.modify_date=timezone.now() # 수정일시 저장
            question.save()
            return redirect('sales:detail',question_id=question.id)

    else:
        form=QuestionForm(instance=question)
    context={'form':form}
    return render(request, 'sales/question_form.html',context)

@login_required(login_url='common:login')
def question_delete(request, question_id):
    """
    sales 질문 삭제
    """
    question=get_object_or_404(Question,pk=question_id)
    if request.user != question.author:
        messages.error(request,'삭제권한이 없습니다')
        return redirect('sales:detail',question_id=question.id)
    question.delete()
    return redirect('sales:index')