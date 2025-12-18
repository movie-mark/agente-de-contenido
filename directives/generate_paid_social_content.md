# Directive: Generación de Contenido para Redes Sociales Pagas

## Objetivo

Generar ideas de contenido para redes sociales pagas organizadas por etapas del embudo de marketing (Descubrimiento, Consideración, Decisión), cada una con una estrategia específica de conversión.

## Inputs Requeridos

- **Archivo JSON del buyer persona**: Ruta al archivo JSON generado previamente por `generate_content.py` que contiene:
  - `buyer_persona`: Resumen, dolores, beneficios, motivadores de compra
  - `product_info`: Empresa, tipo_empresa, producto, ubicacion, cliente_principal

El script acepta el argumento `--input-file` con la ruta al archivo JSON.

## Herramientas

- Script principal: `execution/generate_paid_social_content.py`
- API: Claude API (Anthropic)
- Output: Archivo JSON en `.tmp/paid_social_content_YYYYMMDD_HHMMSS.json`

## Proceso

### Paso 1: Lectura y Validación

1. Leer el archivo JSON especificado
2. Validar que contiene las secciones necesarias:
   - `buyer_persona` (resumen, dolores, beneficios, motivadores_compra)
   - `product_info` (empresa, tipo_empresa, producto, ubicacion, cliente_principal)
3. Extraer toda la información necesaria para los prompts
4. Formatear el buyer persona como texto para usar en los prompts

### Paso 2: Generación de Contenido por Etapa (En Paralelo)

Las tres etapas se generan simultáneamente usando `ThreadPoolExecutor` para optimizar el tiempo de ejecución.

#### 2.1. Descubrimiento (10 ideas)

**Objetivo**: Generar identificación emocional y conciencia del problema sin mencionar aún la solución quirúrgica/procedimiento, preparando el terreno para la siguiente etapa.

**Estrategia**:
- NO mencionar aún la solución específica (cirugía, procedimiento, etc.)
- Enfocarse en hacer que la audiencia se identifique con el problema
- Generar conexión emocional con sus dolores
- Crear conciencia de que existe un problema que necesita solución
- No vender aún, solo sensibilizar sobre el problema

**Estructura de cada idea**:
- `titulo`: Título descriptivo del contenido
- `gancho`: El gancho que tendría al principio del video
- `concepto`: Breve descripción del concepto de la idea

**Prompt base**:
```
Teniendo en cuenta que mi perfil de cliente es:

{buyer_persona_texto}

Genera EXACTAMENTE 10 ideas específicas de videos cortos para redes sociales pagas dirigidos a mis clientes. 

La temática debe ser de DESCUBRIMIENTO: generar identificación emocional y conciencia del problema sin mencionar aún la solución quirúrgica/procedimiento, preparando el terreno para la siguiente etapa.

IMPORTANTE:
- NO menciones aún la solución específica (cirugía, procedimiento, etc.)
- Enfócate en hacer que la audiencia se identifique con el problema
- Genera conexión emocional con sus dolores
- Crea conciencia de que existe un problema que necesita solución
- No vendas aún, solo sensibiliza sobre el problema

Para cada idea dame un título descriptivo, el gancho que tendría al principio y una breve descripción del concepto de la idea.

Responde en formato JSON con un array de objetos, cada uno con las claves: "titulo", "gancho" y "concepto".
```

#### 2.2. Consideración (10 ideas)

**Objetivo**: Establecer superioridad técnica y confianza en el método, diferenciando claramente el enfoque especializado de las opciones genéricas disponibles.

**Estrategia**:
- Mostrar la superioridad técnica del método/procedimiento
- Diferenciar tu enfoque especializado de opciones genéricas
- Generar confianza en el método y la tecnología
- Transición Natural hacia Decisión: cada video debe terminar plantando la semilla de "este es el método correcto, ahora necesitas al especialista correcto para ejecutarlo"
- NO vender aún directamente tu empresa, vender el método correcto

**Estructura de cada idea**:
- `titulo`: Título descriptivo del contenido
- `gancho`: El gancho que tendría al principio del video
- `concepto`: Breve descripción del concepto de la idea

**Prompt base**:
```
Teniendo en cuenta que mi perfil de cliente es:

{buyer_persona_texto}

Genera EXACTAMENTE 10 ideas específicas de videos cortos para redes sociales pagas dirigidos a mis clientes. 

La temática debe ser de CONSIDERACIÓN: establecer superioridad técnica y confianza en el método, diferenciando claramente el enfoque especializado de {empresa} de las opciones genéricas disponibles.

IMPORTANTE:
- Muestra la superioridad técnica del método/procedimiento
- Diferencia tu enfoque especializado de opciones genéricas
- Genera confianza en el método y la tecnología
- Transición Natural hacia Decisión: cada video debe terminar plantando la semilla de "este es el método correcto, ahora necesitas al especialista correcto para ejecutarlo"
- NO vendas aún directamente tu empresa, vende el método correcto

Para cada idea dame un título descriptivo, el gancho que tendría al principio y una breve descripción del concepto de la idea.

Responde en formato JSON con un array de objetos, cada uno con las claves: "titulo", "gancho" y "concepto".
```

#### 2.3. Decisión (10 ideas)

**Objetivo**: Generar confianza personal en {empresa} como LA opción para este procedimiento específico, moviendo de "necesito esta cirugía/procedimiento" a "necesito que ME LA HAGA ELLOS/EN {empresa}".

**Estrategia**:
- Enfocarse en construir confianza personal en {empresa}
- Mostrar por qué {empresa} es LA opción correcta
- Transicionar de "necesito este procedimiento" a "necesito que me lo hagan ellos"
- Mostrar experiencia, casos de éxito, credenciales
- Generar urgencia y acción hacia {empresa} específicamente

**Estructura de cada idea**:
- `titulo`: Título descriptivo del contenido
- `gancho`: El gancho que tendría al principio del video
- `concepto`: Breve descripción del concepto de la idea

**Prompt base**:
```
Teniendo en cuenta que mi perfil de cliente es:

{buyer_persona_texto}

Genera EXACTAMENTE 10 ideas específicas de videos cortos para redes sociales pagas dirigidos a mis clientes. 

La temática debe ser de DECISIÓN: generar confianza personal en {empresa} como LA opción para este procedimiento específico, moviendo de "necesito esta cirugía/procedimiento" a "necesito que ME LA HAGA ELLOS/EN {empresa}".

IMPORTANTE:
- Enfócate en construir confianza personal en {empresa}
- Muestra por qué {empresa} es LA opción correcta
- Transiciona de "necesito este procedimiento" a "necesito que me lo hagan ellos"
- Muestra experiencia, casos de éxito, credenciales
- Genera urgencia y acción hacia {empresa} específicamente

Para cada idea dame un título descriptivo, el gancho que tendría al principio y una breve descripción del concepto de la idea.

Responde en formato JSON con un array de objetos, cada uno con las claves: "titulo", "gancho" y "concepto".
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
  "contenido": {
    "descubrimiento": [
      {
        "titulo": "...",
        "gancho": "...",
        "concepto": "..."
      },
      ...
    ],
    "consideracion": [...],
    "decision": [...]
  }
}
```

El archivo se guarda en `.tmp/paid_social_content_YYYYMMDD_HHMMSS.json` donde la fecha/hora corresponde al momento de ejecución.

## Estrategia por Etapa

### Descubrimiento (Awareness Stage)

**Intent**: Identificación emocional - la persona se identifica con el problema
**Enfoque de contenido**: Problema, dolores, consecuencias emocionales
**Objetivo**: Sensibilizar sin vender
**Transición**: Preparar terreno para que acepten que existe una solución

**Ejemplos de temas**:
- Situaciones cotidianas donde el problema se manifiesta
- Consecuencias emocionales del problema
- Historias de identificación con el dolor
- Realidades no habladas del problema

### Consideración (Consideration Stage)

**Intent**: Investigativo - la persona acepta que hay solución y quiere conocer el método correcto
**Enfoque de contenido**: Método, tecnología, diferenciadores técnicos
**Objetivo**: Establecer confianza en el método correcto
**Transición**: "Este es el método correcto, ahora necesitas el especialista correcto"

**Ejemplos de temas**:
- Por qué este método es superior
- Tecnología vs métodos tradicionales
- Diferencias técnicas importantes
- Beneficios del método correcto

### Decisión (Decision Stage)

**Intent**: Transaccional - la persona quiere la solución y busca dónde obtenerla
**Enfoque de contenido**: Por qué esta empresa/profesional es la mejor opción
**Objetivo**: Generar confianza personal y acción hacia la empresa específica
**Transición**: "Necesito que me lo hagan ellos"

**Ejemplos de temas**:
- Casos de éxito de la empresa
- Experiencia y credenciales
- Testimonios y resultados
- Por qué elegir esta empresa específicamente
- Urgencia y llamados a la acción

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
- Validar que cada etapa genere exactamente 10 ideas

### Formato de Respuesta
- Si Claude no devuelve JSON válido, intentar parsear manualmente
- Validar estructura de cada idea (debe tener título, gancho, concepto)
- Limitar a máximo 10 ideas por etapa (tomar las primeras 10 si hay más)

## Webhook

Si `WEBHOOK_URL_PAID_SOCIAL_CONTENT` está configurado en `.env`, el script enviará automáticamente un webhook al completar exitosamente la generación.

**Estructura del payload del webhook**:
- Las ideas se convierten de arrays a objetos con claves numeradas (`idea_1`, `idea_2`, etc.) para facilitar el mapeo en n8n/Make.com
- Cada etapa tiene su `count` y sus `items` como objeto

## Variables de Entorno

El script requiere las siguientes variables en `.env`:

- `CLAUDE_API_KEY`: API key de Anthropic (requerido)
- `CLAUDE_MODEL`: Modelo a usar (opcional, default: `claude-3-5-sonnet-20241022`)
- `WEBHOOK_URL_PAID_SOCIAL_CONTENT`: URL del webhook para notificaciones (opcional)

## Ejemplo de Uso

```bash
python3 execution/generate_paid_social_content.py --input-file .tmp/content_output_20251216_125317.json
```

## Mejoras Futuras

- Opción para generar solo etapas específicas (no todas)
- Personalización de cantidad de ideas por etapa
- Integración con plataformas de redes sociales para publicación directa
- Análisis de performance de contenido similar
- Sugerencias de optimización basadas en formato de plataforma (Reels, Stories, Feed, etc.)
- Generación de variaciones de cada idea para A/B testing


