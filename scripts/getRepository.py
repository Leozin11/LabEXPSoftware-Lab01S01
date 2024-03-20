import requests
import pandas as pd
import os
from dotenv import load_dotenv
import json

load_dotenv()
chave = os.getenv("key")

graphQL = 'https://api.github.com/graphql'
headers = {'Authorization': 'Bearer %s' % chave}
allResults = list()

def requisicao(repositorios):
    endCursor = None
    startCursor = None

    for i in range(int(repositorios/20)):
        variaveis = {
            "endCursor": endCursor,
            "startCursor": startCursor
        }
        query = """
        query ($endCursor: String) {
          search(query: "stars:>1 fork:false sort:stars-desc", type: REPOSITORY, first:20, after: $endCursor) {
            edges {
              node {
                ... on Repository {
                  owner{
                    login
                  }
                  name
                  createdAt
                  updatedAt
                  primaryLanguage {
                    name
                  }
                  releases {
                    totalCount
                  }
                  totalIssues: issues {
                    totalCount
                  }
                  closedIssues: issues(states: CLOSED) {
                    totalCount
                  }
                  pullRequests(states: MERGED) {
                    totalCount
                  }
                }
              }
            }
            pageInfo {
              endCursor
              startCursor
              hasNextPage
              hasPreviousPage
            }
          }
        }
        """

        request = requests.post(
            url=graphQL, json={'query': query, 'variables': variaveis}, headers=headers)
        resp = request.json()
        allResults.append(resp)
        hasNextPage = resp['data']['search']['pageInfo']['hasNextPage']
        endCursor = resp['data']['search']['pageInfo']['endCursor']
        startCursor = resp['data']['search']['pageInfo']['startCursor']
        
        if not hasNextPage:
            break

    if request.status_code == 200:
        return allResults
    else:
        raise Exception("Falha na Query {}. {}".format(
            request.status_code, query))


repositorios = 1000
res = requisicao(repositorios)

if res is not None:
    # Salvar resultado da consulta em um arquivo JSON
    os.makedirs('scripts/dataset/json', exist_ok=True)
    with open('scripts/dataset/json/resultado_query.json', 'w', encoding='utf-8') as f:
        json.dump(res, f, ensure_ascii=False, indent=2)

    # Carregar o resultado da consulta a partir do arquivo JSON
    with open('scripts/dataset/json/resultado_query.json', 'r') as f:
        data = json.load(f)

    # Converter os dados JSON para DataFrame do Pandas
    df = pd.DataFrame()
    dfs = []
    for i in range(len(data)):
        normalized_data = pd.json_normalize(data[i]['data']['search']['edges'])
        dfs.append(normalized_data)

    df = pd.concat(dfs, ignore_index=True)

    # Salvar o DataFrame em um arquivo CSV
    caminhoCSV = 'scripts/dataset/csv/resultado_query.csv'
    df.to_csv(caminhoCSV, index=False)


    # Verificar se o arquivo CSV foi salvo com sucesso
    if os.path.exists(caminhoCSV):
        print("Resultado da consulta salvo em CSV com sucesso.")
    else:
        print("Falha ao salvar resultado em CSV.")
        print("Verifique se o diretório 'scripts/dataset/csv/' existe e tem permissões adequadas.")


