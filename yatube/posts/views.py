from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from yatube.settings import NUM_OF_PAGES

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post

User = get_user_model()


# Главная страница
def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, NUM_OF_PAGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


# Страница с постами, отфильтрованными по группам
def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.group_posts.all()
    paginator = Paginator(post_list, NUM_OF_PAGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


# Персональная страница пользователя
def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    paginator = Paginator(post_list, NUM_OF_PAGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    following = False
    if (
        request.user.is_authenticated
        and Follow.objects.filter(user=request.user, author=author).exists()
    ):
        following = True
    context = {
        'page_obj': page_obj,
        'author': author,
        'post_list': post_list,
        'following': following
    }
    return render(request, 'posts/profile.html', context)


# Подробная инфомрмация о посте
def post_detail(request, post_id):
    post = Post.objects.get(pk=post_id)
    post_count = post.author.posts.all().count()
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'post_count': post_count,
        'comments': post.comments.all(),
        'form': form
    }
    return render(request, 'posts/post_detail.html', context)


# Создание нового поста
@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user)
    return render(request, template, {'form': form})


# Редактирование существующего поста
@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


# Добавление комментария
@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


# Страница с постами избранных авторов
@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, NUM_OF_PAGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


# Подписка
@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


# Отписка
@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:profile', username=username)
