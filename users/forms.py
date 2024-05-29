from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User


# 회원정보 수정을 위한 Form
class UpdateUserForm(UserChangeForm):
    # 현재 비밀번호 일치해야 수정 가능
    current_password = forms.CharField(label="Current Password", widget=forms.PasswordInput, required=True)

    # 새로운 비밀번호, 확인용 비밀번호는 입력 필수 아님
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
        if len(cleaned_data.get('username')) < 8:
            raise forms.ValidationError("아이디는 8자 이상이어야 합니다.")
        
        if new_password :
            if new_password != confirm_new_password:
                raise forms.ValidationError("새로운 비밀번호와 비밀번호 확인이 일치하지 않습니다.")
            elif len(new_password) < 8:
                raise forms.ValidationError("새로운 비밀번호는 8자 이상이어야 합니다.")
        
        return cleaned_data
