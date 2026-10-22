from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Isso permite que o HTML fale com o Python

# Aqui criamos um "dicionário" de respostas simples
# Você pode adicionar quantas quiser!
RESPONSAS = {
    "ola": "Olá! Sou o assistente do CEU Caminho do Mar. Em que posso ajudar?",
    "horario": "o CEU funciona todos os dias, das 07h às 23h.",
    "secretaria": "A secretaria funciona de segunda a sexta, das 07h às 20h.",
    "ajuda": "Você pode me perguntar sobre: Horários, Secretaria ou Provas."
}

@app.route('/chat', methods=['POST'])
def chat():
    dados = request.json
    mensagem_usuario = dados.get("mensagem", "").lower()

    # Busca a resposta no dicionário. Se não achar, dá uma resposta padrão.
    resposta = RESPONSAS.get(mensagem_usuario, "Desculpe, não entendi. Tente digitar 'ajuda' para ver o que posso fazer.")

    return jsonify({"resposta": resposta})

if __name__ == '__main__':
    app.run(debug=True)