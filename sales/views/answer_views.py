from django.contrib import messages # '수정권한이 없습니다' 오류 메세지 발생시키기 위해
from django.contrib.auth.decorators import login_required # @login_required 애더네이션 적용하기
from django.shortcuts import render, get_object_or_404, redirect, resolve_url 
from django.utils import timezone # 현재시간 timezone.now() 사용하기 위해

from ..models import Question, Answer
from ..forms import AnswerForm

@login_required(login_url='common:login')
def answer_create(request, question_id, result_mesg, out_file): # 인자가 어디에서 전달되는가?
    """
    sales 답변 등록
    """
    question=get_object_or_404(Question, pk=question_id)
    # question.answer_set.create(hcode=request.POST.get('hcode'),
    #                            create_date=timezone.now())
    if request.method == "POST":
        form=AnswerForm(request.POST)
        if form.is_valid():           
            answer=form.save(commit=False) # create_date가 지정될 때까지 임시저장
            answer.damage_result=result_mesg
            answer.predicted_imgfile=out_file            
            answer.author=request.user # 추가한 속성 author 적용
            answer.create_date=timezone.now()
            answer.question=question
            answer.save()

            return redirect('sales:detail', question_id=question.id)
    else:
        form=AnswerForm()
    context={'question':question,'form':form}
    return render(request, 'sales/question_detail.html', context) ##### answer_form으로 변경해라 난중에

@login_required(login_url='common:login')
def answer_modify(request, answer_id):
    """
    sales 답변 수정
    """
    answer=get_object_or_404(Answer,pk=answer_id)
    if request.user !=answer.author:
        messages.error(request,'수정권한이 없습니다')
        return redirect('sales:detail',question_id=answer.question.id)

    if request.method == "POST":
        form=AnswerForm(request.POST,instance = answer)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.author=request.user
            answer.modify_date=timezone.now()
            answer.save()
            return redirect('{}#answer_{}'.format(
                resolve_url('sales:detail',question_id=answer.question.id),answer.id))
    else:
        form = AnswerForm(instance=answer)
    context={'answer':answer,'form':form}
    return render(request,'sales/answer_form.html',context)

@login_required(login_url = 'common:login')
def answer_delete(request,answer_id):
    """
    sales 답변 삭제
    """
    answer=get_object_or_404(Answer, pk=answer_id)
    if request.user != answer.author:
        messages.error(request,'삭제 권한이 없습니다')
    else:
        answer.delete()
    return redirect('sales:detail',question_id=answer.question.id)