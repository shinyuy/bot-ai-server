# Generated by Django 4.2.1 on 2024-08-24 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_store', '0003_datastore_clip_l14_vectors_index'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datastore',
            name='company_website',
            field=models.CharField(max_length=100),
        ),
    ]