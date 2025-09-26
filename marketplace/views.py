from django.db.models.query import QuerySet
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Post, Category, Response

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
    fields = ['title', 'category', 'content', 'price', 'is_active']
    template_name = 'marketplace/edit_post.html'
    context_object_name = 'post'


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
        form.instance.post = Post.objects.get(slug=self.kwargs['slug'])
        return super().form_valid(form)
    
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
    fields = ['title', 'type_post', 'content', 'price', 'category']
    template_name = 'marketplace/create_post.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self) -> str:
        return reverse('post_detail', kwargs={'slug': self.object.slug})
    
