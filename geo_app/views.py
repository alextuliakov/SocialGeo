from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt

from geo_app.forms import UserPassChangeForm, TripForm
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.db import transaction
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect

# Create your views here.
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from django_registration.forms import User

from geo_app.forms import SignupForm, ProfileEditForm
from geo_app.models import Profile, Comment, Like, Trip
from geo_app.forms import SignupForm, ArticleForm
from geo_app.models import Article, FileUpload, GeoPoint, GeoObject
from geo_app.tokens import account_activation_token

menu_items = [
    {'url': '/map',
     'header': 'Карта'},

    {'url': '/articles/list',
     'header': 'Заметки'},

    {'url': '/articles/add',
     'header': 'Добавить заметку'},
]

superuser_menu_items = [
    {'url': '/admin',
     'header': 'Админ-панель'},
]

location, pm_location, placemark = None, None, None


def landing(request):
    context = {
        'menu_items': menu_items,
        'superuser_menu_items': superuser_menu_items,
    }
    return render(request, 'landing.html', context)


@login_required(login_url='/accounts/login')
def admin_profile_create(request):
    context = {}
    p = Profile.objects.filter(user=request.user)
    if len(p) == 0:
        if request.user.is_superuser:
            profile = Profile(user=request.user)
            profile.save()
            context['message'] = 'Профиль для вашего админ-аккаунта создан успешно.'
        else:
            context['message'] = 'У вас нет доступа к данной странице.'
    else:
        context['message'] = 'У вас уже создан профиль.'
    return render(request, 'admin_profile_creation.html', context)


class MapView(ListView):
    model = Article
    template_name = 'map.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        data = super(MapView, self).get_context_data(**kwargs)
        data['menu_items'] = menu_items
        data['superuser_menu_items'] = superuser_menu_items
        data['articles'] = Article.objects.all()
        return data


def sign_up(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            p = Profile()
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            p.user = user
            p.save()
            current_site = get_current_site(request)
            mail_subject = 'Activate your blog account.'
            message = render_to_string('acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )
            email
            email.send()
            return HttpResponse('Подтвердите ваш email, чтобы продолжить')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})


@login_required(login_url='/accounts/login')
def my_profile_show(request):
    """ View-функция страницы личного профиля """
    try:
        profile = Profile.objects.get(user=request.user)
        articles = Article.objects.filter(owner=request.user)
        context = {
            'menu_items': menu_items,
            'superuser_menu_items': superuser_menu_items,
            'user': request.user,
            'profile': profile,
            'articles': articles,
        }
        return render(request, 'profile/profile.html', context)
    except User.DoesNotExist:
        return redirect('/profile/admin')


@csrf_exempt
@login_required(login_url='/accounts/login')
def profile_show(request, username):
    """ View-функция страницы чужого профиля """
    try:
        user = User.objects.get(username=username)
        profile = Profile.objects.get(user=user)
        articles = Article.objects.filter(owner=user)
        context = {
            'menu_items': menu_items,
            'superuser_menu_items': superuser_menu_items,
            'user': user,
            'profile': profile,
            'articles': articles,
        }

        if request.method == 'POST':
            if request.POST.get('action') == 'follow':
                usr_profile = Profile.objects.get(user=request.user)
                profile.followers.add(usr_profile)
                profile.save()
                context['subscribe'] = True
            elif request.POST.get('action') == 'unfollow':
                usr_profile = Profile.objects.get(user=request.user)
                profile.followers.remove(usr_profile)
                profile.save()
                context['subscribe'] = False
        else:
            if len(profile.followers.filter(user=request.user)) > 0:
                context['subscribe'] = True
            else:
                context['subscribe'] = False

        return render(request, 'profile/profile.html', context)
    except User.DoesNotExist:
        return redirect('/profile/admin')


class ProfileArticles(ListView):
    model = Article
    template_name = 'profile/profile_articles_map.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        data = super(ProfileArticles, self).get_context_data(**kwargs)
        data['menu_items'] = menu_items
        data['superuser_menu_items'] = superuser_menu_items
        data['articles'] = Article.objects.filter(owner=User.objects.get(username=self.kwargs.get('username')))
        return data


class ProfileArticlesList(ListView):
    model = Article
    template_name = 'profile/profile_articles_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        data = super(ProfileArticlesList, self).get_context_data(**kwargs)
        data['menu_items'] = menu_items
        data['superuser_menu_items'] = superuser_menu_items
        data['articles'] = Article.objects.filter(owner=User.objects.get(username=self.kwargs.get('username')))
        return data


class ArticleDelete(DeleteView):
    model = Article
    template_name = 'articles/article_delete.html'
    success_url = reverse_lazy('geo_app:profilePage')

    def get_context_data(self, **kwargs):
        data = super(ArticleDelete, self).get_context_data(**kwargs)
        data['menu_items'] = menu_items
        return data

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.owner == request.user:
            self.object.delete()
            return HttpResponseRedirect(ArticleDelete.success_url)
        else:
            raise Http404


@login_required(login_url='/accounts/login')
def profile_edit_general(request):
    """ View-функция страницы редактирования профиля """
    context = {}
    if request.method == 'POST':
        profile = Profile.objects.get(user=request.user)
        profile_form = ProfileEditForm(profile, request.POST, request.FILES)
        if profile_form.is_valid():
            if request.FILES != {}:
                profile_form_nosave = profile_form.save(commit=False)
                profile_form_nosave.avatar = request.FILES['avatar']
                profile_form_nosave.save()
            profile_form.save()
            user = User.objects.get(username=profile_form.cleaned_data['username'])
            profile = Profile.objects.get(user=user)
            context = {
                'menu_items': menu_items,
                'user': user,
                'profile': profile,
                'profile_form': profile_form,
                'success': True,
                'err_dict': None,
            }
        else:
            context['err_dict'] = profile_form.errors
            profile = Profile.objects.get(user=request.user)
            profile_form = ProfileEditForm(instance=profile)
            context['menu_items'] = menu_items
            context['superuser_menu_items'] = superuser_menu_items
            context['user'] = request.user
            context['profile'] = profile
            context['profile_form'] = profile_form
            context['success'] = False
    else:
        profile = Profile.objects.get(user=request.user)
        profile_form = ProfileEditForm(instance=profile)
        context = {
            'menu_items': menu_items,
            'superuser_menu_items': superuser_menu_items,
            'user': request.user,
            'profile': profile,
            'profile_form': profile_form,
            'success': False,
            'err_dict': None,
        }
    return render(request, 'profile/profile_edit.html', context)


@login_required(login_url='/accounts/login')
def profile_edit_password(request):
    """ View-функция страницы смены пароля аккаунта """
    profile = Profile.objects.get(user=request.user)
    form = UserPassChangeForm(request.user)
    context = {
        'menu_items': menu_items,
        'superuser_menu_items': superuser_menu_items,
        'user': request.user,
        'profile': profile,
        'form': form,
        'success': False,
        'error': '',
    }
    if request.method == 'POST':
        form = UserPassChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            context['success'] = True
        else:
            context['error'] = 'Введён неверный старый пароль или новый пароль не подтверждён.'
    return render(request, 'profile/profile_edit_password.html', context)


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('/')
    else:
        return HttpResponse('Некорректная ссылка активации!')


def article_add(request):
    global location
    global pm_location
    global placemark
    if request.is_ajax and request.method == 'GET':
        user_x = request.GET.get('user_x')
        user_y = request.GET.get('user_y')
        pm_x = request.GET.get('pm_x')
        pm_y = request.GET.get('pm_y')
        pm_address = request.GET.get('pm_address')
        pm_city = request.GET.get('pm_city')
        if user_x is not None:
            location = GeoPoint(x_coord=float(user_x), y_coord=float(user_y))
            pm_location = GeoPoint(x_coord=float(pm_x), y_coord=float(pm_y))
            placemark = GeoObject(geometry=pm_location, address=str(pm_address), city=str(pm_city))
    if request.method == 'POST':
        pm_location.save()
        location.save()
        placemark.save()
        form = ArticleForm(request.POST)
        files = request.FILES.getlist('files')
        if form.is_valid():
            article = form.save(commit=False)
            article.owner = request.user
            #
            #
            article.location = location
            article.placemark = placemark
            article.save()
            for f in files:
                file_instance = FileUpload(article=article, file=f)
                file_instance.save()
            return HttpResponseRedirect('/map')
    else:
        form = ArticleForm()
    context = {
        'menu_items': menu_items,
        'superuser_menu_items': superuser_menu_items,
        'form': form,
    }
    return render(request, 'articles/article_add.html', context)


class ArticleEdit(UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'articles/article_edit.html'

    def get_context_data(self, **kwargs):
        data = super(ArticleEdit, self).get_context_data(**kwargs)
        data['menu_items'] = menu_items
        data['superuser_menu_items'] = superuser_menu_items
        global location
        global pm_location
        global placemark
        if self.request.is_ajax and self.request.method == 'GET':
            user_x = self.request.GET.get('user_x')
            user_y = self.request.GET.get('user_y')
            pm_x = self.request.GET.get('pm_x')
            pm_y = self.request.GET.get('pm_y')
            pm_address = self.request.GET.get('pm_address')
            pm_city = self.request.GET.get('pm_city')
            if user_x is not None:
                location = GeoPoint(x_coord=float(user_x), y_coord=float(user_y))
                pm_location = GeoPoint(x_coord=float(pm_x), y_coord=float(pm_y))
                placemark = GeoObject(geometry=pm_location, address=str(pm_address), city=str(pm_city))
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        with transaction.atomic():
            location.save()
            pm_location.save()
            placemark.save()
            form.instance.location.delete()
            form.instance.placemark.geometry.delete()
            form.instance.placemark.delete()
            form.instance.owner = self.request.user
            form.instance.placemark = placemark
            form.instance.location = location
            form.instance.save()
            files = self.request.FILES.getlist('files')
            for f in files:
                file_instance = FileUpload(article=form.instance, file=f)
                file_instance.save()
        return super(ArticleEdit, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('geo_app:landing')


class ArticlesList(ListView):
    model = Article
    template_name = 'articles/article_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        data = super(ArticlesList, self).get_context_data(**kwargs)
        data['menu_items'] = menu_items
        data['superuser_menu_items'] = superuser_menu_items
        data['articles'] = Article.objects.all()
        return data


class ArticleDetail(DetailView):
    model = Article
    template_name = 'articles/article.html'

    def get_context_data(self, **kwargs):
        data = super(ArticleDetail, self).get_context_data(**kwargs)
        cur_article = Article.objects.get(id=self.kwargs.get('pk'))
        data['menu_items'] = menu_items
        data['superuser_menu_items'] = superuser_menu_items
        data['article'] = cur_article
        data['comments'] = cur_article.comment_set.order_by('-pub_date')
        try:
            like = Like.objects.get(owner=self.request.user, article=cur_article)
            data['liked'] = True
        except Like.DoesNotExist:
            if self.request.is_ajax and self.request.method == 'GET':
                if not self.request.GET.get('like') is None:
                    like = Like(article=cur_article, owner=self.request.user)
                    like.save()
        if self.request.is_ajax and self.request.method == 'GET':
            if not self.request.GET.get('context') is None:
                context = self.request.GET.get('context')
                comment = Comment(owner=self.request.user, context=context, article=cur_article)
                comment.save()
            if not self.request.GET.get('unlike') is None:
                like = Like.objects.get(article=cur_article, owner=self.request.user)
                like.delete()
            if not self.request.GET.get('delete') is None and self.request.user == cur_article.owner:
                return HttpResponseRedirect('/article/delete'+str(cur_article.id))
        return data


class ProfileStats(ListView):
    model = Article
    template_name = 'profile/profile_stats.html'

    def get_context_data(self, **kwargs):
        data = super(ProfileStats, self).get_context_data(**kwargs)
        cur_article = Article.objects.all()
        data['menu_items'] = menu_items
        data['superuser_menu_items'] = superuser_menu_items
        return data


class ProfileTrips(ListView):
    model = Trip
    template_name = 'profile/profile_trips.html'

    def get_context_data(self, **kwargs):
        data = super(ProfileTrips, self).get_context_data(**kwargs)
        data['menu_items'] = menu_items
        data['superuser_menu_items'] = superuser_menu_items
        return data


def trip_add(request):
    if request.method == 'POST':
        form = TripForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect('/map')
    else:
        form = TripForm()
    context = {
        'menu_items': menu_items,
        'superuser_menu_items': superuser_menu_items,
        'form': form
    }
    return render(request, 'trips/trip_add.html', context)


def chatroom(request, room_name):
    return render(request, 'chat.html', {
        'room_name': room_name
    })
