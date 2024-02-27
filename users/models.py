from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    name = models.CharField(max_length=100)
    family_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    birthday = models.DateField(null=True, blank=True)
    type_user = models.TextField(null=False, db_column='type_user')
    image = models.ImageField(blank=False,upload_to='profile_pics/', default='image.jpg')
    password = models.CharField(max_length=255)


    username = None
    USERNAME_FIELD= 'email'
    REQUIRED_FIELDS=[]
    class Meta:
        db_table = 'users'
   
class Post(models.Model):
    user  = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    file = models.FileField(upload_to='posts/', null=True, blank=True)
    nb_likes = models.IntegerField(default=0)
    nb_comments = models.IntegerField(default=0)
    poster_name = models.CharField(max_length=100)
    poster_photo = models.ImageField(upload_to='media/posters/', default='poster.jpg')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'posts'
    def __str__(self):
        return self.content

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    content = models.TextField()

    class Meta:
        db_table = 'comments'

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            Notification.objects.create(user=self.post.user, notf=f'{self.user.username} commented on your post: {self.content}')

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            Notification.objects.create(user=self.post.user, notf=f'{self.user.username} liked your post')

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    notf = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'


class Group(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    members = models.ManyToManyField(User, related_name='group_memberships')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups')
    admin = models.ManyToManyField(User, related_name='admin_groups')
    super_admin = models.ManyToManyField(User, related_name='super_admin_groups')
    photo_grp=models.FileField(upload_to='media/group/', null=True, blank=True)
    photo_couv=models.FileField(upload_to='media/group/', null=True, blank=True)
    
    
    class Meta:
        db_table = 'groups'

# class Friendship(models.Model):

#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friends')
#     friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_of')

#     class Meta:
#         db_table = 'friendship'


