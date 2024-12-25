from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10,decimal_places=2)
    image = models.ImageField(upload_to='products')
    stock = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0.0)
    description = models.TextField()
    categories = models.ManyToManyField(Category,blank=True)
    raw_categories = models.TextField(blank=True)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.raw_categories:
            category_names = [name.strip().lower() for name in self.raw_categories.split(',') if name.strip()]
            for category_name in category_names:
                category,created = Category.objects.get_or_create(name=category_name)
                self.categories.add(category)
            print(self.categories.all())
            self.raw_categories = ''
            super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def cart_price(self):
       return sum(item.total_price for item in self.cartitem_set.all())

    def __str__(self):
        return f"Cart of {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    @property
    def total_price(self):
        return self.quantity * self.product.price
    
    def add_item(self):
        self.quantity += 1
        self.save()

    def remove_item(self):
        if self.quantity > 1:
            self.quantity -= 1
            self.save()
        else:
            self.delete()

    def delete_product(self):
        self.delete()

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    