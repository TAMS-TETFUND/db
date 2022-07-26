# Generated by Django 4.0.3 on 2022-07-14 12:29

import datetime
from django.db import migrations, models
import django.db.models.expressions
import django.db.models.functions.text
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0004_alter_attendancesession_start_time'),
    ]

    operations = [
        migrations.CreateModel(
            name='NodeDevice',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('token', models.CharField(max_length=64)),
            ],
        ),
        migrations.RemoveConstraint(
            model_name='stafftitle',
            name='unique_title',
        ),
        migrations.AddField(
            model_name='appuser',
            name='sex',
            field=models.IntegerField(choices=[(1, 'Male'), (2, 'Female')], default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='appuser',
            name='face_encodings',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='appuser',
            name='fingerprint_template',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='attendancesession',
            name='start_time',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 14, 12, 29, 15, 899854, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='student',
            name='face_encodings',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='fingerprint_template',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddConstraint(
            model_name='stafftitle',
            constraint=models.UniqueConstraint(django.db.models.functions.text.Upper(django.db.models.functions.text.Replace('title', django.db.models.expressions.Value('.'), django.db.models.expressions.Value(''))), name='conflicting_title_abbreviation'),
        ),
        migrations.AddConstraint(
            model_name='stafftitle',
            constraint=models.UniqueConstraint(django.db.models.functions.text.Upper('title_full'), name='unique_title'),
        ),
    ]
