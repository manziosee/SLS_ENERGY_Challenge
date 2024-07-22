from django.urls import path
from api.views import user_recommendation

urlpatterns = [
    path('q2', user_recommendation, name='user_recommendation'),
]
