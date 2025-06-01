from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from .models import Customer, Supplier, Product, Store, SupplierDelivery


class CustomUserCreationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'})
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        # user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone', 'street', 'nif']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
            'street': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección'}),
            'nif': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'NIF'}),
        }

    def save(self, commit=True, user=None):
        customer = super().save(commit=False)
        if user:
            customer.user = user  # 🔹 Vincular el usuario correctamente
        else:
            raise ValueError("No se proporcionó un usuario para el Customer.")

        if commit:
            customer.save()
        return customer


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'phone', 'email', 'street', 'nif']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contacto'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo'}),
            'street': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección'}),
            'nif': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'NIF'}),
        }

    def save(self, commit=True, user=None):
        supplier = super().save(commit=False)
        if user:
            supplier.user = user  # 🔹 Vincular el usuario correctamente
        else:
            raise ValueError("No se proporcionó un usuario para el Supplier.")

        if commit:
            supplier.save()
        return supplier


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuario'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}))


class TransferProductForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        label="Product",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    from_store = forms.ModelChoiceField(
        queryset=Store.objects.all(),
        label="Origin Store",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    to_store = forms.ModelChoiceField(
        queryset=Store.objects.all(),
        label="Destination Stores",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    quantity = forms.IntegerField(
        min_value=1,
        label="Amount to transfer",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantity'})
    )

class SupplierDeliveryForm(forms.ModelForm):
    class Meta:
        model = SupplierDelivery
        fields = ["store", "product", "quantity"]
        widgets = {
            'store': forms.Select(attrs={'class': 'form-control'}),
            'product': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Quantity'}),
        }
