from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .models import *
from .serializer import *
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.hashers import make_password
import random

from datetime import datetime, timedelta
from django.utils import timezone
import requests
# Create your views here.



@api_view(['POST'])
def User_Register(request):
    print(True)
    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')
    password = request.data.get('password')
    password_hashed = make_password(password)
    telegram_id = request.data.get('telegram_id')
    phone_number = request.data.get('phone_number')
    username = request.data.get('username')
    location = request.data.get('location')

    # Create the user
    user = CustomUser.objects.create(
        first_name=first_name,
        last_name=last_name,
        password=password_hashed,
        phone_number=phone_number,
        telegram_id=telegram_id,
        username=username,
        location=location
    )
    # Generate a token for the user
    token, created = Token.objects.get_or_create(user=user)

    # Serialize the user data along with the token
    ser = CustomUserSerializer(user)
    user_data = ser.data
    user_data['token'] = token.key

    return Response(user_data, status=201)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def Edit_User(request):
    user = request.user

    # Get updated fields from request data with default values if not provided
    first_name = request.data.get('first_name', user.first_name)
    last_name = request.data.get('last_name', user.last_name)
    username = request.data.get('username', user.username)
    phone_number = request.data.get('phone_number', user.phone_number)
    district_id = request.data.get('location', user.location)
    location = District.objects.get(id=district_id)

    # Update user fields
    user.first_name = first_name
    user.last_name = last_name
    user.username = username
    user.phone_number = phone_number
    user.location = location
    user.save()

    # Respond with the updated user data
    user_data = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'username': user.username,
        'phone_number': user.phone_number,
        'location': user.location
    }

    return Response(user_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def Deactivate_User(request):
    user = request.user

    user.is_active = False
    user.save()

    user_data = {
        'is_active': user.is_active,
    }

    return Response(user_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def Get_User_Data(request):
    serializer = CustomUserSerializer(request.user)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def Add_Book(request):
    user = request.user

    title = request.data.get('title')
    author = request.data.get('author')
    description = request.data.get('description')
    category_id = request.data.get('category')
    try:
        category = Category.objects.get(id=category_id)
    except Category.DoesNotExist:
        return Response({'error': 'Category not found'}, status=status.HTTP_400_BAD_REQUEST)

    if not all([title, author, description]):
        return Response({'error': 'All fields except image are required'}, status=status.HTTP_400_BAD_REQUEST)

    img = request.data.get('img')

    book = Book.objects.create(title=title, author=author, description=description, category=category, img=img)

    user.books.add(book)
    user.save()

    ser = BookSerializer(book)

    return Response(ser.data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def Edit_Book(request, pk):
    user = request.user

    try:
        # Check if the book is associated with the current user
        book = Book.objects.get(id=pk, users=user)
    except Book.DoesNotExist:
        return Response({"detail": "Book not found or you do not have permission to edit it."}, status=status.HTTP_404_NOT_FOUND)

    # Get updated values from the request, or keep existing ones if not provided
    title = request.data.get('title', book.title)
    author = request.data.get('author', book.author)
    description = request.data.get('description', book.description)
    category_id = request.data.get('category', book.category.id)

    try:
        category = Category.objects.get(id=category_id)
    except Category.DoesNotExist:
        return Response({"detail": "Category not found."}, status=status.HTTP_400_BAD_REQUEST)

    # Update book fields
    book.title = title
    book.author = author
    book.description = description
    book.category = category
    book.save()

    # Serialize the updated book and return the response
    ser = BookSerializer(book)
    return Response(ser.data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def Delete_Book(request, pk):
    user = request.user

    try:
        # Check if the book is associated with the current user
        book = Book.objects.get(id=pk, users=user)
    except Book.DoesNotExist:
        return Response({"detail": "Book not found or you do not have permission to delete it."}, status=status.HTTP_404_NOT_FOUND)

    book.delete()

    return Response({"detail": "Book deleted successfully."}, status=status.HTTP_204_NO_CONTENT)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def Get_Random_Books_By_User_Location(request):
    user = request.user
    user_district = user.location

    if not user_district:
        return Response({"detail": "User location is not set."}, status=status.HTTP_400_BAD_REQUEST)

    # Get users in the same district, sorted by the number of referrals (descending)
    users_in_same_district = CustomUser.objects.filter(location=user_district).order_by('-referrals')

    if not users_in_same_district.exists():
        return Response({"detail": "No users found in your district."}, status=status.HTTP_404_NOT_FOUND)

    # Get all books owned by users in the same district
    books_in_same_district = Book.objects.filter(users__in=users_in_same_district).distinct()

    if not books_in_same_district.exists():
        return Response({"detail": "No books available in your district."}, status=status.HTTP_404_NOT_FOUND)

    # Get the number of books to return from the request data
    num_books_to_return = request.query_params.get('num_books', 30)  # Default to 10 if not provided

    try:
        num_books_to_return = int(num_books_to_return)
    except ValueError:
        return Response({"detail": "Invalid number of books specified."}, status=status.HTTP_400_BAD_REQUEST)

    if num_books_to_return <= 0:
        return Response({"detail": "Number of books must be positive."}, status=status.HTTP_400_BAD_REQUEST)

    # Convert queryset to list and shuffle
    books_list = list(books_in_same_district)
    random.shuffle(books_list)

    # Slice the list to get the desired number of random books
    random_books = books_list[:num_books_to_return]

    # Serialize and return the books
    serializer = BookSerializer(random_books, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def Get_Random_Books_All(request):
    # Get the number of books to return from the request data
    num_books_to_return = request.query_params.get('num_books', 30)  # Default to 30 if not provided

    try:
        num_books_to_return = int(num_books_to_return)
    except ValueError:
        return Response({"detail": "Invalid number of books specified."}, status=status.HTTP_400_BAD_REQUEST)

    if num_books_to_return <= 0:
        return Response({"detail": "Number of books must be positive."}, status=status.HTTP_400_BAD_REQUEST)

    # Fetch users ordered by referrals in descending order who have at least one book
    top_users_with_books = CustomUser.objects.filter(books__isnull=False).order_by('-referrals').distinct()

    if not top_users_with_books.exists():
        return Response({"detail": "No users with books available."}, status=status.HTTP_404_NOT_FOUND)

    # Fetch all books from these top users
    top_user_books = Book.objects.filter(users__in=top_users_with_books).distinct()

    if not top_user_books.exists():
        return Response({"detail": "No books available from top users."}, status=status.HTTP_404_NOT_FOUND)

    # Convert queryset to list and shuffle
    books_list = list(top_user_books)
    random.shuffle(books_list)

    # Slice the list to get the desired number of random books
    random_books = books_list[:num_books_to_return]

    # Serialize and return the books
    serializer = BookSerializer(random_books, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def Like_Book(request):
    user = request.user
    book_id = request.data.get('book_id')

    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return Response({"detail": "Book not found."}, status=status.HTTP_404_NOT_FOUND)

    # Check if the user has already liked the book
    if Like.objects.filter(user_liked=user, book_liked=book).exists():
        return Response({"detail": "You have already liked this book."}, status=status.HTTP_400_BAD_REQUEST)

    # Check if the book's owner has liked back
    book_owner = book.users.first()  # Assuming the first user is the book owner
    if book_owner and Like.objects.filter(user_liked=book_owner, book_liked__in=user.books.all()).exists():
        # Create a like instance
        Like.objects.create(
            user_liked=user,
            book_liked=book
        )
        return Response({"detail": "Book liked. The owner will see this like and can choose to like back."},
                        status=status.HTTP_200_OK)

    # If book's owner hasn't liked back, just create a like instance
    Like.objects.create(
        user_liked=user,
        book_liked=book
    )
    return Response({"detail": "Book liked."}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def Like_Back(request):
    user = request.user
    book_id = request.data.get('book_id')

    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return Response({"detail": "Book not found."}, status=status.HTTP_404_NOT_FOUND)

    # Check if the user is the owner of the book
    if not book.users.filter(id=user.id).exists():
        return Response({"detail": "You can only like back for books you own."}, status=status.HTTP_403_FORBIDDEN)

    # Check if there's a pending like to this user
    try:
        like = Like.objects.get(user_liked=user, book_liked=book)
        # Check if the book liked by the user matches any books liked by the book's owner
        liked_back = Like.objects.filter(user_liked=book.users.first(), book_liked__in=user.books.all()).exists()

        if liked_back:
            # Update the like instance to reflect mutual liking
            like.user_liked_back = user
            like.book_liked_back = book
            like.save()
            return Response({"detail": "Like back successful. Both users have liked each other's books."},
                            status=status.HTTP_200_OK)
        else:
            return Response({"detail": "No matching book found to like back."}, status=status.HTTP_404_NOT_FOUND)

    except Like.DoesNotExist:
        return Response({"detail": "No pending like found for this book."}, status=status.HTTP_404_NOT_FOUND)
