from django.db import models


class EpidemicInfo(models.Model):
    country_name = models.CharField(max_length=50, blank=True, null=True)
    add_num = models.IntegerField(blank=True, null=True)
    count_num = models.IntegerField(blank=True, null=True)
    cure_num = models.IntegerField(blank=True, null=True)
    death_num = models.IntegerField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)
