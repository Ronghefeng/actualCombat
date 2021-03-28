from django.db import models

class Topping(models.Model):

    top = models.CharField(max_length=32, verbose_name='配料')


class Pizza(models.Model):

    topping = models.ManyToManyField(Topping, related_query_name='pizza_query_set', related_name='pizaaes',verbose_name='所有配料')


class Publication(models.Model):
    title = models.CharField(max_length=30)

    class Meta:
        ordering = ['title']
        db_table = 'publication'

    def __str__(self):
        return self.title

class Article(models.Model):
    headline = models.CharField(max_length=100)
    publications = models.ManyToManyField(Publication)

    class Meta:
        ordering = ['headline']
        db_table = 'article'

    def __str__(self):
        return self.headline


class MyUser(models.Model):
    name = models.CharField(max_length=32, verbose_name='用户名')


class MySpecialUser(models.Model):
    vipuser = models.OneToOneField(
        'MyUser',
        on_delete=models.CASCADE,
    )
    svipuser = models.OneToOneField(
        'MyUser',
        on_delete=models.CASCADE,
        related_name='svip',
    )

