# Generated by Django 4.2.11 on 2024-05-14 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MarketData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('공중화장실보유여부', models.CharField(max_length=1)),
                ('사용가능상품권', models.CharField(max_length=200)),
                ('소재지도로명주소', models.CharField(max_length=200)),
                ('소재지지번주소', models.CharField(max_length=200)),
                ('시장명', models.CharField(max_length=200)),
                ('주차장보유여부', models.CharField(max_length=1)),
            ],
        ),
    ]