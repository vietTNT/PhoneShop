from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import CustomUserCreationForm, ProductForm, CheckoutForm
from django.db import transaction
from django.http import HttpResponse
from .models import Product, Category
from django.http import JsonResponse
from .models import ProductVariant
from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Min
from .models import Accessory, AccessoryCategory, AccessoryColor, AccessoryVariant
from itertools import chain
from django.core.paginator import Paginator
from django.db.models import Value, CharField, F, Q
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Order, OrderItem, Inventory
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
import random
import string
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model

# Thêm dòng này
User = get_user_model()

# def home(request):
#     new_products = Product.objects.all().order_by('-id')[:12]  # lấy 12 sản phẩm mới nhất
#     return render(request, 'home.html', {'new_products': new_products})
from django.utils import timezone

def home(request):
    # Only redirect admin users to admin dashboard if they are explicitly accessing the home page
    # and not coming from a login redirect
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser) and not request.GET.get('next'):
        return redirect('shop:admin_dashboard')

    news_list = [
        {
            "title": "iPhone 16 ra mắt: chip mới, pin lớn hơn",
            "url": "https://vnexpress.net/iphone-16-ra-mat-chip-moi-pin-lon-hon-4771234.html",
            "source": "VNExpress",
            "thumb": "https://picsum.photos/seed/iphone/120/80",
            "published_at": timezone.now(),
        },
        {
            "title": "Samsung giới thiệu One UI 6.1 mới",
            "url": "https://genk.vn/samsung-ra-mat-one-ui-6-1-20240912084529582.chn",
            "source": "GenK",
            "thumb": "https://picsum.photos/seed/samsung/120/80",
            "published_at": timezone.now(),
        },
        {
            "title": "Top điện thoại đáng mua tháng này",
            "url": "https://tinhte.vn/thread/top-dien-thoai-dang-mua-thang-9-2024.1234567/",
            "source": "Tinh Tế",
            "thumb": "https://picsum.photos/seed/phone/120/80",
            "published_at": timezone.now(),
        },
    ]
    ctx = {
        "new_products": Product.objects.all().order_by('name', '-id')[:12],
        "featured_accessories": Accessory.objects.all().annotate(min_variant_price=Min("accessoryvariant__price")).order_by('-id')[:8],
        "news_list": news_list,
    }
    return render(request, "home.html", ctx)




def product_list(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    q = request.GET.get('q')
    brand = request.GET.get('brand')
    sort = request.GET.get('sort')

    if q:
        products = products.filter(name__icontains=q)
    if brand:
        products = products.filter(brand__iexact=brand)
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')

    ctx = {
        'products': products,
        'categories': categories,
        'page_obj': None,  # sau này dùng Paginator
    }
    return render(request, 'products/list.html', ctx)




def product_detail(request, slug):
    from .models import Product
    product = Product.objects.filter(slug=slug).first()
    if not product:
        from django.http import Http404
        raise Http404('Không tìm thấy sản phẩm')
    related = Product.objects.filter(brand=product.brand).exclude(slug=slug)[:4]
    return render(request, 'products/detail.html', {'product': product, 'related': related})


from django.shortcuts import get_object_or_404
from .models import Product, ProductVariant

# def add_to_cart(request):
#     product_id = request.POST.get("product_id")
#     capacity_id = request.POST.get("capacity_id")
#     color_id = request.POST.get("color_id")
#     quantity = int(request.POST.get("quantity", 1))

#     # Kiểm tra variant
#     variant = get_object_or_404(
#         ProductVariant,
#         product_id=product_id,
#         capacity_id=capacity_id,
#         color_id=color_id
#     )

#     cart = request.session.get("cart", {})

#     key = f"{product_id}-{capacity_id}-{color_id}"
#     if key in cart:
#         cart[key]["quantity"] += quantity
#     else:
#         cart[key] = {
#             "product_id": product_id,
#             "name": variant.product.name,
#             "capacity": variant.capacity.value if variant.capacity else "",
#             "color": variant.color.name if variant.color else "",
#             "price": float(variant.price),
#             "quantity": quantity,
#             "image": variant.product.image.url if variant.product.image else "",
#         }

#     request.session["cart"] = cart
#     request.session.modified = True

#     return JsonResponse({"success": True, "cart_count": sum(item["quantity"] for item in cart.values())})
def add_to_cart(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        capacity_id = request.POST.get("capacity_id")
        color_id = request.POST.get("color_id")
        quantity = int(request.POST.get("quantity", 1))

        variant = get_object_or_404(
            ProductVariant,
            product_id=product_id,
            capacity_id=capacity_id,
            color_id=color_id
        )

        cart = request.session.get("cart", {})

        key = f"{product_id}-{capacity_id}-{color_id}"
        if key in cart:
            cart[key]["quantity"] += quantity
        else:
            cart[key] = {
                "name": variant.product.name,
                "capacity": variant.capacity.name if variant.capacity else "",
                "color": variant.color.name if variant.color else "",
                "price": float(variant.price),
                "quantity": quantity,
                "image": variant.product.image if variant.product.image else "",
                "key": key,
            }

        request.session["cart"] = cart
        request.session.modified = True

        return JsonResponse({
            "success": True,
            "cart_count": sum(item["quantity"] for item in cart.values())
        })

    return JsonResponse({"success": False})


# def cart_view(request):
#     # Giỏ hàng mẫu: lấy 2 sản phẩm đầu tiên từ database (nếu có)
#     products = list(Product.objects.all()[:2])
#     items = []
#     if len(products) > 0:
#         items.append({'id': products[0].id, 'name': products[0].name, 'price': products[0].price, 'qty': 1, 'total': products[0].price})
#     if len(products) > 1:
#         items.append({'id': products[1].id, 'name': products[1].name, 'price': products[1].price, 'qty': 2, 'total': 2 * products[1].price})
#     subtotal = sum(i['total'] for i in items)
#     shipping = 30000 if subtotal < 5000000 else 0
#     total = subtotal + shipping
#     return render(request, 'cart/cart.html', {
#         'items': items,
#         'subtotal': subtotal,
#         'shipping': shipping,
#         'total': total,
#     })
from django.views.decorators.http import require_POST

@require_POST
def update_cart(request):
    product_key = request.POST.get("id")  # key lưu trong session (product_id-capacity-color)
    action = request.POST.get("action")   # plus / minus / remove

    cart = request.session.get("cart", {})

    if product_key in cart:
        if action == "plus":
            cart[product_key]["quantity"] += 1
        elif action == "minus":
            cart[product_key]["quantity"] -= 1
            if cart[product_key]["quantity"] <= 0:
                del cart[product_key]
        elif action == "remove":
            del cart[product_key]

    request.session["cart"] = cart
    request.session.modified = True

    # Tính lại tổng
    subtotal = sum(item["price"] * item["quantity"] for item in cart.values())
    shipping = 30000 if subtotal < 5000000 else 0
    total = subtotal + shipping

    return JsonResponse({
        "cart_count": sum(item["quantity"] for item in cart.values()),
        "subtotal": subtotal,
        "shipping": shipping,
        "total": total,
    })

def cart_view(request):
    cart = request.session.get("cart", {})
    items = []
    subtotal = 0
    for key, item in cart.items():
        total = item["price"] * item["quantity"]
        subtotal += total
        items.append({
            **item,
            "total": total
        })
    shipping = 30000 if subtotal < 5000000 else 0
    total = subtotal + shipping
    return render(request, "cart/cart.html", {
        "items": items,
        "subtotal": subtotal,
        "shipping": shipping,
        "total": total,
    })



@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order.objects.select_related('user'), id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order).select_related('product_variant__product')
    return render(request, 'checkout/order_success.html', {
        'order': order,
        'order_items': order_items,
    })

@login_required
def checkout_view(request):
    cart = request.session.get("cart", {})
    if not cart:
        messages.warning(request, 'Giỏ hàng của bạn đang trống. Vui lòng thêm sản phẩm trước khi thanh toán.')
        return redirect('shop:cart')

    # Tính toán giỏ hàng
    items = []
    subtotal = 0
    for key, item in cart.items():
        total = item["price"] * item["quantity"]
        subtotal += total
        items.append({
            **item,
            "total": total
        })
    shipping = 30000 if subtotal < 5000000 else 0
    total = subtotal + shipping

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Tạo đơn hàng
                    order = Order.objects.create(
                        user=request.user,
                        full_name=form.cleaned_data['full_name'],
                        phone=form.cleaned_data['phone'],
                        email=form.cleaned_data['email'],
                        address=form.cleaned_data['address'],
                        city=form.cleaned_data['city'],
                        district=form.cleaned_data['district'],
                        payment_method=form.cleaned_data['payment_method'],
                        notes=form.cleaned_data.get('notes', ''),
                        total_amount=total,
                        shipping_fee=shipping,
                        status='pending'
                    )

                    # Tạo chi tiết đơn hàng
                    for key, item in cart.items():
                        # Tách key để lấy product_id, capacity_id, color_id
                        parts = key.split('-')
                        if len(parts) == 3:
                            product_id, capacity_id, color_id = parts
                            try:
                                variant = ProductVariant.objects.get(
                                    product_id=product_id,
                                    capacity_id=capacity_id,
                                    color_id=color_id
                                )
                                OrderItem.objects.create(
                                    order=order,
                                    product_variant=variant,
                                    quantity=item['quantity'],
                                    price=item['price']
                                )
                            except ProductVariant.DoesNotExist:
                                # Nếu không tìm thấy variant, bỏ qua hoặc xử lý lỗi
                                pass

                    # Xóa giỏ hàng sau khi đặt hàng thành công
                    request.session['cart'] = {}
                    request.session.modified = True

                    # Gửi thông báo thành công
                    messages.success(request, f'Đặt hàng thành công! Mã đơn hàng của bạn là #{order.id}. Chúng tôi sẽ liên hệ với bạn sớm nhất có thể.')

                    # Chuyển hướng đến trang xác nhận đơn hàng
                    return redirect('shop:order_success', order_id=order.id)

            except Exception as e:
                messages.error(request, f'Có lỗi xảy ra khi đặt hàng: {str(e)}')
        else:
            # Hiển thị lỗi validation
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        # Pre-fill form với thông tin user nếu có
        initial_data = {}
        if request.user.first_name:
            initial_data['full_name'] = request.user.first_name
        if hasattr(request.user, 'phone') and request.user.phone:
            initial_data['phone'] = request.user.phone
        if request.user.email:
            initial_data['email'] = request.user.email

        form = CheckoutForm(initial=initial_data)

    return render(request, 'checkout/checkout.html', {
        'form': form,
        'items': items,
        'subtotal': subtotal,
        'shipping': shipping,
        'total': total,
    })
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import CustomUserCreationForm

def signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                messages.success(request, 'Đăng ký tài khoản thành công! Chào mừng bạn đến với PhoneShop.')
                return redirect('shop:home')
            except Exception as e:
                messages.error(request, f'Có lỗi xảy ra: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        form = CustomUserCreationForm()
    return render(request, "registration/signup.html", {"form": form})

def get_price(request):
    product_id = request.GET.get("product")
    capacity_id = request.GET.get("capacity")
    color_id = request.GET.get("color")

    try:
        variant = ProductVariant.objects.get(
            product_id=product_id,
            capacity_id=capacity_id,
            color_id=color_id
        )
        return JsonResponse({"price": int(variant.price)})
    except ProductVariant.DoesNotExist:
        return JsonResponse({"price": 0})
    
# phần phụ kiện

# def accessory_list(request):
#     cat_slug = request.GET.get("cat", "")
#     brand = request.GET.get("brand")
#     q = request.GET.get("q", "")
#     sort = request.GET.get("sort", "")  # price_asc | price_desc | new

#     # categories = AccessoryCategory.objects.all().order_by("name")

#     # items = Accessory.objects.all().select_related("category")
#     items = Accessory.objects.all()
#     categories = AccessoryCategory.objects.all()
#     if cat_slug:
#         items = items.filter(category__slug=cat_slug)
#     if brand:
#         items = items.filter(brand__iexact=brand)
#     if q:
#         items = items.filter(
#             Q(name__icontains=q) | Q(brand__icontains=q) | Q(specs__icontains=q)
#         )

#     # # Lấy giá hiển thị mặc định = min giá trong các variant (nếu có), còn không thì lấy price
#     items = items.annotate(min_variant_price=Min("accessoryvariant__price"))
#     items = Accessory.objects.all()

#     brands = Accessory.objects.values_list("brand", flat=True).distinct().order_by("brand")



#     if sort == "price_asc":
#         items = items.order_by("min_variant_price", "price")
#     elif sort == "price_desc":
#         items = items.order_by("-min_variant_price", "-price")
#     elif sort == "new":
#         items = items.order_by("-id")
#     else:
#         items = items.order_by("name")

#     ctx = {
#         "categories": categories,
#         "items": items,
#         "active_cat": cat_slug,
#         "brands": brands,
#         "active_brand": brand,
#         "q": q,
#         "sort": sort,
#     }
#     return render(request, "products/accessories_list.html", ctx)
def accessory_list(request):
    cat_slug = request.GET.get("cat", "")
    brand = request.GET.get("brand")
    q = request.GET.get("q", "")
    sort = request.GET.get("sort", "")  # price_asc | price_desc | new

    items = Accessory.objects.all()
    categories = AccessoryCategory.objects.all()

    if cat_slug:
        items = items.filter(category__slug=cat_slug)
    if brand:
        items = items.filter(brand__iexact=brand)
    if q:
        items = items.filter(
            Q(name__icontains=q) | Q(brand__icontains=q) | Q(specs__icontains=q)
        )

    # Thêm giá thấp nhất của variant
    items = items.annotate(min_variant_price=Min("accessoryvariant__price"))

    # Sắp xếp
    if sort == "price_asc":
        items = items.order_by("min_variant_price", "price")
    elif sort == "price_desc":
        items = items.order_by("-min_variant_price", "-price")
    elif sort == "new":
        items = items.order_by("-id")
    else:
        items = items.order_by("name")

    # Danh sách hãng
    brands = Accessory.objects.values_list("brand", flat=True).distinct().order_by("brand")

    ctx = {
        "categories": categories,
        "items": items,
        "active_cat": cat_slug,
        "brands": brands,
        "active_brand": brand,
        "q": q,
        "sort": sort,
    }
    return render(request, "products/accessories_list.html", ctx)

def accessory_detail(request, slug):
    acc = get_object_or_404(
        Accessory.objects.select_related("category"),
        slug=slug
    )

    # Lấy toàn bộ màu + biến thể để client đổi giá
    colors = AccessoryColor.objects.filter(accessory=acc).order_by("id")
    variants = AccessoryVariant.objects.filter(accessory=acc).select_related("color")

    # Map {color_id: price}
    color_prices = {v.color_id: int(v.price) for v in variants}

    ctx = {
        "acc": acc,
        "colors": colors,
        "color_prices": color_prices,
        # giá mặc định: nếu có variant → min variant, không có → acc.price
        "default_price": min(color_prices.values()) if color_prices else int(acc.price),
    }
    return render(request, "products/accessory_detail.html", ctx)

# tất cả điện thoại + phụ kiện
# def all_items_list(request):
#     brand = request.GET.get("brand")
#     sort = request.GET.get("sort")

#     # Lấy cả điện thoại + phụ kiện
#     products = list(Product.objects.all())
#     accessories = list(Accessory.objects.all())

#     items = products + accessories

#     # Nếu lọc theo brand
#     if brand:
#         items = [i for i in items if getattr(i, "brand", "").lower() == brand.lower()]

#     # TODO: nếu cần sắp xếp, bạn xử lý tiếp ở đây

#     ctx = {"items": items, "brand": brand}
#     return render(request, "products/all_items_list.html", ctx)
def all_items_list(request):
    q     = (request.GET.get("q") or "").strip()
    brand = (request.GET.get("brand") or "").strip()
    sort  = (request.GET.get("sort") or "").strip()

    # Phones
    phones_qs = (Product.objects
                 .all()
                 .annotate(kind=Value("phone", output_field=CharField()),
                           final_price=F("price"))
                 .values("id", "name", "slug", "brand", "image", "final_price", "kind"))

    # Accessories
    accs_qs = (Accessory.objects
               .all()
               .annotate(kind=Value("accessory", output_field=CharField()),
                         final_price=F("price"))  # nếu bạn có min_variant_price, đổi F("price") -> Coalesce("min_variant_price","price")
               .values("id", "name", "slug", "brand", "image", "final_price", "kind"))

    # Lọc theo từ khóa
    if q:
        phones_qs = phones_qs.filter(name__icontains=q)
        accs_qs   = accs_qs.filter(name__icontains=q)

    # Lọc theo hãng (tất cả hãng từ cả hai loại)
    if brand:
        phones_qs = phones_qs.filter(brand__iexact=brand)
        accs_qs   = accs_qs.filter(brand__iexact=brand)

    # Gom 2 nguồn lại
    items = list(chain(phones_qs, accs_qs))

    # Sắp xếp
    if sort == "price_asc":
        items.sort(key=lambda x: x["final_price"] or 0)
    elif sort == "price_desc":
        items.sort(key=lambda x: x["final_price"] or 0, reverse=True)
    elif sort == "newest":
        items.sort(key=lambda x: x["id"], reverse=True)
    else:
        items.sort(key=lambda x: x["name"].lower())

    # Phân trang
    paginator = Paginator(items, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    ctx = {
        "items": page_obj.object_list,
        "page_obj": page_obj,
        "q": q,
        "brand": brand,
        "sort": sort,
        # dùng all_brands từ context processor để render bộ lọc hãng
    }
    return render(request, "products/all_items_list.html", ctx)

# Admin views
def is_admin(user):
    return user.is_staff or user.is_superuser

def admin_dashboard(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('shop:home')
    # Tổng quan
    total_products = Product.objects.count()
    total_accessories = Accessory.objects.count()
    total_orders = Order.objects.count()
    total_revenue = Order.objects.filter(status='delivered').aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    # Đơn hàng gần đây
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]

    # Sản phẩm bán chạy (dựa trên OrderItem)
    top_products = OrderItem.objects.values('product_variant__product__name').annotate(
        total_sold=Sum('quantity')
    ).order_by('-total_sold')[:5]

    ctx = {
        'total_products': total_products,
        'total_accessories': total_accessories,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'recent_orders': recent_orders,
        'top_products': top_products,
    }
    return render(request, 'admin/dashboard.html', ctx)

@login_required
def admin_products(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('shop:home')
    products = Product.objects.all()
    sort = request.GET.get('sort')
    if sort == 'name':
        products = products.order_by('name')
    elif sort == 'price':
        products = products.order_by('price')
    elif sort == 'brand':
        products = products.order_by('brand')
    else:
        products = products.order_by('-id')

    paginator = Paginator(products, 20)  # 20 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    ctx = {
        'products': page_obj,
        'sort': sort,
    }
    return render(request, 'admin/products.html', ctx)

@login_required
def admin_product_add(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('shop:home')

    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Sản phẩm "{product.name}" đã được thêm thành công.')
            return redirect('shop:admin_products')
    else:
        form = ProductForm()

    ctx = {
        'form': form,
        'title': 'Thêm sản phẩm mới',
    }
    return render(request, 'admin/product_form.html', ctx)

@login_required
def admin_product_edit(request, product_id):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('shop:home')

    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Sản phẩm "{product.name}" đã được cập nhật thành công.')
            return redirect('shop:admin_products')
    else:
        form = ProductForm(instance=product)

    ctx = {
        'form': form,
        'product': product,
        'title': f'Chỉnh sửa sản phẩm: {product.name}',
    }
    return render(request, 'admin/product_form.html', ctx)

@login_required
def admin_product_delete(request, product_id):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('shop:home')

    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Sản phẩm "{product_name}" đã được xóa thành công.')
        return redirect('shop:admin_products')

    ctx = {
        'product': product,
    }
    return render(request, 'admin/product_confirm_delete.html', ctx)

@login_required
def admin_accessories(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('shop:home')
    accessories = Accessory.objects.all()
    sort = request.GET.get('sort')
    if sort == 'name':
        accessories = accessories.order_by('name')
    elif sort == 'price':
        accessories = accessories.order_by('price')
    elif sort == 'brand':
        accessories = accessories.order_by('brand')
    else:
        accessories = accessories.order_by('-id')

    paginator = Paginator(accessories, 20)  # 20 accessories per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    ctx = {
        'accessories': page_obj,
        'sort': sort,
    }
    return render(request, 'admin/accessories.html', ctx)

@login_required
def admin_accessory_add(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('shop:home')

    if request.method == 'POST':
        form = AccessoryForm(request.POST)
        if form.is_valid():
            accessory = form.save()
            messages.success(request, f'Phụ kiện "{accessory.name}" đã được thêm thành công.')
            return redirect('shop:admin_accessories')
    else:
        form = AccessoryForm()

    ctx = {
        'form': form,
        'title': 'Thêm phụ kiện mới',
    }
    return render(request, 'admin/accessory_form.html', ctx)

@login_required
def admin_accessory_edit(request, accessory_id):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('shop:home')

    accessory = get_object_or_404(Accessory, id=accessory_id)

    if request.method == 'POST':
        form = AccessoryForm(request.POST, instance=accessory)
        if form.is_valid():
            accessory = form.save()
            messages.success(request, f'Phụ kiện "{accessory.name}" đã được cập nhật thành công.')
            return redirect('shop:admin_accessories')
    else:
        form = AccessoryForm(instance=accessory)

    ctx = {
        'form': form,
        'accessory': accessory,
        'title': f'Chỉnh sửa phụ kiện: {accessory.name}',
    }
    return render(request, 'admin/accessory_form.html', ctx)

@login_required
def admin_accessory_delete(request, accessory_id):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('shop:home')

    accessory = get_object_or_404(Accessory, id=accessory_id)

    if request.method == 'POST':
        accessory_name = accessory.name
        accessory.delete()
        messages.success(request, f'Phụ kiện "{accessory_name}" đã được xóa thành công.')
        return redirect('shop:admin_accessories')

    ctx = {
        'accessory': accessory,
    }
    return render(request, 'admin/accessory_confirm_delete.html', ctx)

@login_required
def admin_sales(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('home')
    # Thống kê bán hàng
    period = request.GET.get('period', '30')  # ngày
    days = int(period)
    start_date = timezone.now() - timedelta(days=days)

    orders = Order.objects.filter(created_at__gte=start_date)
    total_sales = orders.filter(status='delivered').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_orders = orders.count()

    # Doanh thu theo ngày
    sales_data = orders.filter(status='delivered').extra(
        select={'date': 'DATE(created_at)'}
    ).values('date').annotate(total=Sum('total_amount')).order_by('date')

    ctx = {
        'total_sales': total_sales,
        'total_orders': total_orders,
        'sales_data': sales_data,
        'period': period,
    }
    return render(request, 'admin/sales.html', ctx)

@login_required
def admin_inventory(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('home')
    # Hiển thị tồn kho
    product_inventory = Inventory.objects.filter(product_variant__isnull=False).select_related('product_variant__product')
    accessory_inventory = Inventory.objects.filter(accessory_variant__isnull=False).select_related('accessory_variant__accessory')

    ctx = {
        'product_inventory': product_inventory,
        'accessory_inventory': accessory_inventory,
    }
    return render(request, 'admin/inventory.html', ctx)
def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            # Tạo mã OTP 6 số
            otp_code = ''.join(random.choices(string.digits, k=6))
            
            # Lưu OTP vào session với thời gian hết hạn
            request.session['otp_code'] = otp_code
            request.session['otp_email'] = email
            request.session['otp_created'] = timezone.now().isoformat()
            
            # Gửi email OTP
            subject = 'Mã xác thực đặt lại mật khẩu - PhoneShop'
            message = f'''
Chào bạn,

Bạn đã yêu cầu đặt lại mật khẩu cho tài khoản PhoneShop.

Mã xác thực của bạn là: {otp_code}

Mã này có hiệu lực trong 10 phút. Vui lòng không chia sẻ mã này với bất kỳ ai.

Nếu bạn không yêu cầu đặt lại mật khẩu, vui lòng bỏ qua email này.

Trân trọng,
Đội ngũ PhoneShop
            '''
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            messages.success(request, f'Mã OTP đã được gửi đến email {email}')
            return redirect('shop:verify_otp')
            
        except User.DoesNotExist:
            messages.error(request, 'Email này không tồn tại trong hệ thống.')
    
    return render(request, 'registration/forgot_password.html')

def verify_otp(request):
    if request.method == "POST":
        otp_input = request.POST.get('otp_code')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Kiểm tra OTP từ session
        stored_otp = request.session.get('otp_code')
        stored_email = request.session.get('otp_email')
        otp_created = request.session.get('otp_created')
        
        if not stored_otp or not stored_email:
            messages.error(request, 'Phiên làm việc đã hết hạn. Vui lòng thử lại.')
            return redirect('shop:forgot_password')
        
        # Kiểm tra thời gian hết hạn (10 phút)
        created_time = timezone.datetime.fromisoformat(otp_created)
        if timezone.now() - created_time > timezone.timedelta(minutes=10):
            messages.error(request, 'Mã OTP đã hết hạn. Vui lòng yêu cầu mã mới.')
            return redirect('shop:forgot_password')
        
        # Kiểm tra OTP
        if otp_input != stored_otp:
            messages.error(request, 'Mã OTP không chính xác.')
            return render(request, 'registration/verify_otp.html')
        
        # Kiểm tra mật khẩu mới
        if new_password != confirm_password:
            messages.error(request, 'Mật khẩu xác nhận không khớp.')
            return render(request, 'registration/verify_otp.html')
        
        if len(new_password) < 8:
            messages.error(request, 'Mật khẩu phải có ít nhất 8 ký tự.')
            return render(request, 'registration/verify_otp.html')
        
        # Cập nhật mật khẩu mới
        try:
            user = User.objects.get(email=stored_email)
            user.set_password(new_password)
            user.save()
            
            # Xóa OTP khỏi session
            del request.session['otp_code']
            del request.session['otp_email'] 
            del request.session['otp_created']
            
            messages.success(request, 'Đặt lại mật khẩu thành công! Bạn có thể đăng nhập bằng mật khẩu mới.')
            return redirect('shop:login')
            
        except User.DoesNotExist:
            messages.error(request, 'Có lỗi xảy ra. Vui lòng thử lại.')
            return redirect('shop:forgot_password')
    
    return render(request, 'registration/verify_otp.html')
