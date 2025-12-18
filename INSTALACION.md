# Guía de Instalación y Configuración

Esta guía te ayudará a configurar el proyecto en un nuevo computador.

## Instalación Automática (Para Cursor/AI Assistant)

Sigue estos pasos en orden. Si algo ya está instalado, el comando te lo dirá y puedes continuar al siguiente paso.

### Paso 1: Verificar si Python está instalado

Primero verifica si Python 3 ya está instalado ejecutando:
```
python3 --version
```

Si ves un número de versión (como "Python 3.9.6" o superior), Python está instalado y puedes pasar al Paso 3.

Si ves un error como "command not found", necesitas instalar Python. Ve al Paso 2.

### Paso 2: Instalar Python según el sistema operativo

**Si estás en macOS:**

Primero verifica si tienes Homebrew instalado ejecutando:
```
brew --version
```

Si Homebrew está instalado, simplemente ejecuta:
```
brew install python3
```

Si Homebrew NO está instalado, primero instálalo ejecutando:
```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Luego instala Python con:
```
brew install python3
```

**Si estás en Linux (Ubuntu o Debian):**

Ejecuta estos dos comandos en orden:
```
sudo apt update
sudo apt install python3 python3-pip -y
```

**Si estás en Linux (Fedora o RHEL):**

Ejecuta:
```
sudo dnf install python3 python3-pip -y
```

**Si estás en Windows:**

Descarga Python desde https://www.python.org/downloads/ y ejecuta el instalador. Asegúrate de marcar la opción "Add Python to PATH" durante la instalación.

Después de instalar Python, vuelve al Paso 1 para verificar que se instaló correctamente.

### Paso 3: Verificar que pip está disponible

Ejecuta:
```
pip3 --version
```

Si ves un número de versión, pip está listo. Continúa al Paso 4.

Si ves un error, instala pip ejecutando:
```
python3 -m ensurepip --upgrade
```

O en Linux, puedes instalar pip directamente:
```
sudo apt install python3-pip
```
(o `sudo dnf install python3-pip` en Fedora)

### Paso 4: Navegar a la carpeta del proyecto

Navega a la carpeta donde copiaste el proyecto. Si la carpeta está en el escritorio, por ejemplo, ejecuta:
```
cd ~/Desktop/"Agente de Movie-Mark"
```

O si está en otra ubicación, ajusta la ruta. Puedes verificar dónde estás con:
```
pwd
```

### Paso 5: Instalar las dependencias del proyecto

Con la carpeta del proyecto como ubicación actual, ejecuta:
```
pip3 install -r requirements.txt
```

Si ves un error de permisos, usa esta versión en su lugar:
```
pip3 install --user -r requirements.txt
```

Esto instalará las librerías necesarias: anthropic (para Claude API) y python-dotenv (para leer variables de entorno).

### Paso 6: Dar permisos de ejecución a los scripts

En macOS o Linux, ejecuta:
```
chmod +x execution/*.py
```

En Windows, este paso no es necesario.

### Paso 7: Verificar que todo funciona

Ejecuta este comando para probar que todo está bien:
```
python3 execution/generate_content.py --help
```

Si ves un mensaje de ayuda mostrando las opciones del script, ¡todo está funcionando correctamente!

### Paso 8: Verificar o crear el archivo .env

Verifica si existe el archivo `.env` en la raíz del proyecto. Si no existe, créalo con este contenido:

```
CLAUDE_API_KEY=tu_api_key_aqui
CLAUDE_MODEL=claude-3-5-sonnet-20241022
```

Recuerda reemplazar `tu_api_key_aqui` con tu API key real de Anthropic.

---

## Requisitos Previos (Referencia)

1. **Python 3.9 o superior**
   - Verifica si ya lo tienes instalado: `python3 --version`
   - Si no lo tienes, descárgalo desde [python.org](https://www.python.org/downloads/)

2. **pip** (gestor de paquetes de Python)
   - Generalmente viene incluido con Python
   - Verifica: `pip3 --version`

## Pasos de Instalación Detallados

### 1. Copiar los archivos

Copia toda la carpeta del proyecto a tu nuevo computador. Asegúrate de copiar:
- Todos los archivos `.py` en `execution/`
- Todos los archivos `.md` en `directives/`
- `requirements.txt`
- `.gitignore`
- `.env` (si existe - **IMPORTANTE**: este archivo contiene tus API keys)

### 2. Crear/Configurar el archivo `.env`

Si no copiaste el archivo `.env`, créalo en la raíz del proyecto con el siguiente contenido:

```env
# API Key de Anthropic (Claude)
CLAUDE_API_KEY=tu_api_key_aqui

# Modelo de Claude a usar (opcional, por defecto usa claude-3-5-sonnet-20241022)
CLAUDE_MODEL=claude-3-5-sonnet-20241022
```

**⚠️ IMPORTANTE**: 
- Reemplaza `tu_api_key_aqui` con tu API key real de Anthropic
- Este archivo NO debe compartirse públicamente (ya está en `.gitignore`)

### 3. Instalar dependencias de Python

Abre una terminal en la carpeta del proyecto y ejecuta:

```bash
pip3 install -r requirements.txt
```

Esto instalará:
- `anthropic` - SDK para usar Claude API
- `python-dotenv` - Para cargar variables de entorno desde `.env`

**Nota**: Si tienes problemas de permisos, usa:
```bash
pip3 install --user -r requirements.txt
```

### 4. Dar permisos de ejecución a los scripts (opcional pero recomendado)

En macOS/Linux:
```bash
chmod +x execution/*.py
```

Esto permitirá ejecutar los scripts directamente.

### 5. Verificar que todo funciona

Prueba ejecutando uno de los scripts con el flag `--help`:

```bash
python3 execution/generate_content.py --help
```

Deberías ver la ayuda del script. Si funciona, ¡todo está listo!

## Estructura de Directorios

El proyecto debe tener esta estructura:

```
Agente de Movie-Mark/
├── .env                    # Variables de entorno (crear si no existe)
├── .gitignore             # Archivos ignorados por git
├── GEMINI.md              # Instrucciones del agente
├── Old_Pompts.md          # Prompts anteriores (referencia)
├── requirements.txt       # Dependencias Python
├── directives/            # Directivas (SOPs)
│   ├── generate_blog_articles.md
│   ├── generate_google_ads_campaign.md
│   └── generate_organic_content.md
├── execution/             # Scripts Python
│   ├── generate_blog_articles.py
│   ├── generate_content.py
│   └── generate_google_ads_campaign.py
└── .tmp/                  # Archivos temporales (se crea automáticamente)
```

## Uso Rápido

### Workflow 1: Generar Contenido Orgánico

```bash
python3 execution/generate_content.py \
  --empresa "Nombre de tu empresa" \
  --tipo-empresa "Tipo de empresa" \
  --producto "Producto o servicio" \
  --ubicacion "Ubicación" \
  --cliente-principal "Cliente objetivo"
```

### Workflow 2: Generar Ideas de Artículos de Blog

```bash
python3 execution/generate_blog_articles.py \
  --input-file .tmp/content_output_YYYYMMDD_HHMMSS.json
```

### Workflow 3: Generar Campaña Google Ads

```bash
python3 execution/generate_google_ads_campaign.py \
  --buyer-persona-file .tmp/content_output_YYYYMMDD_HHMMSS.json \
  --blog-articles-file .tmp/blog_articles_YYYYMMDD_HHMMSS.json
```

## Solución de Problemas

### Error: "CLAUDE_API_KEY no está configurada en .env"
- Verifica que el archivo `.env` existe en la raíz del proyecto
- Verifica que contiene `CLAUDE_API_KEY=tu_api_key_real`
- Asegúrate de no tener espacios alrededor del `=`

### Error: "No module named 'anthropic'"
- Ejecuta: `pip3 install -r requirements.txt`
- Si persiste, verifica que estás usando el mismo Python que tiene pip instalado

### Error: "command not found: python3"
- Python no está instalado o no está en el PATH

**Solución rápida:**

**macOS (con Homebrew):**
```bash
brew install python3
```

**macOS (sin Homebrew):**
- Descarga desde: https://www.python.org/downloads/macos/

**Linux (Ubuntu/Debian):**
```bash
sudo apt update && sudo apt install python3 python3-pip -y
```

**Linux (Fedora/RHEL):**
```bash
sudo dnf install python3 python3-pip -y
```

### Los scripts no tienen permisos de ejecución
- Ejecuta: `chmod +x execution/*.py`
- O ejecuta directamente con: `python3 execution/nombre_script.py`

## Notas Adicionales

- El directorio `.tmp/` se crea automáticamente cuando ejecutas los scripts
- Los archivos en `.tmp/` son temporales y pueden regenerarse
- El archivo `.env` es sensible - nunca lo subas a repositorios públicos
- Si usas un entorno virtual de Python, actívalo antes de instalar dependencias

## Actualizar Dependencias

Si en el futuro se agregan nuevas dependencias, simplemente ejecuta nuevamente:

```bash
pip3 install -r requirements.txt
```

