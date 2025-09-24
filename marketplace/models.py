import os
import logging
from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
logger=logging.getLogger('marketplace')


class Category(models.Model):
    """
    Категория товаров.
    Поле: name
    """
    name = models.CharField(max_length=50, verbose_name='Название категории')
    slug = models.SlugField(max_length=80, unique=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Post(models.Model):
    '''
    Модель объявления.
    Поля: title, category, content, price, type_post,
      author, is_active, updated_at, created_at, slug
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

    def delete(self, *args, **kwargs):
        media_files = []
        
        for media in self.media.all():
            if media.file:
                media_files.append(media.file.name)
        
        super().delete(*args, **kwargs)

        for file_path in media_files:
            try:
                if default_storage.exists(file_path):
                    default_storage.delete(file_path)
                    logger.info(f'Файл удалён: {file_path}')
            except Exception as e:
                logger.error(f'Ошибка при удалении {file_path}: {e}')
    

class PostMedia(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='media')
    file = models.FileField(upload_to='post_media/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # Разрешенные типы файлов
    ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    ALLOWED_VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
    ALLOWED_EXTENSIONS = ALLOWED_IMAGE_EXTENSIONS + ALLOWED_VIDEO_EXTENSIONS
    
    # Запрещенные опасные расширения
    DANGEROUS_EXTENSIONS = ['.exe', '.bat', '.cmd', '.sh', '.php', '.js', '.html']
    
    MAX_SIZE_MB = 50

    class Meta:
        verbose_name = 'Медиафайл'
        verbose_name_plural = 'Медиафайлы'

    def delete(self, *args, **kwargs):
        if self.file:
            try:
                if default_storage.exists(self.file.name):
                    default_storage.delete(self.file.name)
            except Exception as e:
                logger.info(f"Ошибка при удалении файла {self.file.name}: {e}")
        super().delete(*args, **kwargs)

    def clean(self):
        if self.file:
            # Проверка размера файла
            if self.file.size > self.MAX_SIZE_MB * 1024 * 1024:
                raise ValidationError(f'Максимальный размер файла: {self.MAX_SIZE_MB} МБ')
            
            # Получаем расширение файла
            file_name = self.file.name.lower()
            extension = os.path.splitext(file_name)[1]
            
            # Проверка на опасные расширения
            if extension in self.DANGEROUS_EXTENSIONS:
                raise ValidationError(f'Загрузка файлов с расширением {extension} запрещена')
            
            # Проверка на разрешенные типы
            if extension not in self.ALLOWED_EXTENSIONS:
                raise ValidationError(f'Разрешены только: {", ".join(self.ALLOWED_EXTENSIONS)}')
            
            # Дополнительная проверка MIME-типа
            content_type = getattr(self.file, 'content_type', '')
            if content_type and not content_type.startswith(('image/', 'video/')):
                raise ValidationError('Файл должен быть изображением или видео')

    def save(self, *args, **kwargs):
        self.clean()
        
        if self.file and not self.pk:
            count = PostMedia.objects.filter(post=self.post).count()
            ext = os.path.splitext(self.file.name)[1].lower()
            new_filename = f"post-{self.post.id}-{count+1:03d}{ext}"
            self.file.name = f'{self.post.id}/{new_filename}'
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Файл для {self.post.title}'


class Response(models.Model):
    """
    Отзывы на товар.
    Поля: author, post, content, created_at, is_accepted
    """
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
        unique_together = ['author', 'post']