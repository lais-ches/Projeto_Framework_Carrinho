# AUTORA: LAÍS RODRIGUES
# PROJETO CARRINHO DE COMPRAS FRAMEWORK

from fastapi import FastAPI
from typing import List
from pydantic import BaseModel


app = FastAPI()

OK = "OK"
FALHA = "FALHA"


# Classe representando os dados do endereço do cliente
class Endereco(BaseModel):
    id: int
    rua: str
    cep: str
    cidade: str
    estado: str


# Classe representando os dados do cliente
class Usuario(BaseModel):
    id: int
    nome: str
    email: str
    senha: str


# Classe representando a lista de endereços de um cliente
class ListaDeEnderecosDoUsuario(BaseModel):
    usuario: Usuario
    enderecos: List[Endereco] = []


# Classe representando os dados do produto
class Produto(BaseModel):
    id: int
    nome: str
    descricao: str
    preco: float


# Classe representando o carrinho de compras de um cliente com uma lista de produtos
class CarrinhoDeCompras(BaseModel):
    id_usuario: int
    lista_produtos: List[Produto] = []
    preco_total: float
    quantidade_de_produtos: int


db_usuarios = {}
db_produtos = {}
db_end = {}      # enderecos_dos_usuarios
db_carrinhos = {}


# Mensagem de Boas Vindas
@app.get("/")
async def bem_vinda():
    site = "Seja bem vind@ ao Magalu, o maior site de varejo do Brasil! Aqui você encontra uma variedade de produtos e com preços camaradas!\n\
            Para iniciar, crie o seu usuário com nome, email e senha. Adicione o seu endereço, dê início às compras e Vem ser Feliz!! :D"
    return site.replace('\n', '')



# Criar um usuário,
# se tiver outro usuário com o mesmo ID retornar falha, 
# se o email não tiver o @ retornar falha, 
# senha tem que ser maior ou igual a 3 caracteres, 
# senão retornar OK
@app.post("/usuario/")
async def criar_usuário(usuario: Usuario):
    if usuario.id in db_usuarios:           # se o usuário não está registrado
        return FALHA                        # retorna falha
    if "@" not in usuario.email:            # se não tem @ no email do usuario
        return FALHA                        # retorna falha
    if len(usuario.senha) < 3:              # se a senha tem menos que 3 caracteres
        return FALHA                        # retorna falha
    db_usuarios[usuario.id] = usuario       # salva o usuario na memória
    return OK


# Se o id do usuário existir, retornar os dados do usuário
# senão retornar falha
@app.get("/usuario/")
async def retornar_usuario(id: int):
    if id in db_usuarios:                   # se o usuário estiver registrado na memória
        return db_usuarios[id]              # retorna o usuário
    return FALHA


# Se existir um usuário com exatamente o mesmo nome, retornar os dados do usuário
# senão retornar falha
@app.get("/usuario/nome")
async def retornar_usuario_com_nome(nome: str):
    for usuario in db_usuarios.values():    # percorre a lista de usuários (que é um dicionário)
        if usuario.nome == nome:            # se encontrar um usuario com o mesmo nome solicitado
            return usuario                  # retorna o usuário
    return FALHA



# Retornar todos os emails que possuem o mesmo domínio              ########## essa parte não foi solicitada
# (domínio do email é tudo que vêm depois do @)
# senão retornar falha
# @app.get("/usuarios/emails/")
# async def retornar_emails(dominio: str):
#     return FALHA


# Se o id do usuário existir, deletar o usuário e retornar OK
# senão retornar falha
# ao deletar o usuário, deletar também endereços e carrinhos vinculados a ele
@app.delete("/usuario/")
async def deletar_usuario(id: int):
    if id in db_usuarios:                   # se existe um usuario com essa id
        db_usuarios.pop(id)                 # deleta o usuario
        return OK
    return FALHA


# Se não existir usuário com o id_usuario retornar falha, 
# senão cria um endereço, vincula ao usuário e retornar OK
@app.post("/usuario/{id_usuario}/endereco/")
async def criar_endereco(endereco: Endereco, id_usuario: int):
    if id_usuario not in db_usuarios:                                                                       # se não existir o id do usuario
        return FALHA                                                                                        # retorna falha
    if id_usuario in db_end:                                                                                # se existir endereços vinculados ao usuario
        db_end[id_usuario].enderecos.append(endereco)                                                       # anexa o endereço à lista de endereços
    else:                                                                                                   # se não existir endereço
        nova_lista = ListaDeEnderecosDoUsuario(usuario=db_usuarios[id_usuario], enderecos=[endereco])       # um novo endereço é criado e vinculado ao usuário
        db_end[id_usuario] = nova_lista                                                                     # o novo endereço e registrado na memória (que é um dicionário)
    return OK


# Se não existir usuário com o id_usuario retornar falha, 
# senão retornar uma lista de todos os endereços vinculados ao usuário
# caso o usuário não possua nenhum endereço vinculado a ele, retornar 
# uma lista vazia
### Estudar sobre Path Params (https://fastapi.tiangolo.com/tutorial/path-params/)
@app.get("/usuario/{id_usuario}/enderecos/")
async def retornar_enderecos_do_usuario(id_usuario: int):
    if id_usuario not in db_usuarios:                   # se não  existir usuário com essa id
        return FALHA                                    # retorna falha
    if id_usuario in db_end:                            # se existir uma lista de endereços vinculada ao usuário
        return db_end[id_usuario].enderecos             # retorna a lista de endereços
    else:                                               # senão
        lista_vazia = []                                # cria uma lista vazia
        return lista_vazia                              # retorna uma lista vazia
     

# Se não existir endereço com o id_endereco retornar falha, 
# senão deleta endereço correspondente ao id_endereco e retornar OK
# (lembrar de desvincular o endereço ao usuário)
@app.delete("/endereco/{id_endereco}/")
async def deletar_endereco(id_endereco: int):
    for lista_endereco in db_end.values():                  # percorre o dicionário de listas de endereços           
        for endereco in lista_endereco.enderecos:           # percorre cada lista de endereço
            if id_endereco == endereco.id:                  # se existir um endereço com o id solicitado
                lista_endereco.enderecos.remove(endereco)   # remove o endereço
                if len(lista_endereco.enderecos) == 0:      # se a lista de endereços for "0"
                    db_end.pop(lista_endereco.usuario.id)   # a lista de endereços é deletada se estiver vazia
                return OK
    return FALHA



# Se tiver outro produto com o mesmo ID retornar falha, 
# senão cria um produto e retornar OK
@app.post("/produto/")
async def criar_produto(produto: Produto):
    if produto.id in db_produtos:               # se tiver um produto com o mesmo id no dicionário de produtos
        return FALHA                            # retorna falha
    else:                                       
        db_produtos[produto.id] = produto       # cria um produto e registra na memória (no dicionário)
    return OK


@app.get("/produto/{id_produto}")               ########## essa chamada não foi solicitada, mas incluí para eu poder visualizar os produtos cadastrados
async def pegar_produto(id_produto: int):
    if id_produto in db_produtos:               # se houver produto com um certo id
        return db_produtos[id_produto]          # retorna o produto na memória 
    return FALHA

# Se não existir produto com o id_produto retornar falha, 
# senão deleta produto correspondente ao id_produto e retornar OK
# (lembrar de desvincular o produto dos carrinhos do usuário)
@app.delete("/produto/{id_produto}/")
async def deletar_produto(id_produto: int):
    if id_produto in db_produtos:                                               # se existir um produto com o id de produto solicitado
        for carrinho in db_carrinhos.values():                                  # percorre o dicionário de carrinhos
            for produto in carrinho.lista_produtos:                             # percorre a lista de produtos de cada carrinho
                if produto.id==id_produto:                                      # se o id do produto for igual ao id solicitado
                    carrinho.lista_produtos.remove(db_produtos[id_produto])     # remove o produto do carrinho
                    carrinho.preco_total -= db_produtos[id_produto].preco       # atualiza o valor do carrinho (retirando o valor do produto removido)
                    carrinho.quantidade_de_produtos -= 1                        # atualiza a quantidade de produtos do carrinho (retirando a quantidade do produto removido)
        db_produtos.pop(id_produto)                                             # deleta o produto da lista (que é o dicionário)
        return OK
    return FALHA
    


# Se não existir usuário com o id_usuario ou id_produto retornar falha, 
# se não existir um carrinho vinculado ao usuário, crie o carrinho
# e retornar OK
# senão adiciona produto ao carrinho e retornar OK
@app.post("/carrinho/{id_usuario}/{id_produto}/")
async def adicionar_carrinho(id_usuario: int, id_produto: int):
    if id_usuario not in db_usuarios or id_produto not in db_produtos:                  # se não existir id de usuário e id de produtos nos seus respectivos dicionários
        return FALHA                                                                    # retorna falha
    if id_usuario in db_carrinhos:                                                      # se exisir um carrinho vinculado ao id de usuário na memória
        db_carrinhos[id_usuario].lista_produtos.append(db_produtos[id_produto])         # anexa um novo produto à lista de produtos do carrinho
        db_carrinhos[id_usuario].preco_total += (db_produtos[id_produto].preco)         # atualiza o preço total do carrinho
        db_carrinhos[id_usuario].quantidade_de_produtos += 1                            # atualiza a quantidade de produtos do carrinho
    else:                                                                               # se não existir carrinho vinculado ao id de usuário na memória
        criar_carrinho = CarrinhoDeCompras(id_usuario=id_usuario, lista_produtos=[db_produtos[id_produto]],  # cria um carrinho vinculado ao id e inclui o produto nele
                        preco_total=(db_produtos[id_produto].preco), quantidade_de_produtos=1)
        db_carrinhos[id_usuario] = criar_carrinho                                       # registra o carrinho na memória (no dicionário)
    return OK


# Se não existir carrinho com o id_usuario retornar falha, 
# senão retorna o carrinho de compras.
@app.get("/carrinho/{id_usuario}/")
async def retornar_carrinho(id_usuario: int):
    if id_usuario not in db_carrinhos:          # se não existir carrinho vinculado ao id de usuário 
        return FALHA                            # retorna falha
    return db_carrinhos[id_usuario]             # se existir, retorna o carrinho de compras


########### Criei essa chamada para remover produtos do carrinho de compras. 
# Se não existir usuário com o id_usuario ou id_produto ou carrinho retornar falha
# Se tiver, retornar o carrinho atualizado 
@app.delete("/carrinho/{id_usuario}/{id_produto}/")
async def deletar_produto_carrinho(id_usuario: int, id_produto: int):
    if id_usuario not in db_usuarios or id_produto not in db_produtos or id_usuario not in db_carrinhos:    # se nao existir id de usuario, produto ou carrinhos nos seus respecitivos dicionarios
        return FALHA                                                                                        # retorna falha
    for produto in db_carrinhos[id_usuario].lista_produtos:                                         # percorre a lista de produtos do carrinho
        if produto.id==id_produto:                                                                  # se o id do produto for igual ao id solicitado 
            db_carrinhos[id_usuario].lista_produtos.remove(db_produtos[id_produto])                 # remove o produto do carrinho
            db_carrinhos[id_usuario].preco_total -= db_produtos[id_produto].preco                   # atualiza o valor do carrinho (retirando o valor do produto removido) 
            db_carrinhos[id_usuario].quantidade_de_produtos -= 1                                    # atualiza a quantidade de produtos do carrinho (retirando a quantidade do produto removido)
            return OK
    return FALHA


# Se não existir carrinho com o id_usuario retornar falha, 
# senão retorna o o número de itens e o valor total do carrinho de compras.
@app.get("/carrinho/{id_usuario}/total/")
async def retornar_total_carrinho(id_usuario: int):                                                 
    if id_usuario not in db_carrinhos:                                                              # se nao existir carrinho vinculado ao id de usuário
        return FALHA                                                                                # retorna falha
    return db_carrinhos[id_usuario].quantidade_de_produtos, db_carrinhos[id_usuario].preco_total    # retorna a quantidade de produtos do carrinho e seu preço total

# Se não existir usuário com o id_usuario retornar falha, 
# senão deleta o carrinho correspondente ao id_usuario e retornar OK
@app.delete("/carrinho/{id_usuario}/")
async def deletar_carrinho(id_usuario: int):
    if id_usuario not in db_carrinhos:          # se nao existir carrinho vinculado ao id de usuário
        return FALHA                            # retorna falha
    db_carrinhos.pop(id_usuario)                # deleta o carrinho vinculado ao id do usuário
    return OK
