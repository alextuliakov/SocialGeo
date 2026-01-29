from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class GeoPoint(models.Model):
    x_coord = models.FloatField()
    y_coord = models.FloatField()

    def __str__(self):
        return "x: {} y: {}".format(self.x_coord, self.y_coord)


class GeoObject(models.Model):
    geometry = models.OneToOneField(GeoPoint, on_delete=models.CASCADE)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=300)


class Trip(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    header = models.CharField(max_length=100, verbose_name='')
    description = models.TextField(verbose_name='')
    pub_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.header


class Article(models.Model):
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    header = models.CharField(max_length=255, verbose_name='')
    context = models.TextField(verbose_name='')
    location = models.OneToOneField(GeoPoint, on_delete=models.CASCADE, null=True)
    placemark = models.OneToOneField(GeoObject, on_delete=models.CASCADE, null=True)
    pub_date = models.DateTimeField(default=timezone.now)
    edit_date = models.DateTimeField(auto_now=True)
    files = models.ImageField(upload_to='files/%Y/%m/%d', verbose_name='', blank=True)
    trip = models.ForeignKey(Trip, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.header


class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    context = models.TextField(max_length=500)
    pub_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.context


class FileUpload(models.Model):
    name = models.CharField(default=timezone.now(), max_length=100)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    file = models.ImageField(upload_to='files/%Y/%m/%d', verbose_name='')

    def __str__(self):
        return self.file.name


class Like(models.Model):
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=True)


def upload_to(instance, filename):
    return 'images/%s/%s' % (instance.user.username, filename)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=1, default='М', choices=(('М', 'Мужской'), ('Ж', 'Женский')))
    location = models.CharField(max_length=500, default='')
    status = models.CharField(max_length=500, default='')
    avatar = models.ImageField(upload_to=upload_to)
    followers = models.ManyToManyField('Profile', related_name='followed_by')
    
#Hello, this is ci test
