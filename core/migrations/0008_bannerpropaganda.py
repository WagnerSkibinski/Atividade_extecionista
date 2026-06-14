from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0007_perfilusuario"),
    ]

    operations = [
        migrations.CreateModel(
            name="BannerPropaganda",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
                ("titulo", models.CharField(max_length=120)),
                ("imagem", models.ImageField(upload_to="banners/")),
                ("link", models.URLField(blank=True)),
                ("ativo", models.BooleanField(default=True)),
                ("ordem", models.PositiveIntegerField(default=0)),
            ],
            options={
                "verbose_name": "Banner de Propaganda",
                "verbose_name_plural": "Banners de Propaganda",
                "ordering": ["ordem", "-criado_em"],
            },
        ),
    ]
