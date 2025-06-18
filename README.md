# Scrap TJSP

Script para extrair os dados de processos do site do Tribunal de Justiça de São Paulo utilizando a biblioteca Selenium da linguagem Python. A ferramenta extrai as informações de cabeçalho dos processos e salva em formato json, além de baixar os pdfs dos acórdãos deles.


## Histórico:

12/2023: versão 1.0
- Script completo


## Componentes:
- Selenium (v4.33.0)
- PyPDF2 (v3.0.1)


## Requisitos:
- Python 3.13.5
- Pip 25.1.1

## Instalando a Aplicação no Ambiente de Desenvolvimento:

### Baixar e Instalar o Python e o Pip

### Instalar as Dependências Necessárias
```
pip install requirements.txt
```

### Configurar as Variáveis no Arquivo `scrap_tjsp_selenium_any.py`
    - API_KEY - Chave da sua API de quebra captcha
    - WORD_TO_SEARCH - Palavra de interesse a ser buscada nos processos
    - NAME_DIR_TO_SAVE_FILES - Diretório em que serão salvos os processos em pdf

### Executar o Script
```
python scrap_tjsp_selenium_any.py
```


## Observações:
- O script foi testado utilizando a ferramenta 2Captcha para realizar a quebra dos captchas que eventualmente aparecem ao fazer o download dos pdfs (a cada 20 processos baixados), a ferramenta é paga e cobra um valor por cada captcha;
- O Selenium utiliza um driver de navegador, talvez seja necessário atualizar o arquivo `chromedriver.exe`.

