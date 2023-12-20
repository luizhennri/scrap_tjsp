from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import time as time
import json
import math
import os
import shutil
import glob
from random import seed
from random import randint
from PyPDF2 import PdfReader
seed(65464168)

API_KEY = ''
WORD_TO_SEARCH = ''
DB_NAME = '.json'
NAME_DIR_TO_SAVE_FILES = ''
PATH_TO_EXTENSION = r'./ifibfemgeogfhoebkmokieepdoobkbpo.crx'
CHROME_EXECUTABALE_PATH = r'./chromedriver.exe'
SITE_URL = 'https://esaj.tjsp.jus.br/cjsg/consultaCompleta.do'
all_lawsuit = []
log_data = {}
last_page = 0
last_lawsuit = []
PASSED = True

def captcha_solver():
    print('Resolvendo o CAPCTHA...')
    no_resolved = True
    WebDriverWait(navegador, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".captcha-solver_inner"))).click()
    # Espera a extensão resolver o captcha
    while no_resolved:
        try:
            WebDriverWait(navegador, 10).until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, ".captcha-solver-info"), 'Captcha solved!'))
            no_resolved = False
        except:
            pass
    print('CAPCTHA resolvido!')
    WebDriverWait(navegador, 10).until(EC.element_to_be_clickable((By.ID, "pbEnviar"))).click()


def download(link):
    time.sleep(1)
    link.click()
    navegador.switch_to.window(navegador.window_handles[1])
    time.sleep(1)
    # Se a página que abriu, nao tem captcha, faz o download direto
    if( navegador.current_url == 'about:blank'):
        navegador.close()
        navegador.switch_to.window(navegador.window_handles[0])
    # Se não, chama a função pra extensão resolver
    else:
        captcha_solver()
        navegador.close()
        navegador.switch_to.window(navegador.window_handles[0])

def createDB(json_):
    for data in json_:
        with open (f'{DB_NAME}', 'a', encoding='utf-8') as bd:
            json.dump(data, bd, indent = 4, ensure_ascii=False)
            bd.write(',')
            bd.write('\n')

def save_log(page, lawsuit):
    if(page == last_page and PASSED == True):
        for old_lawsuit in last_lawsuit:
            all_lawsuit.append(old_lawsuit)
        all_lawsuit.append(lawsuit)
    else:
        all_lawsuit.append(lawsuit)
    
    dict_log = {
        "Page": page,
        "Lawsuits": all_lawsuit
    }
    with open('log.json', 'w', encoding='utf-8') as log:
            json.dump(dict_log, log, indent = 4, ensure_ascii=False)


def get_info_lawsuit(sentences_pdfs):
    navegador.execute_script("""[...document.querySelectorAll('.fundocinza1')].map((x) => {
    try {
        x.querySelector('img.mostrarocultarementa.cursorpointer').click();
    } catch {
        console.log('Erro');
    }
        });""")
    #Pega todos os dados de capa e salva em um dicionário
    all_data_page = navegador.execute_script("""return (function getInfo() {
        const all = [...document.querySelectorAll('.fundocinza1')].map(x=>[...x.querySelectorAll('tr')]).map(x=> x.map(x=> x.innerText.trim()));
        dict = [];
        for (text of all){
            let jsonObject = {};
            let count = 1;
            text.forEach(item => {
            let [key, ...valueParts] = item.split(':');
            if(count === 1 && valueParts == ''){
                valueParts = [key];
                key = 'Processo';
            }
            const value = valueParts.join(':').trim();
            jsonObject[key.trim()] = value;
            count = count+1;
            });
            const jsonResult = jsonObject;
            dict.push(jsonResult);
            }
        return dict;
        })()""")

    createDB(all_data_page)

def get_sentence(name_file, sentences_pdfs):
    pdf = PdfReader(f'{name_file}')
    pag = pdf.pages[0]

    content_pag = pag.extract_text()

    try:
        sentences_pdfs.append(content_pag.split('decisão:')[1].split('V.')[0].replace("\n", '').replace('"', '').strip(' '))
    except:
        sentences_pdfs.append(None)


preferences = {
    "plugins.always_open_pdf_externally": True,
    "download.default_directory": f'{os.getcwd()}'
}


chop = webdriver.ChromeOptions()
chop.add_extension(f'{PATH_TO_EXTENSION}')
chop.add_experimental_option("prefs", preferences)


# Iniciando o WebDriver
service = Service(executable_path=f'{CHROME_EXECUTABALE_PATH}')
navegador = webdriver.Chrome(service=service, options=chop)

# Acessando o site
navegador.get(f"{SITE_URL}")
navegador.switch_to.window(navegador.window_handles[0])
navegador.execute_script(f'document.querySelector("body > div > div.content > table > tbody > tr:nth-child(1) > td:nth-child(2) > input[type=text]").value="{API_KEY}"')
navegador.execute_script('document.querySelector("#connect").click()')


# Valida a extensão do TwoCaptcha
no_alert = True
while no_alert:
    try:
        WebDriverWait(navegador, 3).until(EC.alert_is_present())
        alert = navegador.switch_to.alert
        alert.accept()
        no_alert = False
        navegador.close()
        time.sleep(1)
        navegador.switch_to.window(navegador.window_handles[0])
    except :
        print("no alert")


# Pesquisa a palavra chave
navegador.find_element(By.XPATH, '//*[@id="iddados.buscaInteiroTeor"]').send_keys(f'"{WORD_TO_SEARCH}"')

# Envia a pesquisa
navegador.find_element(By.XPATH, '//*[@id="pbSubmit"]').click()

try:
    with open('log.json', 'r', encoding='utf-8') as load_log:
        log_data = json.load(load_log)
        last_page = log_data.get('Page')
        last_lawsuit = log_data.get('Lawsuits')
except:
    log_data = {}



WebDriverWait(navegador, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".esajlinklogin.downloadEmenta")))
# Pega todos os links dos processos da página
processos = navegador.execute_script("return document.querySelectorAll('.esajlinklogin.downloadEmenta')")
# Pega o numero dos processos para usar como nome do arquivo
name_file = navegador.execute_script("return [...document.querySelectorAll('.esajlinklogin.downloadEmenta')].map(x=>x.innerText)")
# Calcula a quantidade de página que o script irá rodar
pages = math.ceil(int(navegador.execute_script("return document.querySelector('#nomeAba-A').innerText.split('(')[1].replace(')','')"))/20)


for page, pdfs in enumerate(range(pages)):
    sentences_pdfs = list()

    if(page < last_page):
        # Troca de página
        navegador.execute_script("return [...document.querySelector('.trocaDePagina').querySelectorAll('a')].reverse()[0].click()")
        time.sleep(1)
        # Dedois que troca de página, tem que atualizar as novas informações
        WebDriverWait(navegador, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".esajlinklogin.downloadEmenta")))
        processos = navegador.execute_script("return document.querySelectorAll('.esajlinklogin.downloadEmenta')")
        name_file = navegador.execute_script("return [...document.querySelectorAll('.esajlinklogin.downloadEmenta')].map(x=>x.innerText)")
        all_lawsuit = []
        continue
    print(f'### PAGINA {page + 1} ###')
    for i,item in enumerate(processos):
            if(name_file[i] in last_lawsuit):
                continue
            print(f'fazendo o download de {name_file[i]}...')
            download(item)
            time.sleep(1)
            for file in glob.glob('*.pdf'):
                if(os.path.exists(f'./{NAME_DIR_TO_SAVE_FILES}')):

                    shutil.move(file, f'./{NAME_DIR_TO_SAVE_FILES}/{name_file[i]}___{randint(0, 100000)}.pdf')
                    save_log(page,name_file[i])
                else:

                    os.makedirs(f'./{NAME_DIR_TO_SAVE_FILES}/')
                    shutil.move(file, f'./{NAME_DIR_TO_SAVE_FILES}/{name_file[i]}___{randint(0, 100000)}.pdf')
                    save_log(page,name_file[i])
            PASSED = False
    # Antes de trocar de página pega as informações de capa
    get_info_lawsuit(sentences_pdfs)
    print('\n\n')
    # Troca de página
    navegador.execute_script("return [...document.querySelector('.trocaDePagina').querySelectorAll('a')].reverse()[0].click()")
    # Dedois que troca de página, tem que atualizar as novas informações
    WebDriverWait(navegador, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".esajlinklogin.downloadEmenta")))
    processos = navegador.execute_script("return document.querySelectorAll('.esajlinklogin.downloadEmenta')")
    name_file = navegador.execute_script("return [...document.querySelectorAll('.esajlinklogin.downloadEmenta')].map(x=>x.innerText)")
    all_lawsuit = []
    



