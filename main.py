from flask import Flask, request, jsonify
from flask_cors import CORS
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json

app = Flask(__name__)
CORS(app)

def get_spreadsheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # Pegando a chave do JSON do Render
    try:
        creds_dict = json.loads(os.environ.get('GOOGLE_JSON'))
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        # 🚀 ALTERAÇÃO AQUI: Use o ID da sua planilha em vez do nome!
        # Substitua 'COLOQUE_O_ID_AQUI' pelo código gigante da sua URL
        spreadsheet = client.open_by_key('1CM5X5d6yoK1_UceTw6Sq-XG-bvwrGxcZpzcbuO6Edyk') 
        return spreadsheet
    except Exception as e:
        print(f"Erro ao conectar com Google Sheets: {e}")
        return None

@app.route('/chat', methods=['POST'])
def chat():
    dados = request.json
    msg = dados.get("mensagem", "").lower().strip()

    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({"resposta": "Erro de conexão com o banco de dados."})

        # 1. Se o usuário pediu Atividades/Turmas
        if "atividades" in msg or "turma" in msg:
            aba_turmas = spreadsheet.worksheet("TURMAS")
            dados_t = aba_turmas.get_all_records()
            
            if not dados_t:
                return jsonify({"resposta": "A aba de turmas está vazia no momento."})

            tabela = "<b>📚 Nossas Atividades/Turmas:</b><br><table style='width:100%; border-collapse:collapse; font-size:12px;'>"
            tabela += "<tr style='background-color:#ddd;'><th>Turma</th><th>Horário</th></tr>"
            for linha in dados_t:
                tabela += f"<tr><td>{linha.get('Nome da Turma', 'N/A')}</td><td>{linha.get('Horário', 'N/A')}</td></tr>"
            tabela += "</table>"
            return jsonify({"resposta": tabela})

        # 2. Se o usuário pediu Telefone
        elif "telefone" in msg:
            # Vamos buscar a resposta do telefone na aba FAQ para não ficar estático!
            aba_faq = spreadsheet.worksheet("FAQ")
            dados_faq = aba_faq.get_all_records()
            for linha in dados_faq:
                if "telefone" in linha.get('Pergunta', '').lower():
                    return jsonify({"resposta": linha.get('Resposta')})
            return jsonify({"resposta": "Informação de telefone não encontrada na planilha."})

        # 3. Qualquer outra pergunta -> Busca na aba FAQ
        else:
            aba_faq = spreadsheet.worksheet("FAQ")
            dados_faq = aba_faq.get_all_records()
            
            for linha in dados_faq:
                pergunta_planilha = str(linha.get('Pergunta', '')).lower().strip()
                if pergunta_planilha and (pergunta_planilha in msg or msg in pergunta_planilha):
                    return jsonify({"resposta": linha.get('Resposta')})

            return jsonify({"resposta": "Não encontrei essa informação na planilha. Tente clicar em um dos botões do menu!"})

    except Exception as e:
        print(f"Erro geral: {e}")
        return jsonify({"resposta": "Ocorreu um erro interno ao processar sua solicitação."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
