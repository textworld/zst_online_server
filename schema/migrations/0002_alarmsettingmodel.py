# Generated by Django 3.2.3 on 2021-07-25 04:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schema', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AlarmSettingModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stop_alarm', models.BooleanField(default=False, help_text='是否停止告警')),
                ('sql_id', models.CharField(help_text='sql id', max_length=128, null=True)),
                ('sql_print', models.TextField(help_text='sql指纹', null=True)),
                ('query_time', models.FloatField(default=0.0, help_text='查询时间阈值')),
                ('query_count', models.IntegerField(default=0, help_text='每分钟出现的次数')),
                ('delete', models.BooleanField(default=False, help_text='逻辑删除标志')),
                ('type', models.CharField(choices=[('global', 'Global'), ('schema', 'Schema'), ('SQL', 'SQL')], help_text='设置的类型', max_length=10)),
                ('schema', models.ForeignKey(db_constraint=False, default=None, help_text='库名', null=True, on_delete=django.db.models.deletion.CASCADE, to='schema.schemamodel', to_field='name')),
            ],
        ),
    ]
