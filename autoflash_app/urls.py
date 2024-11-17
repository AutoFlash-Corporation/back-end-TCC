from django.urls import path
from .views import (
    register_user,
    login_user,
    cadastrar_conteudo,
    listar_conteudos,
    cadastrar_flashcard,
    listar_flashcards,
    atualizar_conteudo,
    excluir_conteudo,
    atualizar_flashcard,
    excluir_flashcard,
)

urlpatterns = [
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    
    path('conteudo/', cadastrar_conteudo, name='cadastrar_conteudo'),
    path('conteudo/lista/', listar_conteudos, name='listar_conteudos'),
    path('conteudo/<int:pk>/atualizar/', atualizar_conteudo, name='atualizar_conteudo'),
    path('conteudo/<int:pk>/excluir/', excluir_conteudo, name='excluir_conteudo'),
    
    path('flashcard/', cadastrar_flashcard, name='cadastrar_flashcard'),
    path('flashcard/lista/', listar_flashcards, name='listar_flashcards'),
    path('flashcard/<int:pk>/atualizar/', atualizar_flashcard, name='atualizar_flashcard'),
    path('flashcard/<int:pk>/excluir/', excluir_flashcard, name='excluir_flashcard'),
]
