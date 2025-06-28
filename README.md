# Web_Scraping_IBGE

Projeto: WebScraping dados do IBGE - Dados de Carregamento Dinâmico e links hrefs = # (links vazios)
O script navega no site-alvo (https://www.ibge.gov.br/estatisticas/downloads-estatisticas.html) 
   e inicia os downloads dos arquivos da seção "Acesso_a_internet_e_posse_celular.
O código cria um mecanismo de web scraping complexo que visa simular uma situação real no qual o site contém links falsos href =# com botões de download que requisitam o Javascript para o download.
Além disso, o web scraping consegue driblar a estrutura de arvore com carregamento dinâmico. Ou seja, os dados não estão dentro do HTML inicial. 
A estratégia adotada driblar isso foi adoção de lógica de percurso das ramificações dos caminhos em xpath completo, no qual segue um padrão estrutural.
Ainda, o script dribla o viewer office nativo do navegador Edge que impede o download de arquivos .xlsx e .ods . Para isso, adotei o EdgeProfileKit, já incluso na pasta.
Por fim, no script foi implementado um organizador dos arquivos baixados, copiando a estrutura de pastas do site do IBGE.


 Requisitos
-------------
- Python 3.10 ou superior
- diretório C: e pasta Downloads, destino dos arquivos
- Microsoft Edge instalado e atualizado
- main.py deve estar na mesma pasta e no mesmo nível do EdgeProfileKit
- Necessário estar com o Web Driver do Edge instalado e atualizado, baixe em:
  https://developer.microsoft.com/pt-br/microsoft-edge/tools/webdriver?ch=1&form=MA13LH
- Conexão com a internet para baixar o edgedriver automaticamente
- Pasta `EdgeProfileKit` (inclusa) com configuração já ajustada para baixar arquivos .xlsx e .ods corretamente

 Instalação das dependências
-----------------------------
Abra o terminal dentro da pasta do projeto e execute:

   pip install -r requirements.txt

  Como funciona
----------------
1. O Selenium abre o Edge com o perfil `EdgeProfileKit`, que já tem o visualizador de arquivos do Office desativado.
2. O script navega no site-alvo (https://www.ibge.gov.br/estatisticas/downloads-estatisticas.html) 
   e inicia os downloads dos arquivos da seção "Acesso_a_internet_e_posse_celular.
3. Um organizador em segundo plano detecta os arquivos na pasta Downloads e move para as pastas corretas automaticamente.
4. Tudo funciona sem intervenção manual.

 Para executar
----------------
1. Certifique-se de que a pasta `EdgeProfileKit` está no mesmo diretório do script `main.py`.
2. Rode o script com:

    python main.py

 Estrutura
------------------------
projeto/
├── main.py
├── EdgeProfileKit/       ← Pasta de perfil do Edge com configurações salvas
├── requirements.txt
└── README.txt             ← Este arquivo

📌 Observações
--------------
- **Não mova nem renomeie a pasta `EdgeProfileKit`**, senão o perfil do navegador não será carregado corretamente.
- Os arquivos baixados vão direto pra pasta Downloads e são movidos automaticamente.
- O código foi preparado para funcionar no Windows com Edge e Python.

