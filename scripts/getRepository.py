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

    for i in range(int(repositorios/20)):
        variaveis = {
            "endCursor": endCursor
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
              hasNextPage
            }
          }
        }
        """

        request = requests.post(
            url=graphQL, json={'query': query, 'variaveis': variaveis}, headers=headers)
        resp = request.json()
        allResults.append(resp)
        endCursor = resp['data']['search']['pageInfo']['endCursor']


    if request.status_code == 200:
        return allResults
    else:
        raise Exception("Falha na Query {}. {}".format(
            request.status_code, query))


repositorios = 1000

res = requisicao(repositorios)


os.makedirs('scripts/dataset/json', exist_ok=True)

with open('scripts/dataset/json/resultado_query.json', 'w', encoding='utf-8') as f:
    json.dump(res, f, ensure_ascii=False, indent=2)

with open('scripts/dataset/json/resultado_query.json', 'r') as f:
    data = json.load(f)

df = pd.DataFrame()
dfs = []

for i in range(len(data)):
    normalized_data = pd.json_normalize(data[i]['data']['search']['edges'])
    dfs.append(normalized_data)

df = pd.concat(dfs, ignore_index=True)

caminhoCSV = 'scripts/dataset/csv/resultado_query.csv'
df.to_csv(caminhoCSV, index=False)

if os.path.exists(caminhoCSV):
    print("Resultado da consulta salvo em CSV com sucesso.")
else:
    print("Falha ao salvar resultado em CSV.")