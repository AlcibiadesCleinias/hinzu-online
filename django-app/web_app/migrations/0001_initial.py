# Generated by Django 3.0.5 on 2020-04-24 16:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Embed',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path2similar', models.CharField(max_length=200)),
                ('embeds_of_original', models.BinaryField()),
            ],
        ),
        migrations.CreateModel(
            name='Rate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rate', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('path2combined', models.CharField(max_length=200)),
                ('pub_date', models.DateTimeField(verbose_name='date published')),
                ('embeds', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web_app.Embed')),
            ],
        ),
    ]