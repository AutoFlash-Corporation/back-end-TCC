from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer, LoginSerializer, ConteudoSerializer, FlashcardSerializer
from .models import Conteudo, Flashcard
from django.contrib.auth import login
from rest_framework_simplejwt.tokens import RefreshToken

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
