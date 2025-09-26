from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib import messages

from .models import Post, Category, Response, PostMedia
from .forms import PostForm, PostEditForm

class PostView(ListView):
    model = Post
    ordering = '-updated_at'
    template_name = 'marketplace/posts_list.html'
    context_object_name = 'posts'
    paginate_by = 12

    def get_queryset(self):
        queryset = super().get_queryset().filter(is_active=True)
        
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        type_post = self.request.GET.get('type_post')
        if type_post:
            queryset = queryset.filter(type_post=type_post)
        
        price_min = self.request.GET.get('price_min')
        price_max = self.request.GET.get('price_max')
        if price_min:
            queryset = queryset.filter(price__gte=price_min)
        if price_max:
            queryset = queryset.filter(price__lte=price_max)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class MyPostList(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'marketplace/my_post.html'
    context_object_name = 'my_posts'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user).order_by('-updated_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_posts'] = self.get_queryset().count()
        return context


class PostEdit(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostEditForm
    template_name = 'marketplace/edit_post.html'
    context_object_name = 'post'
    
    def get_success_url(self):
        return reverse_lazy('edit_post', kwargs={'slug': self.kwargs['slug']})

    def form_valid(self, form):
        response = super().form_valid(form)
        files = self.request.FILES.getlist('media_files')
        for file in files:
            try:
                PostMedia.objects.create(post=self.object, file=file)
            except Exception as e:
                print(f'Ошибка загрузки файла: {e}. Изменения поста сохранены')

        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['media_files'] = self.object.media.all()
        return context
        

class PostDetailView(DetailView):
    model = Post
    template_name = 'marketplace/post_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем принятые отзывы
        context['responses'] = self.object.post_response.filter(is_accepted=True)
        return context
 

class CreateResponse(LoginRequiredMixin, CreateView):
    model = Response
    fields = ['content']
    template_name = 'marketplace/add_response.html'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, slug=self.kwargs['slug'])
        response = super().form_valid(form)
        self.send_notification_email(form.instance)    
        return response
    
    def send_notification_email(self, response):
        try:
            html_content = render_to_string(
                'marketplace/response_notif.html',
                {'response': response,
                 'post': response.post,
                 'author': response.author,}
            )
            msg = EmailMultiAlternatives(
                subject=f'Новый отзыв к Вашему объявлению "{response.post.title}"',
                body=f'Пользователь {response.author.username} оставил отзыв к Вашему объявлению "{response.post.title}": {response.content}',
                from_email='mmo_marketplace@temp-mail.com',
                to=[response.post.author.email],
            )
            msg.attach_alternative(html_content, 'text/html')
            msg.send()
        except Exception as e:
            print(f'Ошибка отправки письма {e}')
    
    def get_success_url(self):
        return reverse_lazy('post_detail', kwargs={'slug': self.kwargs['slug']})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = Post.objects.get(slug=self.kwargs['slug'])
        return context
    

class CreatePostView(LoginRequiredMixin, CreateView):
    '''
     title, type_post, content, price, category
    '''
    model = Post
    form_class = PostForm
    template_name = 'marketplace/create_post.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        files = self.request.FILES.getlist('media_files')
        for file in files:
            try:
                PostMedia.objects.create(post=self.object, file=file)
            except Exception as e:
                print(f'Ошибка загрузки медиафайлов: {e}. Объявление сохранено.')
        return response
    
    
    def get_success_url(self) -> str:
        return reverse('post_detail', kwargs={'slug': self.object.slug})
    

class DeleteMediaView(LoginRequiredMixin, DeleteView):
    model = PostMedia
    success_url = reverse_lazy('my_posts')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.post.author == request.user:
            self.object.delete()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return super().delete(request, *args, **kwargs)
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Нет прав на удаление'})
            return JsonResponse({'error': 'Нет прав на удаление'}, status=403)
    
    def get_success_url(self):
        return reverse_lazy('edit_post', kwargs={'slug': self.object.post.slug})
    

class ResponseListView(LoginRequiredMixin, ListView):
    model = Response
    template_name = 'marketplace/response_list.html'
    context_object_name = 'responses'
    paginate_by = 15

    def get_queryset(self):
        queryset = Response.objects.filter(post__author=self.request.user)
        post_slug = self.request.GET.get('post')
        if post_slug:
            queryset = queryset.filter(post__slug=post_slug)
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_posts'] = Post.objects.filter(author=self.request.user)
        context['total_responses'] = self.get_queryset().count()
        return context
    

class ResponseUpdateView(LoginRequiredMixin, UpdateView):
    """Принятие/отклонение отзыва"""
    model = Response
    fields = []
    template_name = 'marketplace/response_confirm.html'
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        action = request.POST.get('action')
        
        # Проверяем, что пользователь - автор объявления
        if self.object.post.author != request.user:
            messages.error(request, 'У вас нет прав для управления этим отзывом')
            return self.get_success_url()
        
        if action == 'accept':
            self.object.is_accepted = True
            self.object.save()
            messages.success(request, 'Отзыв принят и теперь виден на странице объявления')
            
            # Отправляем уведомление автору отзыва
            self.send_acceptance_notification(self.object)
            
        elif action == 'reject':
            self.object.is_accepted = False
            self.object.save()
            messages.info(request, 'Отзыв отклонен')
        
        elif action == 'delete':
            post_slug = self.object.post.slug
            self.object.delete()
            messages.warning(request, 'Отзыв удален')
            return redirect('response_list')
        
        return redirect(self.get_success_url())
    
    def send_acceptance_notification(self, response):
        """Отправка уведомления автору отзыва о принятии"""
        try:
            if response.author.email:
                html_content = render_to_string(
                    'marketplace/response_accepted.html',
                    {
                        'response': response,
                        'post': response.post,
                    }
                )
                
                msg = EmailMultiAlternatives(
                    subject=f'Ваш отзыв принят на объявлении "{response.post.title}"',
                    body=f'Автор объявления "{response.post.title}" принял ваш отзыв.',
                    from_email='mmo_marketplace@example.com',
                    to=[response.author.email],
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                
        except Exception as e:
            print(f"Ошибка при отправке уведомления о принятии: {e}")
    
    def get_success_url(self):
        return reverse_lazy('response_list')


class ResponseDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление отзыва"""
    model = Response
    template_name = 'marketplace/response_confirm.html'
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.post.author != request.user:
            messages.error(request, 'У вас нет прав для удаления этого отзыва')
            return redirect('response_list')
        
        self.object.delete()
        messages.success(request, 'Отзыв успешно удален')
        return redirect('response_list')
    
    def get_success_url(self):
        return reverse_lazy('response_list')   