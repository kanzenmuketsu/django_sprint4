from django.utils import timezone

from django.db.models import Count, Q

from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView, View
)
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Category, Comment, Post
from .forms import CommentForm, PostForm, UserForm

from django.shortcuts import get_object_or_404, redirect
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse, reverse_lazy

from blogicum.settings import MAX_POST_IN_PAGE

User = get_user_model()


def get_user_or_none(request):
    return request.user \
        if not request.user.is_anonymous else None


class PaginateMixin(View):
    paginate_by = MAX_POST_IN_PAGE


class CommentMixin(View):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_success_url(self):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return reverse_lazy(
            'blog:post_detail', args=(post.id,)
        )


class CommentISauthorMixin(View):
    def dispatch(self, *args, **kwargs):
        user = get_user_or_none(self.request)
        if not self.get_object().author == user:
            return redirect(
                reverse('blog:post_detail', args=(self.get_object().id,))
            )
        return super().dispatch(*args, **kwargs)


class CommentDeleteView(CommentMixin, CommentISauthorMixin, DeleteView):
    ...


class CommentUpdateView(CommentMixin, CommentISauthorMixin, UpdateView):
    ...


class CommentCreateView(LoginRequiredMixin, CommentMixin, CreateView):
    def form_valid(self, form):
        form.instance.author = self.request.user
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        form.instance.post = post

        return super().form_valid(form)


class ProfileUpdateView(UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_success_url(self):
        return reverse_lazy('blog:profile', args=(self.request.user.username,))

    def get_object(self):
        if self.request.user.is_anonymous:
            raise Http404()
        return self.request.user


class ProfileListView(PaginateMixin, ListView):
    model = User
    template_name = 'blog/profile.html'

    def get_profile(self):
        username = self.kwargs['name']
        return get_object_or_404(User, username=username)

    def get_queryset(self):
        user = get_user_or_none(self.request)

        return Post.objects.filter(
            author__exact=self.get_profile()
        ).filter(
            Q(is_published__exact=True) | Q(author__exact=user)
        ).annotate(comment_count=Count("comment"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_profile()
        return context


class IndexListView(PaginateMixin, ListView):
    model = Post
    template_name = 'blog/index.html'

    def get_queryset(self):
        return Post.objects.filter(
            is_published__exact=True,
            pub_date__date__lte=timezone.now(),
            category__is_published__exact=True
        ).annotate(comment_count=Count("comment"))


class CategoryListView(PaginateMixin, ListView):
    model = Post
    template_name = 'blog/category.html'

    def get_category(self):
        ctg = get_object_or_404(Category, slug=self.kwargs['category_slug'])
        if not ctg.is_published:
            raise Http404()
        return ctg

    def get_queryset(self):
        return Post.objects.select_related('category').filter(
            is_published__exact=True,
            pub_date__date__lte=timezone.now(),
            category__slug__exact=self.kwargs['category_slug']
        ).annotate(comment_count=Count("comment"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_category()
        return context


class DetailPostView(DetailView):
    model = Post
    template_name = "blog/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()

        user = get_user_or_none(self.request)
        post = self.get_object()
        context['comments'] = \
            Comment.objects.filter(
                post_id__exact=self.kwargs['pk']
        )

        if (
            post.is_published
            and post.category.is_published
            and post.pub_date <= timezone.now()
        ) or post.author == user:
            return context
        raise Http404()


class PostMixin(View):
    model = Post
    template_name = 'blog/create.html'


class PostCreateView(LoginRequiredMixin, PostMixin, CreateView):
    form_class = PostForm

    def get_success_url(self):
        return reverse_lazy('blog:profile', args=(self.request.user.username,))

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, PostMixin, UpdateView):
    form_class = PostForm

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', args=(self.get_object().id,))

    def dispatch(self, *args, **kwargs):
        user = get_user_or_none(self.request)
        if not self.get_object().author == user:
            return redirect(
                reverse('blog:post_detail', args=(self.get_object().id,))
            )
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        pk = self.kwargs['pk']
        author = Post.objects.get(pk=pk).author
        if not author == self.request.user:
            return HttpResponseRedirect(f'/posts/{pk}/')
        return super().form_valid(form)


class PostDeleteView(LoginRequiredMixin, PostMixin, DeleteView):
    success_url = reverse_lazy('blog:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = Post.objects.get(pk=self.kwargs['pk'])
        form = PostForm(instance=post)

        context['form'] = form
        return context

    def dispatch(self, *args, **kwargs):
        user = get_user_or_none(self.request)
        if not self.get_object().author == user:
            raise Http404()
        return super().dispatch(*args, **kwargs)
