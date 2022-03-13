from django.urls import path
from . import views


urlpatterns = [
    path('upload_add/', views.upload_add),
    path('upload_find/', views.upload_find),
    path('delete/', views.delete),

    # These two urls should not be run directly. The two above will redirect to them appropriately
    path('upload_add/add/<str:name>', views.add_face),
    path('upload_find/find/', views.find_person)
]
