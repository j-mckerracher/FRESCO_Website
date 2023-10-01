from django.shortcuts import render

template_dir = 'FRESCO/'


def home(request):
    template = f'{template_dir}home.html'
    return render(request, template)


def about(request):
    template = f'{template_dir}about.html'
    return render(request, template)
