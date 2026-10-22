from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Isso permite que o HTML fale com o Python

# Aqui criamos um "dicionário" de respostas simples
# Você pode adicionar quantas quiser!
RESPONSAS = {
    "ola": "Olá! Eu sou a Marina, a assistente virtual do CEU Caminho do Mar. Em que posso ajudar?",
    "horario": "O CEU funciona todos os dias, das 07h às 23h.",
    "secretaria": "A secretaria da Gestão funciona de segunda a sexta, das 08h às 17h.",
    "ajuda": "Você pode me perguntar sobre: Horários, Atividades Esportivas, Culturais e muito mais.",
    
    # Resposta do Telefone com Tabela HTML
    "telefone": """
    <b>📞 PABX: 3396-5600</b><br><br>
    <table style='width:100%; border-collapse:collapse; font-size:12px;'>
        <tr style='background-color:#ddd;'>
            <th style='border:1px solid #ccc; padding:4px;'>Opção</th>
            <th style='border:1px solid #ccc; padding:4px;'>Setor</th>
        </tr>
        <tr>
            <td style='border:1px solid #ccc; padding:4px; text-align:center;'>1</td>
            <td style='border:1px solid #ccc; padding:4px;'>Secretaria da Gestão</td>
        </tr>
        <tr>
            <td style='border:1px solid #ccc; padding:4px; text-align:center;'>2</td>
            <td style='border:1px solid #ccc; padding:4px;'>CEI (Educação Infantil)</td>
        </tr>
        <tr>
            <td style='border:1px solid #ccc; padding:4px; text-align:center;'>3</td>
            <td style='border:1px solid #ccc; padding:4px;'>EMEI (Ensino Infantil)</td>
        </tr>
        <tr>
            <td style='border:1px solid #ccc; padding:4px; text-align:center;'>4</td>
            <td style='border:1px solid #ccc; padding:4px;'>EMEF (Ensino Fundamental)</td>
        </tr>
    </table>
    """
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
