from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404

from ..models import Question, Answer

# Create your views here.
def index(request):
    """
    sales 목록 출력
    """
    # 입력 인자
    page=request.GET.get('page','1') # 페이지

    # 조회
    question_list=Question.objects.order_by('hcode')

    # 페이징 처리
    paginator=Paginator(question_list, 10) # 페이지당 10개씩 보여주기
    page_obj=paginator.get_page(page) # 페이지 번호를 인수로 받아 해당 페이지의 객체 목록을 반환

    context={'question_list':page_obj}
    return render(request, 'sales/question_list.html',context)

def detail(request,question_id):
    """
    sales 내용 출력
    """
    question=get_object_or_404(Question, pk=question_id)
    context={'question':question}
    return render(request, 'sales/question_detail.html', context)