from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from .models import Movie
from .forms import UserRegisterForm
import time   # (اگر اسکریپ نیاز داری، بماند؛ ولی اینجا استفاده نشده)


@cache_page(60 * 5)            # کش ۵ دقیقه بر اساس URL
# @vary_on_cookie                # محتوای متفاوت برای کاربران لاگین/غیرلاگین
def home(request):
    query = request.GET.get('q', '')
    movies = Movie.objects.all()
    if query:
        movies = movies.filter(
            Q(title__icontains=query) | Q(imdb_code__icontains=query)
        )
    paginator = Paginator(movies, 5)          # ۵ فیلم در هر صفحه
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'movies/home.html', {
        'movies': page_obj,
        'query': query,
    })


def movie_detail(request, imdb_code):
    movie = Movie.objects.get(imdb_code=imdb_code)
    return render(request, 'movies/detail.html', {'movie': movie})


def about(request):
    return render(request, 'movies/about.html')


# ---------- احراز هویت ----------
def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'خوش آمدید {user.username}!')
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'movies/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'نام کاربری یا رمز عبور اشتباه است.')
    return render(request, 'movies/login.html')


def logout_view(request):
    logout(request)
    return redirect('home')


def search_suggestions(request):
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse([], safe=False)
    movies = Movie.objects.filter(
        Q(title__icontains=query) | Q(imdb_code__icontains=query)
    )[:8]
    results = [{'title': m.title, 'year': m.year,
                'imdb_code': m.imdb_code, 'rate': m.imdb_rate}
               for m in movies]
    return JsonResponse(results, safe=False)


def test_speed(request):
    return HttpResponse("fast")