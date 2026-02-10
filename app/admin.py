from django.contrib import admin
from .models import Category, Product, Capacity, Color, ProductVariant
from .models import AccessoryCategory, Accessory, AccessoryColor, AccessoryVariant, AccessoryCompatibleProduct
from .models import Banner, Order, OrderItem, Inventory


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_variant', 'accessory_variant', 'quantity', 'price')
    can_delete = False


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_amount', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__email', 'id')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [OrderItemInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'get_item_name', 'quantity', 'price', 'get_total')
    list_filter = ('order__status', 'order__created_at')
    search_fields = ('order__id', 'order__user__email')

    def get_item_name(self, obj):
        if obj.product_variant:
            return f"{obj.product_variant.product.name} ({obj.product_variant.capacity.name}, {obj.product_variant.color.name})"
        elif obj.accessory_variant:
            return f"{obj.accessory_variant.accessory.name} ({obj.accessory_variant.color.name})"
        return "Unknown Item"
    get_item_name.short_description = "Item"

    def get_total(self, obj):
        return obj.quantity * obj.price
    get_total.short_description = "Total"


# Register your models here.
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Capacity)
admin.site.register(Color)
admin.site.register(ProductVariant)

# phần phụ kiện
admin.site.register(AccessoryCategory)
admin.site.register(Accessory)
admin.site.register(AccessoryColor)
admin.site.register(AccessoryVariant)
admin.site.register(AccessoryCompatibleProduct)

# Admin models
admin.site.register(Banner)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Inventory)
