from enum import unique
from operator import mod
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.deletion import CASCADE

from utils.models import BaseModel


class UserInfo(BaseModel, AbstractUser):
    """
    用户信息
    """

    telephone = models.CharField(max_length=20, verbose_name='telephone')
    avatar = models.FileField(upload_to='avatars/', default='avatar/default.jpg', verbose_name='avatar')

    blog = models.OneToOneField('Blog', null=True, on_delete=models.CASCADE)
    
    def __str__(self) -> str:
        return self.username
    

class Blog(BaseModel, models.Model):
    """博客信息表（个人站点）"""

    title = models.CharField(max_length=64, verbose_name='title')
    site_name = models.CharField(max_length=64, verbose_name='site_name')
    theme = models.CharField(max_length=32, verbose_name='theme')

    def __str__(self) -> str:
        return self.title


class Category(BaseModel, models.Model):
    """博主个人文章分类表"""

    title = models.CharField(max_length=32, verbose_name='title')
    blog = models.ForeignKey('Blog', on_delete=models.CASCADE, verbose_name='blog', related_name='categories')

    def __str__(self) -> str:
        return self.title


class Tag(BaseModel, models.Model):
    """博主个人文章分类表"""

    title = models.CharField(max_length=32, verbose_name='title')
    blog = models.ForeignKey('Blog', on_delete=models.CASCADE, verbose_name='blog', related_name='Tags')

    def __str__(self) -> str:
        return self.title


class Article(BaseModel, models.Model):
    # """
    # 文章表
    # """
    
    title = models.CharField(max_length=64, verbose_name='title')
    abstract = models.CharField(max_length=128, verbose_name='abstract')
    content = models.TextField(verbose_name='content')

    # 考虑到文章评论数、点赞数获取均为跨表查询操作，因此牺牲了创建操作的效率，来提升查询操作的效率
    comment_count = models.IntegerField(verbose_name='comment_count', default=0)
    up_count = models.IntegerField(verbose_name='up_count', default=0)
    down_count = models.IntegerField(verbose_name='down_count', default=0)

    user = models.ForeignKey('UserInfo', on_delete=models.CASCADE, verbose_name='user')
    category = models.ForeignKey('Category', null=True, on_delete=models.SET_NULL, verbose_name='category')
    tag = models.ManyToManyField('Tag', through='ArticleToTag')

    def __str__(self) -> str:
        return self.title
    

class ArticleToTag(models.Model):
    """
    文章-标签中间关联表
    """
    article = models.ForeignKey('Article', on_delete=CASCADE, verbose_name='article')
    tag = models.ForeignKey('Tag', on_delete=CASCADE, verbose_name='tag')

    class Meta:
        unique_together = [
            ('article', 'tag')
        ]
    
    def __str__(self) -> str:
        return self.article.title + '-----' + self.tag.title


class ArticleUpDown(models.Model):
    """
    点赞表
    """

    article = models.ForeignKey('Article', on_delete=models.CASCADE, verbose_name='article')
    user = models.ForeignKey('UserInfo', on_delete=models.CASCADE, verbose_name='user')

    is_up = models.BooleanField(default=True, verbose_name='is_up')

    class Meta:
        unique_together = [
            ('article', 'user')
        ]
    

class Comment(BaseModel, models.Model):
    """
    评论表
    """

    article = models.ForeignKey('Article', on_delete=models.CASCADE, verbose_name='article')
    user = models.ForeignKey('UserInfo', on_delete=models.CASCADE, verbose_name='user')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, verbose_name='org_comment')

    content = models.TextField(verbose_name='content', null=True)

    def __str__(self) -> str:
        return self.content

        