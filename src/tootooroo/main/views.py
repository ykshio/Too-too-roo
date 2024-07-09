from django.views.generic import ListView, DetailView, CreateView, UpdateView, RedirectView, View
from django.shortcuts import render,get_object_or_404, redirect
from django.urls import reverse_lazy
from django.db.models import Count
from main.models import CustomUser, Toot, Follow, Reply, Like, Retoot
from main.forms import TootForm, ProfileEditForm,  ReplyForm
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from .forms import ProfileEditForm
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView
from .models import CustomUser, Toot, Like,Hashtag
from django.views.generic.base import View
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.shortcuts import render


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

    def get_queryset(self):
        sort_option = self.request.GET.get('sort', 'newest')  # デフォルトは新しい順

        if sort_option == 'oldest':
            queryset = Toot.objects.order_by('created_at')
        elif sort_option == 'most_likes':
            # 'likes' という関連名を使用する
            queryset = Toot.objects.annotate(num_likes=Count('likes')).order_by('-num_likes', '-created_at')
        else:
            queryset = Toot.objects.order_by('-created_at')  # デフォルトは新しい順

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = TootForm()
        
        if self.request.user.is_authenticated:
            user = self.request.user.customuser
            liked_toots = Like.objects.filter(user=user).values_list('toot_id', flat=True)
            context['liked_toots'] = liked_toots
            context['following_count'] = user.following.count()
            context['followers_count'] = user.followers.count()
        else:
            context['liked_toots'] = []
            context['following_count'] = 0
            context['followers_count'] = 0
        
        # プロフィール画像を含むユーザー情報をコンテキストに追加
        users = CustomUser.objects.all()
        user_profiles = {user.user.id: user for user in users}
        context['user_profiles'] = user_profiles

        return context

# 変更点のある箇所のみ示します

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
        response = super().form_valid(form)
        form.instance.save()
        return response


class TootDetailView(LoginRequiredMixin, DetailView):
    model = Toot
    template_name = 'toot/toot_detail.html'
    context_object_name = 'toot'
    login_url = '/login/'  # ログインページのURL

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = TootForm()
        context['reply_form'] = ReplyForm()  # ここでReplyFormを追加
        context['replies'] = Reply.objects.filter(toot=self.object)  # ここでリプライを取得

        # いいねしたユーザーのリストを取得してcontextに追加
        likes = self.object.likes.select_related('user')
        context['liked_by_users'] = likes

        if self.request.user.is_authenticated:
            user = self.request.user.customuser
            liked_toots = Like.objects.filter(user=user).values_list('toot_id', flat=True)
            context['liked_toots'] = liked_toots
        else:
            context['liked_toots'] = []

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data()
        reply_form = context['reply_form']
        if reply_form.is_valid():
            reply = reply_form.save(commit=False)
            reply.user = request.user.customuser
            reply.toot = self.object
            reply.save()
            return redirect('toot_detail', pk=self.object.pk)
        return self.render_to_response(context)



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

        # 並び替えオプションを取得
        sort_option = self.request.GET.get('sort', 'newest')  # デフォルトは新しい順

        if sort_option == 'oldest':
            context['toots'] = Toot.objects.filter(user=user_profile).order_by('created_at')
        elif sort_option == 'most_likes':
            context['toots'] = Toot.objects.filter(user=user_profile).annotate(num_likes=Count('likes')).order_by('-num_likes', '-created_at')
        else:
            context['toots'] = Toot.objects.filter(user=user_profile).order_by('-created_at')

        # Tootsの数を取得してcontextに追加
        context['toots_count'] = context['toots'].count()

        if self.request.user.is_authenticated:
            liked_toots = Like.objects.filter(user=user_profile).values_list('toot_id', flat=True)
            context['liked_toots'] = Toot.objects.filter(id__in=liked_toots).order_by('-created_at')
            context['is_following'] = self.request.user.customuser.following.filter(pk=user_profile.pk).exists()
        else:
            context['liked_toots'] = []
            context['is_following'] = False

        # Likesの数を取得してcontextに追加
        context['likes_count'] = Like.objects.filter(toot__user=user_profile).count()

        context['following_count'] = user_profile.following.count()
        context['followers_count'] = user_profile.followers.count()

        # いいねしたユーザーのリストを取得してcontextに追加
        liked_by_users = Like.objects.filter(toot__user=user_profile).select_related('user')
        context['liked_by_users'] = liked_by_users

        return context



class UserLikedTootsView(ListView):
    model = Toot
    template_name = 'toot/user_liked_toots.html'
    context_object_name = 'liked_toots'

    def get_queryset(self):
        user = self.request.user.customuser
        sort_option = self.request.GET.get('sort', 'newest')  # デフォルトは新しい順

        if sort_option == 'oldest':
            liked_toots = Toot.objects.none()  # 空のクエリセットを返す
        else:
            liked_toots = Toot.objects.filter(id__in=user.likes.values_list('toot_id', flat=True)).annotate(num_likes=Count('likes')).order_by('-likes__created_at')

        return liked_toots

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user.customuser
        liked_toots = user.likes.count()  # いいねした投稿の数をカウント
        context['liked_toot_ids'] = user.likes.values_list('toot_id', flat=True)
        context['user_profile'] = user
        context['toots_count'] = liked_toots  # いいねした投稿の数をテンプレートに渡す
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

@login_required
def user_follow(request, pk):
    user_to_follow = get_object_or_404(CustomUser, pk=pk)
    if request.user.is_authenticated:
        follower = request.user.customuser
        Follow.objects.get_or_create(follower=follower, following=user_to_follow)
    return redirect('user_detail', pk=pk)

@login_required
def user_unfollow(request, pk):
    user_to_unfollow = get_object_or_404(CustomUser, pk=pk)
    if request.user.is_authenticated:
        follower = request.user.customuser
        Follow.objects.filter(follower=follower, following=user_to_unfollow).delete()
    return redirect('user_detail', pk=pk)




class UserFollowersView(DetailView):
    model = CustomUser
    template_name = 'toot/user_followers.html'
    context_object_name = 'user_profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_profile = self.get_object()
        followers = Follow.objects.filter(following=user_profile)
        context['followers'] = followers
        return context

class UserFollowingView(DetailView):
    model = CustomUser
    template_name = 'toot/user_following.html'
    context_object_name = 'user_profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_profile = self.get_object()
        following = user_profile.following.all()  # user_profile がフォローしているユーザーのリストを取得する
        context['following'] = following
        return context

    

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


class TootLikesView(ListView):
    template_name = 'toot/toot_likes.html'
    context_object_name = 'likes'

    def get_queryset(self):
        toot = get_object_or_404(Toot, pk=self.kwargs['pk'])
        return Like.objects.filter(toot=toot).select_related('user__user')  # select_relatedでuserをプリフェッチ

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        toot = get_object_or_404(Toot, pk=self.kwargs['pk'])
        context['toot'] = toot
        return context

@require_POST
@login_required
def delete_toot(request, pk):
    toot = get_object_or_404(Toot, pk=pk)
    if request.user.customuser == toot.user:
        toot.delete()
    return redirect('top')

@require_POST
@login_required
def delete_reply(request, pk):
    reply = get_object_or_404(Reply, pk=pk)
    if request.user.customuser == reply.user:
        reply.delete()
    return redirect('toot_detail', pk=reply.toot.pk)



def search(request):
    query = request.GET.get('q')
    toots = Toot.objects.none()

    if query:
        keywords = query.split()

        # 初期化
        content_query = Q()
        user_query = Q()

        for keyword in keywords:
            if keyword.startswith('from:'):
                username = keyword[5:]  # 'from:' の後ろの部分を抽出
                user_query &= Q(user__user__username__icontains=username)
            else:
                content_query |= Q(content__icontains=keyword)

        # AND条件で結合
        if user_query:
            toots = Toot.objects.filter(content_query & user_query)
        else:
            toots = Toot.objects.filter(content_query)

    context = {
        'toots': toots,
        'query': query,
    }
    return render(request, 'toot/search.html', context)



class ReplyCreateView(CreateView):
    model = Reply
    form_class = ReplyForm
    template_name = 'toot/reply_new.html'

    def form_valid(self, form):
        form.instance.user = self.request.user.customuser
        form.instance.toot = get_object_or_404(Toot, pk=self.kwargs['pk'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('toot_detail', kwargs={'pk': self.kwargs['pk']})



class HashtagDetailView(DetailView):
    model = Hashtag
    template_name = 'toot/hashtag_detail.html'
    context_object_name = 'hashtag'

    def get_object(self, queryset=None):
        queryset = Hashtag.objects.all()
        hashtag_id = self.kwargs.get('id')
        hashtag = get_object_or_404(queryset, id=hashtag_id)
        return hashtag

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hashtag = self.object
        context['toots'] = Toot.objects.filter(hashtags__id=hashtag.id)
        return context

from django.shortcuts import get_object_or_404, render
from .models import Toot

def toot_likes(request, toot_id):
    toot = get_object_or_404(Toot, id=toot_id)
    likes = toot.likes.select_related('user')
    return render(request, 'toot/toot_likes.html', {'toot': toot, 'likes': likes})
