from django.shortcuts import render


from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import CustomUser
from .serializers import UserSerializer
from .permissions import IsAdmin,IsManager

from tasks.models import Task



class UserListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get(self, request):
        users = CustomUser.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





class UserDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get_object(self, pk):
        try:
            return CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            return None

    def get(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def put(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ManageUserAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsManager]

    def post(self, request, user_id):
        # 1️⃣ Fetch the target user or return 404
        target_user = get_object_or_404(CustomUser, pk=user_id)

        # 2️⃣ Count that user's incomplete tasks
        incomplete_count = Task.objects.filter(
            assigned_to=target_user,
            completed=False
        ).count()

        # 3️⃣ If fewer than 5, reject
        if incomplete_count < 5:
            return Response(
                {"error": "User must have at least 5 incomplete tasks."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 4️⃣ Toggle active status and save
        target_user.is_active = not target_user.is_active
        target_user.save()

        # 5️⃣ Return success
        return Response({
            "message": f"User {'activated' if target_user.is_active else 'deactivated'}.",
            "user_id": target_user.id,
            "is_active": target_user.is_active
        }, status=status.HTTP_200_OK)