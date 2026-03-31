from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render

from .forms import CustomerRegisterForm
from .models import CustomerProfile


def login_view(request):
    if request.user.is_authenticated:
        return redirect('catalog:product_list')
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, f'Bienvenido, {user.username}.')
        return redirect(request.GET.get('next', '/'))
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'Sesion cerrada correctamente.')
    return redirect('catalog:product_list')


def register_view(request):
    form = CustomerRegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.email = form.cleaned_data['email']
        user.save()
        CustomerProfile.objects.create(
            user=user,
            zone=form.cleaned_data['zone'],
            sector=form.cleaned_data['sector'],
            default_address=form.cleaned_data['default_address'],
        )
        login(request, user)
        messages.success(request, 'Cuenta creada exitosamente.')
        return redirect('catalog:product_list')
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile_view(request):
    profile, _ = CustomerProfile.objects.get_or_create(user=request.user)
    return render(request, 'accounts/profile.html', {'profile': profile})
