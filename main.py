from flask import Flask, request, jsonify
from flask_cors import CORS
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json

app = Flask(__name__)
CORS(app)

# --- CONFIGURAÇÃO DO GOOGLE SHEETS ---
def get_spreadsheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = json.loads(os.environ.get('GOOGLE_JSON'))
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    
    # TROQUE PELO NOME REAL DA SUA PLANILHA
    spreadsheet = client.open("carteirinhas do CEU") 
    return spreadsheet

RESPONSAS_FIXAS = {
    "ola": "Olá! Eu sou a Marina, a assistente Virtual do CEU Caminho do Mar. Você quer saber sobre nossas **Atividades**, **Turmas** ou precisa de **Ajuda**?",
    "ajuda": "Eu posso te ajudar com: <br>1. <b>Atividades/Dúvidas:</b> Basta perguntar.<br>2. <b>Turmas:</b> Digite o nome da turma ou apenas 'turmas'.<br>3. <b>Telefone:</b> Digite 'telefone'.",
}

@app.route('/chat', methods=['POST'])
def chat():
    dados = request.json
    msg_usuario = dados.get("mensagem", "").lower()

    if msg_usuario in RESPONSAS_FIXAS:
        return jsonify({"resposta": RESPONSAS_FIXAS[msg_usuario]})

    try:
        spreadsheet = get_spreadsheet()
        
        # --- LÓGICA 1: BUSCA POR TURMAS ---
        # Se a mensagem contiver a palavra "turma" ou "classe"
        if "turma" in msg_usuario or "classe" in msg_usuario:
            aba_turmas = spreadsheet.worksheet("TURMAS")
            dados_turmas = aba_turmas.get_all_records()
            
            # Se o usuário perguntou por uma turma específica (ex: "turma 1 ano a")
            # Vamos tentar encontrar qual linha da planilha bate com a mensagem
            for linha in dados_turmas:
                nome_turma = str(linha.get('Nome da Turma', '')).lower()
                if nome_turma in msg_usuario:
                    # Monta a resposta com os dados daquela turma
                    resp = f"<b>Turma: {linha.get('TURMAS')}</b><br>"
                    resp += f"👨‍🏫 Professor: {linha.get('PROFESSOR', 'Não informado')}<br>"
                    resp += f"⏰ Horário: {linha.get('HOR_AULAS', 'Não informado')}<br>"
                    resp += f"🚪 Sala: {linha.get('ESPACO', 'Não informado')}"
                    return jsonify({"resposta": resp})
            
            # Se ele disse apenas "turmas" ou não achou a específica, mostra todas em tabela
            tabela_html = "<b>Aqui estão nossas turmas:</b><br><table style='width:100%; border-collapse:collapse; font-size:12px;'>"
            tabela_html += "<tr style='background-color:#ddd;'><th>Turma</th><th>Horário</th></tr>"
            for linha in dados_turmas:
                tabela_html += f"<tr><td>{linha.get('Nome da Turma')}</td><td>{linha.get('Horário')}</td></tr>"
            tabela_html += "</table>"
            return jsonify({"resposta": tabela_html})

        # --- LÓGICA 2: BUSCA NO FAQ (Aba Nova) ---
        aba_faq = spreadsheet.worksheet("FAQ")
        dados_faq = aba_faq.get_all_records()
        
        for linha in dados_faq:
            if linha['Pergunta'].lower() in msg_usuario:
                return jsonify({"resposta": linha['Resposta']})

        return jsonify({"resposta": "Ainda não encontrei essa informação. Tente digitar 'ajuda' para ver o que posso fazer."})

    except Exception as e:
        print(f"Erro: {e}")
        return jsonify({"resposta": "Estou com problemas para acessar meus dados agora. Tente mais tarde!"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
