from django.contrib import messages, auth
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, UpdateView

from authapp.forms import UserLoginForm, UserRegisterForm, UserProfilerForm, UserProfileEditForm
from authapp.models import User, UserProfile
from baskets.models import Basket
from mainapp.mixin import BaseClassContextMixin, UserDispatchMixin


class LoginListView(LoginView, BaseClassContextMixin):
    template_name = 'authapp/login.html'
    form_class = UserLoginForm
    title = 'GeekShop - Авторизация'

    # def get(self, request, *args, **kwargs):
    #     if request.user.is_authenticated:
    #         return HttpResponseRedirect(reverse('index'))
    #     return HttpResponseRedirect(reverse('authapp:login'))


class RegisterListView(FormView, BaseClassContextMixin):
    model = User
    template_name = 'authapp/register.html'
    form_class = UserRegisterForm
    title = 'GeekShop - Регистрация'
    success_url = reverse_lazy('auth:login')

    def post(self, request, *args, **kwargs):

        form = self.form_class(data=request.POST)
        if form.is_valid():
            user = form.save()
            user.send_verify_mail()
            messages.set_level(request, messages.SUCCESS)
            messages.success(request, 'Регистрация успешна, ссылка для активации выслана на указанный email!')
            return HttpResponseRedirect(reverse('authapp:login'))
        else:
            messages.set_level(request, messages.ERROR)
            messages.error(request, form.errors)
            return render(request, self.template_name, {'form': form})

    def verify(self, email, activation_key):
        try:
            user = User.objects.get(email=email)
            if user.activation_key == activation_key and not user.is_activation_key_expired():
                user.activation_key = ''
                user.is_active = True
                user.save()
                auth.login(self, user, backend='django.contrib.auth.backends.ModelBackend')
                return render(self, 'authapp/verification.html')
            else:
                print(f'error activation user: {user}')
                return HttpResponseRedirect(reverse('authapp:register'))
        except Exception as e:
            print(f'error activation user: {e.args}')
            return HttpResponseRedirect(reverse('index'))


class ProfileFormView(UpdateView, BaseClassContextMixin, UserDispatchMixin):
    template_name = 'authapp/profile.html'
    form_class = UserProfilerForm
    success_url = reverse_lazy('authapp:profile')
    title = 'GeekShop - Профиль'

    def post(self, request, *args, **kwargs):
        form = UserProfilerForm(request.POST, request.FILES, instance=request.user)
        profile_form = UserProfileEditForm(request.POST, request.FILES,
                                           instance=request.user.userprofile)
        if form.is_valid() and profile_form.is_valid():
            form.save()
            return redirect(self.get_success_url())

    def form_valid(self, form):
        messages.set_level(self.request, messages.SUCCESS)
        messages.success(self.request, "Вы успешно зарегистрировались")
        super().form_valid(form)
        return HttpResponseRedirect(self.get_success_url())

    def get_object(self, *args, **kwargs):
        return get_object_or_404(User, pk=self.request.user.pk)

    def get_context_data(self, **kwargs):
        context = super(ProfileFormView, self).get_context_data(**kwargs)
        context['profile'] = UserProfileEditForm(instance=self.request.user.userprofile)
        return context


class Logout(LogoutView):
    template_name = "mainapp/index.html"


@receiver(post_save, sender=get_user_model())
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.userprofile.save()
