from django.conf import settings
from django.db import models
import re
from django.utils.text import slugify
from unidecode import unidecode

class CustomUser(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    created_at = models.DateTimeField('アカウント作成日', auto_now_add=True)
    updated_at = models.DateTimeField('アカウント更新日', auto_now=True)

    def __str__(self):
        return self.user.username

class Hashtag(models.Model):
    name = models.CharField('ハッシュタグ', max_length=255, unique=True)
    slug = models.SlugField('スラッグ', default='', editable=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            cleaned_name = unidecode(self.name)
            base_slug = slugify(cleaned_name.lower())

            slug = base_slug
            num = 1
            while Hashtag.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            
            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Toot(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='toots', verbose_name='投稿者')
    content = models.CharField('内容', max_length=280)
    created_at = models.DateTimeField('投稿日', auto_now_add=True)
    updated_at = models.DateTimeField('更新日', auto_now=True)
    original_toot = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='original_toot_retoots', verbose_name='元のトゥート')
    like_count = models.PositiveIntegerField(default=0)
    hashtags = models.ManyToManyField(Hashtag, blank=True, related_name='toots')

    def __str__(self):
        return self.content
    
    @property
    def reply_count(self):
        return self.replies.count()
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._update_hashtags()

    def _update_hashtags(self):
        hashtags = re.findall(r'#(\w+)', self.content)
        self.hashtags.clear()
        for tag in hashtags:
            hashtag, created = Hashtag.objects.get_or_create(name=tag)
            self.hashtags.add(hashtag)

class Follow(models.Model):
    follower = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='following', verbose_name='フォロワー')
    following = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='followers', verbose_name='フォロー中')
    created_at = models.DateTimeField('フォロー日', auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')

class Reply(models.Model):
    toot = models.ForeignKey(Toot, on_delete=models.CASCADE, related_name='replies', verbose_name='トゥート')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='投稿者')
    content = models.CharField('内容', max_length=280)
    created_at = models.DateTimeField('投稿日', auto_now_add=True)
    updated_at = models.DateTimeField('更新日', auto_now=True)

    def __str__(self):
        return self.content

class Like(models.Model):
    toot = models.ForeignKey(Toot, on_delete=models.CASCADE, related_name='likes', verbose_name='トゥート')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='ユーザー')
    created_at = models.DateTimeField('いいね日', auto_now_add=True)

    class Meta:
        unique_together = ('toot', 'user')

class Retoot(models.Model):
    toot = models.ForeignKey(Toot, on_delete=models.CASCADE, related_name='retoot_retoots', verbose_name='トゥート')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='ユーザー')
    created_at = models.DateTimeField('リトゥート日', auto_now_add=True)

    class Meta:
        unique_together = ('toot', 'user')

