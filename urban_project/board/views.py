"""
В этом файле определены функции представления Django, содержащие логику обработки запросов пользователя

Первый блок - импорты библиотек и форм из других модулей:
- для визуализации шаблонов и перенаправления пользователей на разные страницы
- модель, представляющая рекламные объявления в базе данных
- формы для создания/редактирования рекламных объявлений и регистрации пользователей
- встроенного декоратора login_required, который используется для ограничения доступа к представлениям и требует, чтобы
пользователь прошел аутентификацию. Если пользователь не вошел в систему, он будет перенаправлен на страницу входа.

Далее идут импорты:
- функции для обработки аутентификации пользователей
- вспомогательной функция, которая используется для получения запроса из базы данных.
Если объект не найден, автоматически выдается ошибка 404 (применяется для упрощения кода).
- импортируем пагинатор для ограничения количества объявлений на одной странице
"""
from django.shortcuts import render, redirect, get_object_or_404
from .models import Advertisement, UserProfile
from board.forms import AdvertisementForm, SignUpForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.core.paginator import Paginator


def logout_view(request):
    """
    Эта функция предназначена для выхода пользователя из системы.
    Она обрабатывает HTTP-запрос, и ее основная задача — завершить сессию текущего пользователя.
    Параметр request — это объект, содержащий информацию о текущем запросе.
    Он передается автоматически Django при вызове функции представления.
    Эта строка выполняет перенаправление пользователя на страницу с именем home.
    Функция redirect создает HTTP-ответ, который сообщает браузеру, что необходимо перейти на другой URL.
    """
    logout(request)
    return redirect('home')


def signup(request):
    """
    Функция для управления регистрацией пользователей. Если метод запроса — POST, он обрабатывает отправленную форму.
    Если форма действительна, она сохраняет пользователя, авторизует его и перенаправляет на страницу объявлений.
    Если метод запроса — GET, отображается пустая форма регистрации
    UserProfile.objects.create(user=user) - создает профиль пользователя
    return render - возвращает страницу регистрации с формой
    """
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            return redirect('/board')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def home(request):
    """
    Функция для отображения домашней страницы.
    Параметр: request — объект запроса, который содержит информацию о запросе пользователя.
    Использует функцию render, чтобы вернуть HTML-страницу home.html.
    """
    return render(request, 'home.html')


def advertisement_list(request):
    """
    Функция для отображения списка всех рекламных объявлений.
    Она получает все данные из модели Advertisement.
    Возвращает HTML-страницу advertisement_list.html с контекстом, содержащим все объявления.
    Контекст передается как словарь, где ключ — advertisements, а значение — список объявлений;
    user_profiles - словарь профилей пользователей.
    Настройка пагинации:
    paginator - создаем экземпляр Paginator, который разбивает список объявлений на страницы, показывая по 10
    объявлений на каждой странице;
    page_number - извлекаем номер страницы из параметров запроса GET;
    page_obj - получаем объект, представляющий текущую страницу. Передаем его в шаблон.
    """
    advertisements = Advertisement.objects.all()

    # Настройка пагинации
    paginator = Paginator(advertisements, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'board/advertisement_list.html', {'page_obj': page_obj})


def advertisement_detail(request, pk):
    """
    Функция для отображения деталей конкретного объявления (первичный ключ объявления и подробности рекламы).
    Она показывает детали конкретного объявления по его первичному ключу (pk): извлекает одно объявление
    с указанным первичным ключом. Если объявление с таким ключом не найдено, будет вызвано исключение DoesNotExist.
    Возвращает HTML-страницу advertisement_detail.html с контекстом, содержащим детали конкретного объявления
    user_profile: профиль автора объявления. Сначала получаем его из словаря, затем функция его возвращает.
    """
    advertisement = Advertisement.objects.get(pk=pk)
    return render(request, 'board/advertisement_detail.html', {'advertisement': advertisement})


@login_required
def add_advertisement(request):
    """
    Функция позволяет добавлять новое объявление. Если метод запроса - "POST", то он обрабатывает отправленную форму.
    Если форма действительна, она связывает рекламу с текущим пользователем и сохраняет ее.
    После сохранения перенаправляет на список объявлений. Если метод запроса — "GET", то отображается пустая форма.
    Параметр request.FILES необходим для корректной обработки файлов, загружаемых через форму (например, изображений)
    """
    if request.method == "POST":
        form = AdvertisementForm(request.POST, request.FILES)
        if form.is_valid():
            advertisement = form.save(commit=False)
            advertisement.author = request.user
            advertisement.save()
            return redirect('board:advertisement_list')
    else:
        form = AdvertisementForm()
    return render(request, 'board/add_advertisement.html', {'form': form})


@login_required
def edit_advertisement(request, pk):
    """
    Функция обеспечивает безопасное редактирование объявления, проверяя права доступа пользователя,
    и обрабатывая как POST, так и GET запросы.
    Сначала извлекает объявление с заданным первичным ключом или возвращает ошибку 404, если оно не найдено.

    Далее идет проверка, является ли текущий пользователь автором конкретного объявления.
    Если не является, то функция перенаправляет его на список объявлений.
    В конце функция рендерит шаблон, передавая ему форму. Это позволяет пользователю редактировать объявление.
    """
    advertisement = get_object_or_404(Advertisement, pk=pk)

    if advertisement.author != request.user:
        return redirect('board:advertisement_list')

    if request.method == 'POST':
        form = AdvertisementForm(request.POST, request.FILES, instance=advertisement)
        if form.is_valid():
            form.save()
            return redirect('board:advertisement_detail', pk=advertisement.pk)
    else:
        form = AdvertisementForm(instance=advertisement)

    return render(request, 'board/edit_advertisement.html', {'form': form, 'advertisement': advertisement})


@login_required
def delete_advertisement(request, pk):
    """
      Функция реализует безопасное и удобное удаление объявлений с подтверждением от пользователя.
    Сначала извлекает объект Advertisement по заданному первичному ключу (pk).
    Если объявление не найдено, будет вызвана ошибка 404, что улучшает обработку ошибок.
      Далее идет проверка на соответствие текущего пользователя автору объявления.
    Это важно для обеспечения безопасности и предотвращения несанкционированного удаления объявлений.
    Если пользователь не является автором, он перенаправляется на список объявлений, без доступа к функции удаления.
      Если запрос является POST, это означает, что пользователь подтвердил намерение удалить объявление.
    В этом случае объявление удаляется из базы данных.
    После успешного удаления пользователь перенаправляется на страницу со списком объявлений.
      Если метод запроса не POST, функция отображает страницу подтверждения удаления.
    Передача объекта advertisement в шаблон позволяет пользователю увидеть, что именно он собирается удалить.
    """
    advertisement = get_object_or_404(Advertisement, pk=pk)

    if advertisement.author != request.user:
        return redirect('board:advertisement_list')

    if request.method == 'POST':
        advertisement.delete()
        return redirect('board:advertisement_list')

    return render(request, 'board/delete_advertisement_confirm.html',
                  {'advertisement': advertisement})


@login_required
def like_advertisement(request, pk):
    """
    Функция позволяет обработать действия лайков к объявлению. Она защищена декоратором, который требует, чтобы
    пользователь был аутентифицирован. Если пользователь не вошел в систему, он будет перенаправлен на страницу входа.
    Функция get_object_or_404 используется для получения объекта объявления по его первичному ключу (pk).
    Если объявление не найдено, будет возвращена ошибка 404.
    - request: объект запроса, содержащий информацию о текущем запросе пользователя;
    - pk: первичный ключ объявления, к которому добавляется лайк;
    - redirect: перенаправляет пользователя на страницу деталей объявления;
    - блок profile: обновление статистики пользователя.
    """
    advertisement = get_object_or_404(Advertisement, pk=pk)
    advertisement.likes += 1
    advertisement.save()

    profile = UserProfile.objects.get(user=advertisement.author)
    profile.total_likes += 1
    profile.save()

    return redirect('board:advertisement_detail', pk=pk)


@login_required
def dislike_advertisement(request, pk):
    """
    Функция позволяет обработать действия дизлайков к объявлению. Она защищена декоратором, который требует, чтобы
    пользователь был аутентифицирован. Если пользователь не вошел в систему, он будет перенаправлен на страницу входа.
    Функция get_object_or_404 используется для получения объекта объявления по его первичному ключу (pk).
    Если объявление не найдено, будет возвращена ошибка 404.
    - request: объект запроса, содержащий информацию о текущем запросе пользователя;
    - pk: первичный ключ объявления, к которому добавляется дизлайк;
    - redirect: перенаправляет пользователя на страницу деталей объявления;
    - блок profile: обновление статистики пользователя.
    """
    advertisement = get_object_or_404(Advertisement, pk=pk)
    advertisement.dislikes += 1
    advertisement.save()

    profile = UserProfile.objects.get(user=advertisement.author)
    profile.total_dislikes += 1
    profile.save()

    return redirect('board:advertisement_detail', pk=pk)
