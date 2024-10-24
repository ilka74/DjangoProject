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
"""
from django.shortcuts import render, redirect
from board.models import Advertisement
from board.forms import AdvertisementForm, SignUpForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import get_object_or_404


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
    """
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/board')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form}) # возвращает страницу регистрации с формой


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
    Контекст передается как словарь, где ключ — advertisements, а значение — список объявлений.
    """
    advertisements = Advertisement.objects.all()
    return render(request, 'board/advertisement_list.html', {'advertisements': advertisements})


def advertisement_detail(request, pk):
    """
    Функция для отображения деталей конкретного объявления (первичный ключ объявления и подробности рекламы).
    Она показывает детали конкретного объявления по его первичному ключу (pk): извлекает одно объявление
    с указанным первичным ключом. Если объявление с таким ключом не найдено, будет вызвано исключение DoesNotExist.
    Возвращает HTML-страницу advertisement_detail.html с контекстом, содержащим детали конкретного объявления
    """
    advertisement = Advertisement.objects.get(pk=pk)
    return render(request, 'board/advertisement_detail.html', {'advertisement': advertisement})


@login_required
def add_advertisement(request):
    """
    Функция позволяет добавлять новое объявление. Если метод запроса - "POST", то он обрабатывает отправленную форму.
    Если форма действительна, она связывает рекламу с текущим пользователем и сохраняет ее.
    После сохранения перенаправляет на список объявлений. Если метод запроса — "GET", то отображается пустая форма.
    """
    if request.method == "POST":
        form = AdvertisementForm(request.POST)
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
        form = AdvertisementForm(request.POST, instance=advertisement)
        if form.is_valid():
            form.save()
            return redirect('board:advertisement_detail', pk=advertisement.pk)
    else:
        form = AdvertisementForm(instance=advertisement)

    return render(request, 'board/edit_advertisement.html', {'form': form})


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
