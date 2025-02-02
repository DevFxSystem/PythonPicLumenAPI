from flask import Flask, request, jsonify
from flask import send_file
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import requests
import time
import os
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)
@app.route("/gerar_imagem", methods=["GET"])
def gerar_imagem():
    """
    Gera uma imagem com base no prompt fornecido.
    ---
    parameters:
      - name: prompt
        in: query
        type: string
        required: true
        description: O prompt para gerar a imagem.
    responses:
      200:
        description: Um dicionário com a URL da imagem gerada.
        schema:
          type: object
          properties:
            url_imagem:
              type: string
              description: A URL da imagem gerada.
    """
    prompt = request.args.get("prompt")
    if not prompt:
        return jsonify({"erro": "Prompt não fornecido"}), 400

    # URLs
    url_login = "https://piclumen.com/app/account"
    url_gerador = "https://piclumen.com/app/image-generator/create"

    # Credenciais de login
    usuario = "direcaofxsystem@gmail.com"
    senha = "piclumen123"

    # Inicia o navegador
    driver = webdriver.Chrome()
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')  # Desabilitar GPU pode ser necessário em alguns sistemas

    # Inicia o navegador Chrome em modo headless
    driver = webdriver.Chrome(options=chrome_options)
    try:
        # Acessa a página de login
        driver.get(url_login)

        # Espera o campo de usuário estar presente
        campo_usuario = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/div[1]/div[2]/div[1]/div/div[3]/div/div[1]/div/div/div[1]/div/input'))
        )
        # Insere o usuário
        campo_usuario.send_keys(usuario)

        # Espera o campo de senha estar presente
        campo_senha = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/div[1]/div[2]/div[1]/div/div[3]/div/div[2]/div/div/div[1]/div/input'))
        )
        # Insere a senha
        campo_senha.send_keys(senha)

        # Espera o botão de submit estar presente
        botao_submit = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/div[1]/div[2]/div[1]/div/div[3]/div/div[4]/button'))
        )
        # Clica no botão de submit
        botao_submit.click()

        # Aguarda um tempo para o login ser processado
        time.sleep(10)

        # Agora que está logado, acessa a página do gerador de imagens
        driver.get(url_gerador)

        # Aguarda um tempo para escrever o texto
        time.sleep(5)
        # Espera o elemento textarea estar presente na página
        textarea = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/div[1]/div[2]/div/div[1]/div/div[1]/div[1]/div/div/div/div[1]/textarea'))
        )
        # Insere o prompt no textarea
        textarea.send_keys(prompt.replace('%20', ' '))

        # Espera o botão de gerar imagem estar presente
        botao_gerar = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/div[1]/div[2]/div/div[1]/div/div[1]/button[1]'))
        )
        botao_gerar.click()
        time.sleep(10)

        # Espera o elemento com data-index="0" estar presente
        elemento_data_index_0 = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@data-index="0"]'))
        )

        # Encontra a primeira imagem dentro do elemento com data-index="0"
        imagem = elemento_data_index_0.find_elements(By.TAG_NAME, 'img')[0]

        # Obtém o link da imagem
        link_imagem = imagem.get_attribute('src')

        # Extrai a primeira palavra do prompt
        primeira_palavra = prompt.split()[0]

         # Cria a pasta "imagens" se ela não existir
        if not os.path.exists('imagens'):
            os.makedirs('imagens')

        # Nome do arquivo da imagem com o caminho completo
        nome_arquivo = os.path.join('imagens', f'{primeira_palavra}.jpg')

        # Baixa a imagem com o nome baseado na primeira palavra do prompt
        response = requests.get(link_imagem)
        with open(nome_arquivo, 'wb') as arquivo:
            arquivo.write(response.content)
        
        
        #response = requests.get(link_imagem)
        #with open(f'{primeira_palavra}.jpg', 'wb') as arquivo:
        #    arquivo.write(response.content)

        return send_file(nome_arquivo, mimetype='image/jpeg', as_attachment=True)
        #return jsonify({"url_imagem": link_imagem})

    finally:
        # Fecha o navegador
        driver.quit()

if __name__ == "__main__":
    app.run(debug=True)