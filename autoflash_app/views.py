from django.contrib.auth import authenticate
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer, LoginSerializer, ConteudoSerializer, FlashcardSerializer
from .models import Conteudo, Flashcard
from django.contrib.auth import login
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse
import google.generativeai as genai
import json
import logging
import re

# Definindo o esquema de pergunta e resposta
from typing_extensions import TypedDict


class Flashcard(TypedDict):
    pergunta: str
    resposta: str


logger = logging.getLogger(__name__)




@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Apenas usuários autenticados podem acessar
def gerar_conteudo(request):
    """
    Endpoint para gerar conteúdo usando o modelo Gemini.
    O cliente deve enviar o prompt no corpo da solicitação.
    """
    try:
        # Obter os parâmetros adicionais: nível e número de cards
        nivel = request.data.get("nivel", "medio").lower()
        numero_cards = request.data.get("numero_cards")

        # Validar o número de cards (entre 5 e 15)
        if not (5 <= numero_cards <= 15):
            return Response({"error": "O número de cards deve ser entre 5 e 15."}, status=status.HTTP_400_BAD_REQUEST)

        # Validar o nível de dificuldade
        niveis_validos = ["facil", "medio", "dificil"]
        if nivel not in niveis_validos:
            return Response({"error": "O nível de dificuldade deve ser 'facil', 'medio' ou 'dificil'."}, status=status.HTTP_400_BAD_REQUEST)

        # Configurar a API Gemini
        genai.configure(api_key="AIzaSyCxk_fIvuQ1xR_vxdjGcQIEd9IlGRwp8rg")

        # Obter o conteúdo (texto base) do corpo da requisição
        conteudo = request.data.get("conteudo", "")
        if not conteudo:
            return Response({"error": "O campo 'conteudo' é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

        # Montar o prompt incluindo o conteúdo, nível e número de cards
        prompt = f"Crie {numero_cards} perguntas, com as respostas, de nível '{nivel}' com base no seguinte conteúdo: {conteudo}"

        # Usar o modelo gemini-exp-1121 diretamente
        model_name = "gemini-exp-1121"

        # Instanciar o modelo
        model = genai.GenerativeModel(model_name)

        # Gerar o conteúdo com o prompt fornecido
        response = model.generate_content(prompt)

        # Supondo que o modelo retorne as perguntas e respostas em um formato específico
        generated_content = response.text  # O conteúdo gerado pelo modelo

        # Processar o conteúdo gerado para transformá-lo em um formato JSON (perguntas e respostas)
        flashcards = []
        lines = generated_content.splitlines()

        # Loop para processar as perguntas e respostas
        for i in range(0, len(lines), 2):
            question_line = lines[i].strip()
            answer_line = lines[i+1].strip() if i+1 < len(lines) else ""

            # Remover asteriscos e outras formatações extras
            question = question_line.replace("**", "").replace("Pergunta", "").strip()
            answer = answer_line.replace("**", "").replace("Resposta", "").strip()

            # Adicionar ao flashcard apenas se a pergunta e resposta não estiverem vazias
            if question and answer:
                flashcards.append({
                    "question": question,
                    "answer": answer
                })

            # Se o número de cards atingiu o limite, parar de adicionar
            if len(flashcards) >= numero_cards:
                break

        # Retornar o JSON com as perguntas e respostas
        return Response({"flashcards": flashcards}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    
    
    
    
    
    
      
    
    

@api_view(['POST'])
def register_user(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login_user(request):
    if request.method == 'POST':
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            login(request, user)  # Login the user (optional, for session-based auth)
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Cadastrar Conteúdo
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cadastrar_conteudo(request):
    if request.method == 'POST':
        serializer = ConteudoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(usuario=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Visualizar Conteúdos
@api_view(['GET'])
def listar_conteudos(request):
    if request.method == 'GET':
        conteudos = Conteudo.objects.filter(usuario=request.user)
        serializer = ConteudoSerializer(conteudos, many=True)
        return Response(serializer.data)

# Cadastrar Flashcard
@api_view(['POST'])
def cadastrar_flashcard(request):
    if request.method == 'POST':
        serializer = FlashcardSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(usuario=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Visualizar Flashcards
@api_view(['GET'])
def listar_flashcards(request):
    if request.method == 'GET':
        flashcards = Flashcard.objects.filter(usuario=request.user)
        serializer = FlashcardSerializer(flashcards, many=True)
        return Response(serializer.data)

# Atualizar Conteúdo
@api_view(['PUT'])
def atualizar_conteudo(request, pk):
    try:
        conteudo = Conteudo.objects.get(pk=pk, usuario=request.user)
    except Conteudo.DoesNotExist:
        return Response({"error": "Conteúdo não encontrado"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = ConteudoSerializer(conteudo, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Excluir Conteúdo
@api_view(['DELETE'])
def excluir_conteudo(request, pk):
    try:
        conteudo = Conteudo.objects.get(pk=pk, usuario=request.user)
    except Conteudo.DoesNotExist:
        return Response({"error": "Conteúdo não encontrado"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        conteudo.delete()
        return Response({"message": "Conteúdo excluído com sucesso"}, status=status.HTTP_204_NO_CONTENT)

# Atualizar Flashcard
@api_view(['PUT'])
def atualizar_flashcard(request, pk):
    try:
        flashcard = Flashcard.objects.get(pk=pk, usuario=request.user)
    except Flashcard.DoesNotExist:
        return Response({"error": "Flashcard não encontrado"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = FlashcardSerializer(flashcard, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Excluir Flashcard
@api_view(['DELETE'])
def excluir_flashcard(request, pk):
    try:
        flashcard = Flashcard.objects.get(pk=pk, usuario=request.user)
    except Flashcard.DoesNotExist:
        return Response({"error": "Flashcard não encontrado"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        flashcard.delete()
        return Response({"message": "Flashcard excluído com sucesso"}, status=status.HTTP_204_NO_CONTENT)
