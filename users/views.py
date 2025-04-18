from django.shortcuts import render

from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .models import CustomUser
from .serializers import UserSerializer
from .permissions import IsAdmin, IsManager
from tasks.models import Task


class UserListCreateAPIView(APIView):
    """
    GET: List all users (Admin only).
    POST: Create a new user (Admin only).
    """
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get(self, request):
        # Fetch all users from the database
        users = CustomUser.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Create a new user from request data
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailAPIView(APIView):
    """
    Handles retrieval, update, and deletion of a specific user (Admin only).
    """
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get_object(self, pk):
        # Utility method to fetch a user by primary key
        try:
            return CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            return None

    def get(self, request, pk):
        # Retrieve a user's details
        user = self.get_object(pk)
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def put(self, request, pk):
        # Fully update a user
        user = self.get_object(pk)
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        # Partially update a user (e.g., just the email or is_active status)
        user = self.get_object(pk)
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        # Delete the user
        user = self.get_object(pk)
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ManageUserAPIView(APIView):
    """
    POST: Allows a manager to activate/deactivate a user.
          Only works if the user has at least 5 incomplete tasks.
    """
    permission_classes = [permissions.IsAuthenticated, IsManager]

    def post(self, request, user_id):
        # 1️⃣ Get the user by ID or return 404 if not found
        target_user = get_object_or_404(CustomUser, pk=user_id)

        # 2️⃣ Count how many incomplete tasks this user has
        incomplete_count = Task.objects.filter(
            assigned_to=target_user,
            completed=False
        ).count()

        # 3️⃣ If fewer than 5, do not allow status change
        if incomplete_count < 5:
            return Response(
                {"error": "User must have at least 5 incomplete tasks."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 4️⃣ Toggle the user's active status
        target_user.is_active = not target_user.is_active
        target_user.save()

        # 5️⃣ Return a success response with the new status
        return Response({
            "message": f"User {'activated' if target_user.is_active else 'deactivated'}.",
            "user_id": target_user.id,
            "is_active": target_user.is_active
        }, status=status.HTTP_200_OK)



