# Generated by Django 3.2.4 on 2023-07-26 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserCart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField(verbose_name='Количество')),
            ],
            options={
                'verbose_name': 'Корзина пользователя',
                'verbose_name_plural': 'Корзина пользователя',
                'ordering': ['pk'],
            },
        ),
    ]
