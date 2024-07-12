from django.conf import settings
from django.db import models
import re
from django.utils.text import slugify
from unidecode import unidecode
from django.db.models import UniqueConstraint
from PIL import Image 

class CustomUser(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    created_at = models.DateTimeField('アカウント作成日', auto_now_add=True)
    updated_at = models.DateTimeField('アカウント更新日', auto_now=True)
    BACKGROUND_COLOR_CHOICES = [
        ('#343a40', 'ダークカラー'),
        ('#f8f9fa', 'ライトカラー'),
        ('#007bff', 'ブルー'),
        ('#28a745', 'グリーン'),
        ('#dc3545', 'レッド'),
    ]
    background_color = models.CharField('背景色', max_length=7, choices=BACKGROUND_COLOR_CHOICES, default='#343a40') # デフォルトはダークカラー
    display_name = models.CharField('表示名', max_length=150, default='', blank=True)   # 表示名フィールドを追加、デフォルトは空文字列
    
    def __str__(self):
        return f"{self.display_name} @ {self.user.username}" if self.display_name else self.user.username
    
    def get_display_name(self):
        # ページごとにカスタマイズして取得するロジックを記述
        return self.display_name  # 例: デフォルトでは display_name を返す

    def get_username(self):
        # ページごとにカスタマイズして取得するロジックを記述
        return self.user.username  # 例: デフォルトでは username を返す
    
    def save(self, *args, **kwargs):
        if self.profile_image:
            img = Image.open(self.profile_image)
            img = img.convert('RGB')
            size = min(img.size)  # 小さい方のサイズを取得
            img = img.crop((0, 0, size, size))  # 正方形にトリミング
            img = img.resize((300, 300), Image.LANCZOS)  # LANCZOSに変更
            img.save(self.profile_image.path)

        super(CustomUser, self).save(*args, **kwargs)

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
        return f"{self.get_display_name()} @ {self.get_username()}: {self.content}"
    
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
    
    def get_display_name(self):
        # ページごとにカスタマイズして取得するロジックを記述
        return self.user.display_name  # 例: デフォルトでは display_name を返す

    def get_username(self):
        # ページごとにカスタマイズして取得するロジックを記述
        return self.user.user.username  # 例: デフォルトでは username を返す

class Follow(models.Model):
    follower = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='following', verbose_name='フォロワー')
    following = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='followers', verbose_name='フォロー中')
    created_at = models.DateTimeField('フォロー日', auto_now_add=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['follower', 'following'], name='unique_follow')
        ]


class Reply(models.Model):
    toot = models.ForeignKey(Toot, on_delete=models.CASCADE, related_name='replies', verbose_name='トゥート')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='投稿者')
    content = models.CharField('内容', max_length=280)
    created_at = models.DateTimeField('投稿日', auto_now_add=True)
    updated_at = models.DateTimeField('更新日', auto_now=True)

    def __str__(self):
        return self.content
    
    def get_display_name(self):
        # ページごとにカスタマイズして取得するロジックを記述
        return self.user.display_name  # 例: デフォルトでは display_name を返す

    def get_username(self):
        # ページごとにカスタマイズして取得するロジックを記述
        return self.user.user.username  # 例: デフォルトでは username を返す

class Like(models.Model):
    toot = models.ForeignKey(Toot, on_delete=models.CASCADE, related_name='likes', verbose_name='トゥート')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='ユーザー')
    created_at = models.DateTimeField('いいね日', auto_now_add=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['toot', 'user'], name='unique_like')
        ]
    
    def get_display_name(self):
        # ページごとにカスタマイズして取得するロジックを記述
        return self.user.display_name  # 例: デフォルトでは display_name を返す

    def get_username(self):
        # ページごとにカスタマイズして取得するロジックを記述
        return self.user.user.username  # 例: デフォルトでは username を返す

class Retoot(models.Model):
    toot = models.ForeignKey(Toot, on_delete=models.CASCADE, related_name='retoot_retoots', verbose_name='トゥート')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='ユーザー')
    created_at = models.DateTimeField('リトゥート日', auto_now_add=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['toot', 'user'], name='unique_retoot')
        ]
