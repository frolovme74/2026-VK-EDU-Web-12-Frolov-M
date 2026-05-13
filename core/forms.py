from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from core.models import Profile
from django.contrib.auth import authenticate

class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")
    password_repeat = forms.CharField(widget=forms.PasswordInput, label="Повторите пароль")
    avatar = forms.ImageField(required=False, label="Аватар")

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_password_repeat(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password_repeat']:
            raise forms.ValidationError("Пароли не совпадают")
        validate_password(cd['password'])
        return cd['password_repeat']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()

            profile, created = Profile.objects.get_or_create(user=user)
            
            if self.cleaned_data.get('avatar'):
                profile.avatar = self.cleaned_data['avatar']
                profile.save()
                
        return user
    
    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        
        if avatar:
            if avatar.size > 2 * 1024 * 1024:
                raise forms.ValidationError("Файл слишком большой. Максимальный размер — 2 МБ.")

class LoginForm(forms.Form):
    username = forms.CharField(label="Логин")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError("Неверный логин или пароль")

            self.user_cache = user
        return cleaned_data

class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileSettingsForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar']
        widgets = {
        'avatar': forms.FileInput(attrs={'class': 'form-input-file'}),
        }

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        
        if avatar:
            if avatar.size > 2 * 1024 * 1024:
                raise forms.ValidationError("Файл слишком большой. Максимальный размер — 2 МБ.")
            