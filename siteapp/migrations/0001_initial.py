# Generated by Django 3.2.3 on 2021-05-22 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HistoryOpModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(max_length=128, verbose_name='操作用户')),
                ('op_module', models.CharField(max_length=128, verbose_name='操作模块')),
                ('log', models.TextField(verbose_name='日志')),
                ('op_time', models.DateTimeField(auto_now_add=True, verbose_name='操作时间')),
            ],
            options={
                'verbose_name': '操作记录',
                'db_table': 't_history_op',
            },
        ),
        migrations.CreateModel(
            name='NewsModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128)),
                ('url', models.TextField()),
                ('hash', models.CharField(max_length=128)),
                ('insert_time', models.DateTimeField(auto_now_add=True, null=True)),
            ],
            options={
                'verbose_name': '新闻',
                'db_table': 't_news_list',
            },
        ),
        migrations.CreateModel(
            name='ProxyModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.GenericIPAddressField()),
                ('port', models.IntegerField()),
                ('expire_time', models.DateTimeField()),
                ('city', models.CharField(max_length=64)),
                ('isp', models.CharField(max_length=64)),
                ('call_count', models.IntegerField(default=0)),
                ('failed_count', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name': 'ip代理',
                'db_table': 't_ip_proxy',
            },
        ),
    ]
