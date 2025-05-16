"""
Script de transformação dos dados brutos extraídos da Kabum.

Este script processa os arquivos CSV localizados no bucket 'kabum-raw',
aplica limpezas e extrações estruturadas sobre os campos (ex: preço, desconto, unidades restantes),
e salva os dados transformados no bucket 'kabum-processed'.

As transformações incluem:
- Conversão de preços de string para float.
- Extração de percentual de desconto.
- Normalização de avaliações e unidades.
- Separação do nome do produto e seus detalhes.

Execução:
    python transformation.py
"""

import pandas as pd
import numpy as np
import re
import logging
from google.cloud import storage
from io import StringIO

# Configuração do logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def transformacao_kabum():
    """
    Função principal que aplica a transformação dos dados coletados da Kabum.
    Lê arquivos CSV do bucket raw, transforma os dados, e escreve arquivos no bucket processed.

    Returns:
        str: Mensagem indicando que todos os arquivos foram processados com sucesso.
    """
    raw_bucket_name = 'kabum-raw'
    processed_bucket_name = 'kabum-processed'
    prefix_raw = "promocao/"

    client = storage.Client()
    raw_bucket = client.bucket(raw_bucket_name)
    processed_bucket = client.bucket(processed_bucket_name)

    blobs = raw_bucket.list_blobs(prefix=prefix_raw)

    for blob in blobs:
        if blob.name.endswith('.csv'):
            logging.info(f"Processando o arquivo: {blob.name}")
            csv_data = blob.download_as_text()
            produtos_transformado = pd.read_csv(StringIO(csv_data))

            # Funções auxiliares de transformação
            def extrair_valor(texto):
                """Extrai o valor numérico de um texto com símbolo 'R$'."""
                if pd.isna(texto) or texto == "":
                    texto = "0"
                texto = texto.replace("R$", "").strip().replace(".", "").replace(",", ".")
                return float(texto)

            def extrair_desconto(texto):
                """Extrai o percentual numérico de um texto de desconto ('-35%')."""
                if pd.isna(texto):
                    return 0
                match = re.search(r'-?(\d+)%', str(texto))
                return int(match.group(1)) if match else 0

            def extrair_avaliacao(valor):
                """Extrai o número de avaliações do texto ('(123)')."""
                if pd.isna(valor) or valor in ["None", "[]"]:
                    return 0
                match = re.search(r'\((\d+)\)', str(valor))
                return int(match.group(1)) if match else 0

            def extrair_unidades(texto):
                """Extrai número de unidades restantes ('Restam 2 unid.')."""
                if pd.isna(texto) or texto == "[]":
                    return 0
                match = re.search(r'Restam (\d+)\s+unid\.', texto)
                return int(match.group(1)) if match else 0

            def coluna_detalhes(nome_produto):
                """Separa nome e detalhes de um produto com base em vírgula."""
                partes = nome_produto.split(',', 1)
                if len(partes) > 1:
                    return pd.Series([partes[0].strip(), partes[1].strip()])
                return pd.Series([nome_produto, ''])

            # Aplicações das transformações
            produtos_transformado["preco_antigo"] = produtos_transformado["preco_antigo"].apply(extrair_valor)
            produtos_transformado["preco_atual"] = produtos_transformado["preco_atual"].apply(extrair_valor)
            produtos_transformado['credito'] = produtos_transformado['credito'].apply(lambda x: f"Em até {x.strip()}" if pd.notna(x) else "")
            produtos_transformado["desconto_percentual"] = produtos_transformado["desconto"].apply(extrair_desconto)
            produtos_transformado.drop(columns=["desconto"], inplace=True)
            produtos_transformado["avaliacao"] = produtos_transformado["avaliacao"].apply(extrair_avaliacao).astype(int)
            produtos_transformado["unidades"] = produtos_transformado["unidades"].astype(str).apply(extrair_unidades)
            produtos_transformado[['nome_produto', 'detalhes']] = produtos_transformado['nome_produto'].apply(coluna_detalhes)

            # Reordenação e seleção final das colunas
            produtos_transformado = produtos_transformado[[
                'nome_produto', 'detalhes', 'preco_atual', 'preco_antigo',
                'desconto_percentual', 'avaliacao', 'unidades', 'cupom', 'link'
            ]]

            # Upload para o bucket processed
            path_processed = f"promocao/{blob.name.split('/')[-1].replace('raw', 'processed')}"
            blob_processed = processed_bucket.blob(path_processed)

            blob_processed.upload_from_string(
                produtos_transformado.to_csv(index=False),
                content_type='text/csv'
            )

            logging.info(f"Arquivo processado foi carregado com sucesso em: {path_processed}")

    return "Processamento concluído para todos os arquivos CSV."


def main():
    """
    Função executada ao rodar o script diretamente.
    Dispara o processo de transformação e loga o resultado final.
    """
    resultado = transformacao_kabum()
    logging.info(resultado)


if __name__ == "__main__":
    main()
