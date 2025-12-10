from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('houses', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='house',
            name='cover_image',
            field=models.ImageField(blank=True, max_length=500, null=True, upload_to='houses/', verbose_name='封面图'),
        ),
    ]

