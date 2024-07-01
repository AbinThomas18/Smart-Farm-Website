from django.contrib import admin
from .models import *
from django.utils.html import format_html
# Register your models here.

class Users(admin.ModelAdmin):
    list_display = ('name', 'mobile', 'address','email','district','state','is_buyer','is_farmer')


# Check if LogoPredictionAdmin is not already registered before registering
if not admin.site.is_registered(Users):
    admin.site.register(User, Users)

class Categ(admin.ModelAdmin):
    list_display = ('name','display_image' )

    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50px" height="50px" />'.format(obj.image.url))
        else:
            return "No Image"

    display_image.short_description = 'Image Preview'

admin.site.register(Category, Categ)

class Prod(admin.ModelAdmin):
    list_display = ('name','stock_in_kg','category','expiration_date','display_image','price','description','delivery_available' )

    def display_image(self, obj):
        if obj.imageURL_1:
            return format_html('<img src="{}" width="50px" height="50px" />'.format(obj.imageURL_1))
        else:
            return "No Image"

    display_image.short_description = 'Image Preview'

admin.site.register(Product, Prod)

class Purchaser(admin.ModelAdmin):
    list_display = ('user_name','product_name','quantity')

    def user_name(self, obj):
        return obj.user.name

    user_name.short_description = 'Purchaser Name'

    def product_name(self, obj):
        return obj.product.name

    product_name.short_description = 'Product Name'


admin.site.register(PurchaserProduct, Purchaser)