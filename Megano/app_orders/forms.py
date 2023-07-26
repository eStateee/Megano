from django import forms


class OrderParamForm(forms.Form):
    first_name = forms.CharField(max_length=100, label="Имя")
    last_name = forms.CharField(max_length=100, label="Фамилия")
    patronymic = forms.CharField(max_length=100, label="Отчество")
    phone = forms.CharField(max_length=12, label="Телефон")
    email = forms.EmailField(label="E-mail")
    password1 = forms.CharField(required=False, label="Пароль")
    password2 = forms.CharField(required=False, label="Подтверждение пароля")

    def password_check(self):
        password1 = self.data.get("password1")
        password2 = self.data.get("password2")
        if password1 != password2:
            return False
        return True

    def clean_password1(self):
        if not self.data.get("password1"):
            return None
        if self.password_check():
            return self.cleaned_data.get("password1")
        else:
            raise forms.ValidationError("Введённые пароли должны совпадать")

    def clean_password2(self):
        if not self.data.get("password1"):
            return None
        if self.password_check():
            return self.cleaned_data.get("password2")
        else:
            raise forms.ValidationError("Введённые пароли должны совпадать")


class OrderDeliveryForm(forms.Form):
    CHOICES = [
        ("ordinary", "ordinary"),
        ("express", "express"),
    ]
    delivery = forms.ChoiceField(choices=CHOICES, label="Тип доставки")
    city = forms.CharField(max_length=25, label="Город")
    address = forms.CharField(max_length=500, label="Адрес")


class OrderPaymentForm(forms.Form):
    CHOICES = [
        ("online", "online"),
        ("someone", "someone"),
    ]
    payment = forms.ChoiceField(choices=CHOICES, label="Способ оплаты")
