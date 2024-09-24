from django.db import models

class Flashcard(models.Model):
    pergunta = models.TextField()
    resposta = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.pergunta
