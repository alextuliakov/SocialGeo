from django.contrib import admin

# Register your models here.
from geo_app.models import Article, Comment, FileUpload, GeoObject, GeoPoint, Like
from geo_app.models import Profile


class ProfileAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Пользователь', {'fields': ['user']}),
        ('Пол', {'fields': ['gender']}),
        ('Местоположение', {'fields': ['location']}),
        ('Статус', {'fields': ['status']}),
        ('Аватар', {'fields': ['avatar']}),
    ]


class CommentInLine(admin.TabularInline):
    model = Comment
    verbose_name_plural = 'Комментарии'
    extra = 0


class ImageInLine(admin.TabularInline):
    model = FileUpload
    verbose_name_plural = 'Фотографии'
    extra = 0


class ArticleAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Создатель', {'fields': ['owner']}),
        ('Заголовок', {'fields': ['header']}),
        ('Текст статьи', {'fields': ['context']}),
        ('Дата публикации', {'fields': ['pub_date']}),
        ('Выбранная метка', {'fields': ['placemark']}),
        ('Сделано из точки', {'fields': ['location']})
    ]
    inlines = [CommentInLine, ImageInLine]


class GeoObjectAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Адрес', {'fields': ['address']}),
        ('Город ', {'fields': ['city']}),
    ]


class GeoPointAdmin(admin.ModelAdmin):
    fieldsets = [
        ('x', {'fields': ['x_coord']}),
        ('', {'fields': ['y_coord']})
    ]


class FileUploadAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Файл', {'fields': ['file']})
    ]


class LikeAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Хозяин', {'fields': ['owner']}),
        ('Статья', {'fields': ['article']}),
    ]


admin.site.register(Profile, ProfileAdmin)
admin.site.register(FileUpload, FileUploadAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(GeoObject, GeoObjectAdmin)
admin.site.register(GeoPoint, GeoPointAdmin)
admin.site.register(Like, LikeAdmin)