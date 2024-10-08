from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm


class UserCreationForm(BaseUserCreationForm):
    class Meta(BaseUserCreationForm.Meta):
        fields = ('username', 'email', 'first_name', 'last_name',
                  'is_superuser', 'is_staff')
