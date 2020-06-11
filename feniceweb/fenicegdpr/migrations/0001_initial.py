# Generated by Django 3.0.2 on 2020-06-11 17:39

from django.db import migrations, models
import django.db.models.expressions
import fenicemisc.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GDPRAgreement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=4096)),
                ('text', fenicemisc.fields.CleanHtmlField(max_length=8192)),
                ('version', models.CharField(max_length=1024)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='GDPRPolicy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=8192)),
                ('version', models.CharField(max_length=1024, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AddConstraint(
            model_name='gdprpolicy',
            constraint=models.CheckConstraint(check=models.Q(created__lte=django.db.models.expressions.F('last_modified')), name='gdprpolicy_correct_datetime'),
        ),
        migrations.AddConstraint(
            model_name='gdpragreement',
            constraint=models.UniqueConstraint(fields=('name', 'version'), name='unique_name_version'),
        ),
        migrations.AddConstraint(
            model_name='gdpragreement',
            constraint=models.CheckConstraint(check=models.Q(created__lte=django.db.models.expressions.F('last_modified')), name='gdpragreement_correct_datetime'),
        ),
    ]