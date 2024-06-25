from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_raster, name='upload_raster'),
    path('raster/<int:pk>/', views.view_raster, name='view_raster'),
    path('api/flood-zones/', views.get_flood_zones_geojson, name='get_flood_zones_geojson'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


