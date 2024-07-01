from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    is_farmer = models.BooleanField(default=False, verbose_name="Is Farmer")
    is_buyer = models.BooleanField(default=False, verbose_name="Is Buyer")
    name = models.CharField(max_length=100,null=True, blank=True)
    mobile = models.CharField(max_length=15,null=True, blank=True)
    address = models.CharField(max_length=200,null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    state = models.CharField(max_length=100,null=True, blank=True)
    district = models.CharField(max_length=100,null=True, blank=True)
    pan= models.CharField(max_length=12,null=True, blank=True)
    bank= models.CharField(max_length=20,null=True, blank=True)

    def __str__(self):
        return self.username

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Category Name",null=True, blank=True)
    image = models.ImageField(upload_to='category_images/', null=True, blank=True, verbose_name="Category Image")

    def __str__(self):
        return self.name
    
    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return  url
    
class Product(models.Model):
    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products', verbose_name="Farmer")
    name = models.CharField(max_length=100, verbose_name="Product Name",null=True, blank=True)
    stock_in_kg = models.FloatField(verbose_name="Stock in KG",null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name="Product Category")
    expiration_date = models.DateField(verbose_name="Expiration Date",null=True, blank=True)
    images = models.ImageField(upload_to='product_images/', null=True, blank=True, verbose_name="Product Images")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Product Price",null=True, blank=True)
    description = models.TextField(verbose_name="Product Description",null=True, blank=True)
    delivery_available = models.BooleanField(default=False, verbose_name="Delivery Available")

    @property
    def imageURL_1(self):
        try:
            url = self.images.url
        except:
            url = ''
        return  url
    
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart', verbose_name="User")
    products = models.ManyToManyField('Product', through='CartItem', verbose_name="Products in Cart")

class CartItem(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, verbose_name="Product")
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE, verbose_name="Cart")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Quantity")

# models.py
class PurchaserProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchased_products', verbose_name="Purchaser")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Product")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Quantity")
