from django.db import models
from django.contrib.auth.models import User


class Advertisement(models.Model):
    """
    Этот класс представляет собой описание модели объявления.
    Описание полей:
    title: заголовок объявления - текстовое поле длиной не более 255 символов;
    content: основная часть рекламы - текстовое поле допускающее большой объем текста;
    author: внешний ключ, связывающий данную модель с моделью User. "on_delete=models.CASCADE" означает,
        что если пользователь удален, то связанные с ним рекламные объявления также удаляются;
    created_at: автоматически устанавливает текущую дату и время при создании объявления;
    image: поле для загрузки изображений, не обязательное. Если изображение не загружено, поле может быть пустым.
        upload_to='advertisements/' определяет индикатор, в котором сохраняются загружаемые изображения.
    """
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='advertisements/', blank=True, null=True)

    def __str__(self):
        """
        Метод, возвращающий строковое представление объекта, отображающее заголовок рекламы.
        """
        return self.title


class Comment(models.Model):
    """
    Класс модели для комментариев:
    advertisement: внешний ключ, связанный с моделью Advertisement;
    related_name='comments' позволяет выполнять запрос комментариев, связанных с рекламой;
    author: внешний ключ, ссылающийся на модель User, аналогичный модели Advertisement;
    content: сохраняет содержимое комментария;
    created_at: автоматически устанавливает текущую дату и время при создании.
    """
    advertisement = models.ForeignKey(Advertisement, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Метод, который возвращает форматированное строковое представление комментария,
        включая автора и связанную с ним рекламу.
        """
        return f'Comment by {self.author} on {self.advertisement}'
