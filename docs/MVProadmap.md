# Roadmap — Radar de Tendências IA (MVP → Plataforma)

## Objetivo do Projeto

Criar uma plataforma SaaS que utiliza **múltiplas fontes de inteligência de mercado** para ajudar vendedores a identificar:

* produtos com potencial;
* tendência de crescimento;
* saturação;
* concorrência;
* oportunidade real de teste.

O foco NÃO é prever o futuro.

O foco é:

> **Reduzir decisões ruins usando dados públicos agregados de múltiplas fontes.**

---

# FASE 0 — Validação de Interesse (✅ CONCLUÍDA)

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

# FASE 1 — MVP Funcional (✅ PARCIALMENTE CONCLUÍDA)

## Status Atual

### ✅ Infraestrutura Completa

* Django project structure
* PostgreSQL database
* Deployment on Render
* Environment configuration
* Zero 500 errors architecture

### ✅ Apps Django

* **Landing app**: Landing page funcional
* **Market app**: Sistema de análise de produtos

### ✅ Sistema de Análise

* Pesquisa de produtos
* Algoritmo de scoring (Demanda 35%, Concorrência 30%, Saturação 20%, Preço 15%)
* Classificação de oportunidades (bad, risky, good, excellent)
* Resumo inteligente com IA
* Interface de resultados
* Histórico de buscas no banco

### ✅ Mercado Livre Integration (OAuth Complete)

* OAuth 2.0 flow implementado
* PKCE (Proof Key for Code Exchange) security
* Token persistence em PostgreSQL (`MercadoLivreToken` model)
* Automatic token refresh
* Authenticated API requests
* Admin interface com masked tokens
* Complete debugging infrastructure

**Status:** OAuth funciona perfeitamente. Token persistence funciona. API communication funciona.

**Limitação descoberta:** Mercado Livre endpoint bloqueado por policy (`PA_UNAUTHORIZED_RESULT_FROM_POLICIES`)

Veja: `docs/mercado_livre_policy_block.md`

### ✅ Provider System Architecture

* Mock data provider (deterministic, baseado em hash)
* Graceful fallback system
* Provider status badges
* Comprehensive logging
* Debug management command (`python manage.py test_ml_api`)

### ✅ Database Models

```python
class ProductSearch(models.Model):
    query, source, is_public_test, ip_address, user, created_at

class MarketAnalysis(models.Model):
    demand_score, competition_score, saturation_score, price_score
    final_score, classification, confidence_level
    summary, raw_data

class MercadoLivreToken(models.Model):
    access_token, refresh_token, expires_at
    token_type, scope, user_id_ml
```

### ✅ Django Admin

* ProductSearch admin
* MarketAnalysis admin (read-only)
* MercadoLivreToken admin (masked security)

---

## Lições Aprendidas: Mercado Livre API

### O Que Funciona

✅ OAuth authentication
✅ Token persistence (PostgreSQL)
✅ Token refresh logic
✅ API communication
✅ Request/response handling

### Bloqueio por Policy

❌ Mercado Livre search endpoint retorna:

```json
{
  "error": "PA_UNAUTHORIZED_RESULT_FROM_POLICIES",
  "message": "forbidden",
  "status": 403
}
```

**Causa provável:**
* App developer novo não revisado
* Endpoint de marketplace discovery restrito
* Políticas anti-abuso
* Falta de aprovação comercial
* Restrições de descoberta de produtos

**Importante:** Isso NÃO é falha técnica. É limitação de permissão da plataforma.

### Conclusão Estratégica

**Dependência de um único provider é arriscada.**

Mercado Livre pode:
* Mudar políticas
* Bloquear endpoints
* Aumentar custos
* Restringir acesso

**Solução:** Arquitetura multi-provider desde o MVP.

---

# NOVA ARQUITETURA: Multi-Provider Intelligence Engine

## Visão Estratégica

Radar de Tendências evolui de:

> "Ferramenta de análise do Mercado Livre"

Para:

> **"Engine de inteligência de mercado multi-fonte com agregação de sinais e scoring proprietário."**

## Vantagens

✅ **Resiliência:** Falha de um provider não derruba o sistema
✅ **Qualidade:** Múltiplos sinais = análise mais robusta
✅ **Escalabilidade:** Adicionar novos providers é modular
✅ **Competitividade:** Dados exclusivos de múltiplas fontes
✅ **Independência:** Não depende de aprovação de uma única plataforma

---

# Provider Architecture

Veja documentação completa: `docs/provider_architecture.md`

## Provider Abstraction Layer

```python
class BaseProvider:
    def get_marketplace_data(query) -> dict
    def is_available() -> bool
    def get_status() -> str

class MercadoLivreProvider(BaseProvider):
    # OAuth-based when available

class GoogleTrendsProvider(BaseProvider):
    # pytrends integration

class SerpProvider(BaseProvider):
    # SerpAPI/DataForSEO

class MockProvider(BaseProvider):
    # Fallback determinístico
```

## Aggregation Layer

```python
class MarketIntelligence:
    providers = [
        MercadoLivreProvider(),
        GoogleTrendsProvider(),
        SerpProvider(),
        MockProvider()  # Always available fallback
    ]

    def analyze_product(query):
        signals = aggregate_signals(query)
        scores = calculate_scores(signals)
        classification = classify_opportunity(scores)
        summary = generate_summary(signals, scores)
        return analysis
```

---

# Próximas Fases — Atualizado

## FASE 1.5 — Stabilize Current MVP (🔄 EM ANDAMENTO)

**Objetivo:** Sistema robusto e funcional mesmo sem providers externos.

### Tarefas

* ✅ Mock data system funcionando
* ✅ Provider fallback logic
* ✅ Zero 500 errors
* 🔄 Improve UI/UX
* 🔄 Better error messages
* 🔄 Provider status indicators
* 🔄 Mock data quality improvements

**Prazo:** 1 semana

---

## FASE 2 — Google Trends Integration (📋 PRÓXIMO)

**Objetivo:** Primeira fonte real de dados independente de marketplaces.

### Implementação

```python
# market/services/google_trends.py

import pytrends
from pytrends.request import TrendReq

class GoogleTrendsProvider:
    def get_trends_data(query):
        # Historical trend
        # Growth indicators
        # Related queries
        # Regional interest
        # Momentum scoring
```

### Métricas

* Crescimento 30 dias
* Crescimento 90 dias
* Tendência de alta/baixa
* Interesse regional
* Queries relacionadas

### Scoring

* Tendência crescente → +3 pontos
* Tendência estável → 0 pontos
* Tendência decrescente → -3 pontos

**Prazo:** 1-2 semanas

---

## FASE 3 — SERP & Search Intelligence (📋 PLANEJADO)

**Objetivo:** Adicionar sinais de search volume, shopping signals, keyword data.

### Providers

**SerpAPI:** https://serpapi.com/
* Google Shopping results
* Keyword volume estimates
* Competitor analysis
* Price comparison

**DataForSEO:** https://dataforseo.com/
* Google Shopping API
* Google Trends API
* Keyword research
* SERP features

### Implementação

```python
class SerpProvider:
    def get_shopping_data(query):
        # Product count
        # Price ranges
        # Merchant count
        # Ad presence
        # Shopping features
```

### Métricas

* Volume de anúncios shopping
* Número de merchants
* Faixa de preço
* Presença de ads
* Features destacadas

**Prazo:** 2-3 semanas

---

## FASE 4 — Controlled Web Scraping (📋 PLANEJADO)

**Objetivo:** Coletar dados públicos de marketplaces sem depender de APIs.

### Architecture

```python
class ScraperProvider:
    def scrape_marketplace(query, marketplace='mercadolivre'):
        # Rotating user agents
        # Request throttling
        # Retry logic
        # HTML parsing
        # Anti-detection measures
        # Cache layer
```

### Targets

* Mercado Livre (public listings)
* Shopee
* Amazon.com.br
* Magazine Luiza
* Casas Bahia

### Safety

* Respect robots.txt
* Rate limiting
* Caching (avoid repeat requests)
* User-agent rotation
* Graceful error handling

**Prazo:** 3-4 semanas

---

## FASE 5 — Multi-Marketplace Expansion (📋 FUTURO)

**Objetivo:** Adicionar marketplaces adicionais conforme APIs ficam disponíveis.

### Potential Providers

**Shopee Open Platform**
* Product search
* Pricing data
* Seller metrics

**Amazon Product Advertising API**
* Best sellers
* Price history
* Reviews

**AliExpress Affiliate API**
* Trending products
* Price data
* International signals

**TikTok Shop API** (quando disponível)
* Viral products
* Social commerce signals

**Mercado Livre** (quando policies permitirem)
* Re-enable authenticated requests
* Use approved endpoints only

---

## FASE 6 — Internal Intelligence Layer (📋 FUTURO)

**Objetivo:** Criar vantagem competitiva com dados proprietários.

### Features

**Historical Tracking**
```python
class TrendTracker:
    def track_product_over_time(product_id):
        # Daily snapshots
        # Price evolution
        # Demand changes
        # Competition growth
```

**User Behavior Analytics**
```python
class UserIntelligence:
    def analyze_search_patterns():
        # Most searched products
        # Trending categories
        # User CTR
        # Conversion signals
```

**Predictive Scoring**
```python
class PredictiveEngine:
    def predict_trend_momentum(product, historical_data):
        # ML-based prediction
        # Trend acceleration
        # Saturation detection
        # Opportunity timing
```

### Data Sources

* Historical search database
* User interaction data
* CTR analytics
* Saved searches
* Repeat queries
* Product lifecycle tracking

**Prazo:** 3+ meses

---

# Stack Técnico — Atual

## Backend

* Django 4.2
* Django REST Framework (futuro)
* PostgreSQL
* Python 3.11+

## Frontend

* Django Templates (atual)
* Bootstrap 5
* React (futuro)

## Infrastructure

* Render (deployment)
* GitHub (version control)
* PostgreSQL (Render managed)

## APIs & Services

* Mercado Livre OAuth (implemented, blocked by policy)
* pytrends (planned)
* SerpAPI (planned)
* DataForSEO (planned)

## Security

* OAuth 2.0 + PKCE
* Token encryption
* Environment variables
* CSRF protection
* SSL/HTTPS

---

# Provider Status Matrix

| Provider | Status | Type | Cost | Priority |
|----------|--------|------|------|----------|
| MockProvider | ✅ Active | Fallback | Free | Core |
| MercadoLivreProvider | ⚠️ Blocked | OAuth API | Free | Medium |
| GoogleTrendsProvider | 📋 Planned | pytrends | Free | High |
| SerpProvider | 📋 Planned | SerpAPI | Paid | Medium |
| DataForSEOProvider | 📋 Planned | API | Paid | Medium |
| ScraperProvider | 📋 Planned | Scraping | Free | High |
| ShopeeProvider | 📋 Future | API | Free | Low |
| AmazonProvider | 📋 Future | API | Free | Low |

---

# Development Rules

## Critical Rules

1. ✅ **Never block MVP on external provider approval**
2. ✅ **Always have fallback data**
3. ✅ **Never generate 500 errors from provider failures**
4. ✅ **All providers must support graceful degradation**
5. ✅ **System must always return valid analysis**

## Provider Implementation Rules

```python
# ✅ CORRECT
try:
    data = provider.fetch_data(query)
    if data:
        return normalize_data(data)
except Exception as e:
    log_error(e)
    # Continue to next provider

# ❌ INCORRECT
data = provider.fetch_data(query)  # Can crash entire request
return normalize_data(data)  # No fallback
```

## Scoring Rules

* Minimum 2 providers for production analysis
* Mock data clearly labeled
* Confidence level based on provider count
* Transparent source attribution

---

# Modelo de Monetização — Atualizado

## Gratuito

* 5 análises/dia
* Score básico
* 1 fonte de dados
* Sem histórico

## Pro ($19.90/mês)

* Análises ilimitadas
* Score avançado
* Múltiplas fontes agregadas
* Histórico completo
* Alertas de tendência
* Dados históricos

## Business ($49.90/mês)

* Tudo do Pro
* API access
* White-label reports
* Priority support
* Custom providers

---

# Timeline Realista — Atualizado

## ✅ Semanas 1-4 (Concluído)

* Django structure
* Landing page
* Market app
* OAuth integration
* Token persistence
* Scoring system
* Mock provider
* Deployment

## 🔄 Semana 5 (Atual)

* UI/UX improvements
* Error handling polish
* Provider status indicators
* Documentation updates

## 📋 Semanas 6-7

* Google Trends integration
* Trend scoring
* Historical curves
* Related queries

## 📋 Semanas 8-10

* SERP provider integration
* Shopping signals
* Keyword volume
* Multi-source aggregation

## 📋 Semanas 11-14

* Scraping architecture
* First marketplace scrapers
* Cache layer
* Parser abstraction

## 📋 Semanas 15+

* Additional providers
* Internal intelligence
* Dashboard v2
* User analytics

---

# Prioridade Estratégica

O objetivo NÃO é:

> "ter acesso a todas as APIs possíveis."

O objetivo é:

> **"Agregar múltiplos sinais de mercado para entregar decisões melhores do que qualquer fonte isolada."**

## Vantagem Competitiva

Competitors dependem de:
* Uma única API
* Dados limitados
* Perspectiva única

**Radar de Tendências oferece:**
* Múltiplas fontes
* Agregação inteligente
* Scoring proprietário
* Resiliência a bloqueios
* Inteligência exclusiva

---

# Conclusão

A limitação do Mercado Livre API **NÃO é um problema.**

É uma **oportunidade de construir arquitetura superior.**

Plataformas que dependem de um único provider são vulneráveis.

Plataformas que agregam múltiplas fontes são **valiosas e defensáveis.**

---

# Próximos Passos Imediatos

1. ✅ Documentar arquitetura multi-provider
2. ✅ Documentar bloqueio Mercado Livre
3. 🔄 Polish current MVP UI
4. 📋 Implementar Google Trends
5. 📋 Implementar SERP signals
6. 📋 Build scraping layer

**Foco:** MVP robusto e multi-fonte em 8-12 semanas.
