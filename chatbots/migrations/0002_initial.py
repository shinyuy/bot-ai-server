# Generated by Django 4.2.1 on 2024-09-17 17:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('company', '0001_initial'),
        ('chatbots', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatbot',
            name='company_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='company.company'),
        ),
    ]