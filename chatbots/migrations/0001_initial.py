# Generated by Django 4.2.1 on 2024-09-17 17:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Chatbot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('industry', models.CharField(max_length=100, null=True)),
                ('number_of_queries', models.PositiveIntegerField(default=0)),
                ('number_of_users', models.PositiveIntegerField(default=0)),
                ('website', models.CharField(max_length=100, unique=True)),
                ('phone_number', models.CharField(max_length=100, unique=True)),
                ('public', models.BooleanField(default=True)),
                ('is_social_media_enabled', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ChatbotQuery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('query_text', models.TextField()),
                ('response_text', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('chatbot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chatbots.chatbot')),
            ],
        ),
    ]