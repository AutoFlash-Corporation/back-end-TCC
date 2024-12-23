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
from datetime import date, timedelta

from django.utils.timezone import now




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
 
    
    
    
    
#---------------- login e cadastro -----------------------   
    
    

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





#-------------------- conteudos-------------------------


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



@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Apenas usuários autenticados podem acessar
def obter_um_conteudo(request, conteudo_id):
    """
    Endpoint para obter as informações detalhadas de um único conteúdo.
    """
    try:
        # Busca o conteúdo pelo ID e verifica se pertence ao usuário autenticado
        conteudo = Conteudo.objects.get(id=conteudo_id, usuario=request.user)
        
        # Serializa os dados do conteúdo
        serializer = ConteudoSerializer(conteudo)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Conteudo.DoesNotExist:
        # Retorna erro se o conteúdo não for encontrado ou não pertencer ao usuário
        return Response({"error": "Conteúdo não encontrado ou não pertence ao usuário."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Erro ao obter conteúdo {conteudo_id}: {str(e)}")
        return Response({"error": "Ocorreu um erro ao processar a solicitação."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def contar_conteudos(request):
    """
    Retorna o total de conteúdos do usuário autenticado.
    """
    try:
        usuario = request.user
        total_conteudos = Conteudo.objects.filter(usuario=usuario).count()
        
        return Response({
            "total_conteudos": total_conteudos,
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Erro ao contar conteúdos: {str(e)}")
        return Response({"error": "Erro ao processar a solicitação."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)










# ------------------------------ flashcards -----------------------------


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



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_flashcards_por_conteudo(request, conteudo_id):
    try:
        # Verifica se o conteúdo existe e pertence ao usuário
        conteudo = Conteudo.objects.get(id=conteudo_id, usuario=request.user)
        
        # Filtra flashcards relacionados ao conteúdo
        flashcards = Flashcard.objects.filter(conteudo=conteudo)

        # Verifica se flashcards são encontrados
        if not flashcards.exists():
            return Response({"message": "Nenhum flashcard encontrado para este conteúdo."}, status=status.HTTP_404_NOT_FOUND)
        
        # Serializa os flashcards
        serializer = FlashcardSerializer(flashcards, many=True)
        return Response(serializer.data)
    except Conteudo.DoesNotExist:
        return Response({"error": "Conteúdo não encontrado ou não pertence ao usuário."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Erro ao listar flashcards para o conteúdo {conteudo_id}: {str(e)}")
        return Response({"error": "Ocorreu um erro ao processar a solicitação."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def detalhar_flashcard(request, pk):
    """
    Endpoint para obter os detalhes de um único flashcard.
    """
    try:
        # Buscar o flashcard pelo ID e validar o proprietário
        flashcard = Flashcard.objects.get(pk=pk, usuario=request.user)
        serializer = FlashcardSerializer(flashcard)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Flashcard.DoesNotExist:
        return Response({"error": "Flashcard não encontrado ou não pertence ao usuário."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Erro ao obter detalhes do flashcard {pk}: {str(e)}")
        return Response({"error": "Ocorreu um erro ao processar a solicitação."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def contar_flashcards(request):
    """
    Retorna o número total de flashcards que o usuário possui.
    """
    try:
        # Contar os flashcards do usuário autenticado
        total_flashcards = Flashcard.objects.filter(usuario=request.user).count()
        return Response({"total_flashcards": total_flashcards}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Erro ao contar flashcards: {str(e)}")
        return Response({"error": "Ocorreu um erro ao processar a solicitação."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@api_view(['POST'])
@permission_classes([IsAuthenticated])
def revisar_flashcards(request):
    """
    Endpoint para revisar flashcards. O cliente envia o ID do flashcard e o resultado da revisão.
    """
    try:
        flashcard_id = request.data.get('flashcard_id')  # ID do flashcard que está sendo revisado
        resultado = request.data.get('resultado')  # Resultado da revisão: 'nao_lembrei', 'lembrei_dificuldade', etc.

        if not flashcard_id or not resultado:
            return Response({"error": "ID do flashcard e resultado são obrigatórios."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Buscar o flashcard
        flashcard = Flashcard.objects.get(id=flashcard_id, usuario=request.user)

        # Atualizar a revisão do flashcard
        flashcard.atualizar_revisao(resultado)

        # Retornar o próximo flashcard ou uma mensagem informando que acabou
        flashcards_a_revisar = Flashcard.objects.filter(conteudo=flashcard.conteudo, next_review__lte=datetime.now()).order_by('next_review')
        
        if flashcards_a_revisar.exists():
            proximo_flashcard = flashcards_a_revisar.first()
            return Response({
                "proximo_flashcard": FlashcardSerializer(proximo_flashcard).data
            }, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Todos os flashcards foram revisados para hoje."}, status=status.HTTP_200_OK)

    except Flashcard.DoesNotExist:
        return Response({"error": "Flashcard não encontrado."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obter_proximo_flashcard(request, conteudo_id):
    """
    Retorna o próximo flashcard a ser revisado para um conteúdo específico.
    """
    try:
        usuario = request.user
        conteudo = Conteudo.objects.get(id=conteudo_id, usuario=usuario)

        # Buscar o próximo flashcard com revisão pendente
        flashcard = Flashcard.objects.filter(
            conteudo=conteudo,
            usuario=usuario,
            next_review__lte=date.today(),  # Verifica datas de revisão pendentes
        ).order_by('next_review').first()

        if not flashcard:
            return Response({"message": "Nenhum flashcard disponível para revisão."}, status=status.HTTP_404_NOT_FOUND)

        # Serializar e retornar o flashcard
        serializer = FlashcardSerializer(flashcard)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Conteudo.DoesNotExist:
        return Response({"error": "Conteúdo não encontrado ou não pertence ao usuário."}, status=status.HTTP_404_NOT_FOUND)
    
    
    
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def atualizar_flashcard_revisao(request, flashcard_id):
    
    #Atualiza a eficácia e intervalo de um flashcard com base na resposta do usuário.
    
    try:
        usuario = request.user
        flashcard = Flashcard.objects.get(id=flashcard_id, usuario=usuario)

        resultado = request.data.get("resultado")
        if resultado not in ["nao_lembrei", "lembrei_dificuldade", "lembrei_bem", "lembrei_facilidade"]:
            return Response({"error": "Resultado inválido."}, status=status.HTTP_400_BAD_REQUEST)

        # Atualizar o flashcard com base no resultado
        flashcard.atualizar_revisao(resultado)
        return Response({"message": "Flashcard atualizado com sucesso."}, status=status.HTTP_200_OK)
    except Flashcard.DoesNotExist:
        return Response({"error": "Flashcard não encontrado ou não pertence ao usuário."}, status=status.HTTP_404_NOT_FOUND)
    





@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Garantir que o usuário esteja autenticado
def flashcards_para_amanha(request):
    # Obter a data de amanhã
    amanha = (now().date() + timedelta(days=1))
    
    # Filtrar flashcards do usuário autenticado cuja data de próxima revisão é amanhã
    flashcards_amanha = Flashcard.objects.filter(usuario=request.user, next_review=amanha)
    
    # Contar o número de flashcards
    flashcards_count = flashcards_amanha.count()
    
    return Response({"flashcards_para_amanha": flashcards_count})



@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Garantir que o usuário esteja autenticado
def flashcards_para_hoje(request):
    hoje = now().date()
    flashcards_hoje = Flashcard.objects.filter(usuario=request.user, next_review=hoje)
    flashcards_count = flashcards_hoje.count()
    return Response({"flashcards_para_hoje": flashcards_count})