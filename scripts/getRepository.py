import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
chave = os.getenv("key")
graphql_url = "https://api.github.com/graphql"

query = """{
  search(query:"stars>1 fork:false sort:stars-desc", type:REPOSITORY, 
  first:100){
    nodes{
      ... on Repository{
        name
        owner{
          login
        }
        createdAt
        pullRequests{totalCount}
        releases{totalCount}
        updatedAt
        primaryLanguage{name}
        totalIssues: issues{totalCount}
        closedIssues: issues(states: CLOSED){totalCount}
      }
    }
  }
}
"""

headers = {
    'Authorization': 'Bearer %s' % chave,
}

# Dados da requisição
data = {
    'query': query,
}

# Se você ainda não tiver, crie o diretório 'scripts/dataset/json'
output_directory = os.path.join('scripts/dataset', 'json')
os.makedirs(output_directory, exist_ok=True)

# Caminho completo para o arquivo dentro da pasta 'dataset/json'
output_file_path = os.path.join(output_directory, 'resultado_query.json')

response = requests.post(graphql_url, headers=headers, json=data)


if response.status_code == 200:
    resultado = response.json()


    with open(output_file_path, 'w') as file:
        json.dump(resultado, file, ensure_ascii=False, indent=4)

    print("Resultado salvo com sucesso em:", output_file_path)
else:
    print(f"Falha na requisição. Código de status: {response.status_code}")
    print(response.text)
