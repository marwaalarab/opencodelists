# Generated by Django 2.2.11 on 2020-04-07 13:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('ctv3', '0001_initial'),
        ('snomedct', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Mapping',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('ctv3_term_type', models.CharField(max_length=1)),
                ('map_status', models.BooleanField()),
                ('effective_date', models.DateField()),
                ('is_assured', models.BooleanField()),
                ('ctv3_concept', models.ForeignKey(db_constraint=False, on_delete=django.db.models.deletion.PROTECT, related_name='snomedct_mappings', to='ctv3.Concept')),
                ('ctv3_term', models.ForeignKey(db_constraint=False, on_delete=django.db.models.deletion.PROTECT, related_name='snomedct_mappings', to='ctv3.Term')),
                ('sct_concept', models.ForeignKey(db_constraint=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='ctv3_mappings', to='snomedct.Concept')),
                ('sct_description', models.ForeignKey(db_constraint=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='ctv3_mappings', to='snomedct.Description')),
            ],
        ),
    ]