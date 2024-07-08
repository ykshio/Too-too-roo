from django.views.generic import ListView, DetailView, CreateView, UpdateView, RedirectView
from django.shortcuts import render,get_object_or_404, redirect
from django.urls import reverse_lazy
from main.models import CustomUser, Toot, Follow, Reply, Like, Retoot
from main.forms import TootForm, ProfileEditForm
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from .forms import ProfileEditForm

from django.shortcuts import get_object_or_404
from django.views.generic import DetailView
from .models import CustomUser, Toot, Like



def root_view(request):
    if request.user.is_authenticated:
        return redirect('top')
    else:
        return redirect('login')
    

@login_required
def top_view(request):
    return redirect('top')


# 既存のビュー
# def top(request):
#     toots = Toot.objects.all()
#     context = {'toots': toots}
#     return render(request, 'toot/top.html',context)

# 新しいクラスベースのビュー
class TopView(ListView):
    model = Toot
    template_name = 'toot/top.html'
    context_object_name = 'toots'
    ordering = ['-created_at']
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = TootForm()
        
        if self.request.user.is_authenticated:
            user = self.request.user.customuser
            liked_toots = Like.objects.filter(user=user).values_list('toot_id', flat=True)
            context['liked_toots'] = liked_toots
        else:
            context['liked_toots'] = []
        
        # プロフィール画像を含むユーザー情報をコンテキストに追加
        users = CustomUser.objects.all()
        user_profiles = {user.user.id: user for user in users}
        context['user_profiles'] = user_profiles

        return context

class TootCreateView(CreateView):
    model = Toot
    form_class = TootForm
    template_name = 'toot/toot_new.html'
    success_url = reverse_lazy('top')

    def form_valid(self, form):
        try:
            form.instance.user = self.request.user.customuser
        except CustomUser.DoesNotExist:
            # Handle the case where CustomUser does not exist by creating it
            custom_user = CustomUser.objects.create(user=self.request.user)
            form.instance.user = custom_user
        return super().form_valid(form)


class TootDetailView(LoginRequiredMixin, DetailView):
    model = Toot
    template_name = 'toot/toot_detail.html'
    context_object_name = 'toot'
    login_url = '/login/'  # ログインページのURL

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = TootForm()
        if self.request.user.is_authenticated:
            user = self.request.user.customuser
            liked_toots = Like.objects.filter(user=user).values_list('toot_id', flat=True)
            context['liked_toots'] = liked_toots
        else:
            context['liked_toots'] = []
        return context


class TootUpdateView(UpdateView):
    model = Toot
    template_name = 'toot/toot_edit.html'
    fields = ['content']


class UserDetailView(DetailView):
    model = CustomUser
    template_name = 'toot/user_detail.html'
    context_object_name = 'user_profile'

    def get_object(self):
        return get_object_or_404(CustomUser, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_profile = self.get_object()
        
        # ログインユーザーがいいねした投稿の一覧を取得する
        if self.request.user.is_authenticated:
            liked_toots = Like.objects.filter(user=self.request.user.customuser).values_list('toot_id', flat=True)
            context['liked_toots'] = liked_toots
            context['is_following'] = self.request.user.customuser.following.filter(pk=user_profile.pk).exists()
        else:
            context['liked_toots'] = []
            context['is_following'] = False
        
        # その他のコンテキストデータの取得
        context['toots'] = Toot.objects.filter(user=user_profile).order_by('-created_at')
        context['following_count'] = user_profile.following.count()
        context['followers_count'] = user_profile.followers.count()

        return context


class UserLikedTootsView(ListView):
    model = Toot
    template_name = 'toot/user_liked_toots.html'
    context_object_name = 'liked_toots'

    def get_queryset(self):
        user = self.request.user.customuser
        liked_toots = Like.objects.filter(user=user).values_list('toot_id', flat=True)
        return Toot.objects.filter(id__in=liked_toots).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_profile'] = self.request.user.customuser
        return context
    


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = ProfileEditForm
    template_name = 'toot/user_edit.html'
    success_url = reverse_lazy('user_detail')

    def get_object(self):
        return get_object_or_404(CustomUser, pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse_lazy('user_detail', kwargs={'pk': self.object.pk})
    
    

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

class LikeTootView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        user = self.request.user.customuser
        toot = get_object_or_404(Toot, pk=kwargs['pk'])
        like, created = Like.objects.get_or_create(user=user, toot=toot)
        if created:
            toot.like_count += 1
        else:
            toot.likes.filter(user=user).delete()
            toot.like_count -= 1
        toot.save()
        referer_url = self.request.META.get('HTTP_REFERER', '/')
        return f"{referer_url}#toot-{toot.id}"

class RetootCreateView(RedirectView):
    pattern_name = 'toot_detail'

    def get_redirect_url(self, *args, **kwargs):
        user = self.request.user.customuser
        toot = get_object_or_404(Toot, pk=kwargs['pk'])
        Retoot.objects.get_or_create(user=user, toot=toot)
        return super().get_redirect_url(*args, **kwargs)

