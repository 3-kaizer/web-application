from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Customer


class CustomerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email Address')
    phone = forms.CharField(max_length=20, required=False, label='Phone Number')
    address = forms.CharField(max_length=250, required=False, label='Address')
    city = forms.CharField(max_length=100, required=False, label='City')
    postal_code = forms.CharField(max_length=20, required=False, label='Postal Code')
    country = forms.CharField(max_length=50, required=False, label='Country')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 
                  'phone', 'address', 'city', 'postal_code', 'country']

    def save(self, commit=True):
        user = super().save(commit=True)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            
            # Create Customer profile
            Customer.objects.create(
                user=user,
                email=self.cleaned_data['email'],
                phone=self.cleaned_data.get('phone', ''),
                address=self.cleaned_data.get('address', ''),
                city=self.cleaned_data.get('city', ''),
                postal_code=self.cleaned_data.get('postal_code', ''),
                country=self.cleaned_data.get('country', ''),
            )
        return user