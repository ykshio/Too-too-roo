from django import forms
from main.models import Toot
from main.models import CustomUser
from .models import Reply
class TootForm(forms.ModelForm):
    class Meta:
        model = Toot
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5, 'placeholder': '投稿を入力...'}),
        }



class ProfileEditForm(forms.ModelForm):
    username = forms.CharField(label='ユーザー名', max_length=150)
    background_color = forms.ChoiceField(label='背景色', choices=CustomUser.BACKGROUND_COLOR_CHOICES)
    
    class Meta:
        model = CustomUser
        fields = ['username', 'bio', 'profile_image', 'background_color']

    def __init__(self, *args, **kwargs):
        super(ProfileEditForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['username'].initial = self.instance.user.username

    def save(self, commit=True):
        user = super(ProfileEditForm, self).save(commit=False)
        user.user.username = self.cleaned_data['username']
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