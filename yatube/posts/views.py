from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect

from .models import Post, Group


def authorized_only(func):
    def check_user(request, *args, **kwargs):
        if request.user.is_authenticated:
            return func(request, *args, **kwargs)
        return redirect('/auth/login/')

    return check_user


# Главная страница
def index(request):
    template = 'posts/index.html'
    title = "Последние обновления на сайте"
    text = 'Добро пожаловать в Yatube! Говорим обо всем на свете'
    # posts = Post.objects.order_by('-pub_date')[:10]
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
@authorized_only
def group_list(request, slug):
    group = get_object_or_404(Group, slug=slug)
    template = 'posts/group_list.html'
    # posts = Post.objects.filter(group=group).order_by('-pub_date')[:10]
    posts = group.group_name.all()[:10]
    context = {
        'group': group,
        'posts': posts,
    }
    return render(request, template, context)


# Страница со списком групп
@login_required
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


# Страница выбранного поста
# def single_post(request, group_name, number_post):
#     template = 'posts/single_post.html'
#     context = {
#         'text': Post.text,
#         'author': Post.author,
#         'pub_date': Post.pub_date,
#         'group': Post.group,
#     }
#     return render(request, template, context)
