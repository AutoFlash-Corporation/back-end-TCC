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
    conteudo = models.ForeignKey(Conteudo, null=True, blank=True, on_delete=models.SET_NULL)
    usuario = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        return f"Flashcard: {self.pergunta[:30]}..."
