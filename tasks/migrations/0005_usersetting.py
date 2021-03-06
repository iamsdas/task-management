# Generated by Django 4.0.1 on 2022-02-11 16:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('tasks', '0004_statushistory'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserSetting',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('preffered_mail_hour', models.IntegerField(default=0)),
            ],
        ),
    ]
