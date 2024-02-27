from rest_framework import serializers
from .models import Group, Notification, User , Post , Comment , Like

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'family_name', 'type_user', 'email', 'birthday', 'password', 'image']
        extra_kwargs = {
            'password': {'write_only': True}
        }      

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
    

class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(write_only=True, required=True)


class PostSerializer(serializers.ModelSerializer):
    poster_name = serializers.CharField(source='user.username', read_only=True)
    poster_photo = serializers.ImageField(source='user.profile_picture', read_only=True)
    notifications = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'user', 'content', 'file', 'nb_comments', 'poster_name', 'poster_photo', 'created_at', 'updated_at', 'notifications']
    def get_notifications(self, obj):
        notifications = Notification.objects.filter(post=obj)
        serializer = NotificationSerializer(notifications, many=True)
        return serializer.data

class CommentSerializer(serializers.ModelSerializer):
    post =  serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())

    class Meta:
        model = Comment
        fields = ['id', 'user', 'post' , 'content']


class LikeSerializer(serializers.ModelSerializer):
    user =  serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Like
        fields = '__all__'


class LikeSerializerGET(serializers.ModelSerializer):
    user =  UserSerializer()
    post =  PostSerializer()
    class Meta:
        model = Like
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = '__all__'

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'

# class FriendshipSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Friendship
#         fields = '__all__'