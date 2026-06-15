from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import CustomUserCreationForm, CustomUserUpdateForm


def register_view(request):
    """
    Регистрация пользователя.

    Если метод GET, показываем пустую форму. Если POST, проверяем данные,
    сохраняем пользователя и сразу авторизуем его через login().
    """

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('blog:post_list')
    else:
        form = CustomUserCreationForm()

    return render(request, 'users/register.html', {'form': form})


@login_required
def profile_view(request):
    """
    Простое редактирование профиля текущего пользователя.

    request.user уже содержит авторизованного пользователя. Мы передаем его
    в instance, чтобы форма редактировала существующую запись, а не создавала
    новую.
    """

    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('users:profile')
    else:
        form = CustomUserUpdateForm(instance=request.user)

    return render(request, 'users/profile.html', {'form': form})

# Create your views here.
