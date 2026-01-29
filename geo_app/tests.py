from django.test import TestCase

from geo_app.forms import ProfileEditForm


class ProfileEditFormTest(TestCase):
    """ Тест формы ProfileEditForm
     (форма редактирования данных пользователя (без пароля))
     """
    def setUp(self):
        pass

    def test_profile_edit_valid_email_1(self):
        test_data = {
            'username': 'AlexTULL',
            'email': '02@gmail.com',
        }
        form = ProfileEditForm(data=test_data)
        self.assertTrue(form.is_valid())

    def test_profile_edit_valid_email_2(self):
        test_data = {
            'username': 'AlexTULL',
            'email': '@gmail.com',
        }
        form = ProfileEditForm(data=test_data)
        self.assertTrue(form.is_valid())

    def test_profile_edit_valid_email_3(self):
        test_data = {
            'username': 'AlexTULL',
            'email': '02@gmail',
        }
        form = ProfileEditForm(data=test_data)
        self.assertTrue(form.is_valid())

    def test_profile_edit_valid_email_4(self):
        test_data = {
            'username': 'AlexTULL',
            'email': '02@gmail.',
        }
        form = ProfileEditForm(data=test_data)
        self.assertTrue(form.is_valid())

    def test_profile_edit_valid_email_5(self):
        test_data = {
            'username': 'AlexTULLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL',
            'email': 'alex02@gmail.com',
        }
        form = ProfileEditForm(data=test_data)
        self.assertTrue(form.is_valid())
