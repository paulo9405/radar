# Roadmap — Radar de Tendências IA (MVP → Plataforma)

## Objetivo do Projeto

Criar uma plataforma SaaS que utiliza sinais públicos de mercado para ajudar vendedores a identificar:

* produtos com potencial;
* tendência de crescimento;
* saturação;
* concorrência;
* oportunidade real de teste.

O foco NÃO é prever o futuro.

O foco é:

> reduzir decisões ruins usando dados públicos de mercado.

---

# FASE 0 — Validação de Interesse (CONCLUÍDA)

## Objetivo

Validar:

* interesse real;
* comunicação;
* CTR dos anúncios;
* geração de leads;
* percepção de valor.

## O que foi feito

* Landing page;
* Facebook/Instagram Ads;
* Criativos;
* Formulário de acesso antecipado;
* Coleta de WhatsApp;
* Estrutura visual do produto;
* Posicionamento da marca.

## Resultado esperado

Validar:

* CAC inicial;
* taxa de cadastro;
* interesse do público;
* comentários e feedbacks.

---

# FASE 1 — MVP Funcional (PRIORIDADE MÁXIMA)

## Objetivo

Entregar um sistema REAL e funcional o mais rápido possível.

Sem IA complexa.

Sem automações gigantes.

Sem promessas irreais.

---

# Stack Recomendada

## Backend

* Django
* Django REST Framework

## Frontend

* Django Templates inicialmente
  OU
* React futuramente

## Banco

* PostgreSQL

## Infra

* Render / Railway / VPS simples inicialmente

---

# Funcionalidades do MVP

## 1. Pesquisa de Produto

Usuário digita:

* nome do produto;
* nicho;
* palavra-chave.

Ex:

* “Luminária Sunset”
* “Mini impressora térmica”
* “Projetor portátil”

---

## 2. Coleta de Dados

# FONTES PRINCIPAIS

---

## Mercado Livre API (PRINCIPAL)

### Objetivo

Coletar:

* quantidade de anúncios;
* faixa de preço;
* vendedores;
* avaliações;
* concorrência;
* saturação.

### Método

API oficial do Mercado Livre.

### Necessário

* criar aplicação developer;
* client id;
* client secret;
* token OAuth.

### Vantagem

Melhor fonte para MVP no Brasil.

---

## Google Trends

### Objetivo

Medir:

* crescimento de busca;
* interesse ao longo do tempo;
* sazonalidade.

### Método inicial

* pytrends
  OU
* SerpAPI/DataForSEO.

### Futuramente

Migrar para API oficial do Google Trends quando estável/publicamente disponível.

### Métricas

* crescimento 30 dias;
* crescimento 90 dias;
* estabilidade;
* tendência.

---

## Google Search / Shopping

### Objetivo

Medir:

* presença do produto;
* força competitiva;
* sinais externos;
* marketplaces adicionais.

### Método

* SerpAPI
  OU
* DataForSEO.

---

# FASE 1.5 — Estrutura Inteligente de Dados

## Objetivo

Transformar dados brutos em sinais úteis.

---

# Sistema de Score

## Exemplo

### Tendência

* Busca subindo → positivo
* Busca caindo → negativo

### Concorrência

* Muitos vendedores → negativo
* Poucos vendedores → positivo

### Saturação

* Guerra de preço → negativo

### Faixa de preço

* Margem saudável → positivo

---

# Fórmula Inicial

## Score Final

* Tendência → 35%
* Concorrência → 30%
* Saturação → 20%
* Preço/Margem → 15%

---

# Classificação

## 0–3

Produto ruim

## 4–6

Arriscado

## 7–8

Boa oportunidade

## 9–10

Alta oportunidade

---

# Resposta Inteligente (IA)

A IA NÃO decide os dados.

Ela interpreta.

## Exemplo de saída

> “Produto apresenta crescimento recente de interesse, baixa saturação e concorrência moderada. Pode valer um teste inicial com estoque reduzido.”

---

# FASE 2 — Painel e Histórico

## Objetivo

Melhorar retenção.

---

# Funcionalidades

## Histórico de pesquisas

Usuário pode:

* salvar análises;
* comparar produtos;
* revisar tendências.

---

## Dashboard

Mostrar:

* produtos em alta;
* nichos aquecendo;
* oportunidades recentes.

---

## Alertas

Exemplo:

> “Produto X aumentou 42% nas buscas nos últimos 7 dias.”

---

# FASE 3 — Expansão de Fontes

## Amazon Product Advertising API

### Objetivo

Adicionar:

* preços;
* avaliações;
* concorrência;
* oferta.

### Observação

Amazon possui requisitos chatos para manter acesso.

Não priorizar agora.

---

## Shopee Open Platform

### Objetivo

Expandir sinais de marketplace.

### Problema

API menos amigável para pesquisa pública ampla.

Entrar apenas depois.

---

## TikTok Trends / Social Signals

### Objetivo

Detectar:

* produtos viralizando;
* sinais sociais;
* crescimento antecipado.

---

# FASE 4 — Base Própria de Inteligência

## Objetivo

Criar vantagem competitiva real.

---

# Sistema começa a aprender com:

* buscas dos usuários;
* produtos mais pesquisados;
* análises salvas;
* tendências internas;
* comportamento agregado.

---

# FASE 5 — IA Mais Forte

## Possíveis recursos futuros

### IA conversacional

Usuário pergunta:

> “Vale vender isso em 2026?”

---

### Recomendações automáticas

> “Produtos similares com menor concorrência.”

---

### Comparador de nichos

Ex:

* Pet
  vs
* Cozinha
  vs
* Gamer

---

# Modelo de Monetização

## Gratuito

* pesquisas limitadas;
* score básico.

---

## Pro

* análises ilimitadas;
* histórico;
* alertas;
* tendências avançadas.

---

# Ordem REALISTA de Desenvolvimento

## Semana 1

* Estrutura Django
* Banco
* Usuários
* Tela pesquisa

---

## Semana 2

* Integração Mercado Livre
* Google Trends
* Sistema de score

---

## Semana 3

* Resultado visual
* Dashboard básico
* Histórico

---

## Semana 4

* Melhorias
* Deploy
* Testes reais
* Feedback dos usuários

---

# Prioridade Estratégica

O objetivo NÃO é:

> “criar IA revolucionária.”

O objetivo é:

> “entregar decisões melhores usando sinais reais de mercado.”

Isso é muito mais viável.
