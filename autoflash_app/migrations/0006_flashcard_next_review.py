# Generated by Django 5.1.3 on 2024-12-04 22:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('autoflash_app', '0005_remove_flashcard_prox_revisao_flashcard_eficacia_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='flashcard',
            name='next_review',
            field=models.DateField(blank=True, null=True),
        ),
    ]
