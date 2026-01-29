import re

from PIL.Image import open as img_open
from django.contrib.auth.forms import UserCreationForm, UsernameField, PasswordChangeForm
from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.core.files import File
from django.core.validators import validate_email, EmailValidator
from django.forms import model_to_dict, fields_for_model, ClearableFileInput
from django.forms.widgets import ChoiceWidget, Select
from django.utils.encoding import punycode

from geo_app.models import Profile, Trip

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field, HTML, ButtonHolder, Submit
from django.forms import ClearableFileInput

from geo_app.models import Article, FileUpload


class SignupForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='Обязательно')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class UserPassChangeForm(PasswordChangeForm):
    """ Форма смены пароля пользователя """
    error_messages = {
        'password_mismatch': 'Пароли не совпадают',
        'password_incorrect': "Your old password was entered incorrectly. Please enter it again.",
    }
    old_password = forms.CharField(
        label="Старый пароль",
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'autofocus': True}),
    )
    new_password1 = forms.CharField(
        label="Новый пароль",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
        help_text="<ul><li>Пароль не должен содержать персональные данные</li>"
                  "<li>Пароль должен состоять как минимум из 8 символов</li>"
                  "<li>Пароль не должен быть похож на часто используемые</li>"
                  "<li>Пароль не может состоять только из цифр</li></ul>",
    )
    new_password2 = forms.CharField(
        label="Подтверждение нового пароля",
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )


def replace_form_fields(m1_fields, m2_fields):

    """ Функция, перемещающая поля модели 2 (m2) выше полей модели 1 (m1)
     Создано для правильного порядка полей в форме, содержащей поля двух моделей.
     * вспомогательная функция *
    """

    flds = {}
    for k, v in m1_fields.items():
        if k in m2_fields:
            flds[k] = v
    for k, v in m1_fields.items():
        if k not in m2_fields:
            flds[k] = v
    return flds


class ProfileEditForm(forms.ModelForm):
    """ Форма редактирования данных пользователя """
    class Meta:
        model = Profile
        exclude = ['user', 'status', 'location', 'followers']
        error_messages = {
            'username': {
                'max_length': 'Длина имени пользователя должна составлять не более 36 символов.',
            },
            'email': {
                'invalid': 'Неверный email.',
            },
        }
        help_texts = {
            'avatar': 'Изображение должно быть размером 300х300 пикселей.'
        }
        labels = {
            'gender': 'Пол',
            'avatar': 'Аватарка',
        }

    def __init__(self, instance=None, *args, **kwargs):
        _fields = ('username', 'first_name', 'last_name', 'email')
        _initial = model_to_dict(instance.user, _fields) if instance is not None else {}
        super(ProfileEditForm, self).__init__(initial=_initial, instance=instance, *args, **kwargs)
        self.fields.update(fields_for_model(User, _fields))
        self.fields = replace_form_fields(self.fields, _fields)
        self.fields['username'].required = True
        self.fields['username'].label = 'Никнейм (имя пользователя)'
        self.fields['username'].max_length = 36
        self.fields['username'].help_text = '36 знаков и менее. Допускаются буквы, цифры, символы @/./+/-/_'
        self.fields['first_name'].label = 'Имя'
        self.fields['last_name'].label = 'Фамилия'
        self.fields['email'].required = True
        self.fields['email'].label = 'Email'
        self.fields['gender'].required = False
        self.fields['avatar'].required = False
        self.fields['avatar'].widget.initial_text = 'Текущая'
        self.fields['avatar'].widget.input_text = 'Изменить'
        self.fields['avatar'].widget.clear_checkbox_label = 'Отмена'

    def save(self, *args, **kwargs):
        u = self.instance.user
        u.username = self.cleaned_data['username']
        u.first_name = self.cleaned_data['first_name']
        u.last_name = self.cleaned_data['last_name']
        u.email = self.cleaned_data['email']
        u.save()
        profile = super(ProfileEditForm, self).save(*args, **kwargs)
        return profile

    def clean_avatar(self):
        avatar = self.cleaned_data['avatar']
        img = img_open(avatar)
        img.verify()
        if img.width != 300 or img.height != 300:
            raise ValidationError('Изображение должно быть 300х300 пикселей!')
        return avatar

    def clean_email(self):
        email = self.cleaned_data['email']
        regex = r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)'
        if not re.match(regex, email):
            raise ValidationError('Неверный Email!')
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        if len(username) > 36:
            raise ValidationError('Длина имени пользователя не должна превышать 36 символов!')

        regex = r'^[\w.@+-]+\Z'

        if not re.match(regex, username):
            raise ValidationError('В имени пользователя присутствуют недопустимые символы!')

        return username


class ArticleForm(forms.ModelForm):

    class Meta:
        model = Article
        fields = ['header', 'context', 'files']
        widgets = {
            'files': ClearableFileInput(attrs={'multiple': True, 'id': 'upload'}),
        }

    def __init__(self, *args, **kwargs):
        super(ArticleForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = ''
        self.helper.field_class = ''
        self.helper.layout = Layout(
            Div(
                Field('header', placeholder='Заголовок...'),
                Field('context', placeholder='Текст заметки...'),
                Div(
                    HTML(""" <span> Загрузить фотографии </span> """),
                    Field('files', css_class='upload'),
                    css_class='image-input btn btn-outline-secondary btn-sm'
                ),
                HTML(
                    """
                    <div class="container">
                    <div class="row">
                    <div class="card col-6">
                        <div class="card-header">
                            Текущая геолокации
                        </div>
                        <ul class="list-group list-group-flush">
                            <li class="list-group-item">Полный адрес: <span id="address_loc"></span></li>
                            <li class="list-group-item">Город: <span id="city_loc"></span></li>
                            <li class="list-group-item"> Кординаты объекта: x: <span id="x_loc"></span>, y: <span id="y_loc"></span></li>
                        </ul>
                    </div><br>
                    <div class="card col-6" style="width: 30rem; display:none;" id="choiceTable">
                        <div class="card-header">
                            Выбранная геолокации
                        </div>
                        <ul class="list-group list-group-flush">
                            <li class="list-group-item">Полный адрес: <span id="address_choice"></span></li>
                            <li class="list-group-item">Город: <span id="city_choice"></span></li>
                            <li class="list-group-item"> Кординаты объекта: x: <span id="x_choice"></span>, y: <span id="y_choice"></span></li>
                        </ul>
                    </div>
                    </div>
                    </div>
                    <br>
                    """
                ),
                ButtonHolder(
                    Submit('submit', 'Сохранить'),
                ),
            )
        )


class TripForm(forms.ModelForm):

    class Meta:
        model = Trip
        fields = ['header', 'description']

    def __init__(self, *args, **kwargs):
        super(TripForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = ''
        self.helper.field_class = ''
        self.helper.layout = Layout(
            Div(
                Field('header', placeholder='Заголовок...'),
                Field('description', placeholder='Опишиите вашу поездку...'),
                ButtonHolder(
                    Submit('submit', 'Сохранить'),
                ),
            )
        )