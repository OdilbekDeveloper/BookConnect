from django.contrib import admin
from .models import CustomUser, Book, Category, Like, City, District

# Custom User Admin
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'phone_number', 'telegram_id', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'phone_number', 'telegram_id')
    list_filter = ('is_active',)
    readonly_fields = ('last_login', 'date_joined')
    filter_horizontal = ('books',)

# Book Admin
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'description')
    search_fields = ('title', 'author', 'description')
    list_filter = ('category',)

# Category Admin
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# Like Admin
@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user_liked', 'book_liked', 'user_liked_back', 'book_liked_back', 'datetime')
    search_fields = ('user_liked__username', 'book_liked__title', 'user_liked_back__username', 'book_liked_back__title')
    list_filter = ('datetime',)
    readonly_fields = ('datetime',)

# City Admin
@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# District Admin
@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'city')
    search_fields = ('name', 'city__name')
    list_filter = ('city',)
