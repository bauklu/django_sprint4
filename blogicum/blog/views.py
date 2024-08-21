from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView
from django.http import Http404
from django.core.paginator import Paginator
from django.utils import timezone

from .forms import PostForm, CommentsForm, ProfileForm
from blog.models import Post, Category, Comments
from blog.mixins import OnlyAuthorMixin
from blog.ordered_annotated_posts import get_ordered_annotated_posts


POSTS_PER_PAGE = 10


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    ordering = '-pub_date'
    paginate_by = POSTS_PER_PAGE

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = get_ordered_annotated_posts(Post.filtered_posts.all())
        return queryset


@login_required
def create_post(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    context = {'form': form}
    if form.is_valid():
        instance = form.save(commit=False)
        instance.author = request.user
        instance.save()
        return redirect('blog:profile', instance.author)
    return render(request, 'blog/create.html', context)


@login_required
def edit_post(request, post_id):
    instance = get_object_or_404(Post, pk=post_id)
    if instance.author != request.user:
        return redirect('blog:post_detail', pk=post_id)
    form = PostForm(request.POST or None, instance=instance)
    context = {'form': form}
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', pk=post_id)
    return render(request, 'blog/create.html', context)


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'
    form_class = PostForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instance = get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        form = PostForm(instance=instance)
        context = {'form': form}
        return context
    success_url = reverse_lazy('blog:index')


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = "post"

    def get_context_data(self, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs.get('pk'))
        author = post.author
        if not post.is_published and author != self.request.user:
            raise Http404(
                'Post not found')
        context = super().get_context_data(**kwargs)
        context['form'] = CommentsForm()
        context['comments'] = (
            self.object.comments.select_related('author').
            order_by('created_at')
        )
        return context


def category_posts(request, category):
    template = 'blog/category.html'
    posts = get_ordered_annotated_posts(Post.filtered_posts.all().filter(
        category__slug=category)
    )
    category_obj = get_object_or_404(
        Category, slug=category, is_published=True)
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'category': category_obj,
               'page_obj': page_obj}
    return render(request, template, context)


class ProfileView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    slug_url_kwarg = 'username'
    context_object_name = 'profile'
    ordering = '-pub_date'
    paginate_by = POSTS_PER_PAGE

    def get_queryset(self):
        queryset = super().get_queryset()
        author = self.kwargs['username']
        queryset = get_ordered_annotated_posts(
            queryset.filter(author__username=author))
        if author != self.request.user.username:
            queryset = queryset.filter(
                is_published=True, category__is_published=True
            ).exclude(pub_date__gt=timezone.now())
            return queryset
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User,
            username=self.kwargs.get('username'))
        return context


@login_required
def edit_profile(request):
    instance = get_object_or_404(User, username=request.user.username)
    form = ProfileForm(request.POST or None, instance=instance)
    context = {'form': form}
    if form.is_valid():
        form.save()
        return redirect('blog:profile', request.user.username)
    return render(request, 'blog/user.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentsForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', pk=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    instance = get_object_or_404(Comments, pk=comment_id, post__id=post_id)
    if instance.author != request.user:
        return redirect('blog:post_detail', post_id)
    form = CommentsForm(request.POST or None,
                        instance=instance)
    context = {'form': form,
               'comment': instance}
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', pk=post_id)
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, post_id, comment_id):
    instance = get_object_or_404(Comments, pk=comment_id, post__id=post_id)
    if instance.author != request.user:
        return redirect('blog:post_detail', post_id)
    context = {'comment': instance}
    if request.method == 'POST':
        instance.delete()
        return redirect('blog:post_detail', pk=post_id)
    return render(request, 'blog/comment.html', context)
