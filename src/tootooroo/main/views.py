from django.views.generic import ListView, DetailView, CreateView, UpdateView, RedirectView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from .models import CustomUser, Toot, Follow, Reply, Like, Retoot

# 既存のビュー
def top(request):
    return render(request, 'toot/top.html')

# 新しいクラスベースのビュー
class TopView(ListView):
    model = Toot
    template_name = 'toot/top.html'
    context_object_name = 'toots'
    ordering = ['-created_at']

class TootCreateView(CreateView):
    model = Toot
    template_name = 'toot/toot_new.html'
    fields = ['content']

    def form_valid(self, form):
        form.instance.user = self.request.user.customuser
        return super().form_valid(form)

class TootDetailView(DetailView):
    model = Toot
    template_name = 'toot/toot_detail.html'

class TootUpdateView(UpdateView):
    model = Toot
    template_name = 'toot/toot_edit.html'
    fields = ['content']

class UserDetailView(DetailView):
    model = CustomUser
    template_name = 'toot/user_detail.html'
    context_object_name = 'user_detail'

class UserUpdateView(UpdateView):
    model = CustomUser
    template_name = 'toot/user_edit.html'
    fields = ['bio', 'profile_image']

class UserFollowView(RedirectView):
    pattern_name = 'user_detail'

    def get_redirect_url(self, *args, **kwargs):
        follower = self.request.user.customuser
        following = get_object_or_404(CustomUser, pk=kwargs['pk'])
        Follow.objects.get_or_create(follower=follower, following=following)
        return super().get_redirect_url(*args, **kwargs)

class UserFollowersView(DetailView):
    model = CustomUser
    template_name = 'toot/user_followers.html'
    context_object_name = 'user_detail'

class UserFollowingView(DetailView):
    model = CustomUser
    template_name = 'toot/user_following.html'
    context_object_name = 'user_detail'

class UserTootsView(ListView):
    model = Toot
    template_name = 'toot/user_toots.html'
    context_object_name = 'toots'

    def get_queryset(self):
        user = CustomUser.objects.get(pk=self.kwargs['pk'])
        return Toot.objects.filter(user=user).order_by('-created_at')

class ReplyCreateView(CreateView):
    model = Reply
    template_name = 'toot/reply_new.html'
    fields = ['content']

    def form_valid(self, form):
        form.instance.user = self.request.user.customuser
        form.instance.toot = get_object_or_404(Toot, pk=self.kwargs['pk'])
        return super().form_valid(form)

class LikeTootView(RedirectView):
    pattern_name = 'toot_detail'

    def get_redirect_url(self, *args, **kwargs):
        user = self.request.user.customuser
        toot = get_object_or_404(Toot, pk=kwargs['pk'])
        Like.objects.get_or_create(user=user, toot=toot)
        return super().get_redirect_url(*args, **kwargs)

class RetootCreateView(RedirectView):
    pattern_name = 'toot_detail'

    def get_redirect_url(self, *args, **kwargs):
        user = self.request.user.customuser
        toot = get_object_or_404(Toot, pk=kwargs['pk'])
        Retoot.objects.get_or_create(user=user, toot=toot)
        return super().get_redirect_url(*args, **kwargs)

