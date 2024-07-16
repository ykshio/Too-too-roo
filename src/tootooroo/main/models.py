from django.conf import settings
from django.db import models
import re
from django.utils.text import slugify
from unidecode import unidecode
from django.db.models import UniqueConstraint
from PIL import Image

class Department(models.Model):
    name = models.CharField('部署名', max_length=100, unique=True)

    def __str__(self):
        return self.name

class CustomUser(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(max_length=300, blank=True, null=True)
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
    background_color = models.CharField('背景色', max_length=7, choices=BACKGROUND_COLOR_CHOICES, default='#343a40')
    display_name = models.CharField('表示名', max_length=30, default='', blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')

    def __str__(self):
        return f"{self.display_name} @ {self.user.username}" if self.display_name else self.user.username

    def get_display_name(self):
        return self.display_name

    def get_username(self):
        return self.user.username

    def save(self, *args, **kwargs):
        if self.profile_image:
            img = Image.open(self.profile_image)
            img = img.convert('RGB')
            size = min(img.size)
            img = img.crop((0, 0, size, size))
            img = img.resize((300, 300), Image.LANCZOS)
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
        self._notify_followers()
        self._notify_mentions()

    def _update_hashtags(self):
        hashtags = re.findall(r'#(\w+)', self.content)
        self.hashtags.clear()
        for tag in hashtags:
            hashtag, created = Hashtag.objects.get_or_create(name=tag)
            self.hashtags.add(hashtag)

    def _notify_followers(self):
        followers = self.user.followers.all()
        for follower in followers:
            Notification.objects.create(
                user=follower.follower,
                from_user=self.user,
                notification_type=Notification.TOOT,
                toot=self,
                message=f"{self.get_display_name()}が新しいトゥートを投稿しました"
            )

    def _notify_mentions(self):
        mentions = re.findall(r'@(\w+)', self.content)
        for username in mentions:
            try:
                mentioned_user = CustomUser.objects.get(user__username=username)
                Notification.objects.create(
                    user=mentioned_user,
                    from_user=self.user,
                    notification_type=Notification.MENTION,
                    toot=self,
                    message=f"{self.get_display_name()}があなたをメンションしました"
                )
            except CustomUser.DoesNotExist:
                pass
    
    def get_display_name(self):
        return self.user.display_name

    def get_username(self):
        return self.user.user.username

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
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        Notification.objects.create(
            user=self.toot.user,
            from_user=self.user,
            notification_type=Notification.REPLY,
            toot=self.toot,
            message=f"{self.user.get_display_name()}があなたのトゥートに返信しました"
        )
    
    def get_display_name(self):
        return self.user.display_name

    def get_username(self):
        return self.user.user.username

class Like(models.Model):
    toot = models.ForeignKey(Toot, on_delete=models.CASCADE, related_name='likes', verbose_name='トゥート')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='ユーザー')
    created_at = models.DateTimeField('いいね日', auto_now_add=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['toot', 'user'], name='unique_like')
        ]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        Notification.objects.create(
            user=self.toot.user,
            from_user=self.user,
            notification_type=Notification.LIKE,
            toot=self.toot,
            message=f"{self.user.get_display_name()}があなたのトゥートにいいねしました"
        )
    
    def get_display_name(self):
        return self.user.display_name

    def get_username(self):
        return self.user.user.username

class Retoot(models.Model):
    toot = models.ForeignKey(Toot, on_delete=models.CASCADE, related_name='retoot_retoots', verbose_name='トゥート')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='ユーザー')
    created_at = models.DateTimeField('リトゥート日', auto_now_add=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['toot', 'user'], name='unique_retoot')
        ]

class Notification(models.Model):
    TOOT = 'toot'
    REPLY = 'reply'
    LIKE = 'like'
    MENTION = 'mention'
    FOLLOW = 'follow'

    NOTIFICATION_TYPES = [
        (TOOT, 'トゥート'),
        (REPLY, 'リプライ'),
        (LIKE, 'いいね'),
        (MENTION, 'メンション'),
        (FOLLOW, 'フォロー')
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications', verbose_name='通知受信者')
    from_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_notifications', verbose_name='通知送信者')
    notification_type = models.CharField('通知タイプ', max_length=10, choices=NOTIFICATION_TYPES)
    toot = models.ForeignKey(Toot, on_delete=models.CASCADE, related_name='notifications', verbose_name='関連トゥート', null=True, blank=True)
    message = models.CharField('メッセージ', max_length=255, default='')
    is_read = models.BooleanField('既読', default=False)
    created_at = models.DateTimeField('作成日', auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user}への通知: {self.message or '新しい通知'}"
