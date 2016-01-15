from django.shortcuts import render
from .models import Splendid
from .forms import SplendidForm
from django.shortcuts import redirect
from django.conf import settings

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.

def pack_list(request):
    packs_list = Splendid.objects.all().order_by('-id')

    paginator = Paginator(packs_list, 10) # Show 2 contacts per page

    page = request.GET.get('page')
    try:
        packs = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        packs = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        packs = paginator.page(paginator.num_pages)
    return render(request, 'appsplendid/pack_list.html', {'packs': packs, 'media_url':settings.MEDIA_URL})

def pack_new(request):
    if request.method == "POST":
        form = SplendidForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('appsplendid.views.pack_list')
    else:
        form = SplendidForm()
    return render(request, 'appsplendid/pack_edit.html', {'form': form})


