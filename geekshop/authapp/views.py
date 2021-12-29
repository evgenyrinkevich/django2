from django.contrib import messages, auth
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, UpdateView

from authapp.forms import UserLoginForm, UserRegisterForm, UserProfilerForm
from authapp.models import User
from baskets.models import Basket
from mainapp.mixin import BaseClassContextMixin, UserDispatchMixin


class LoginListView(LoginView, BaseClassContextMixin):
    template_name = 'authapp/login.html'
    form_class = UserLoginForm
    title = 'GeekShop - Авторизация'


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
            print(user.activation_key)
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

    def form_valid(self, form):
        messages.set_level(self.request, messages.SUCCESS)
        messages.success(self.request, "Вы успешно зарегистрировались")
        super().form_valid(form)
        return HttpResponseRedirect(self.get_success_url())

    def get_object(self, *args, **kwargs):
        return get_object_or_404(User, pk=self.request.user.pk)


class Logout(LogoutView):
    template_name = "mainapp/index.html"
