import requests
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Flashcard
from .serializers import FlashcardSerializer
from django.conf import settings
from django.shortcuts import render

def index(request):
    return render(request, 'AutoFlash/index.html')

class FlashcardViewSet(viewsets.ModelViewSet):
    queryset = Flashcard.objects.all() #busca todos os flashcards
    serializer_class = FlashcardSerializer # Usa o serializer que irá definir 

    # Endpoint para gerar flashcards a partir de um resumo
    @action(detail=False, methods=['post'])
    def gerar_flashcards(self, request):
        texto = request.data.get('texto')
        
        # Enviar o texto para a API do Gemini
        gemini_response = requests.post(
            'https://api.gemini.com/generate',  # URL da API do Gemini (exemplo)
            json={'input_text': texto},
            headers={'Authorization': f'Bearer {settings.GEMINI_API_KEY}'}
        )

        # Parse da resposta da API do Gemini
        if gemini_response.status_code == 200:
            data = gemini_response.json()
            flashcards = data['flashcards']  # Assumindo que vem uma lista de flashcards

            # Armazenar os flashcards no banco de dados
            for card in flashcards:
                Flashcard.objects.create(pergunta=card['pergunta'], resposta=card['resposta'])

            return Response({'mensagem': 'Flashcards gerados e armazenados com sucesso!'})
        else:
            return Response({'erro': 'Erro ao integrar com o Gemini API'}, status=500)
