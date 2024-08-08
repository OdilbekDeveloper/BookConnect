from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.

class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    telegram_id = models.IntegerField(unique=True, blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    books = models.ManyToManyField("Book", blank=True, related_name='users')
    location = models.ForeignKey("District", on_delete=models.SET_NULL, related_name='residents', null=True)
    is_active = models.BooleanField(default=True)
    referrals = models.IntegerField(default=0)

    def __str__(self):
        return self.username


class Book(models.Model):
    title = models.CharField(max_length=50)
    author = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey("Category", on_delete=models.SET_NULL, null=True)
    img = models.ImageField(upload_to="books/%Y/%m/%d")

    def __str__(self):
        return self.title


class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Like(models.Model):
    user_liked = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='likes_given')
    book_liked = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='likes_received')
    user_liked_back = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='likes_received_back', null=True, blank=True)
    book_liked_back = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='likes_given_back', null=True, blank=True)
    datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user_liked', 'book_liked')

    def __str__(self):
        return f"{self.user_liked.username} likes {self.book_liked.title}"


class City(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}, {self.name}"

class District(models.Model):
    name = models.CharField(max_length=100)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='districts')

    def __str__(self):
        return f"{self.name}, {self.city.name}"
