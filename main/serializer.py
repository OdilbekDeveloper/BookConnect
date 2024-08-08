from rest_framework import serializers
from .models import CustomUser, Book, Category, Like

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class BookSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)  # Nested serializer for category

    class Meta:
        model = Book
        fields = '__all__'

class CustomUserSerializer(serializers.ModelSerializer):
    books = BookSerializer(many=True, read_only=True)  # Nested serializer for books

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'first_name', 'last_name', 'phone_number', 'telegram_id', 'email', 'books', 'location', 'is_active', 'referrals')

class LikeSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)  # Nested serializer for user
    book = BookSerializer(read_only=True)  # Nested serializer for book

    class Meta:
        model = Like
        fields = ('user', 'book', 'datetime')
