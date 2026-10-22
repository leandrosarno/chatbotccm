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
    # VERIFIQUE SE O NOME ABAIXO ESTÁ EXATAMENTE IGUAL AO DA SUA PLANILHA
    spreadsheet = client.open("carteirinhas do CEU") 
    return spreadsheet

RESPONSAS_FIXAS = {
    "ola": "Olá! Sou o assistente do CCM. Você quer saber sobre nossas **Atividades**, **Turmas** ou precisa de **Ajuda**?",
    "ajuda": "Eu posso te ajudar com: <br>1. <b>Atividades/Dúvidas:</b> Basta perguntar.<br>2. <b>Turmas:</b> Digite o nome da turma ou apenas 'turmas'.<br>3. <b>Telefone:</b> Digite 'telefone'.",
    "telefone": "<b>📞 PABX: 3396-5600</b><br>Consulte as opções de ramal na secretaria."
}

@app.route('/chat', methods=['POST'])
def chat():
    dados = request.json
    # .strip() remove espaços inúteis no início e no fim
    msg_usuario = dados.get("mensagem", "").lower().strip()

    # 1. BUSCA FLEXÍVEL NAS RESPOSTAS FIXAS
    # Agora ele checa se a palavra-chave está CONTIDA na frase do usuário
    for chave in RESPONSAS_FIXAS:
        if chave in msg_usuario:
            return jsonify({"resposta": RESPONSAS_FIXAS[chave]})

    try:
        spreadsheet = get_spreadsheet()
        
        # 2. BUSCA NA ABA TURMAS
        if "turma" in msg_usuario or "classe" in msg_usuario:
            aba_turmas = spreadsheet.worksheet("TURMAS")
            dados_turmas = aba_turmas.get_all_records()
            
            for linha in dados_turmas:
                nome_turma = str(linha.get('MODALIDADE', '')).lower().strip()
                if nome_turma and nome_turma in msg_usuario:
                    resp = f"<b>Turma: {linha.get('MODALIDADE')}</b><br>"
                    resp += f"👨‍🏫 Professor: {linha.get('PROFESSOR', 'Não informado')}<br>"
                    resp += f"⏰ Horário: {linha.get('HOR_AULAS', 'Não informado')}<br>"
                    resp += f"🚪 Sala: {linha.get('ESPACO', 'Não informado')}"
                    return jsonify({"resposta": resp})
            
            # Lista geral de turmas
            tabela_html = "<b>Aqui estão nossas turmas:</b><br><table style='width:100%; border-collapse:collapse; font-size:12px;'>"
            tabela_html += "<tr style='background-color:#ddd;'><th>Turma</th><th>Horário</th></tr>"
            for linha in dados_turmas:
                tabela_html += f"<tr><td>{linha.get('carteirinhas do CEU')}</td><td>{linha.get('HOR_AULAS')}</td></tr>"
            tabela_html += "</table>"
            return jsonify({"resposta": tabela_html})

        # 3. BUSCA NA ABA FAQ
        aba_faq = spreadsheet.worksheet("FAQ")
        dados_faq = aba_faq.get_all_records()
        
        for linha in dados_faq:
            pergunta_planilha = str(linha.get('Pergunta', '')).lower().strip()
            if pergunta_planilha and pergunta_planilha in msg_usuario:
                return jsonify({"resposta": linha.get('Resposta', 'Sem resposta cadastrada.')})

        return jsonify({"resposta": "Desculpe, não encontrei essa informação. Tente digitar 'ajuda' para ver o que posso fazer."})

    except Exception as e:
        print(f"Erro: {e}")
        return jsonify({"resposta": "Ops! Estou com dificuldades para ler meus dados agora. Tente novamente em instantes!"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
