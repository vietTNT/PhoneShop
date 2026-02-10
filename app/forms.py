from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django import forms
from django.core.exceptions import ValidationError

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Họ và tên'
        }),
        error_messages={
            'required': 'Vui lòng nhập họ và tên.',
            'max_length': 'Họ và tên không được vượt quá 30 ký tự.'
        }
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        }),
        error_messages={
            'required': 'Vui lòng nhập địa chỉ email.',
            'invalid': 'Địa chỉ email không hợp lệ.'
        }
    )
    phone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Số điện thoại'
        }),
        error_messages={
            'max_length': 'Số điện thoại không được vượt quá 15 ký tự.'
        }
    )
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        error_messages={
            'invalid': 'Ngày sinh không hợp lệ.'
        }
    )
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'phone', 'date_of_birth', 'password1', 'password2')
        error_messages = {
            'email': {
                'unique': 'Email này đã được sử dụng.',
            }
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Tùy chỉnh thông báo lỗi cho password
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Mật khẩu'
        })
        self.fields['password1'].error_messages = {
            'required': 'Vui lòng nhập mật khẩu.',
        }
        self.fields['password1'].help_text = 'Mật khẩu tối thiểu 8 ký tự, có ít nhất 1 chữ số và 1 ký tự'
        
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nhập lại mật khẩu'
        })
        self.fields['password2'].error_messages = {
            'required': 'Vui lòng xác nhận mật khẩu.',
        }
        
        # Remove username field if exists
        if 'username' in self.fields:
            del self.fields['username']
    
    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if password1:
            if len(password1) < 8:
                raise ValidationError('Mật khẩu phải có ít nhất 8 ký tự.')
            if password1.isdigit():
                raise ValidationError('Mật khẩu không được chỉ chứa toàn số.')
            if password1.lower() in ['password', '123456789', 'qwerty', 'abc123']:
                raise ValidationError('Mật khẩu này quá phổ biến.')
        return password1
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError('Mật khẩu xác nhận không khớp.')
        return password2
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise ValidationError('Email này đã được sử dụng.')
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Loại bỏ khoảng trắng và ký tự đặc biệt
            phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            if not phone.isdigit():
                raise ValidationError('Số điện thoại chỉ được chứa số.')
            if len(phone) < 10:
                raise ValidationError('Số điện thoại phải có ít nhất 10 chữ số.')
        return phone
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.phone = self.cleaned_data.get('phone', '')
        user.date_of_birth = self.cleaned_data.get('date_of_birth')
        if commit:
            user.save()
        return user

# Product Form (nếu có)
class ProductForm(forms.ModelForm):
    class Meta:
        model = User  # Thay bằng model Product nếu có
        fields = '__all__'

# Custom Authentication Form (nếu cần)
class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Email'
        })
        self.fields['username'].error_messages = {
            'required': 'Vui lòng nhập email.',
        }
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Mật khẩu'
        })
        self.fields['password'].error_messages = {
            'required': 'Vui lòng nhập mật khẩu.',
        }

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise ValidationError('Tài khoản này đã bị vô hiệu hóa.')

# Checkout Form
class CheckoutForm(forms.Form):
    full_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Họ và tên'
        }),
        error_messages={
            'required': 'Vui lòng nhập họ và tên.',
            'max_length': 'Họ và tên không được vượt quá 100 ký tự.'
        }
    )
    phone = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Số điện thoại'
        }),
        error_messages={
            'required': 'Vui lòng nhập số điện thoại.',
            'max_length': 'Số điện thoại không được vượt quá 15 ký tự.'
        }
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        }),
        error_messages={
            'required': 'Vui lòng nhập địa chỉ email.',
            'invalid': 'Địa chỉ email không hợp lệ.'
        }
    )
    address = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Địa chỉ'
        }),
        error_messages={
            'required': 'Vui lòng nhập địa chỉ.',
            'max_length': 'Địa chỉ không được vượt quá 255 ký tự.'
        }
    )
    city = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tỉnh/Thành phố'
        }),
        error_messages={
            'required': 'Vui lòng nhập tỉnh/thành phố.',
            'max_length': 'Tỉnh/thành phố không được vượt quá 50 ký tự.'
        }
    )
    district = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Quận/Huyện'
        }),
        error_messages={
            'required': 'Vui lòng nhập quận/huyện.',
            'max_length': 'Quận/huyện không được vượt quá 50 ký tự.'
        }
    )
    payment_method = forms.ChoiceField(
        choices=[
            ('cod', 'Thanh toán khi nhận hàng'),
            ('bank', 'Chuyển khoản ngân hàng'),
        ],
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        error_messages={
            'required': 'Vui lòng chọn phương thức thanh toán.',
            'invalid_choice': 'Phương thức thanh toán không hợp lệ.'
        }
    )
    notes = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Ghi chú (tùy chọn)',
            'rows': 3
        }),
        error_messages={
            'max_length': 'Ghi chú không được vượt quá 500 ký tự.'
        }
    )

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Loại bỏ khoảng trắng và ký tự đặc biệt
            phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            if not phone.isdigit():
                raise ValidationError('Số điện thoại chỉ được chứa số.')
            if len(phone) < 10:
                raise ValidationError('Số điện thoại phải có ít nhất 10 chữ số.')
        return phone
