from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile
import re

class UserRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label='نام')
    last_name = forms.CharField(max_length=30, required=True, label='نام خانوادگی')
    email = forms.EmailField(required=True, label='ایمیل')
    phone = forms.CharField(max_length=15, required=True, label='شماره تلفن')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'password1', 'password2']

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        # اعتبارسنجی ساده (مثال ایران: 09xxxxxxxxx)
        if not re.match(r'^09\d{9}$', phone):
            raise forms.ValidationError('شماره موبایل معتبر نیست.')
        # یکتا بودن شماره
        if UserProfile.objects.filter(phone=phone).exists():
            raise forms.ValidationError('این شماره قبلاً ثبت شده است.')
        return phone

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            # پروفایل به‌وسیله سیگنال ساخته شده، شماره را ذخیره می‌کنیم
            user.profile.phone = self.cleaned_data['phone']
            user.profile.save()
        return user