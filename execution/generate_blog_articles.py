#!/usr/bin/env python3
"""
Script para generar ideas de artículos de blog con estrategia SEO.
Basado en el buyer persona generado previamente.
"""

import os
import json
import sys
import argparse
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path
from dotenv import load_dotenv
from anthropic import Anthropic
import requests

# Cargar variables de entorno
load_dotenv()

# Configuración
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
WEBHOOK_URL_BLOG_ARTICLES = os.getenv("WEBHOOK_URL_BLOG_ARTICLES")  # Opcional

if not CLAUDE_API_KEY:
    print("ERROR: CLAUDE_API_KEY no está configurada en .env")
    sys.exit(1)

# Inicializar cliente de Claude
client = Anthropic(api_key=CLAUDE_API_KEY)


def cargar_buyer_persona(file_path: str) -> Dict[str, Any]:
    """Carga y valida el archivo JSON del buyer persona."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Validar estructura
        if "buyer_persona" not in data:
            raise ValueError("El archivo no contiene 'buyer_persona'")
        
        if "product_info" not in data:
            raise ValueError("El archivo no contiene 'product_info'")
        
        buyer_persona = data["buyer_persona"]
        product_info = data["product_info"]
        
        # Validar campos requeridos
        required_bp_fields = ["resumen", "dolores", "beneficios", "motivadores_compra"]
        for field in required_bp_fields:
            if field not in buyer_persona:
                raise ValueError(f"buyer_persona no contiene '{field}'")
        
        required_pi_fields = ["empresa", "tipo_empresa", "producto", "ubicacion", "cliente_principal"]
        for field in required_pi_fields:
            if field not in product_info:
                raise ValueError(f"product_info no contiene '{field}'")
        
        return {
            "buyer_persona": buyer_persona,
            "product_info": product_info,
            "source_file": file_path
        }
        
    except FileNotFoundError:
        print(f"ERROR: El archivo '{file_path}' no existe")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: El archivo no es un JSON válido: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"ERROR: {e}")
        sys.exit(1)


def formatear_buyer_persona_texto(buyer_persona: Dict[str, Any]) -> str:
    """Formatea el buyer persona como texto para usar en prompts."""
    texto = f"Resumen del cliente: {buyer_persona.get('resumen', 'N/A')}\n\n"
    
    if buyer_persona.get('dolores'):
        texto += "Dolores/Pain Points:\n"
        for dolor in buyer_persona['dolores']:
            texto += f"- {dolor}\n"
        texto += "\n"
    
    if buyer_persona.get('beneficios'):
        texto += "Beneficios del producto/servicio:\n"
        for beneficio in buyer_persona['beneficios']:
            texto += f"- {beneficio}\n"
        texto += "\n"
    
    if buyer_persona.get('motivadores_compra'):
        texto += "Motivadores de compra:\n"
        for motivador in buyer_persona['motivadores_compra']:
            texto += f"- {motivador}\n"
    
    return texto


def generar_articulos_descubrimiento(buyer_persona_texto: str, product_info: Dict[str, str]) -> List[Dict[str, Any]]:
    """Genera 4 ideas de artículos para la etapa de Descubrimiento."""
    prompt = f"""Basándote en el perfil de buyer persona y los dolores identificados, genera 4 ideas de artículos de blog para personas que están descubriendo que tienen un problema. Estos artículos deben hablar sobre el problema, sus síntomas, consecuencias, impacto en la vida diaria, etc.

Perfil del buyer persona:
{buyer_persona_texto}

Para cada artículo proporciona:
- Título atractivo y optimizado para SEO (máximo 60 caracteres)
- Descripción del contenido del artículo (qué temas cubrirá, estructura sugerida)
- Keyword principal (relacionada con el problema/dolor específico)
- 2 keywords secundarias (también relacionadas con el problema, pero variaciones del término principal)

Las keywords deben ser términos que alguien usaría al buscar información sobre el problema, NO sobre la solución. Piensa en cómo buscaría alguien que aún no sabe que existe una solución específica.

Responde en formato JSON con un array de objetos, cada uno con las claves: "titulo", "descripcion", "keyword_principal", "keywords_secundarias" (array con exactamente 2 elementos)."""

    print("\n🔄 Generando artículos: Descubrimiento (4 ideas)...")
    
    try:
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=4096,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        respuesta_texto = message.content[0].text
        
        # Intentar parsear JSON
        try:
            inicio = respuesta_texto.find('[')
            fin = respuesta_texto.rfind(']') + 1
            if inicio != -1 and fin > inicio:
                json_str = respuesta_texto[inicio:fin]
                articulos = json.loads(json_str)
                
                # Validar estructura
                for art in articulos:
                    if not all(k in art for k in ["titulo", "descripcion", "keyword_principal", "keywords_secundarias"]):
                        raise ValueError("Estructura de artículo incompleta")
                    if not isinstance(art["keywords_secundarias"], list) or len(art["keywords_secundarias"]) != 2:
                        raise ValueError("keywords_secundarias debe ser un array con 2 elementos")
            else:
                raise ValueError("No se encontró array JSON en la respuesta")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"⚠️  Advertencia: No se pudo parsear JSON automáticamente. Error: {e}")
            articulos = []
        
        print(f"✅ Descubrimiento generado exitosamente ({len(articulos)} ideas)")
        return articulos[:4]  # Asegurar máximo 4
        
    except Exception as e:
        print(f"❌ Error al generar artículos de Descubrimiento: {e}")
        return []


def generar_articulos_consideracion(buyer_persona_texto: str, product_info: Dict[str, str]) -> List[Dict[str, Any]]:
    """Genera 3 ideas de artículos para la etapa de Consideración."""
    prompt = f"""Basándote en el perfil de buyer persona y el producto/servicio {product_info['producto']}, genera 3 ideas de artículos de blog para personas que ya conocen el problema y están considerando soluciones. Estos artículos deben hablar sobre la solución (producto/servicio), cómo funciona, beneficios, proceso, etc.

Perfil del buyer persona:
{buyer_persona_texto}

Producto/Servicio: {product_info['producto']}

Para cada artículo proporciona:
- Título atractivo y optimizado para SEO (máximo 60 caracteres)
- Descripción del contenido del artículo (qué temas cubrirá, estructura sugerida)
- Keyword principal (debe incluir el nombre del producto/servicio/procedimiento: {product_info['producto']})
- 2 keywords secundarias (también relacionadas con el producto/servicio, pueden incluir variaciones o términos relacionados)

Las keywords deben ser términos que alguien usaría al buscar información sobre el producto/servicio específico. La persona ya sabe que existe esta solución y quiere saber más sobre ella.

Responde en formato JSON con un array de objetos, cada uno con las claves: "titulo", "descripcion", "keyword_principal", "keywords_secundarias" (array con exactamente 2 elementos)."""

    print("\n🔄 Generando artículos: Consideración (3 ideas)...")
    
    try:
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=4096,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        respuesta_texto = message.content[0].text
        
        # Intentar parsear JSON
        try:
            inicio = respuesta_texto.find('[')
            fin = respuesta_texto.rfind(']') + 1
            if inicio != -1 and fin > inicio:
                json_str = respuesta_texto[inicio:fin]
                articulos = json.loads(json_str)
                
                # Validar estructura
                for art in articulos:
                    if not all(k in art for k in ["titulo", "descripcion", "keyword_principal", "keywords_secundarias"]):
                        raise ValueError("Estructura de artículo incompleta")
                    if not isinstance(art["keywords_secundarias"], list) or len(art["keywords_secundarias"]) != 2:
                        raise ValueError("keywords_secundarias debe ser un array con 2 elementos")
            else:
                raise ValueError("No se encontró array JSON en la respuesta")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"⚠️  Advertencia: No se pudo parsear JSON automáticamente. Error: {e}")
            articulos = []
        
        print(f"✅ Consideración generada exitosamente ({len(articulos)} ideas)")
        return articulos[:3]  # Asegurar máximo 3
        
    except Exception as e:
        print(f"❌ Error al generar artículos de Consideración: {e}")
        return []


def generar_articulos_decision(buyer_persona_texto: str, product_info: Dict[str, str]) -> List[Dict[str, Any]]:
    """Genera 3 ideas de artículos para la etapa de Decisión."""
    prompt = f"""Basándote en el perfil de buyer persona, el producto/servicio {product_info['producto']}, la información de la empresa {product_info['empresa']} y la ubicación {product_info['ubicacion']}, genera 3 ideas de artículos de blog para personas que están listas para decidir dónde obtener la solución. Estos artículos deben hablar sobre por qué esta empresa/profesional es la mejor opción, qué los diferencia, experiencia, casos de éxito, etc.

Perfil del buyer persona:
{buyer_persona_texto}

Empresa: {product_info['empresa']}
Tipo de empresa: {product_info['tipo_empresa']}
Ubicación: {product_info['ubicacion']}
Producto/Servicio: {product_info['producto']}

Para cada artículo proporciona:
- Título atractivo y optimizado para SEO (máximo 60 caracteres)
- Descripción del contenido del artículo (qué temas cubrirá, estructura sugerida)
- Keyword principal (debe incluir el nombre de la empresa "{product_info['empresa']}", o empresa + ubicación "{product_info['empresa']} {product_info['ubicacion']}", o términos como "mejor {product_info['tipo_empresa']} {product_info['ubicacion']}")
- 2 keywords secundarias (pueden incluir empresa + servicio, empresa + ubicación, o términos de comparación como "mejor", "recomendado", "precio", etc.)

Las keywords deben ser términos que alguien usaría al buscar específicamente la empresa o comparar opciones en la ubicación. La persona ya decidió que quiere la solución y está buscando dónde obtenerla.

Responde en formato JSON con un array de objetos, cada uno con las claves: "titulo", "descripcion", "keyword_principal", "keywords_secundarias" (array con exactamente 2 elementos)."""

    print("\n🔄 Generando artículos: Decisión (3 ideas)...")
    
    try:
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=4096,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        respuesta_texto = message.content[0].text
        
        # Intentar parsear JSON
        try:
            inicio = respuesta_texto.find('[')
            fin = respuesta_texto.rfind(']') + 1
            if inicio != -1 and fin > inicio:
                json_str = respuesta_texto[inicio:fin]
                articulos = json.loads(json_str)
                
                # Validar estructura
                for art in articulos:
                    if not all(k in art for k in ["titulo", "descripcion", "keyword_principal", "keywords_secundarias"]):
                        raise ValueError("Estructura de artículo incompleta")
                    if not isinstance(art["keywords_secundarias"], list) or len(art["keywords_secundarias"]) != 2:
                        raise ValueError("keywords_secundarias debe ser un array con 2 elementos")
            else:
                raise ValueError("No se encontró array JSON en la respuesta")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"⚠️  Advertencia: No se pudo parsear JSON automáticamente. Error: {e}")
            articulos = []
        
        print(f"✅ Decisión generada exitosamente ({len(articulos)} ideas)")
        return articulos[:3]  # Asegurar máximo 3
        
    except Exception as e:
        print(f"❌ Error al generar artículos de Decisión: {e}")
        return []


def convertir_array_a_objeto(array: List[Any], prefijo: str = "item") -> Dict[str, Any]:
    """Convierte un array en un objeto con claves numeradas para facilitar mapeo en n8n.
    
    Args:
        array: Lista a convertir
        prefijo: Prefijo para las claves (por defecto "item")
        
    Returns:
        Diccionario con claves como "item_1", "item_2", etc.
    """
    if not array:
        return {}
    return {f"{prefijo}_{i+1}": item for i, item in enumerate(array)}


def enviar_webhook(webhook_url: str, resultado: Dict[str, Any], output_file: str) -> bool:
    """Envía un webhook con los resultados del proceso de generación de artículos de blog.
    
    Args:
        webhook_url: URL del webhook a enviar
        resultado: Diccionario con los resultados del proceso
        output_file: Ruta del archivo JSON generado
        
    Returns:
        True si el webhook se envió exitosamente, False en caso contrario
    """
    try:
        articulos = resultado.get("articulos", {})
        
        # Estructurar el payload para el webhook
        payload = {
            "event": "blog_articles_generation_completed",
            "status": "success",
            "timestamp": resultado.get("timestamp"),
            "output_file": output_file,
            "workflow": "generate_blog_articles",
            "data": {
                "source_file": resultado.get("source_file"),
                "product_info": resultado.get("product_info", {}),
                "articulos": {
                    "descubrimiento": {
                        "count": len(articulos.get("descubrimiento", [])),
                        "items": convertir_array_a_objeto(articulos.get("descubrimiento", []), "articulo")
                    },
                    "consideracion": {
                        "count": len(articulos.get("consideracion", [])),
                        "items": convertir_array_a_objeto(articulos.get("consideracion", []), "articulo")
                    },
                    "decision": {
                        "count": len(articulos.get("decision", [])),
                        "items": convertir_array_a_objeto(articulos.get("decision", []), "articulo")
                    },
                    "total_count": (
                        len(articulos.get("descubrimiento", [])) +
                        len(articulos.get("consideracion", [])) +
                        len(articulos.get("decision", []))
                    )
                }
            }
        }
        
        # Enviar webhook
        response = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        response.raise_for_status()
        print(f"✅ Webhook enviado exitosamente a {webhook_url}")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Advertencia: Error al enviar webhook: {e}")
        return False
    except Exception as e:
        print(f"⚠️  Advertencia: Error inesperado al enviar webhook: {e}")
        return False


def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(
        description="Generador de Ideas de Artículos de Blog con Estrategia SEO",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--input-file",
        required=True,
        help="Ruta al archivo JSON del buyer persona generado previamente"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Generador de Ideas de Artículos de Blog con SEO")
    print("=" * 60)
    
    # Cargar buyer persona
    print(f"\n📂 Leyendo archivo: {args.input_file}")
    data = cargar_buyer_persona(args.input_file)
    
    buyer_persona = data["buyer_persona"]
    product_info = data["product_info"]
    source_file = data["source_file"]
    
    buyer_persona_texto = formatear_buyer_persona_texto(buyer_persona)
    
    print("\n" + "=" * 60)
    print("Iniciando generación de artículos...")
    print("=" * 60)
    
    try:
        # Generar artículos por etapa
        articulos_descubrimiento = generar_articulos_descubrimiento(buyer_persona_texto, product_info)
        articulos_consideracion = generar_articulos_consideracion(buyer_persona_texto, product_info)
        articulos_decision = generar_articulos_decision(buyer_persona_texto, product_info)
        
        # Consolidar resultados
        resultado = {
            "timestamp": datetime.now().isoformat(),
            "source_file": source_file,
            "product_info": product_info,
            "articulos": {
                "descubrimiento": articulos_descubrimiento,
                "consideracion": articulos_consideracion,
                "decision": articulos_decision
            }
        }
        
        # Guardar en archivo JSON
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f".tmp/blog_articles_{timestamp_str}.json"
        
        os.makedirs(".tmp", exist_ok=True)
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)
        
        print("\n" + "=" * 60)
        print("✅ Proceso completado exitosamente")
        print("=" * 60)
        print(f"\nResultados guardados en: {output_file}")
        print(f"\nResumen:")
        print(f"  - Descubrimiento: {len(articulos_descubrimiento)} artículos")
        print(f"  - Consideración: {len(articulos_consideracion)} artículos")
        print(f"  - Decisión: {len(articulos_decision)} artículos")
        print(f"  - Total: {len(articulos_descubrimiento) + len(articulos_consideracion) + len(articulos_decision)} artículos")
        
        # Enviar webhook si está configurado
        if WEBHOOK_URL_BLOG_ARTICLES:
            print(f"\n📡 Enviando webhook a {WEBHOOK_URL_BLOG_ARTICLES}...")
            enviar_webhook(WEBHOOK_URL_BLOG_ARTICLES, resultado, output_file)
        else:
            print("\nℹ️  WEBHOOK_URL_BLOG_ARTICLES no configurado en .env - omitiendo envío de webhook")
        
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

