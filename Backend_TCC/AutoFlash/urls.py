from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FlashcardViewSet
from django.contrib import admin  # Importando o admin aqui

# Criação do roteador
router = DefaultRouter()
router.register(r'flashcards', FlashcardViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),  # Remova essa linha se não precisar do admin aqui
    path('', include(router.urls)),  # Roteando os endpoints do FlashcardViewSet
]
