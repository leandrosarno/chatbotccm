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
    creds_dict = json.loads(os.environ.get('GOOGLE_JSON'))
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open("carteirinhas do CEU") # <--- VERIFIQUE O NOME
    return spreadsheet

@app.route('/chat', methods=['POST'])
def chat():
    dados = request.json
    msg = dados.get("mensagem", "").lower().strip()

    try:
        spreadsheet = get_spreadsheet()

        # MENU: ATIVIDADES -> Puxa da aba TURMAS
        if "atividades" in msg:
            aba_turmas = spreadsheet.worksheet("TURMAS")
            dados = aba_turmas.get_all_records()
            
            tabela = "<b>📚 Nossas Atividades/Turmas:</b><br><table style='width:100%; border-collapse:collapse; font-size:12px;'>"
            tabela += "<tr style='background-color:#ddd;'><th>Turma</th><th>Horário</th></tr>"
            for linha in dados:
                tabela += f"<tr><td>{linha.get('MODALIDADE')}</td><td>{linha.get('HOR_AULAS')}</td></tr>"
            tabela += "</table>"
            return jsonify({"resposta": tabela})

        # MENU: SECRETARIA/FAQ -> Puxa da aba FAQ
        elif "secretaria" in msg or "duvidas" in msg:
            aba_faq = spreadsheet.worksheet("FAQ")
            dados_faq = aba_faq.get_all_records()
            
            respostas = "<b>📋 Perguntas Frequentes:</b><br><br>"
            for linha in dados_faq:
                respostas += f"<b>{linha.get('Pergunta')}</b>: {linha.get('Resposta')}<br><br>"
            return jsonify({"resposta": respostas})

        # MENU: TELEFONE
        elif "telefone" in msg:
            return jsonify({"resposta": "<b>📞 PABX: 3396-5600</b><br>Opção 1: Secretaria | Opção 2: CEI | Opção 3: EMEI | Opção 4: EMEF"})

        # RESPOSTA PADRÃO
        else:
            return jsonify({"resposta": "Por favor, escolha uma das opções no menu abaixo para que eu possa te ajudar! 👇"})

    except Exception as e:
        print(f"Erro: {e}")
        return jsonify({"resposta": "Houve um erro ao acessar a planilha. Verifique as configurações."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
