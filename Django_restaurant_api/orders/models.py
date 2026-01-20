from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import mark_safe
from django.contrib.auth.models import User
from decimal import Decimal

STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('processing', 'Processing'),
    ('delivered', 'Delivered'),
)

class Category(models.Model):
    cid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet='abcdefgh12345')
    title = models.CharField(max_length=100)
    image = models.ImageField(blank=True, null=True, upload_to='category/')

    class Meta:
        verbose_name_plural = 'Categories'
    
    def category_image(self):
        if self.image:
            return mark_safe(f'<img src="{self.image.url}" width="50" height="50" />')
        return "No Image"
    
    def __str__(self):
        return self.title


def product_image_path(instance, filename):
    category_title = instance.category.title if instance.category else "uncategorized"
    return f'products/{category_title}/{filename}'


class Product(models.Model):
    pid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet='abcdefgh12345')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='category')
    title = models.CharField(max_length=100, default='Affordable meal')
    image = models.ImageField(upload_to=product_image_path, default='product.jpg')
    description = models.TextField(null=True, blank=True, default='This is the product')
    price = models.DecimalField(max_digits=12, decimal_places=2, default='0.00')
    product_status = models.CharField(choices=STATUS_CHOICES, max_length=10, default='pending')
    in_stock = models.BooleanField(default=True)
    date = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Products'
        ordering = ['-date']

    def product_image(self):
        if self.image:
            return mark_safe(f'<img src="{self.image.url}" width="50" height="50" />')
        return "No Image"
    
    def __str__(self):
        return self.title
    

class ProductImages(models.Model):
    images = models.ImageField(upload_to=product_image_path, default='product.jpg')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='p_images')
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Product Images'
    
    def product_image(self):
        if self.images:
            return mark_safe(f'<img src="{self.images.url}" width="50" height="50" />')
        return "No Image"

# Temporary cart model (session-like, user adds items here)
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product')
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    date_added = models.DateTimeField(auto_now_add=True)

    def product_image(self):
        if self.product.image:
            return mark_safe(f'<img src="{self.product.image.url}" width="50" height="50" />')
        return "No Image"

    def multiply_price(self):
        return self.price * self.quantity

    def __str__(self):
        return f'{self.user} | {self.product} | {self.quantity}'

# Permanent order batch (represents one checkout)
class OrderBatch(models.Model):
    bid = ShortUUIDField(unique=True, length=10, max_length=20)
    # user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='order_batches')
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    date_created = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f'Batch {self.batch_id} - {self.user}'

# Items that belong to an order batch
class OrderBatchItem(models.Model):
    batch = models.ForeignKey(OrderBatch, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    def product_image(self):
        if self.product.image:
            return mark_safe(f'<img src="{self.product.image.url}" width="50" height="50" />')
        return "No Image"

    def multiply_price(self):
        return self.price * self.quantity

    def __str__(self):
        return f'{self.product} x {self.quantity} in {self.batch}'
