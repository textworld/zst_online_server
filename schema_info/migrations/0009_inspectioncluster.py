# Generated by Django 3.1.7 on 2021-05-07 02:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schema_info', '0008_auto_20210506_0908'),
    ]

    operations = [
        migrations.CreateModel(
            name='InspectionCluster',
            fields=[
                ('mysqlcluster_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='schema_info.mysqlcluster')),
                ('inspect_need', models.BooleanField(default=True)),
            ],
            bases=('schema_info.mysqlcluster',),
        ),
    ]
