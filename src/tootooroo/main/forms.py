from django import forms
from main.models import Toot
from main.models import CustomUser
from .models import Reply
from django.contrib.auth.models import User
import re

class TootForm(forms.ModelForm):
    class Meta:
        model = Toot
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5, 'placeholder': '投稿を入力...'}),
        }



class ProfileEditForm(forms.ModelForm):
    username = forms.CharField(label='ユーザーID', max_length=150)
    display_name = forms.CharField(label='表示名', max_length=150)  # 表示名フィールドを追加
    background_color = forms.ChoiceField(label='背景色', choices=CustomUser.BACKGROUND_COLOR_CHOICES)
    
    class Meta:
        model = CustomUser
        fields = ['username', 'display_name', 'bio', 'profile_image', 'background_color','department']
        
    def clean_username(self):
        new_username = self.cleaned_data['username']
        current_username = self.instance.user.username

        if CustomUser.objects.exclude(pk=self.instance.pk).filter(user__username=new_username).exists():
            raise forms.ValidationError('このユーザー名は既に使用されています。別のユーザー名を入力してください。')
        # バリデーション: アルファベット、数字、アンダースコアのみを許可
        if not re.match(r'^[a-zA-Z0-9_]+$', new_username):
            raise forms.ValidationError('ユーザーIDにはアルファベット、数字、アンダースコア(_)のみ使用できます。')

        return new_username

    def __init__(self, *args, **kwargs):
        super(ProfileEditForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['username'].initial = self.instance.user.username

    def save(self, commit=True):
        user = super(ProfileEditForm, self).save(commit=False)
        user.user.username = self.cleaned_data['username']
        user.display_name = self.cleaned_data['display_name']  # display_name を保存
        if commit:
            user.user.save()
            user.save()
        return user
    


class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5, 'placeholder': 'リプライを入力...'}),
        }
        
class BackgroundColorForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['background_color']
        widgets = {
            'background_color': forms.RadioSelect(choices=[
                ('#343a40', 'Dark'),
                ('#007bff', 'Blue'),
                ('#28a745', 'Green'),
                ('#dc3545', 'Red'),
                ('#ffc107', 'Yellow')
            ])
        }