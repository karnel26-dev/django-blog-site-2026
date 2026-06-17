from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Category, Post, Tag


def post_list(request):
    """
    Главная страница со списком постов.

    Здесь показаны сразу несколько типичных задач:
    - поиск по заголовку и тексту;
    - фильтрация по автору, категории и тегу;
    - сортировка по дате, заголовку и количеству лайков.
    """

    posts = Post.objects.select_related('author', 'category').prefetch_related('tags', 'likes')

    query = request.GET.get('q', '').strip()
    author_id = request.GET.get('author', '')
    category_id = request.GET.get('category', '')
    tag_id = request.GET.get('tag', '')
    sort = request.GET.get('sort', '-created_at')

    if query:
        posts = posts.filter(Q(title__icontains=query) | Q(text__icontains=query))

    if author_id:
        posts = posts.filter(author_id=author_id)

    if category_id:
        posts = posts.filter(category_id=category_id)

    if tag_id:
        posts = posts.filter(tags__id=tag_id)

    # annotate добавляет к каждому посту вычисленное поле likes_count.
    # По нему можно сортировать список.
    posts = posts.annotate(likes_count=Count('likes'))

    allowed_sort_fields = {
        '-created_at': '-created_at',
        'created_at': 'created_at',
        'title': 'title',
        '-likes': '-likes_count',
        'likes': 'likes_count',
    }
    posts = posts.order_by(allowed_sort_fields.get(sort, '-created_at'))

    context = {
        'posts': posts,
        'query': query,
        'authors': get_user_model().objects.all().order_by('username'),
        'categories': Category.objects.all(),
        'tags': Tag.objects.all(),
        'selected_author': author_id,
        'selected_category': category_id,
        'selected_tag': tag_id,
        'selected_sort': sort,
        'page_heading': 'Посты',
        'page_description': 'Читайте посты, ищите по тексту, фильтруйте по автору, категории и тегам.',
    }
    return render(request, 'blog/post_list.html', context)


@login_required
def my_posts(request):
    """
    Список постов текущего пользователя.

    Используем отдельный view, чтобы студентам было видно, как получить
    записи, связанные с request.user.
    """

    posts = (
        Post.objects.select_related('author', 'category')
        .prefetch_related('tags', 'likes')
        .filter(author=request.user)
        .annotate(likes_count=Count('likes'))
        .order_by('-created_at')
    )
    context = {
        'posts': posts,
        'page_heading': 'Мои посты',
        'page_description': 'Все посты, которые вы создали.',
        'hide_filters': True,
    }
    return render(request, 'blog/post_list.html', context)


def user_posts(request, user_id):
    """
    Просмотр постов любого пользователя.

    user_id приходит из адреса страницы. Если пользователя нет, Django вернет
    стандартную страницу 404.
    """

    author = get_object_or_404(get_user_model(), pk=user_id)
    posts = (
        Post.objects.select_related('author', 'category')
        .prefetch_related('tags', 'likes')
        .filter(author=author)
        .annotate(likes_count=Count('likes'))
        .order_by('-created_at')
    )
    context = {
        'posts': posts,
        'page_heading': f'Посты пользователя {author.username}',
        'page_description': 'Публичный список постов выбранного автора.',
        'hide_filters': True,
    }
    return render(request, 'blog/post_list.html', context)


def post_detail(request, pk):
    """Страница одного поста."""

    post = get_object_or_404(
        Post.objects.select_related('author', 'category').prefetch_related('tags', 'likes'),
        pk=pk,
    )
    return render(request, 'blog/post_detail.html', {'post': post})


@login_required
def post_create(request):
    """
    Создание поста.

    author не выводится в форме. Мы ставим автора автоматически из request.user,
    чтобы пользователь не мог создать пост от чужого имени.
    """

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            messages.success(request, 'Пост создан.')
            return redirect(post)
    else:
        form = PostForm()

    return render(request, 'blog/post_form.html', {'form': form, 'title': 'Новый пост'})


@login_required
def post_update(request, pk):
    """
    Редактирование поста.

    Редактировать можно только свои посты. Администратор тоже редактирует только
    свои посты, как указано в задании.
    """

    post = get_object_or_404(Post, pk=pk)

    if post.author != request.user:
        messages.error(request, 'Можно редактировать только свои посты.')
        return redirect(post)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Пост обновлен.')
            return redirect(post)
    else:
        form = PostForm(instance=post)

    return render(request, 'blog/post_form.html', {'form': form, 'title': 'Редактировать пост'})


@login_required
def post_delete(request, pk):
    """
    Удаление поста.

    Обычный пользователь может удалить только свой пост.
    Администратор (is_staff=True) может удалить любой пост.
    """

    post = get_object_or_404(Post, pk=pk)

    if post.author != request.user and not request.user.is_staff:
        messages.error(request, 'Удалять можно только свои посты.')
        return redirect(post)

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Пост удален.')
        return redirect('blog:post_list')

    return render(request, 'blog/post_confirm_delete.html', {'post': post})


@login_required
def post_like(request, pk):
    """
    Поставить или убрать лайк.

    Повторный клик работает как переключатель: если лайк уже есть, он удаляется.
    """

    post = get_object_or_404(Post, pk=pk)

    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)

    return redirect(request.META.get('HTTP_REFERER', post.get_absolute_url()))

# Create your views here.
