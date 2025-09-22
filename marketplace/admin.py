from django.contrib import admin
from .models import Category, Post, PostMedia, Response

class PostMediaInline(admin.TabularInline):
    model = PostMedia
    extra = 1
    fields = ['file']
    readonly_fields = ['uploaded_at']

class ResponseInline(admin.TabularInline):
    model = Response
    extra = 0  # Не показывать пустые формы для новых отзывов
    fields = ['author', 'content', 'created_at', 'is_accepted']
    readonly_fields = ['author', 'content', 'created_at']  # Только is_accepted можно редактировать
    classes = ['collapse'] #Сворачивается блок с отзывами

    def has_add_permission(self, request, obj=None):
        # Запрещаем добавлять отзывы через админку (они создаются через сайт)
        return False

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['author', 'category', 'title', 'price', 'type_post', 'is_active', 'updated_at']
    list_filter = ['category', 'type_post', 'is_active', 'updated_at']
    #search_fields = ['category', 'author', 'type_post']
    list_editable = ['price', 'is_active']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [PostMediaInline, ResponseInline]