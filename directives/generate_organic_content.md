# Directive: Generación de Contenido Orgánico para Clientes

## Objetivo

Generar contenido orgánico para clientes mediante un proceso de dos etapas:
1. Crear un perfil detallado del buyer persona basado en información del producto/servicio/tratamiento
2. Generar 50 ideas de contenido (10 por cada tipo) usando el buyer persona como contexto

## Inputs Requeridos

El script solicitará interactivamente la siguiente información:

- **Nombre de la empresa o Persona**: Nombre del negocio o persona que vende
- **Qué es la empresa**: Tipo de empresa/negocio
- **Qué vendes en esta campaña**: Descripción del producto/servicio/tratamiento específico
- **En dónde lo vendes**: Ubicación o canal de venta
- **Principal Cliente**: Descripción del cliente objetivo principal

## Herramientas

- Script principal: `execution/generate_content.py`
- API: Claude API (Anthropic)
- Output: Archivo JSON en `.tmp/content_output_YYYYMMDD_HHMMSS.json`

## Proceso

### Paso 1: Generar Buyer Persona

Usa el siguiente prompt base (adaptado de `Old_Pompts.md`):

```
Soy {nombre_empresa}, {tipo_empresa}, y vendo {producto}, en {ubicacion} y mi principal cliente son {cliente_principal}. 

Crea un resumen a modo de estudio del cliente, de las características de las personas que me compran y qué buscan en mi producto. Incluye al menos 10 de sus dolores, y al menos 10 beneficios que proporciona mi producto, así como los principales motivadores de compra.
```

El resultado debe estructurarse en:
- Resumen general del cliente
- Lista de al menos 10 dolores
- Lista de al menos 10 beneficios del producto
- Lista de motivadores de compra principales

### Paso 2: Generar Tipos de Contenido

Para cada tipo de contenido, usa el buyer persona generado como contexto y aplica el prompt correspondiente:

#### 2.1. Contenido de Opinión Personal
```
Teniendo en cuenta que mi perfil de cliente es:

{buyer_persona_completo}

Dame 10 ideas específicas de videos cortos para redes sociales dirigidos a mis clientes. La temática de estas ideas debe ser opinión personal (comentar noticia o tema polémico). Deben ser ideas muy interesantes. Deben lograr que la audiencia conecte conmigo y mi producto. Para cada idea dame el gancho que tendría al principio y una breve descripción del concepto de la idea.

Responde en formato JSON con un array de objetos, cada uno con las claves: "gancho" y "descripcion".
```

#### 2.2. Contenido de Información Contraintuitiva
```
Teniendo en cuenta que mi perfil de cliente es:

{buyer_persona_completo}

Dame 10 ideas específicas de videos cortos para redes sociales dirigidos a mis clientes. La temática de estas ideas debe ser contenido educativo con información contraintuitiva. Deben ser ideas muy interesantes. Deben lograr que la audiencia conecte conmigo y mi producto. Para cada idea dame el gancho que tendría al principio y una breve descripción del concepto de la idea.

Responde en formato JSON con un array de objetos, cada uno con las claves: "gancho" y "descripcion".
```

#### 2.3. Contenido Educativo Práctico
```
Teniendo en cuenta que mi perfil de cliente es:

{buyer_persona_completo}

Dame 10 ideas específicas de videos cortos para redes sociales dirigidos a mis clientes. La temática de estas ideas debe ser contenido educativo con información práctica muy útil. Deben ser ideas muy interesantes. Deben lograr que la audiencia conecte conmigo y mi producto. Para cada idea dame el gancho que tendría al principio y una breve descripción del concepto de la idea.

Responde en formato JSON con un array de objetos, cada uno con las claves: "gancho" y "descripcion".
```

#### 2.4. Contenido de Historias Interesantes y Logros
```
Teniendo en cuenta que mi perfil de cliente es:

{buyer_persona_completo}

Dame 10 ideas específicas de videos cortos para redes sociales dirigidos a mis clientes. La temática de estas ideas debe ser historias interesantes MÍAS (de quien crea el contenido - el profesional o empresa), y particularmente logros profesionales, casos exitosos que haya manejado, momentos de superación profesional, o logros significativos en mi carrera o negocio. Deben ser ideas muy interesantes que muestren mi experiencia, resultados y trayectoria. Deben lograr que la audiencia conecte conmigo y mi producto. Para cada idea dame el gancho que tendría al principio y una breve descripción del concepto de la idea.

Responde en formato JSON con un array de objetos, cada uno con las claves: "gancho" y "descripcion".
```

#### 2.5. Contenido de Momentos Vulnerables
```
Teniendo en cuenta que mi perfil de cliente es:

{buyer_persona_completo}

Dame 10 ideas específicas de videos cortos para redes sociales dirigidos a mis clientes. La temática de estas ideas debe ser momentos vulnerables MÍOS (de quien crea el contenido - el profesional o empresa), no de los clientes. Estos deben ser momentos personales, honestos y auténticos que muestren mi humanidad, mis dudas, mis errores, mis miedos o momentos difíciles relacionados con mi profesión, negocio o trayectoria. Deben ser ideas muy interesantes que generen conexión emocional y humanicen mi marca. Para cada idea dame el gancho que tendría al principio y una breve descripción del concepto de la idea.

Responde en formato JSON con un array de objetos, cada uno con las claves: "gancho" y "descripcion".
```

## Output

Archivo JSON con la siguiente estructura:

```json
{
  "timestamp": "YYYY-MM-DDTHH:MM:SS",
  "product_info": {
    "empresa": "...",
    "tipo_empresa": "...",
    "producto": "...",
    "ubicacion": "...",
    "cliente_principal": "..."
  },
  "buyer_persona": {
    "resumen": "...",
    "dolores": ["dolor1", "dolor2", ...],
    "beneficios": ["beneficio1", "beneficio2", ...],
    "motivadores_compra": ["motivador1", "motivador2", ...]
  },
  "contenido": {
    "opinion_personal": [
      {"gancho": "...", "descripcion": "..."},
      ...
    ],
    "contraintuitivo": [
      {"gancho": "...", "descripcion": "..."},
      ...
    ],
    "educativo_practico": [
      {"gancho": "...", "descripcion": "..."},
      ...
    ],
    "historias_logros": [
      {"gancho": "...", "descripcion": "..."},
      ...
    ],
    "momentos_vulnerables": [
      {"gancho": "...", "descripcion": "..."},
      ...
    ]
  }
}
```

El archivo se guarda en `.tmp/content_output_YYYYMMDD_HHMMSS.json` donde la fecha/hora corresponde al momento de ejecución.

## Edge Cases y Manejo de Errores

### Validación de Inputs
- Todos los campos son requeridos. Si alguno está vacío, solicitar nuevamente.
- Validar que las respuestas no sean solo espacios en blanco.

### Errores de API
- **Rate Limits**: Si se alcanza el rate limit, esperar e informar al usuario. Considerar implementar retry con backoff exponencial.
- **Timeout**: Si una llamada excede el timeout, reintentar hasta 2 veces antes de fallar.
- **Errores de Autenticación**: Verificar que `CLAUDE_API_KEY` esté correctamente configurada en `.env`.
- **Errores de Red**: Implementar retry lógico para errores transitorios.

### Estado Intermedio
- Si falla la generación de buyer persona, no continuar con los contenidos.
- Si falla la generación de un tipo de contenido específico, registrar el error pero continuar con los demás tipos.
- Si hay un fallo parcial, guardar el estado hasta donde se llegó (con notas de errores).

### Formato de Respuesta
- Si Claude no devuelve JSON válido, intentar parsear manualmente o solicitar formato correcto.
- Validar que cada tipo de contenido tenga exactamente 10 ideas (o al menos un número razonable si hay problemas).

## Variables de Entorno

El script requiere las siguientes variables en `.env`:

- `CLAUDE_API_KEY`: API key de Anthropic (requerido)
- `CLAUDE_MODEL`: Modelo a usar (opcional, default: `claude-3-5-sonnet-20241022`)

## Mejoras Futuras

- Opción para generar solo tipos específicos de contenido (no todos)
- Integración con Google Sheets como deliverable alternativo
- Guardar historial de ejecuciones para referencia
- Validación y mejora automática de prompts basada en resultados


