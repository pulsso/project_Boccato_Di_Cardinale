from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm


def contact_view(request):
    form = ContactForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, '¡Mensaje enviado! Te responderemos pronto.')
        return redirect('contact:contact')
    return render(request, 'contact/contact.html', {'form': form})