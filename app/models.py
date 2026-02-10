from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.text import slugify
from django.conf import settings

# ----- Category -----
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# ----- Product -----
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    brand = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=12, decimal_places=0)  # Giá gốc
    image = models.URLField(blank=True)
    specs = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.name} - {self.brand}"


    class Meta:
        ordering = ['-id']

# ----- Custom User Manager -----
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email phải được nhập")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


# ----- Custom User -----
class CustomUser(AbstractUser):
    username = None  # bỏ username, chỉ dùng email
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # khi tạo superuser chỉ cần email + password

    objects = CustomUserManager()

    def __str__(self):
        return self.email
class Capacity(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="capacities")
    name = models.CharField(max_length=50)

class Color(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="colors")
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True)
class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    capacity = models.ForeignKey(Capacity, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=12, decimal_places=0)




class AccessoryCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Accessory(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    brand = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=12, decimal_places=0)
    image = models.CharField(max_length=200)
    specs = models.JSONField()  # Django sẽ tạo CHECK json_valid trên MySQL 8+
    category = models.ForeignKey(AccessoryCategory, on_delete=models.RESTRICT)

    def __str__(self):
        return self.name
    def get_absolute_url(self):
        return reverse("accessory_detail", args=[self.slug])
class AccessoryColor(models.Model):
    accessory = models.ForeignKey(Accessory, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True)

    def __str__(self):
        return f"{self.accessory.name} - {self.name}"

class AccessoryVariant(models.Model):
    accessory = models.ForeignKey(Accessory, on_delete=models.CASCADE)
    color = models.ForeignKey(AccessoryColor, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=12, decimal_places=0)

    def __str__(self):
        return f"{self.accessory.name} / {self.color.name}"

# Tuỳ chọn: tương thích với sản phẩm
class AccessoryCompatibleProduct(models.Model):
    accessory = models.ForeignKey(Accessory, on_delete=models.CASCADE)
    product = models.ForeignKey('app.Product', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('accessory', 'product')

# ----- Banner -----
class Banner(models.Model):
    title = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='banners/')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or f"Banner {self.id}"

# ----- Order -----
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ xử lý'),
        ('processing', 'Đang xử lý'),
        ('shipped', 'Đã giao'),
        ('delivered', 'Đã nhận'),
        ('cancelled', 'Đã hủy'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=12, decimal_places=0)
    shipping_fee = models.DecimalField(max_digits=12, decimal_places=0, default=0)

    # Shipping information
    full_name = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    district = models.CharField(max_length=50, blank=True, null=True)
    payment_method = models.CharField(max_length=20, choices=[
        ('cod', 'Thanh toán khi nhận hàng'),
        ('bank', 'Chuyển khoản ngân hàng'),
    ], blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} - {self.user.email}"

# ----- OrderItem -----
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    accessory_variant = models.ForeignKey(AccessoryVariant, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=0)  # Giá tại thời điểm mua

    def __str__(self):
        if self.product_variant:
            return f"{self.product_variant.product.name} x{self.quantity}"
        elif self.accessory_variant:
            return f"{self.accessory_variant.accessory.name} x{self.quantity}"
        return f"Item x{self.quantity}"

# ----- Inventory -----
class Inventory(models.Model):
    product_variant = models.OneToOneField(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    accessory_variant = models.OneToOneField(AccessoryVariant, on_delete=models.CASCADE, null=True, blank=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.product_variant:
            return f"Inventory for {self.product_variant.product.name}"
        elif self.accessory_variant:
            return f"Inventory for {self.accessory_variant.accessory.name}"
        return f"Inventory {self.id}"
