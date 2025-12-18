# Directive: Generación de Ideas de Artículos de Blog con Estrategia SEO

## Objetivo

Generar ideas de artículos de blog organizadas por etapas del embudo de marketing (Descubrimiento, Consideración, Decisión), cada una con una estrategia SEO específica que incluye keywords principales y secundarias.

## Inputs Requeridos

- **Archivo JSON del buyer persona**: Ruta al archivo JSON generado previamente por `generate_content.py` que contiene:
  - `buyer_persona`: Resumen, dolores, beneficios, motivadores de compra
  - `product_info`: Empresa, tipo_empresa, producto, ubicacion, cliente_principal

El script acepta el argumento `--input-file` con la ruta al archivo JSON.

## Herramientas

- Script principal: `execution/generate_blog_articles.py`
- API: Claude API (Anthropic)
- Output: Archivo JSON en `.tmp/blog_articles_YYYYMMDD_HHMMSS.json`

## Proceso

### Paso 1: Lectura y Validación

1. Leer el archivo JSON especificado
2. Validar que contiene las secciones necesarias:
   - `buyer_persona` (resumen, dolores, beneficios, motivadores_compra)
   - `product_info` (empresa, tipo_empresa, producto, ubicacion, cliente_principal)
3. Extraer toda la información necesaria para los prompts

### Paso 2: Generación de Artículos por Etapa

#### 2.1. Descubrimiento (4 artículos)

**Objetivo**: Personas que están descubriendo que tienen un problema.

**Estrategia SEO**:
- Keywords relacionadas con dolores/problemas identificados en el buyer persona
- Términos de búsqueda que usa alguien que aún no conoce la solución
- Ejemplos: "problemas de visión sin gafas", "sequedad ocular por lentes", "incomodidad con lentes de contacto"

**Prompt base**:
```
Basándote en el perfil de buyer persona y los dolores identificados, genera 4 ideas de artículos de blog para personas que están descubriendo que tienen un problema. Estos artículos deben hablar sobre el problema, sus síntomas, consecuencias, impacto en la vida diaria, etc.

Para cada artículo proporciona:
- Título atractivo y optimizado para SEO (máximo 60 caracteres)
- Descripción del contenido del artículo (qué temas cubrirá, estructura sugerida)
- Keyword principal (relacionada con el problema/dolor específico)
- 2 keywords secundarias (también relacionadas con el problema, pero variaciones del término principal)

Las keywords deben ser términos que alguien usaría al buscar información sobre el problema, NO sobre la solución. Piensa en cómo buscaría alguien que aún no sabe que existe una solución específica.

Responde en formato JSON con un array de objetos, cada uno con las claves: "titulo", "descripcion", "keyword_principal", "keywords_secundarias" (array con 2 elementos).
```

#### 2.2. Consideración (3 artículos)

**Objetivo**: Personas que ya conocen el problema y están considerando soluciones.

**Estrategia SEO**:
- Keywords que incluyen el nombre del producto/servicio/procedimiento
- Términos de búsqueda sobre la solución específica
- Ejemplos: "cirugía refractiva", "cirugía láser para la vista", "operación para corregir miopía"

**Prompt base**:
```
Basándote en el perfil de buyer persona y el producto/servicio {producto}, genera 3 ideas de artículos de blog para personas que ya conocen el problema y están considerando soluciones. Estos artículos deben hablar sobre la solución (producto/servicio), cómo funciona, beneficios, proceso, etc.

Para cada artículo proporciona:
- Título atractivo y optimizado para SEO (máximo 60 caracteres)
- Descripción del contenido del artículo (qué temas cubrirá, estructura sugerida)
- Keyword principal (debe incluir el nombre del producto/servicio/procedimiento)
- 2 keywords secundarias (también relacionadas con el producto/servicio, pueden incluir variaciones o términos relacionados)

Las keywords deben ser términos que alguien usaría al buscar información sobre el producto/servicio específico. La persona ya sabe que existe esta solución y quiere saber más sobre ella.

Responde en formato JSON con un array de objetos, cada uno con las claves: "titulo", "descripcion", "keyword_principal", "keywords_secundarias" (array con 2 elementos).
```

#### 2.3. Decisión (3 artículos)

**Objetivo**: Personas que están listas para decidir dónde obtener la solución.

**Estrategia SEO**:
- Keywords que incluyen el nombre de la empresa o empresa + ubicación
- Términos de comparación o búsqueda local
- Ejemplos: "Visiontech Clinic", "cirugía refractiva Bogotá", "mejor clínica oftalmológica Bogotá", "cirugía láser recomendada en {ubicacion}"

**Prompt base**:
```
Basándote en el perfil de buyer persona, el producto/servicio {producto}, la información de la empresa {empresa} y la ubicación {ubicacion}, genera 3 ideas de artículos de blog para personas que están listas para decidir dónde obtener la solución. Estos artículos deben hablar sobre por qué esta empresa/profesional es la mejor opción, qué los diferencia, experiencia, casos de éxito, etc.

Para cada artículo proporciona:
- Título atractivo y optimizado para SEO (máximo 60 caracteres)
- Descripción del contenido del artículo (qué temas cubrirá, estructura sugerida)
- Keyword principal (debe incluir el nombre de la empresa, o empresa + ubicación, o términos como "mejor {tipo_empresa} {ubicacion}")
- 2 keywords secundarias (pueden incluir empresa + servicio, empresa + ubicación, o términos de comparación como "mejor", "recomendado", "precio", etc.)

Las keywords deben ser términos que alguien usaría al buscar específicamente la empresa o comparar opciones en la ubicación. La persona ya decidió que quiere la solución y está buscando dónde obtenerla.

Responde en formato JSON con un array de objetos, cada uno con las claves: "titulo", "descripcion", "keyword_principal", "keywords_secundarias" (array con 2 elementos).
```

## Output

Archivo JSON con la siguiente estructura:

```json
{
  "timestamp": "YYYY-MM-DDTHH:MM:SS",
  "source_file": "ruta/al/archivo/original.json",
  "product_info": {
    "empresa": "...",
    "tipo_empresa": "...",
    "producto": "...",
    "ubicacion": "...",
    "cliente_principal": "..."
  },
  "articulos": {
    "descubrimiento": [
      {
        "titulo": "...",
        "descripcion": "...",
        "keyword_principal": "...",
        "keywords_secundarias": ["...", "..."]
      },
      ...
    ],
    "consideracion": [...],
    "decision": [...]
  }
}
```

El archivo se guarda en `.tmp/blog_articles_YYYYMMDD_HHMMSS.json` donde la fecha/hora corresponde al momento de ejecución.

## Estrategia SEO Detallada

### Descubrimiento (Awareness Stage)

**Intent de búsqueda**: Informativo - la persona no sabe que hay una solución específica
**Enfoque de contenido**: Problema, síntomas, consecuencias, impacto
**Keywords**: 
- Basadas en dolores/pain points
- Preguntas comunes ("por qué", "qué causa", "cómo afecta")
- Sintomas y problemas cotidianos

### Consideración (Consideration Stage)

**Intent de búsqueda**: Investigativo - la persona sabe que existe una solución y quiere entenderla
**Enfoque de contenido**: Solución, cómo funciona, beneficios, proceso
**Keywords**:
- Nombre del producto/servicio/procedimiento
- "Cómo funciona", "qué es", "beneficios de"
- Comparaciones ("vs", "alternativas")

### Decisión (Decision Stage)

**Intent de búsqueda**: Transaccional - la persona quiere comprar/contratar y busca dónde
**Enfoque de contenido**: Por qué somos mejores, diferenciadores, casos de éxito
**Keywords**:
- Nombre de empresa
- Empresa + ubicación
- Empresa + servicio
- "Mejor", "recomendado", "precio", "opiniones"
- Búsquedas locales

## Edge Cases y Manejo de Errores

### Validación de Input
- Verificar que el archivo JSON existe
- Validar formato JSON válido
- Verificar que contiene `buyer_persona` y `product_info`
- Validar que las secciones tienen los campos necesarios

### Errores de API
- **Rate Limits**: Esperar e informar al usuario. Considerar retry con backoff exponencial
- **Timeout**: Reintentar hasta 2 veces antes de fallar
- **Errores de Autenticación**: Verificar que `CLAUDE_API_KEY` esté configurada en `.env`
- **Errores de Red**: Implementar retry lógico para errores transitorios

### Estado Intermedio
- Si falla la generación de una etapa específica, registrar el error pero continuar con las demás
- Guardar estado parcial si hay fallos (con notas de errores)
- Validar que cada etapa genere el número correcto de artículos

### Formato de Respuesta
- Si Claude no devuelve JSON válido, intentar parsear manualmente
- Validar estructura de cada artículo (debe tener título, descripción, keyword_principal, keywords_secundarias)
- Asegurar que keywords_secundarias sea un array con exactamente 2 elementos

## Variables de Entorno

El script requiere las siguientes variables en `.env`:

- `CLAUDE_API_KEY`: API key de Anthropic (requerido)
- `CLAUDE_MODEL`: Modelo a usar (opcional, default: `claude-3-5-sonnet-20241022`)

## Ejemplo de Uso

```bash
python3 execution/generate_blog_articles.py --input-file .tmp/content_output_20251216_125317.json
```

## Mejoras Futuras

- Opción para generar solo etapas específicas (no todas)
- Validación de competencia de keywords usando herramientas SEO
- Sugerencias de extensión de artículo basadas en keyword difficulty
- Integración con Google Sheets como deliverable alternativo
- Generación de briefs más detallados para cada artículo

