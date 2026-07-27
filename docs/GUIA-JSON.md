# Guia Rápido de JSON (aplicado ao dia a dia)

Objetivo: em ~30 minutos de leitura, você conseguir ler, escrever e depurar JSON com
confiança — e entender por que ele é a "língua" que conecta formulários, APIs, CRMs e LLMs.

---

## 1. O que é JSON, em uma frase

**JSON (JavaScript Object Notation)** é um formato de texto para representar dados
estruturados, feito para ser fácil de ler por humanos e fácil de parsear por máquinas.
Praticamente toda API do mundo (CRM, ERP, LLM, formulários) troca dados em JSON.

## 2. Os únicos 6 tipos que existem

| Tipo      | Exemplo                  | Observação                          |
|-----------|---------------------------|--------------------------------------|
| string    | `"João Silva"`             | sempre entre aspas **duplas**        |
| number    | `42`, `3.5`, `-10`         | sem aspas, sem vírgula decimal (use `.`) |
| boolean   | `true` / `false`           | minúsculo, sem aspas                 |
| null      | `null`                     | representa "ausência de valor"       |
| object    | `{ "chave": "valor" }`     | pares chave-valor, entre `{}`        |
| array     | `[1, 2, 3]`                | lista ordenada, entre `[]`           |

Tudo em JSON é combinação desses 6 tipos. Nada mais.

## 3. Exemplo real deste projeto (payload de entrada)

```json
{
  "lead_id": "lead_00231",
  "nome": "Ana Ferreira",
  "email": "ana.ferreira@empresa.com",
  "empresa": "Empresa Exemplo Ltda",
  "cargo": "Diretora de Marketing",
  "numero_funcionarios": 85,
  "setor": "E-commerce",
  "orcamento_estimado_usd": 4500,
  "origem": "formulario_site",
  "respostas_pesquisa": {
    "principal_desafio": "Baixa conversão de leads",
    "prazo_para_decisao": "30 dias",
    "ja_usa_ferramenta_similar": false
  }
}
```

Repare:
- `lead_id`, `nome`, `email` → **strings**
- `numero_funcionarios`, `orcamento_estimado_usd` → **numbers**
- `ja_usa_ferramenta_similar` → **boolean**
- `respostas_pesquisa` → um **object dentro do object** (aninhamento/nesting)

## 4. Exemplo real da saída da LLM (o que você quer garantir que sempre venha assim)

```json
{
  "lead_id": "lead_00231",
  "score": 82,
  "classification": "hot",
  "icp_match": {
    "setor_alvo": true,
    "tamanho_empresa_ok": true,
    "orcamento_ok": true,
    "cargo_decisor": true
  },
  "reasoning": "Setor e porte compatíveis com o ICP, cargo decisor e orçamento acima do mínimo.",
  "recommended_action": "Encaminhar para SDR imediatamente (contato em até 1h)."
}
```

Isso é o que chamamos de **saída parametrizada**: um contrato fixo de campos e tipos
que o seu CRM/sistema pode consumir sem "adivinhar" o formato.

## 5. Os 5 erros mais comuns (e como evitar)

1. **Aspas simples em vez de duplas** → `{'nome': 'Ana'}` ❌ / `{"nome": "Ana"}` ✅
2. **Vírgula sobrando no final** → `{"a": 1, "b": 2,}` ❌ (JSON não aceita "trailing comma")
3. **Números com aspas quando não deveriam** → `"score": "82"` (vira string) vs `"score": 82` (vira número) — isso quebra cálculos e comparações no seu sistema.
4. **Chaves sem aspas** → `{nome: "Ana"}` ❌ / `{"nome": "Ana"}` ✅
5. **Comentários dentro do JSON** → JSON **não suporta comentários** (`//` ou `/* */` não são válidos).

## 6. Como validar um JSON rapidamente

- Online: colar em [jsonlint.com](https://jsonlint.com) ou [jsonformatter.org](https://jsonformatter.org)
- No terminal (Linux/Mac), com `jq` instalado:
  ```bash
  cat examples/sample_lead_input.json | jq .
  ```
  Se o `jq` conseguir formatar sem erro, o JSON é válido.
- Em Python:
  ```python
  import json
  with open("examples/sample_lead_input.json") as f:
      data = json.load(f)  # lança exceção se o JSON for inválido
  print(data["nome"])
  ```

## 7. JSON Schema: o "contrato" que a LLM deve seguir

Um **JSON Schema** descreve as regras que um JSON precisa obedecer (quais campos existem,
quais tipos, quais são obrigatórios). É isso que usamos em `src/llm_client.py` para
**forçar** a LLM a devolver exatamente o formato esperado, em vez de confiar que ela vai
"lembrar" o formato certo.

Exemplo simplificado de schema para o score de lead:

```json
{
  "type": "object",
  "properties": {
    "score": { "type": "integer", "minimum": 0, "maximum": 100 },
    "classification": { "type": "string", "enum": ["hot", "warm", "cold"] }
  },
  "required": ["score", "classification"]
}
```

Ler esse schema em voz alta: *"score é um número inteiro entre 0 e 100; classification
é obrigatoriamente uma das três palavras: hot, warm ou cold."*

## 8. Aplicando no dia a dia (fora deste projeto)

- **Planilhas/CSV → JSON**: ferramentas como `csvjson` ou o próprio Python (`pandas.read_csv().to_json()`) convertem facilmente.
- **Configurações de sistemas** (ex: `config/icp.json` deste projeto): editar regras de negócio sem tocar em código.
- **Depuração de bugs de API**: quando uma integração falha, 90% das vezes é porque o
  JSON enviado não bate com o que a API espera (tipo errado, campo faltando).
- **Prompts para LLMs**: sempre que precisar de uma saída "parseável", peça explicitamente
  um schema JSON e, se a API permitir (como a da Anthropic via *tool use*), force esse
  formato — não confie em "responda em JSON" como texto livre, porque a LLM pode
  ocasionalmente adicionar explicações antes/depois do JSON.

## 9. Checklist mental para revisar qualquer JSON em 10 segundos

- [ ] Todo texto está entre aspas **duplas**?
- [ ] Não sobrou vírgula depois do último item de um objeto/array?
- [ ] Números estão sem aspas (a menos que você realmente queira texto)?
- [ ] Todo `{` tem um `}` correspondente, todo `[` tem um `]`?
- [ ] Não há comentários (`//`) dentro do arquivo?

Com isso você já resolve a maioria dos problemas práticos do dia a dia.
