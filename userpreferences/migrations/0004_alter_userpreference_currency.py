# Generated by Django 3.2.4 on 2021-09-08 15:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userpreferences', '0003_alter_userpreference_currency'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userpreference',
            name='currency',
            field=models.CharField(default='INR - Indian Rupee', max_length=255),
        ),
    ]
