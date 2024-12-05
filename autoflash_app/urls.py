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
    gerar_flashcard,
    listar_flashcards_por_conteudo,
    obter_um_conteudo,
    detalhar_flashcard,
    contar_flashcards,
    contar_conteudos,
    obter_proximo_flashcard,
    atualizar_flashcard_revisao,
    flashcards_para_amanha
)

urlpatterns = [
    path('gerar_flashcard/', gerar_flashcard, name='gerar_flashcard'),
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    
    path('conteudo/', cadastrar_conteudo, name='cadastrar_conteudo'),
    path('conteudo/lista/', listar_conteudos, name='listar_conteudos'),
    path('conteudo/<int:pk>/atualizar/', atualizar_conteudo, name='atualizar_conteudo'),
    path('conteudo/<int:pk>/excluir/', excluir_conteudo, name='excluir_conteudo'),
    path('conteudo/<int:conteudo_id>/', obter_um_conteudo, name='obter_um_conteudo'),
    path('conteudo/contar/', contar_conteudos, name='contar_conteudos_flashcards'),

    path('flashcard/', cadastrar_flashcard, name='cadastrar_flashcard'),
    path('flashcard/conteudo/<int:conteudo_id>/', listar_flashcards_por_conteudo, name='listar_flashcards_por_conteudo'),
    path('flashcard/lista/', listar_flashcards, name='listar_flashcards'),
    path('flashcard/<int:pk>/atualizar/', atualizar_flashcard, name='atualizar_flashcard'),
    path('flashcard/<int:pk>/', detalhar_flashcard, name='detalhar_flashcard'),
    path('flashcard/<int:pk>/excluir/', excluir_flashcard, name='excluir_flashcard'),
    path('flashcard/contar/', contar_flashcards, name='contar_flashcards'),

    path('proximo_flashcard/<int:conteudo_id>/', obter_proximo_flashcard, name='obter_proximo_flashcard'),
    path('flashcard/<int:flashcard_id>/atualizar_revisao/', atualizar_flashcard_revisao, name='atualizar_flashcard_revisao'),
    path('flashcards-para-amanha/', flashcards_para_amanha, name='flashcards-para-amanha'),



]
