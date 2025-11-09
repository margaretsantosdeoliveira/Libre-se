from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests, json
import requests.exceptions
# Importe seu dicionário local (AJUSTE O CAMINHO!)
# from source.infrastructure.persistence.bd import dicionario_libras

# Simulação do dicionário local para testes
dicionario_libras = {"olá": "https://url-video-ola.mp4", "exemplo": "https://url-video-exemplo.mp4"}

# Defina a URL real da API do Vlibras para tradução (AJUSTE CONFORME A DOC OFICIAL!)
VLIBRAS_API_URL = "SUA_URL_API_VLIBRAS_PARA_TRADUZIR" 

app = Flask(__name__, template_folder="templates")
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/translate', methods=['POST'])
def translate_to_libras():
    """
    Traduz um texto para Libras usando a API do VLibras e retorna o JSON com o URL do vídeo.
    Em caso de falha, tenta o dicionário local.
    """
    
    # 1. Obter o texto da requisição POST
    data = request.get_json()
    text_to_translate = data.get('text', '').strip()

    if not text_to_translate:
        return jsonify({'error': 'Nenhum texto fornecido para tradução.'}), 400

    # Normaliza o texto para o fallback (dicionário local)
    normalized_text = text_to_translate.lower()
    
    # 1. TENTATIVA COM A API VLIBRAS
    try:
        # A API do VLibras precisa do texto como parâmetro.
        # Use um timeout para evitar que a requisição trave.
        
        # ** IMPORTANTE: AJUSTE ESTA URL E A LÓGICA DE GERAÇÃO (ASSÍNCRONA) **
        url_com_texto = f"{VLIBRAS_API_URL}?text={text_to_translate}"
        response = requests.get(url_com_texto, timeout=15)
        
        # Se o status for 200 (SUCESSO)
        if response.status_code == 200:
            response_json = response.json()
            print(f"SUCESSO na API VLibras: {response.status_code}")
            
            # ** AJUSTE: O campo que contém a URL do vídeo na resposta da API **
            # Assumindo que a API retorna o URL do vídeo em um campo chamado 'video_url' ou 'result'
            video_url = response_json.get('video_url') or response_json.get('result')

            if video_url:
                 # Retorna o JSON com o URL do vídeo encontrado na API
                return jsonify({"result": "SUCESSO na API VLibras", "video_url": video_url})
            else:
                print("DEBUG: API VLibras retornou 200, mas o JSON não continha 'video_url'. Tentando dicionário local.")
                # Continua para o fallback se a resposta 200 não tiver o dado esperado
                
        else:
            # Erros como 400 (Bad Request), 404 (Not Found), etc.
            print(f"DEBUG: VLibras API retornou status {response.status_code}. Tentando dicionário local.")
            
    except requests.exceptions.RequestException as e:
        # Erros de conexão, timeout (que você já tratou no código anterior)
        print(f"DEBUG: Erro de conexão de rede ou timeout com VLibras API ({e.__class__.__name__}). Tentando dicionário local.")

    except json.JSONDecodeError:
        # Erro se a resposta 200 da API não for um JSON válido
        print("DEBUG: API VLibras retornou sucesso, mas com JSON inválido. Tentando dicionário local.")
        
    except Exception as e:
        # Outros erros inesperados
        print(f"DEBUG: Erro interno inesperado: {e}. Tentando dicionário local.")


    # 2. TENTATIVA COM O DICIONÁRIO INTERNO (FALLBACK)
    if normalized_text in dicionario_libras:
        video_url = dicionario_libras[normalized_text]
        print("SUCESSO no dicionário local")
        # Retorna o JSON com o URL do vídeo do dicionário local
        return jsonify({"result": "SUCESSO no dicionário local", "video_url": video_url})
    
    # 3. FALHA TOTAL
    error_detail = "Tradução falhou. A API Vlibras está inacessível (ou falhou) e o texto não está no dicionário local."
    # Retorna o erro com o status 503 (Service Unavailable)
    return jsonify({'tradução falhou': error_detail}), 503

# if __name__ == '__main__':
#     app.run(debug=True)