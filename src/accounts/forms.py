from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import User, EmailActivation, GuestEmail
from .signals import user_logged_in


class GuestForm(forms.ModelForm):
    # email = forms.EmailField()
    class Meta:
        model = GuestEmail
        fields = [
            'email'
        ]

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(GuestForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        # Save the provided password in hashed format
        obj = super(GuestForm, self).save(commit=False)

        if commit:
            obj.save()
            request = self.request
            request.session['guest_email_id'] = obj.id

        return obj


class LoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean(self):
        request = self.request
        data = self.cleaned_data
        email = data.get("email")
        password = data.get("password")
        qs = User.objects.filter(email=email)

        if qs.exists():
            # User email is registered, check active
            not_active = qs.filter(is_active=False)

            if not_active.exists():
                # not active, check email activation
                link = reverse("account:resend-activation")
                reconfirm_msg = """
                    Go to <a href='{resend_link}'>resend confirmation email</a>.
                """.format(resend_link=link)
                confirm_email = EmailActivation.objects.filter(email=email)
                is_confirmable = confirm_email.confirmable().exists()

                if is_confirmable:
                    msg1 = "Please check your email to confirm your account or " + reconfirm_msg.lower()
                    raise forms.ValidationError(mark_safe(msg1))

                email_confirm_exists = EmailActivation.objects.email_exists(email).exists()

                if email_confirm_exists:
                    msg2 = "Email not confirmed. " + reconfirm_msg
                    raise forms.ValidationError(mark_safe(msg2))

                if not is_confirmable and not email_confirm_exists:
                    raise forms.ValidationError("This user is inactive.")

        user = authenticate(request, username=email, password=password)

        if user is None:
            raise forms.ValidationError("Invalid credentials")

        login(request, user)
        self.user = user

        return data

    # def form_valid(self, form):
    #     request = self.request
    #     email = form.cleaned_data.get("email")
    #     password = form.cleaned_data.get("password")
    #     next_ = request.GET.get('next')
    #     next_post = request.POST.get('next')
    #     redirect_path = next_ or next_post or None
    #
    #     if user is not None:
    #         if not user.is_active:
    #             messages.error(request, "Ths user is inactive")
    #             return super(LoginView, self).form_invalid(form)
    #
    #         login(request, user)
    #         user_logged_in.send(user.__class__, instance=user, request=request)
    #
    #         try:
    #             del request.session['guest_email_id']
    #         except:
    #             pass
    #
    #         if is_safe_url(redirect_path, request.get_host()):
    #             return redirect(redirect_path)
    #         else:
    #             return redirect("/")
    #
    #     return super(LoginView, self).form_invalid(form)


class RegisterForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', )

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(RegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])

        user.is_active = False      # Send confirmation email
        # obj = EmailActivation.objects.create(user=user)
        # obj.send_activation_email()

        if commit:
            user.save()
        return user


class ReactivateEmailForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = EmailActivation.objects.email_exists(email)

        if not qs.exists():
            register_link = reverse("password_reset")
            msg = """This email does no exist, 
                would you like to <a href="{link}">register</a>? """.format(link=register_link)

            raise forms.ValidationError(mark_safe(msg))
        return email


class UserDetailChangeForm(forms.ModelForm):
    full_name = forms.CharField(label='Name', required=False, widget=forms.TextInput(attrs={"class": 'form-control'}))

    class Meta:
        model = User
        fields = ['full_name']


class UserAdminCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', )

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserAdminCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_active = False      # Send confirmation email
        if commit:
            user.save()
        return user


class UserAdminChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'password', 'is_active', 'admin')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'admin')
    list_filter = ('admin',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ()}),
        ('Permissions', {'fields': ('admin',)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

