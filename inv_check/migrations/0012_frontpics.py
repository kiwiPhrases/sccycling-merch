# Generated by Django 3.0.6 on 2020-05-25 05:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inv_check', '0011_auto_20200524_2112'),
    ]

    operations = [
        migrations.CreateModel(
            name='FrontPics',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('picLabel', models.CharField(default='front merch pic', max_length=15, verbose_name='alternative label')),
                ('imgurl', models.URLField(default='https://drive.google.com/uc?id=1WZFyFdPikqZtkAI1KtvgmMJzJBzNHT8U', verbose_name='image')),
            ],
        ),
    ]
