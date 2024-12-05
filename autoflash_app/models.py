from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import get_user_model
from datetime import timedelta, date, datetime

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
    
    # Campos de repetição espaçada
    intervalo = models.IntegerField(default=0)  # Intervalo de repetição em dias
    eficacia = models.IntegerField(default=0)  # Eficácia do cartão (baseada na resposta do usuário)
    next_review = models.DateField(default=date.today, null=True, blank=True)  # Define a revisão inicial para hoje
    usuariointervalo = models.IntegerField(default=1)  # Campo adicionado

    def atualizar_revisao(self, resultado):
        if resultado == "nao_lembrei":
            self.intervalo = 1  # Revisar no dia seguinte
        elif resultado == "lembrei_dificuldade":
            self.intervalo = max(2, self.intervalo)  # Aumentar o intervalo, mas não muito
        elif resultado == "lembrei_bem":
            self.intervalo = int(self.intervalo * 2.5)  # Aumentar o intervalo substancialmente
        elif resultado == "lembrei_facilidade":
            self.intervalo = int(self.intervalo * 4)  # Revisão muito mais espaçada

        self.eficacia = {"nao_lembrei": 0, "lembrei_dificuldade": 1, "lembrei_bem": 2, "lembrei_facilidade": 3}[resultado]
        self.next_review = date.today() + timedelta(days=self.intervalo)
        self.save()
        
        
    def __str__(self):
        return f"Flashcard: {self.pergunta[:30]}..."