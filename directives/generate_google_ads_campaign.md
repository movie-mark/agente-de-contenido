# Directive: Generación de Campaña Google Ads Completa

## Objetivo

Generar una campaña completa de Google Ads estructurada con keywords organizadas por intención de búsqueda, anuncios (Responsive Search Ads), extensiones y configuraciones, basándose en el buyer persona y los artículos de blog generados previamente.

## Inputs Requeridos

El script acepta los siguientes argumentos:

- `--buyer-persona-file` (opcional): Ruta al archivo JSON del buyer persona generado por `generate_content.py`
- `--blog-articles-file` (opcional): Ruta al archivo JSON de artículos de blog generado por `generate_blog_articles.py`

Si no se proporcionan archivos, el script puede usar información básica del producto, pero es recomendable proporcionar al menos uno de los archivos para mejores resultados.

## Herramientas

- Script principal: `execution/generate_google_ads_campaign.py`
- API: Claude API (Anthropic)
- Output: Archivo JSON en `.tmp/google_ads_campaign_YYYYMMDD_HHMMSS.json`

## Proceso

### Paso 1: Lectura y Validación

1. Leer los archivos JSON especificados (si se proporcionan)
2. Validar estructura y extraer información:
   - `buyer_persona`: Resumen, dolores, beneficios, motivadores
   - `product_info`: Empresa, tipo_empresa, producto, ubicacion, cliente_principal
   - `articulos`: Keywords de artículos de blog organizadas por etapa

### Paso 2: Generación de Keywords por Intención

La campaña se organiza en grupos de anuncios por intención de búsqueda:

#### 2.1. Intención Informativa (Awareness/Discovery)

**Objetivo**: Personas que buscan información sobre el problema o solución.

**Fuentes de keywords**:
- Artículos de Descubrimiento (del archivo de blog articles)
- Dolores del buyer persona
- Variaciones informativas: "qué es", "cómo funciona", "síntomas de", "problemas de", "por qué"

**Match Types**:
- PHRASE: Para términos específicos
- BROAD_MODIFIER: Para variaciones con mayor alcance

**Cantidad**: 15-20 keywords por grupo

**Ejemplo de grupos**:
- "Problemas y síntomas"
- "Información sobre la condición"
- "Cómo funciona [solución]"

#### 2.2. Intención Transaccional (Consideration/Purchase)

**Objetivo**: Personas que buscan comprar o contratar el servicio.

**Fuentes de keywords**:
- Artículos de Consideración y Decisión
- Términos comerciales: "precio de", "costo de", "dónde hacer", "mejor lugar para", "cuánto cuesta"
- Producto/servicio + ubicación

**Match Types**:
- EXACT: Para términos de alta intención de compra
- PHRASE: Para variaciones comerciales

**Cantidad**: 15-20 keywords por grupo

**Ejemplo de grupos**:
- "Precios y costos"
- "Dónde hacer [servicio]"
- "Mejor [servicio] en [ubicación]"

#### 2.3. Intención Navegacional (Brand/Decision)

**Objetivo**: Personas que buscan específicamente la empresa o marca.

**Fuentes de keywords**:
- Nombre de empresa
- Empresa + ubicación
- Empresa + servicio/producto
- Variaciones del nombre

**Match Types**:
- EXACT: Para búsquedas exactas de marca
- PHRASE: Para variaciones con marca

**Cantidad**: 10-15 keywords

**Ejemplo de grupo**:
- "Búsquedas de marca [Empresa]"

### Paso 3: Generación de Anuncios (Responsive Search Ads)

Para cada grupo de anuncios, generar 3-5 variaciones de anuncios responsive:

**Estructura de cada anuncio**:
- **Headlines** (mínimo 3, recomendado 5-10 variaciones):
  - Incluir keyword principal del grupo
  - Incluir beneficio principal del buyer persona
  - Incluir call-to-action
  - Mencionar ubicación si es relevante
  - Longitud: 30 caracteres máximo por headline

- **Descriptions** (mínimo 2, recomendado 3-4 variaciones):
  - Expandir beneficios específicos
  - Incluir diferenciadores clave
  - Incluir call-to-action
  - Mencionar garantías o certificaciones si aplica
  - Longitud: 90 caracteres máximo por description

- **Final URL**: Sugerencia basada en tipo de artículo o página principal
- **Path1/Path2**: Categorías para tracking (ej: "servicio", "contacto", "blog")

### Paso 4: Generación de Extensiones de Anuncios

Generar extensiones aplicables a toda la campaña:

#### 4.1. Sitelinks (4-6 recomendados)
- Enlaces a páginas importantes del sitio
- Títulos descriptivos y atractivos
- Descripciones cortas (opcional)
- Ejemplos: "Nuestros Servicios", "Sobre Nosotros", "Agendar Cita", "Contacto", "Blog"

#### 4.2. Callouts (4-6 recomendados)
- Beneficios clave extraídos del buyer persona
- Diferenciadores competitivos
- Garantías o certificaciones
- Longitud: 25 caracteres máximo
- Ejemplos: "Tecnología de última generación", "Equipo experto certificado", "Resultados garantizados"

#### 4.3. Structured Snippets
- Tipos de servicio/procedimiento ofrecidos
- Características destacadas
- Organizados por categorías estándar de Google Ads

### Paso 5: Configuraciones de Campaña

Configurar parámetros básicos de la campaña:

- **Nombre de Campaña**: `[Producto] [Ubicación] - [Tipo]`
- **Tipo**: SEARCH (Búsqueda)
- **Ubicaciones**: Basado en `product_info.ubicacion`
- **Idiomas**: Español (es)
- **Presupuesto Sugerido**: Estimación basada en tipo de negocio y competencia
- **Estrategia de Ofertas**: Sugerencia inicial (CPC manual o Maximizar clics)
- **Red de Búsqueda**: Google Search (recomendado inicialmente)

## Output

Archivo JSON con la siguiente estructura:

```json
{
  "timestamp": "YYYY-MM-DDTHH:MM:SS",
  "source_files": {
    "buyer_persona": "ruta/al/archivo.json",
    "blog_articles": "ruta/al/archivo.json"
  },
  "product_info": {
    "empresa": "...",
    "tipo_empresa": "...",
    "producto": "...",
    "ubicacion": "...",
    "cliente_principal": "..."
  },
  "campaign": {
    "name": "Campaña [Producto] [Ubicación]",
    "type": "SEARCH",
    "settings": {
      "locations": ["..."],
      "languages": ["es"],
      "budget_suggestion": "...",
      "bid_strategy": "..."
    },
    "ad_groups": [
      {
        "name": "Intención Informativa - [Tema]",
        "keywords": [
          {
            "keyword": "...",
            "match_type": "PHRASE|EXACT|BROAD_MODIFIER",
            "suggested_bid": "..."
          }
        ],
        "ads": [
          {
            "headlines": ["...", "...", "..."],
            "descriptions": ["...", "..."],
            "final_url": "...",
            "path1": "...",
            "path2": "..."
          }
        ]
      }
    ],
    "extensions": {
      "sitelinks": [
        {
          "text": "...",
          "description": "...",
          "final_url": "..."
        }
      ],
      "callouts": ["...", "..."],
      "structured_snippets": {
        "header": "...",
        "values": ["...", "..."]
      }
    }
  }
}
```

El archivo se guarda en `.tmp/google_ads_campaign_YYYYMMDD_HHMMSS.json`.

## Estrategia de Keywords por Intención

### Informativo
- **Intent de búsqueda**: Aprender sobre el problema/solución
- **Etapa del embudo**: Awareness/Discovery
- **Match types**: PHRASE, BROAD_MODIFIER
- **Ejemplos**: "qué es cirugía refractiva", "síntomas miopía", "problemas lentes contacto"

### Transaccional
- **Intent de búsqueda**: Buscar dónde comprar/contratar
- **Etapa del embudo**: Consideration/Purchase
- **Match types**: EXACT, PHRASE
- **Ejemplos**: "precio cirugía refractiva", "dónde hacer cirugía refractiva Bogotá"

### Navegacional
- **Intent de búsqueda**: Buscar marca específica
- **Etapa del embudo**: Decision
- **Match types**: EXACT, PHRASE
- **Ejemplos**: "Visiontech Clinic", "Visiontech Bogotá"

## Mejores Prácticas Implementadas

### Keywords
- Agrupar keywords similares en mismo grupo de anuncios
- Usar match types apropiados para cada intención
- Incluir variaciones de palabras clave (singular/plural, sinónimos)
- Sugerir bids iniciales (estimaciones, ajustar según datos reales)

### Anuncios
- Headlines relevantes que incluyan keywords del grupo
- Descriptions que expandan beneficios y diferenciadores
- CTAs claros y orientados a acción
- Múltiples variaciones para testing A/B
- URLs relevantes y descriptivas

### Extensiones
- Sitelinks a páginas de alta conversión
- Callouts que resalten beneficios únicos
- Structured snippets organizados por categoría

## Edge Cases y Manejo de Errores

### Validación de Input
- Verificar que los archivos JSON existen (si se proporcionan)
- Validar formato JSON
- Validar que contienen las secciones necesarias
- Si no hay archivos, usar información mínima requerida

### Errores de API
- **Rate Limits**: Esperar e informar al usuario
- **Timeout**: Reintentar hasta 2 veces
- **Errores de Autenticación**: Verificar `CLAUDE_API_KEY`
- **Errores de Red**: Retry lógico para errores transitorios

### Validación de Contenido
- Asegurar que headlines no excedan 30 caracteres
- Asegurar que descriptions no excedan 90 caracteres
- Asegurar que callouts no excedan 25 caracteres
- Validar formato de URLs (placeholder si no hay URL real)

## Variables de Entorno

El script requiere las siguientes variables en `.env`:

- `CLAUDE_API_KEY`: API key de Anthropic (requerido)
- `CLAUDE_MODEL`: Modelo a usar (opcional, default: `claude-3-5-sonnet-20241022`)

## Ejemplo de Uso

```bash
# Con ambos archivos
python3 execution/generate_google_ads_campaign.py \
  --buyer-persona-file .tmp/content_output_20251216_125317.json \
  --blog-articles-file .tmp/blog_articles_20251216_134459.json

# Solo con buyer persona
python3 execution/generate_google_ads_campaign.py \
  --buyer-persona-file .tmp/content_output_20251216_125317.json

# Solo con artículos de blog
python3 execution/generate_google_ads_campaign.py \
  --blog-articles-file .tmp/blog_articles_20251216_134459.json
```

## Notas Importantes

- **URLs**: Las URLs finales pueden ser placeholders o sugerencias. Deben actualizarse con URLs reales antes de publicar.
- **Bids**: Los bids sugeridos son estimaciones iniciales y deben ajustarse según datos de mercado y performance.
- **Presupuesto**: El presupuesto sugerido es una recomendación inicial basada en tipo de negocio.
- **Importación**: La estructura JSON es compatible con herramientas de gestión de Google Ads, pero puede requerir transformación para importación directa.

## Mejoras Futuras

- Generación de archivos CSV para importación directa a Google Ads Editor
- Integración con Google Ads API para creación automática de campañas
- Análisis de competencia para ajustar bids y keywords
- Generación de negative keywords
- Sugerencias de landing pages optimizadas
- Análisis de ROI estimado

