from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import get_user_model

class CustomUser(AbstractUser):
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    
    def __str__(self):
        return self.username


class Conteudo(models.Model):
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    usuario = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        return self.titulo


class Flashcard(models.Model):
    pergunta = models.TextField()
    resposta = models.TextField()
    conteudo = models.ForeignKey(Conteudo, on_delete=models.CASCADE)  # Remove null=True e blank=True
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='flashcards')
    
    def __str__(self):
        return f"Flashcard: {self.pergunta[:30]}..."        
