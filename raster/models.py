from django.db import models

class FloodRiskZone(models.Model):
    name = models.CharField(max_length=255)
    raster = models.FileField(upload_to='rasters/')
    classified_raster = models.FileField(upload_to='vector_data/')
    min_value = models.FloatField(null=True, blank=True)
    max_value = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name