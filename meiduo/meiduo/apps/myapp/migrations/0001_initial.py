# Generated by Django 3.1.7 on 2021-03-25 02:40

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Topping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('top', models.CharField(max_length=32, verbose_name='配料')),
            ],
        ),
        migrations.CreateModel(
            name='Pizza',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('topping', models.ManyToManyField(related_name='toppings', related_query_name='topps', to='myapp.Topping', verbose_name='所有配料')),
            ],
        ),
    ]
