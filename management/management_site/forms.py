from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Employee

class SignUpForm(UserCreationForm):
    email = forms.EmailField(label="", widget=forms.TextInput(attrs={'placeholder': 'Email Address'}))
    first_name = forms.CharField(label="", max_length=50, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(label="", max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        tailwind_input = (
            'block w-full rounded-md border border-gray-300 dark:border-gray-600 '
            'bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white '
            'placeholder-gray-400 dark:placeholder-gray-400 focus:outline-none focus:ring-2 '
            'focus:ring-blue-500 focus:border-blue-500'
        )

        for name, field in self.fields.items():
            field.label = ''
            field.widget.attrs['class'] = tailwind_input

        self.fields['username'].widget.attrs['placeholder'] = 'User Name'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'

        self.fields['username'].help_text = (
            'Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'
        )
        self.fields['password1'].help_text = (
            "Your password must contain at least 8 characters, can't be too similar to your other personal information, \n"
            "can't be a commonly used password, and can't be entirely numeric."
        )
        self.fields['password2'].help_text = (
            'Enter the same password as before, for verification.'
        )

class AddRecordForm(forms.ModelForm):
    first_name = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder": "First Name"}), label="")
    last_name = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder": "Last Name"}), label="")
    email = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder": "Email"}), label="")
    phone = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder": "Phone"}), label="")
    address = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder": "Address"}), label="")
    city = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder": "City"}), label="")
    state = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder": "State"}), label="")
    zipcode = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder": "Zipcode"}), label="")

    class Meta:
        model = Employee
        exclude = ("tenant_id", "created_at")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        tailwind_input = (
            'block w-full rounded-md border border-gray-300 dark:border-gray-600 '
            'bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white '
            'placeholder-gray-400 dark:placeholder-gray-400 focus:outline-none focus:ring-2 '
            'focus:ring-blue-500 focus:border-blue-500'
        )
        for field in self.fields.values():
            field.widget.attrs['class'] = tailwind_input