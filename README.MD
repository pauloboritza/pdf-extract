# Objetivo
- Pequeno script feito em Python para extrai textos de documentos PDF, sejam eles texto nativo ou imagens, ignorando partes sem valor como cabeçalhos e rodapés.
## Preparar o ambiente Windows
- No console digite os comandos:
- `python -m venv .\venv`
- `.\venv\Scripts\activate`
- `pip install pymupdf numpy pandas scikit-learn pytesseract pillow`
- Instale o Tesseract OCR: [LINK](https://github.com/tesseract-ocr/tessdoc/blob/main/Installation.md); Binário Windows: [LINK](https://digi.bib.uni-mannheim.de/tesseract/); ao instalar não se esqueça de adicionar o idioma adequado.
- Caso tenha problemas por ter instalado o tesseract em uma local diferente do padrão, ajuste a variável `pytesseract.pytesseract.tesseract_cmd` na pasta `src/image_ocr_processor.py`
## Executar:
- `python extract.py --pdf D:\PASTA\DE\ORIGEM\doc.pdf --output D:\PASTA\DE\DESTINO\texto.txt --lang por`
- parâmetro `--lang por` refere-se ao idioma português, para mais opções: [LINK](https://tesseract-ocr.github.io/tessdoc/Data-Files-in-different-versions.html)
### Manutenção da Ordem do Texto OCR:

- Implementação: Todos os elementos de texto (digitais e OCR) são armazenados em uma lista `text_elements` com suas respectivas coordenadas. Após a coleta, essa lista é ordenada com base nas coordenadas `(y0, x0)` para preservar a ordem visual do documento.

### Remoção de Cabeçalhos e Rodapés:

- Implementação: A classe `HeaderFooterDetector` identifica as áreas de cabeçalho e rodapé. Durante a extração, qualquer bloco de texto que esteja dentro dessas áreas é ignorado.
- Utilizando o algoritmo de clustering HDBSCAN para identificar e agrupar blocos de texto que possivelmente correspondem a cabeçalhos e rodapés em um documento PDF.

- `self.page_count` Representa o número total de páginas no documento PDF que está sendo processado. Serve para dimensionar o tamanho mínimo dos clusters com base no tamanho do documento. Um documento maior pode ter cabeçalhos e rodapés mais consistentes e espalhados por mais páginas.
- `self.hff` É um fator de ajuste (hiperparâmetro) que determina a fração do número total de páginas a ser usada para calcular o tamanho mínimo dos clusters. No código, `self.hff` está definido como `0.76`. HFF pode ser interpretado como "Header/Footer Factor" (Fator de Cabeçalho/Rodapé), que ajusta quão grande deve ser um cluster para ser considerado como um cabeçalho ou rodapé. Um valor de `0.76` significa que o tamanho mínimo do cluster será 76% do número total de páginas, o que pode ser adequado para documentos com cabeçalhos e rodapés altamente consistentes.
- `np.floor(self.page_count * self.hff)` Calcula o produto de `page_count` e `hff`, e então arredonda para baixo para obter um número inteiro. Isso define o tamanho mínimo dos clusters baseado na proporção das páginas que se espera que contenham cabeçalhos ou rodapés. Arredondar para baixo (floor) garante que o tamanho mínimo seja sempre um número inteiro menor ou igual ao produto original.
- `int(np.floor(self.page_count * self.hff))` Converte o resultado arredondado (float) para um inteiro, que é necessário para o parâmetro `min_cluster_size` do HDBSCAN. O HDBSCAN requer que min_cluster_size seja um número inteiro que representa o número mínimo de pontos necessários para formar um cluster.
- `max(int(np.floor(self.page_count * self.hff)), 2)` Garante que o tamanho mínimo do cluster `(min_clust)` nunca seja inferior a 2, mesmo que o cálculo inicial resulte em um valor menor. Isso evita que o HDBSCAN tente formar clusters muito pequenos, o que poderia resultar em agrupamentos irrelevantes ou ruído. Um valor mínimo de 2 garante que apenas grupos significativos sejam considerados como possíveis cabeçalhos ou rodapés.
- Mais informações e documentação [LINK](https://scikit-learn.org/1.5/modules/generated/sklearn.cluster.HDBSCAN.html)

### Tratamento de Erros e Logs:

- Mensagens de erro e depuração serão exibidas no console para facilitar a identificação de problemas durante a execução, sem interromper o script.

### Modularidade e Responsabilidade Única:

- Implementação: O código foi separado em classes com responsabilidades únicas, seguindo o Princípio da Responsabilidade Única (SRP). Isso facilita a manutenção, a escalabilidade e a testabilidade do código.