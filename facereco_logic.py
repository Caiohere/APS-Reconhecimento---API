# Arquivo: facereco_logic.py

import face_recognition
import numpy as np
import cv2

# --- FUNÇÃO PARA O CADASTRO (REGISTRO) ---
def extrair_codificacao_facial(image_bytes: bytes):
    """
    Recebe os bytes de uma imagem, processa-a seguindo as 4 primeiras fases
    de PDI e retorna a codificação facial (vetor de 128 dimensões).

    Esta função é ideal para a etapa de registro de um novo usuário.
    """
    # ==============================================================================
    # FASE 1: SENSOR (AQUISIÇÃO) 
    # No contexto da API, a aquisição é receber os bytes e decodificá-los
    # para um formato que o OpenCV possa usar (array NumPy).
    # ==============================================================================
    np_array = np.frombuffer(image_bytes, np.uint8)
    imagem_bgr = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    
    # Se a imagem não puder ser decodificada, retorna None.
    if imagem_bgr is None:
        print("Erro: Não foi possível decodificar a imagem.")
        return None

    # ==============================================================================
    # FASE 2: PRÉ-PROCESSAMENTO 
    # A biblioteca face_recognition espera imagens no padrão de cores RGB.
    # O OpenCV carrega em BGR por padrão, então precisamos converter.
    # ==============================================================================
    imagem_rgb = cv2.cvtColor(imagem_bgr, cv2.COLOR_BGR2RGB)

    # ==============================================================================
    # FASE 3: SEGMENTAÇÃO 
    # Aqui, segmentamos a imagem para encontrar a localização dos rostos.
    # A função face_locations retorna uma lista de coordenadas (topo, dir, baixo, esq).
    # ==============================================================================
    localizacoes_rostos = face_recognition.face_locations(imagem_rgb)

    # Para um registro de qualidade, garantimos que há APENAS UM rosto na foto.
    if len(localizacoes_rostos) != 1:
        print(f"Erro: Encontrado {len(localizacoes_rostos)} rostos. Esperado 1.")
        return None

    # ==============================================================================
    # FASE 4: EXTRAÇÃO DE CARACTERÍSTICAS 
    # Convertendo o rosto localizado em um vetor numérico de 128 dimensões,
    # que é a "assinatura" única daquele rosto.
    # ==============================================================================
    codificacoes_faciais = face_recognition.face_encodings(imagem_rgb, localizacoes_rostos)
    
    #codificacao_bytes = codificacoes_faciais[0].tobytes()

    # Retorna a primeira (e única) codificação encontrada.
    return codificacoes_faciais[0]


# --- FUNÇÃO PARA A AUTENTICAÇÃO ---
def identificar_rosto(image_bytes: bytes, codificacoes_conhecidas: list, metadados_conhecidos: list):
    """
    Recebe os bytes de uma nova imagem, uma lista de codificações faciais conhecidas
    e uma lista de metadados correspondentes.
    Executa todas as 5 fases de PDI e retorna o resultado da identificação.
    """
    # As 4 primeiras fases são idênticas ao processo de extração.
    # Reutilizamos a função que já criamos.
    codificacao_rosto_desconhecido = extrair_codificacao_facial(image_bytes)

    # Se nenhum rosto único foi encontrado na imagem de teste, retorna falha.
    if codificacao_rosto_desconhecido is None:
        return {"status": "falha", "mensagem": "Não foi possível encontrar um rosto único na imagem."}

    # ==============================================================================
    # FASE 5: CLASSIFICAÇÃO E INTERPRETAÇÃO 
    # Comparamos a nova codificação facial com a lista de todas as codificações
    # conhecidas que foram carregadas do banco de dados.
    # ==============================================================================
    
    # CLASSIFICAÇÃO:
    # A função compare_faces retorna uma lista de True/False.
    # True na posição 'i' significa que a codificação desconhecida corresponde à
    # codificação conhecida na posição 'i' da lista.
    # O parâmetro 'tolerance' define o quão estrita é a comparação (padrão é 0.6).
    # Valores menores = mais estrito.
    matches = face_recognition.compare_faces(codificacoes_conhecidas, codificacao_rosto_desconhecido, tolerance=0.6)

    # INTERPRETAÇÃO:
    resultado = {"status": "falha", "mensagem": "Usuário não reconhecido."}

    # Se houve pelo menos uma correspondência (um 'True' na lista)...
    if True in matches:
        # Encontra o índice da primeira correspondência.
        primeiro_match_idx = matches.index(True)
        
        # Usa esse índice para buscar os metadados do usuário correspondente.
        metadados = metadados_conhecidos[primeiro_match_idx]
        
        # Monta a resposta de sucesso com base nos metadados.
        resultado = {
            "status": "sucesso",
            "id": metadados["id"],
            "nome": metadados["nome"],
            "nivel_acesso": metadados["nivel_acesso"]
        }

    return resultado