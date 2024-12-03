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
from django.contrib import admin
import json
import logging
import re
import openai

admin.site.register(Flashcard)


# Configuração do logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

# Definindo o esquema de pergunta e resposta
from typing_extensions import TypedDict





@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Apenas usuários autenticados podem acessar
def gerar_flashcard(request):
    """
    Endpoint para gerar conteúdo usando o modelo Gemini.
    O cliente deve enviar o prompt no corpo da solicitação.
    """
    try:
        # Obter os parâmetros adicionais: nível e número de cards
        nivel = request.data.get("nivel", "medio").lower()
        numero_cards = request.data.get("numero_cards")
        usuario = request.user  # Usando o usuário autenticado
        conteudo_id = request.data.get("conteudo")  # Recebe o ID do conteúdo

        
        # Validar o número de cards (entre 5 e 15)
        if not (5 <= numero_cards <= 15):
            return Response({"error": "O número de cards deve ser entre 5 e 15."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar o nível de dificuldade
        niveis_validos = ["facil", "medio", "dificil"]
        if nivel not in niveis_validos:
            return Response({"error": "O nível de dificuldade deve ser 'facil', 'medio' ou 'dificil'."}, status=status.HTTP_400_BAD_REQUEST)
        
         # Buscar o conteúdo no banco de dados pelo ID
        try:
            conteudo_obj = Conteudo.objects.get(id=conteudo_id, usuario=usuario)
        except Conteudo.DoesNotExist:
            return Response({"error": "Conteúdo não encontrado ou não pertence ao usuário."}, status=status.HTTP_404_NOT_FOUND)
        
        conteudo_texto = conteudo_obj.descricao  # Pegar a descrição do conteúdo
        
        
        # Montar o prompt incluindo o conteúdo, nível e número de cards
        prompt = f"""
        Baseado no seguinte conteúdo:
        {conteudo_texto}

        Gere {numero_cards} flashcards de nível '{nivel}'. Cada flashcard deve ter uma pergunta e uma resposta claras e diretas. Estruture no seguinte formato:
        Pergunta: ...
        Resposta: ...
        """
        
        # Configurar a API da OpenAI
        openai.api_key = "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"
        # Fazer a chamada para o modelo GPT
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # ou "gpt-3.5-turbo"
            messages=[{
                "role": "system", "content": "Você é um assistente que gera flashcards com base em conteúdos fornecidos."
            }, {
                "role": "user", "content": prompt
            }],
            max_tokens=1500,
            temperature=0.7
        )
        
        # Processar o conteúdo gerado
        generated_content = response['choices'][0]['message']['content']
        print(f"Conteúdo gerado: {generated_content}")
        logger.info(f"Conteúdo gerado: {generated_content}")
        
        
    
        
        # Processar o conteúdo gerado para transformá-lo em um formato de flashcard
        flashcards = []
        lines = generated_content.strip().split('\n')
        card_id = 1  # Iniciando o ID dos flashcards

        for i in range(0, len(lines), 2):  # Cada par de linhas será uma pergunta e uma resposta
            title_line = lines[i].strip()
            question_line = lines[i + 1].strip() if i + 1 < len(lines) else ""
            answer_line = lines[i + 2].strip() if i + 2 < len(lines) else ""
            
            # Extrair a pergunta e resposta do conteúdo
            question = re.sub(r"^Pergunta: ", "", question_line).strip()
            answer = re.sub(r"^Resposta: ", "", answer_line).strip()
            
            
            if question and answer:
                flashcards.append({
                    "id": card_id,  # Atribuindo um ID único
                    "question": question,  # Aqui, mantemos apenas a pergunta
                    "answer": answer  # Aqui, mantemos apenas a resposta
                })
                card_id += 1  # Incrementando o ID para o próximo flashcard

        # Salvar os flashcards no banco de dados
        for flashcard in flashcards:
            Flashcard.objects.create(
                pergunta=flashcard['question'],
                resposta=flashcard['answer'],
                conteudo=conteudo_obj,
                usuario=usuario
            )
            
            
        return Response({"flashcards": flashcards}, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Erro ao gerar conteúdo: {str(e)}")
        return Response({"error": "Ocorreu um erro ao processar a solicitação."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
    
    
    
    
      
    
    

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
@permission_classes([IsAuthenticated])
def listar_conteudos(request):
    if request.method == 'GET':
        conteudos = Conteudo.objects.filter(usuario=request.user)
        serializer = ConteudoSerializer(conteudos, many=True)
        return Response(serializer.data)

# Cadastrar Flashcard
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cadastrar_flashcard(request):
    if request.method == 'POST':
        serializer = FlashcardSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(usuario=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Visualizar Flashcards
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_flashcards(request):
    try:
        # Filtra flashcards do usuário autenticado
        flashcards = Flashcard.objects.filter(usuario=request.user)
        
        # Verifica se flashcards são retornados
        if not flashcards.exists():
            return Response({"message": "Nenhum flashcard encontrado."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = FlashcardSerializer(flashcards, many=True)
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Erro ao listar flashcards: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Atualizar Conteúdo
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
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
