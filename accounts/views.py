from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm

# Create your views here.
def signUp (request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            redirect('login')
            messages.success(request, ('Registration successful!'))
            return redirect('home')
    else:

        form = UserCreationForm()

        context= {
            'form':form,
            'title': 'Register'
        }

    return render(request, 'registration/register.html', context)