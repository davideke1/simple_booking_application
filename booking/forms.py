from django import forms
from .models import CustomUser, Cylinder, Booking


class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)
    role_choices = [
        ('user', 'User'),
        ('delivery', 'Delivery'),
    ]
    role = forms.ChoiceField(label='Role', choices=role_choices, widget=forms.RadioSelect)

    class Meta:
        model = CustomUser
        fields = ('email', 'password1', 'password2', 'role')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        role = self.cleaned_data.get('role')
        if role == 'delivery':
            user.is_delivery = True
        else:
            user.is_delivery = False
        user.is_active = False  # Deactivate until email confirmation
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class CylinderForm(forms.ModelForm):
    class Meta:
        model = Cylinder
        fields = ['type', 'stock']


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['cylinder_type', 'preferred_delivery_date', 'delivery_address']


class AssignDeliveryForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['delivery_person', 'status']


class UpdateDeliveryStatusForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].choices = [('In_Transit', 'In_Transit'), ('Delivered', 'Delivered')]

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        if status not in ['In_Transit', 'Delivered']:
            raise forms.ValidationError("You can only update the delivery status to 'Delivered or In Transit'.")
        return cleaned_data
