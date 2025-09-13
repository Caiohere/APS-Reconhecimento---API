# Arquivo: database.py

import sqlite3
import json
import numpy as np

DB_NAME = 'usuarios.db'

def criar_tabela_se_nao_existir():
    """Conecta ao banco de dados e cria a tabela 'usuarios' se ela não existir."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            nivel_acesso INTEGER NOT NULL,
            codificacao_facial BLOB NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Tabela 'usuarios' verificada/criada com sucesso.")

import sqlite3
import numpy as np

DB_NAME = "seu_banco.db"

# NOTA: O processo de salvar a codificação no banco deve ser algo como:
# codificacao_bytes = codificacao_ndarray.tobytes()
# cursor.execute("INSERT INTO usuarios (..., codificacao_facial) VALUES (?, ?)", (..., codificacao_bytes))

def buscar_usuario_por_codificacao(codificacao_candidata: np.ndarray, tolerancia: float = 0.6):
    """
    Busca no banco de dados o usuário com a codificação facial mais próxima.
    
    Retorna os dados do usuário se a menor distância encontrada for menor que a tolerância,
    caso contrário, retorna None.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Busca TODAS as codificações e dados dos usuários
    try:
        cursor.execute("SELECT id, nome, nivel_acesso, codificacao_facial FROM usuarios")
        usuarios_com_codificacao = cursor.fetchall()
    finally:
        conn.close()

    if not usuarios_com_codificacao:
        return None

    melhor_distancia = float('inf')
    melhor_usuario_match = None

    # 2. Itera em Python para encontrar a correspondência mais próxima
    for usuario_id, nome, nivel_acesso, codificacao_blob in usuarios_com_codificacao:
        if codificacao_blob is None:
            continue

        # 3. Converte o blob do banco de dados de volta para um array numpy
        #    A presunção é que foi salvo com ndarray.tobytes()
        codificacao_db = np.frombuffer(codificacao_blob, dtype=np.float64) # Ajuste o dtype se necessário

        # 4. Calcula a distância euclidiana
        distancia = np.linalg.norm(codificacao_candidata - codificacao_db)

        # 5. Mantém o registro da menor distância encontrada
        if distancia < melhor_distancia:
            melhor_distancia = distancia
            melhor_usuario_match = {
                "id": usuario_id, 
                "nome": nome, 
                "nivel": nivel_acesso 
            }

    # 6. Verifica se a melhor correspondência está dentro da tolerância aceitável
    if melhor_distancia <= tolerancia:
        print(f"Match encontrado: {melhor_usuario_match['nome']} com distância {melhor_distancia:.4f}")
        return melhor_usuario_match["id"], melhor_usuario_match["nome"], melhor_usuario_match["nivel"]
    else:
        #print(f"Nenhum match encontrado. Menor distância foi {melhor_distancia:.4f} (acima da tolerância de {tolerancia})")
        return None

def salvar_usuario(nome: str, nivel_acesso: int, codificacao: np.ndarray):
    """
    Salva um novo usuário no banco de dados.
    Converte a codificação facial (array NumPy) para uma string JSON antes de salvar.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Converte o array NumPy para uma lista e depois para uma string JSON
    #codificacao_json = json.dumps(codificacao.tolist())

    #print(codificacao)
    codificacao_bytes = codificacao.tobytes()
    
    cursor.execute(
        "INSERT INTO usuarios (nome, nivel_acesso, codificacao_facial) VALUES (?, ?, ?)",
        (nome, nivel_acesso, codificacao_bytes)
    )
    
    conn.commit()
    conn.close()
    print(f"Usuário '{nome}' salvo no banco de dados.")

def carregar_todos_usuarios():
    """
    Carrega todos os usuários do banco de dados e converte as codificações
    de volta para arrays NumPy.
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, nome, nivel_acesso, codificacao_facial FROM usuarios")
    usuarios = cursor.fetchall()
    
    conn.close()
    
    codificacoes_conhecidas = []
    metadados_conhecidos = []
    
    for usuario in usuarios:
        codificacao_lista = json.loads(usuario['codificacao_facial'])
        codificacao_np = np.array(codificacao_lista)
        
        codificacoes_conhecidas.append(codificacao_np)
        metadados_conhecidos.append({
            "id": usuario['id'],
            "nome": usuario['nome'],
            "nivel_acesso": usuario['nivel_acesso']
        })
        
    print(f"Carregados {len(codificacoes_conhecidas)} usuários do banco de dados.")
    return codificacoes_conhecidas, metadados_conhecidos