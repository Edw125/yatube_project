from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect

from .forms import PostForm
from .models import Post, Group, User


# Главная страница
def index(request):
    template = 'posts/index.html'
    title = 'Последние обновления на сайте'
    text = 'Добро пожаловать в Yatube! Говорим обо всем на свете'
    posts = Post.objects.all()
    paginator = Paginator(posts, 10)
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
    posts = group.group_name.all()
    paginator = Paginator(posts, 10)
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
    quantity = posts.count()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'author': author,
        'quantity': quantity,
        'page_obj': page_obj,
    }
    return render(request, template, context)


# Страница одного поста
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user
    quantity = post.author.posts.count()
    context = {
        'user': user,
        'post': post,
        'quantity': quantity,
    }
    return render(request, 'posts/post_detail.html', context)


# Создать пост
@login_required
def post_create(request):
    form = PostForm(request.POST or None)
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
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'is_edit': True,
        'post_id': post_id,
    }
    return render(request, 'posts/update_post.html', context)
