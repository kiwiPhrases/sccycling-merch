# Generated by Django 3.0.6 on 2020-09-28 19:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inv_check', '0015_delete_itemorder'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='address2',
            field=models.CharField(blank=True, default='', max_length=10, null=True),
        ),
    ]
