from django.views.generic import ListView, DetailView, CreateView, UpdateView, RedirectView
from django.shortcuts import render,get_object_or_404, redirect
from django.urls import reverse_lazy
from main.models import CustomUser, Toot, Follow, Reply, Like, Retoot
from main.forms import TootForm
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView



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
    usrmodel = CustomUser
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
        return context

class TootUpdateView(UpdateView):
    model = Toot
    template_name = 'toot/toot_edit.html'
    fields = ['content']

class UserDetailView(DetailView):
    model = get_user_model()
    template_name = 'toot/user_detail.html'
    context_object_name = 'user_profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        context['toots'] = Toot.objects.filter(user=user).order_by('-created_at')
        context['following_count'] = user.following.count()
        context['followers_count'] = user.followers.count()
        if self.request.user.is_authenticated:
            context['liked_toots'] = self.request.user.customuser.likes.values_list('toot_id', flat=True)
        return context

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
        # リファラーを使用しない場合はここでリダイレクト先のURLを返す
        return self.request.META.get('HTTP_REFERER', '/')

class RetootCreateView(RedirectView):
    pattern_name = 'toot_detail'

    def get_redirect_url(self, *args, **kwargs):
        user = self.request.user.customuser
        toot = get_object_or_404(Toot, pk=kwargs['pk'])
        Retoot.objects.get_or_create(user=user, toot=toot)
        return super().get_redirect_url(*args, **kwargs)
