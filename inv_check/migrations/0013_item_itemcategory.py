# Generated by Django 3.0.6 on 2020-07-30 22:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inv_check', '0012_frontpics'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='itemcategory',
            field=models.CharField(choices=[('jersey', 'jersey'), ('bibs', 'bibs'), ('accessories', 'accessories'), ('bike & parts', 'bike & parts')], default='accessories', max_length=13),
        ),
    ]
