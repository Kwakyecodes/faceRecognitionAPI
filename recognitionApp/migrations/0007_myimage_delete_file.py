# Generated by Django 4.0.3 on 2022-03-13 08:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recognitionApp', '0006_file'),
    ]

    operations = [
        migrations.CreateModel(
            name='myImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to='')),
            ],
        ),
        migrations.DeleteModel(
            name='File',
        ),
    ]
