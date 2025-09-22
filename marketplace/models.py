from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название категории')
    slug = models.SlugField(max_length=80, unique=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Post(models.Model):
    '''
    Модель объявления. Основная сущность на сайте.
    '''
    WTS = 'wts'
    WTB = 'wtb'
    POST = [(WTS, 'Продажа'),
            (WTB, 'Покупка')]
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    category = models.ForeignKey(Category, on_delete=models.PROTECT,
                                 related_name='category_posts', verbose_name='Категория')
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    content = models.TextField(verbose_name='Содержание')
    price = models.IntegerField(validators= [MinValueValidator(0)], verbose_name='Цена')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    type_post = models.CharField(max_length=3, choices=POST, blank=False, verbose_name='Тип объявления')
    is_active = models.BooleanField(default=True, verbose_name='Активно')
    slug = models.SlugField(max_length=80, unique=True)

    def __str__(self):
        name_type = dict(self.POST).get(self.type_post, 'Unknown')
        return f'{name_type}: {self.title} (Автор: {self.author.username})'
        
    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'
        ordering = ['-created_at']


class PostMedia(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='media')
    file = models.FileField(upload_to='media/')
    file_type = models.CharField(max_length=10)
    
    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'

class Response(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author_response')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_response')
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_accepted = models.BooleanField(default=False, verbose_name='Принят')
    
    def __str__(self):
        return f'Отклик от {self.author.username} на "{self.post.title}"'
    
    class Meta:
        verbose_name = 'Отклик'
        verbose_name_plural = 'Отклики'
        ordering = ['-created_at']
        unique_together = ['author', 'post']  # Важно!
