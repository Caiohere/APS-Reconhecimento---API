# Arquivo: main.py

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware  # Adicione este import
import numpy as np

# Importe as funções do seu novo módulo de banco de dados
import database
from facereco_logic import extrair_codificacao_facial, identificar_rosto

app = FastAPI(title="API de Autenticação Biométrica")

# Adicione o middleware CORS logo após criar o app
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://192.168.1.9:8080",
        "http://localhost:8080"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================================================================
# INICIALIZAÇÃO: Garante que a tabela do DB exista ao iniciar a aplicação
# ==============================================================================
@app.on_event("startup")
def startup_event():
    database.criar_tabela_se_nao_existir()

# ==============================================================================

@app.post("/registrar")    
async def register_user(nome: str = Form(...), nivel: int = Form(...), file: UploadFile = File(...)):

    database.criar_tabela_se_nao_existir()

    image_bytes = await file.read()

    if not image_bytes:
        # Se nenhum dado foi lido do arquivo, retorna um erro 400
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O arquivo enviado está vazio. Por favor, anexe uma imagem válida."
        )
    
    codificacao = extrair_codificacao_facial(image_bytes)
    
    if codificacao is None:
        return {"status": "falha", "mensagem": "Não foi possível processar a imagem. Verifique se há apenas um rosto nela."}
    
    # Usa a função do database.py para salvar o usuário
    database.salvar_usuario(nome, nivel, codificacao)
    
    id, nome, nivel = database.buscar_usuario_por_codificacao(codificacao)
    
    print(id, nome, nivel)

    return {"status": "sucesso",
             "id": id,
             "nome": nome,
             "nivel_acesso": nivel,
             "mensagem": "Usuário registrado com sucesso."}


@app.post("/autenticar")
async def authenticate_user(file: UploadFile = File(...)):
    image_bytes = await file.read()

    if not image_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O arquivo enviado está vazio. Por favor, anexe uma imagem válida."
        )

    codificacoes_conhecidas, metadados_conhecidos = database.carregar_todos_usuarios()

    if not codificacoes_conhecidas:
        return {"status": "erro", "nome": None, "id": None, "mensagem": "Nenhum usuário cadastrado no sistema para comparar."}

    resultado_identificacao = identificar_rosto(
        image_bytes,
        codificacoes_conhecidas,
        metadados_conhecidos
    )

    # Supondo que resultado_identificacao contenha 'nome' e 'id' se sucesso
    if resultado_identificacao.get("status") == "sucesso":
        return {
            "status": "sucesso",
            "nome": resultado_identificacao.get("nome"),
            "id": resultado_identificacao.get("id"),
            "nivel_acesso": resultado_identificacao.get("nivel_acesso"),
            "mensagem": "Usuário autenticado com sucesso."
        }
    else:
        return {
            "status": "erro",
            "nome": None,
            "id": None,
            "mensagem": resultado_identificacao.get("mensagem", "Falha na autenticação.")
        }