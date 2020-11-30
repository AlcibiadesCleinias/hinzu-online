from django.urls import path

from . import views

app_name = 'web_app'

urlpatterns = [
    path('', views.upload_file, name='upload_file'),
    path('result/<str:domain>/', views.show_result, name='show_result'),
    path('api/addlike/', views.addlike, name='addlike'),
    path('api/fetch-image/<str:image_path_crypted>/', views.fetchImage, name='fetchImage'),
    path('favicon.ico/', views.favicon, name='favicon'),
    # 4 reactApp
    path('api-react/addlike/', views.RateImgView.as_view(), name='react_addlike'),
    path('api-react/upload/', views.UploadImgView.as_view(), name= 'upload_view'),
]
