from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User


class UpdateUserForm(UserChangeForm):
    current_password = forms.CharField(label="Current Password", widget=forms.PasswordInput, required=True)
    new_password = forms.CharField(label="New Password", widget=forms.PasswordInput, required=False)
    confirm_new_password = forms.CharField(label="Confirm New Password", widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = ('username', 'email')

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.instance.check_password(current_password):
            raise forms.ValidationError("현재 비밀번호가 일치하지 않습니다.")
        return current_password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_new_password = cleaned_data.get('confirm_new_password')
        if new_password != confirm_new_password:
            raise forms.ValidationError("새로운 비밀번호와 비밀번호 확인이 일치하지 않습니다.")
        return cleaned_data
