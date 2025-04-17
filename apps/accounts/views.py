from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import RegistrationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import redirect

def simple_logout_view(request):
    logout(request)
    return redirect('login')


# def register_view(request):
#     if request.method == 'POST':
#         form = RegistrationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             # Optionally automatically log in the user after registration
#             login(request, user)
#             return redirect('transactions:dashboard')
#     else:
#         form = RegistrationForm()
#     return render(request, 'accounts/register.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Explicitly provide the backend.
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('transactions:dashboard')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})
