from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
# from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Group, Comment, Post, User, Follow


# Главная страница
def index(request):
    template = 'posts/index.html'
    title = 'Последние обновления на сайте'
    text = 'Добро пожаловать в Yatube! Говорим обо всем на свете'
    posts = Post.objects.all()
    paginator = Paginator(posts, settings.NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'title': title,
        'text': text,
        'page_obj': page_obj,
    }
    return render(request, template, context)


# Страница группы с сортировкой по 10 постов
def group_list(request, slug):
    group = get_object_or_404(Group, slug=slug)
    template = 'posts/group_list.html'
    posts = group.posts.all()
    paginator = Paginator(posts, settings.NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


# Страница со списком групп
def groups(request):
    template = 'posts/groups.html'
    title = 'Информация о группах проекта Yatube'
    text = 'Список тематических групп'
    groups = Group.objects.all()
    context = {
        'title': title,
        'text': text,
        'groups': groups,
    }
    return render(request, template, context)


# Страница профиля
def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author_id=author.id)
    following = request.user.is_authenticated and author.following.exists()
    paginator = Paginator(posts, settings.NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following,
        'user': request.user
    }
    return render(request, template, context)


# Страница одного поста
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    quantity = post.author.posts.count()
    user = request.user
    form = CommentForm(request.POST or None)
    context = {
        'user': user,
        'post': post,
        'quantity': quantity,
        'form': form,
    }
    comments = Comment.objects.filter(post_id=post_id)
    if comments:
        context.update({'comments': comments})
    return render(request, 'posts/post_detail.html', context)


# Создать пост
@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        form = form.save(commit=False)
        form.author = request.user
        form.save()
        return redirect('posts:profile', form.author)
    context = {
        'form': form,
        'is_edit': False
    }
    return render(request, 'posts/post_create.html', context)


# Редактировать пост
@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'is_edit': True,
        'post_id': post_id,
    }
    return render(request, 'posts/update_post.html', context)


# Оставить комментарий
@login_required
def add_comment(request, post_id):
    form = CommentForm(request.POST or None)
    if form.is_valid():
        post = Post.objects.get(pk=post_id)
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    authors = Follow.objects.filter(user=request.user)
    following_authors = User.objects.filter(following__in=authors)
    posts = Post.objects.filter(author__in=following_authors)
    paginator = Paginator(posts, settings.NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(user=request.user, author=author)
    if request.user != author and not follow:
        Follow.objects.create(
            user=request.user,
            author=author
        )
        return redirect('posts:profile', username=username)
    else:
        return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(
        user=request.user,
        author=author
    ).delete()
    return redirect('posts:profile', username=username)
