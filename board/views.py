from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from .models import Question, Answer, Comment, Like
from .forms import CommentForm, QuestionForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponseForbidden

def index(request):
    query = request.GET.get('q')  # 검색어를 가져옵니다
    top_questions = Question.objects.order_by('-likes')[:10]

    if query:
        latest_questions_list = Question.objects.filter(title__icontains=query).order_by('-pub_date')
    else:
        latest_questions_list = Question.objects.order_by('-pub_date')

    paginator = Paginator(latest_questions_list, 10)  # 페이지 당 10개의 질문
    page_number = request.GET.get('page')
    latest_questions = paginator.get_page(page_number)

    return render(request, 'board/index.html', {
        'top_questions': top_questions,
        'latest_questions': latest_questions,
        'query': query  # 검색어를 템플릿에 전달합니다
    })

def question_detail(request, pk):
    question = get_object_or_404(Question, pk=pk)
    comments = Comment.objects.filter(question=question).order_by('pub_date')
    user = request.user
    has_liked = False
    if user.is_authenticated:
        has_liked = Like.objects.filter(user=user, question=question).exists()
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.question = question
            comment.user = request.user  # 댓글 작성자 설정
            comment.pub_date = timezone.now()
            comment.save()
            return redirect('board:question_detail', pk=question.pk)
    else:
        form = CommentForm()
    return render(request, 'board/question_detail.html', {
        'question': question,
        'comments': comments,
        'has_liked': has_liked,
        'form': form,
    })

@login_required
def like_question(request, pk):
    question = get_object_or_404(Question, pk=pk)
    user = request.user

    like, created = Like.objects.get_or_create(user=user, question=question)
    if not created:
        # 이미 좋아요를 누른 경우, 좋아요를 취소
        like.delete()
        question.likes -= 1
    else:
        # 좋아요 추가
        question.likes += 1
    question.save()

    return redirect('board:question_detail', pk=question.pk)

def add_comment_to_question(request, pk):
    question = get_object_or_404(Question, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.question = question
            comment.save()
            return redirect('board:question_detail', pk=question.pk)
    else:
        form = CommentForm()
    return render(request, 'board/add_comment_to_question.html', {'form': form})

@login_required
def create_question(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        image = request.FILES.get('image')

        question = Question(title=title, content=content, pub_date=timezone.now(), user=request.user, image=image)
        question.save()

        return redirect('board:index')

    return render(request, 'board/create_question.html')

@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if comment.user != request.user:
        return HttpResponseForbidden("You are not allowed to delete this comment.")
    
    comment.delete()
    return redirect('board:question_detail', pk=comment.question.pk)
