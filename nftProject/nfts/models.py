from django.db import models

# Create your models here.


class NFTSeriesModel(models.Model):
    name = models.CharField(max_length=16, null=False, db_index=True)
    series = models.ForeignKey(to='NFTSeriesModel', on_delete=models.CASCADE, max_length=16, null=True, default='park')
    describe = models.TextField(max_length=255)


class NFTSetModel(models.Model):
    name = models.CharField(max_length=16, null=False)
    series = models.ForeignKey(to='NFTSeriesModel', on_delete=models.CASCADE, max_length=16, null=True)
