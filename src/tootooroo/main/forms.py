from django import forms
from main.models import Toot
from main.models import CustomUser
class TootForm(forms.ModelForm):
    class Meta:
        model = Toot
        fields = ['content']



class ProfileEditForm(forms.ModelForm):
    username = forms.CharField(label='ユーザー名', max_length=150)

    class Meta:
        model = CustomUser
        fields = ['username', 'bio', 'profile_image']

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