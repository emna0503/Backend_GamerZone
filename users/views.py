from django.shortcuts import get_object_or_404
from rest_framework import generics , status 
from rest_framework.response import Response
from .serializers import CommentSerializer, GroupSerializer, LikeSerializer, NotificationSerializer, PostSerializer, UserSerializer, LoginSerializer ,LikeSerializerGET
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Comment, Group, Like, Notification, User, Post
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated


# Create your views here.

class SignUpView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer=UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginView(generics.CreateAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        identifier = request.data.get('email')
        password = request.data.get('password')

        if not identifier:
            raise AuthenticationFailed('No credentials provided')

        user = User.objects.filter(email=identifier).first()

        if user is None:
            raise AuthenticationFailed('User not found!')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password!')

        return_user = UserSerializer(user).data
        token = RefreshToken.for_user(user=user) #génère un nouveau token de rafraîchissement associé à un utilisateur spécifique, généralement après que l'utilisateur s'est correctement authentifié.

        return Response(data={
            "access": str(token.access_token),
            "refresh": str(token),
            "user": return_user
                            })


class LogoutView(APIView):
    def post(self, request):
        try:
            del request.session['refresh_token']
        except KeyError:
            pass

        return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)


class userView(APIView):
    def get_permissions(self):
        return [IsAuthenticated()]
    def get(self, request, *args, **kwargs):
        user_data = UserSerializer(request.user)
        return Response(data={
            "user": user_data.data
        })
    

class PostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, post_id):
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return Response({"message": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

        if post.user != request.user:
            return Response({"message": "You are not allowed to update this post"}, status=status.HTTP_403_FORBIDDEN)

        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def get(self, request, post_id=None):
        if post_id:
            try:
                post = Post.objects.get(pk=post_id)
                serializer = PostSerializer(post)
                return Response(serializer.data)
            except Post.DoesNotExist:
                return Response({"message": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            posts = Post.objects.filter(user=request.user)
            serializer = PostSerializer(posts, many=True)
            return Response(serializer.data)


    def delete(self, request, post_id):
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return Response({"message": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

        if post.user  != request.user:
            return Response({"message": "You are not allowed to delete this post"}, status=status.HTTP_403_FORBIDDEN)

        post.delete()
        return Response({"message": "Post deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class LikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_id=request.user.id
        user_instance = User.objects.get(id=user_id)
        request.data['user'] = user_instance.id
        serializer = LikeSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            post = serializer.validated_data['post']
            Notification.objects.create(user=request.user, post=post, notf='like')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else :
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    def get(self, request, like_id=None, *args, **kwargs):
        if like_id is None:
            like = Like.objects.filter(user=request.user.id)
            serializer = LikeSerializerGET(like, many=True)
            return Response(serializer.data)
        else:
            try:
                like = Like.objects.filter(pk=like_id)     
            except Like.DoesNotExist:
                return Response({"message": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
            serializer = LikeSerializerGET(like, many=True)
        return Response(serializer.data)
   
    def delete(self, request, like_id):
        try:
            like = Like.objects.get(pk=like_id)
        except Like.DoesNotExist:
            return Response({"message": "Like not found"}, status=status.HTTP_404_NOT_FOUND)

        if like.user != request.user:
            return Response({"message": "You are not allowed to delete this like"}, status=status.HTTP_403_FORBIDDEN)

        like.delete()
        return Response({"message": "Like deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class CommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            post = serializer.validated_data['post']
            Notification.objects.create(user=request.user, post=post, notf='comment')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def get(self, request, *args, **kwargs):
        comments = Comment.objects.filter(user=request.user)
        serializer = CommentSerializer(comments, many=True)
        return Response(data={"comments": serializer.data})


    def put(self, request, comment_id):
        try:
            comment = Comment.objects.get(pk=comment_id)
        except Comment.DoesNotExist:
            return Response({"message": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)

        if comment.user != request.user:
            return Response({"message": "You are not allowed to update this comment"}, status=status.HTTP_403_FORBIDDEN)

        serializer = CommentSerializer(comment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, comment_id):
        try:
            comment = Comment.objects.get(pk=comment_id)
        except Comment.DoesNotExist:
            return Response({"message": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)

        if comment.user != request.user:
            return Response({"message": "You are not allowed to delete this comment"}, status=status.HTTP_403_FORBIDDEN)

        comment.delete()
        return Response({"message": "Comment deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    
class NotificationView(APIView):
    def get(self, request):
        notifications = Notification.objects.filter(user=request.user.id)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)
    
    def delete(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk, user=request.user)
            notification.delete()
            return Response({'detail': f'La notification {notification.id} a été supprimée.'})
        except Notification.DoesNotExist:
            return Response({'error': 'Cette notification n\'existe pas'}, status=status.HTTP_404_NOT_FOUND)
   

# # class CreateGroupView(generics.CreateAPIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = GroupSerializer

#     def post(self, request, *args, **kwargs):
#         serializer = GroupSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save(admin=request.user)
#             group = serializer.instance
#             group_serializer = GroupSerializer(group)
#             return Response(group_serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def get(self, request, *args, **kwargs):
#         groups = Group.objects.all()
#         serializer = GroupSerializer(groups, many=True)
#         return Response(serializer.data)
    

   
# # class JoinGroupView(APIView):
# #     permission_classes = [IsAuthenticated]

# #     def post(self, request, group_id, *args, **kwargs):
# #         group = get_object_or_404(Group, pk=group_id)
# #         group.members.add(request.user)
# #         return Response({"message": f"You have joined the group '{group.name}'"}, status=status.HTTP_200_OK)



# # class LeaveGroupView(APIView):
# #     permission_classes = [IsAuthenticated]

# #     def post(self, request, group_id, *args, **kwargs):
# #         group = get_object_or_404(Group, pk=group_id)
# #         group.members.remove(request.user)
# #         return Response({"message": f"You have left the group '{group.name}'"}, status=status.HTTP_200_OK)


# # class GroupMembersView(APIView):
# #     permission_classes = [IsAuthenticated]

# #     def get(self, request, group_id, *args, **kwargs):
# #         group = get_object_or_404(Group, pk=group_id)
# #         if request.user in group.members.all():
# #             members = group.members.all()
# #             serializer = UserSerializer(members, many=True)
# #             return Response(serializer.data)
# #         else:
# #             return Response({"message": "You are not a member of this group"}, status=status.HTTP_403_FORBIDDEN)


# # class GroupDetailsView(generics.RetrieveUpdateDestroyAPIView):
# #     serializer_class = GroupSerializer
# #     permission_classes = [IsAuthenticated]

# #     def delete(self, request, *args, **kwargs):
# #         group = self.get_object()
# #         if request.user == group.admin or request.user.group_admin:
# #             group.delete()
# #             return Response({"message": f"Group '{group.name}' has been deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
# #         else:
# #             return Response({"message": "You do not have permission to delete this group"}, status=status.HTTP_403_FORBIDDEN)

# #     def put(self, request, *args, **kwargs):
# #         group = self.get_object()
# #         if request.user == group.admin or request.user.group_admin:
# #             serializer = self.get_serializer(group, data=request.data, partial=True)
# #             serializer.is_valid(raise_exception=True)
# #             serializer.save()
# #             return Response(serializer.data)
# #         else:
# #             return Response({"message": "You do not have permission to modify this group"}, status=status.HTTP_403_FORBIDDEN)

# #     def post(self, request, *args, **kwargs):
# #         group = self.get_object()
# #         user_email = request.data.get('email') 
# #         user_to_invite = User.objects.filter(email=user_email).first()
# #         if user_to_invite:
# #             group.members.add(user_to_invite)
# #             return Response({"message": f"User '{user_to_invite.email}' has been invited to the group '{group.name}'"}, status=status.HTTP_200_OK)
# #         else:
# #             return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

# #     def remove_user_from_group(self, request, *args, **kwargs):
# #         group = self.get_object()
# #         user_id = request.data.get('user_id')
# #         if user_id:
# #             user_to_remove = User.objects.filter(id=user_id).first()
# #             if user_to_remove:
# #                 group.members.remove(user_to_remove)
# #                 return Response({"message": f"User '{user_to_remove.email}' has been removed from the group '{group.name}'"}, status=status.HTTP_200_OK)
# #             else:
# #                 return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
# #         else:
# #             return Response({"message": "User ID is required to remove a user from the group"}, status=status.HTTP_400_BAD_REQUEST)


# # class InviteFriendsToGroupView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         user = request.user
#         friends = Friendship.objects.filter(user=user)
#         friend_serializer = FriendshipSerializer(friends, many=True)
#         return Response(friend_serializer.data)

#     def post(self, request, *args, **kwargs):
#         selected_friends_ids = request.data.get('selected_friends', [])
#         group_id = kwargs.get('group_id')
#         group = Group.objects.get(id=group_id)
#         invited_friends = User.objects.filter(id__in=selected_friends_ids)
        
#         for friend in invited_friends:
#             group.members.add(friend)
#             notification_message = f"Vous avez été invité à rejoindre le groupe '{group.name}' par {request.user.username}."
#             Notification.objects.create(user=friend, message=notification_message)
#         return Response({"message": "Invitations sent successfully"}, status=status.HTTP_200_OK)


class GroupMembersView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, group_id, *args, **kwargs):
        group = get_object_or_404(Group, pk=group_id)
        group.members.add(request.user)
        return Response({'message': 'Joined group successfully'})

    def delete(self, request, group_id, *args, **kwargs):
        group = get_object_or_404(Group, pk=group_id)
        group.members.remove(request.user)
        return Response({'message': 'Left group successfully'})

    def get(self, request, group_id, *args, **kwargs):
        group = get_object_or_404(Group, pk=group_id)
        members = group.members.all()
        return Response({'members': members})


class GroupView(generics.RetrieveAPIView, generics.CreateAPIView, generics.DestroyAPIView):
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        group = serializer.save(creator=request.user)
        group.members.add(request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.creator == request.user or request.user in instance.admin.all() or request.user in instance.super_admin.all():
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'message': 'You are not authorized to delete this group'}, status=status.HTTP_403_FORBIDDEN)


class GroupControlView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, group_id):
        group = get_object_or_404(Group, pk=group_id)
        if request.user == group.creator or request.user in group.admin.all() or request.user in group.super_admin.all():
            return Response({'message': 'Post added successfully'})
        else:
            return Response({'message': 'You are not authorized to add posts to this group'}, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, group_id):
        group = get_object_or_404(Group, pk=group_id)
        if request.user == group.creator or request.user in group.admin.all() or request.user in group.super_admin.all():
            return Response({'message': 'Deleted successfully'})
        else:
            return Response({'message': 'You are not authorized to perform this action'}, status=status.HTTP_403_FORBIDDEN)



