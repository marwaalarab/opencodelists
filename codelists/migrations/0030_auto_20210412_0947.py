# Generated by Django 3.1.7 on 2021-04-12 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("codelists", "0029_auto_20210223_1123"),
    ]

    operations = [
        migrations.AddField(
            model_name="search",
            name="code",
            field=models.CharField(max_length=18, null=True),
        ),
        migrations.AlterField(
            model_name="search",
            name="term",
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddConstraint(
            model_name="search",
            constraint=models.CheckConstraint(
                check=models.Q(
                    models.Q(("code__isnull", True), ("term__isnull", False)),
                    models.Q(("code__isnull", False), ("term__isnull", True)),
                    _connector="OR",
                ),
                name="codelists_search_term_xor_code",
            ),
        ),
    ]
