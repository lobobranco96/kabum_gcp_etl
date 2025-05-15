import pandas as pd
import numpy as np
import re
from google.cloud import storage
from io import StringIO

def transformacao_kabum():
    bucket_name = 'kabum-raw'  
    prefix_raw = "raw/promocao/"  

    # Inicializando o cliente de storage do Google Cloud
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    # Listando os arquivos no diretório "raw/promocao" do bucket
    blobs = bucket.list_blobs(prefix=prefix_raw)

    # Iterando sobre cada arquivo CSV encontrado no diretório
    for blob in blobs:
        if blob.name.endswith('.csv'):  # Apenas arquivos CSV
            print(f"Processando o arquivo: {blob.name}")

            # Lendo o arquivo CSV do GCS
            csv_data = blob.download_as_text()
            produtos_transformado = pd.read_csv(StringIO(csv_data))

            # Funções de transformação
            def extrair_valor(texto):
                if pd.isna(texto) or texto == "":
                    texto = "0"
                texto = texto.replace("R$", "").strip()
                texto = texto.replace(".", "").replace(",", ".")
                return float(texto)

            def extrair_desconto(texto):
                if pd.isna(texto):
                    return 0
                match = re.search(r'-?(\d+)%', str(texto))
                return int(match.group(1)) if match else 0

            def extrair_avaliacao(valor):
                if pd.isna(valor) or valor in ["None", "[]"]:
                    return 0
                match = re.search(r'\((\d+)\)', str(valor))
                return int(match.group(1)) if match else 0

            def extrair_unidades(texto):
                if pd.isna(texto) or texto == "[]":
                    return 0
                match = re.search(r'Restam (\d+)\s+unid\.', texto)
                return int(match.group(1)) if match else 0

            def coluna_detalhes(nome_produto):
                partes = nome_produto.split(',', 1)
                if len(partes) > 1:
                    nome = partes[0].strip()
                    detalhes = partes[1].strip()
                else:
                    nome = nome_produto
                    detalhes = ''
                return pd.Series([nome, detalhes])

            # Aplicando transformações
            produtos_transformado["preco_antigo"] = produtos_transformado["preco_antigo"].apply(extrair_valor)
            produtos_transformado["preco_atual"] = produtos_transformado["preco_atual"].apply(extrair_valor)
            produtos_transformado['credito'] = produtos_transformado['credito'].apply(lambda x: f"Em até {x.strip()}" if pd.notna(x) else "")
            produtos_transformado["desconto_percentual"] = produtos_transformado["desconto"].apply(extrair_desconto)
            produtos_transformado.drop(columns=["desconto"], inplace=True)
            produtos_transformado["avaliacao"] = produtos_transformado["avaliacao"].apply(extrair_avaliacao).astype(int)
            produtos_transformado["unidades"] = produtos_transformado["unidades"].astype(str).apply(extrair_unidades)
            produtos_transformado[['nome_produto', 'detalhes']] = produtos_transformado['nome_produto'].apply(coluna_detalhes)

            # Reorganizando as colunas
            produtos_transformado = produtos_transformado[['nome_produto', 'detalhes', 'preco_atual', 'preco_antigo', 'desconto_percentual', 'avaliacao', 'unidades', 'cupom', 'link']]

            # Caminho do arquivo processado no GCS
            path_processed = f"processed/promocao/{blob.name.split('/')[-1].replace('raw', 'processed')}"

            # Salvando o arquivo processado no GCS
            blob_processed = bucket.blob(path_processed)
            with blob_processed.open("w") as f:
                produtos_transformado.to_csv(f, index=False)

            print(f"Arquivo processado foi carregado com sucesso em: {path_processed}")

    return "Processamento concluído para todos os arquivos CSV."