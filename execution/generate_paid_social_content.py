#!/usr/bin/env python3
"""
Script para generar ideas de contenido para redes sociales pagas.
Basado en el buyer persona generado previamente.
Genera contenido de Descubrimiento, Consideración y Decisión.
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
from concurrent.futures import ThreadPoolExecutor, as_completed

# Cargar variables de entorno
load_dotenv()

# Configuración
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
WEBHOOK_URL_PAID_SOCIAL_CONTENT = os.getenv("WEBHOOK_URL_PAID_SOCIAL_CONTENT")  # Opcional

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
    texto = f"Resumen: {buyer_persona.get('resumen', 'N/A')}\n\n"
    
    if buyer_persona.get('dolores'):
        texto += f"Dolores:\n"
        for dolor in buyer_persona['dolores']:
            texto += f"- {dolor}\n"
        texto += "\n"
    
    if buyer_persona.get('beneficios'):
        texto += f"Beneficios del producto:\n"
        for beneficio in buyer_persona['beneficios']:
            texto += f"- {beneficio}\n"
        texto += "\n"
    
    if buyer_persona.get('motivadores_compra'):
        texto += f"Motivadores de compra:\n"
        for motivador in buyer_persona['motivadores_compra']:
            texto += f"- {motivador}\n"
    
    return texto


def generar_contenido_descubrimiento(buyer_persona_texto: str, product_info: Dict[str, str]) -> List[Dict[str, str]]:
    """Genera 10 ideas de contenido de descubrimiento para redes sociales pagas."""
    empresa = product_info.get('empresa', 'la empresa')
    
    prompt = f"""Teniendo en cuenta que mi perfil de cliente es:

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

Responde en formato JSON con un array de objetos, cada uno con las claves: "titulo", "gancho" y "concepto"."""

    print("\n🔄 Generando contenido: Descubrimiento (10 ideas)...")
    
    try:
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=4096,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        respuesta_texto = message.content[0].text
        
        try:
            inicio = respuesta_texto.find('[')
            fin = respuesta_texto.rfind(']') + 1
            if inicio != -1 and fin > inicio:
                json_str = respuesta_texto[inicio:fin]
                contenido = json.loads(json_str)
                
                # Validar estructura
                for item in contenido:
                    if not all(k in item for k in ["titulo", "gancho", "concepto"]):
                        raise ValueError("Estructura de contenido incompleta")
            else:
                raise ValueError("No se encontró array JSON en la respuesta")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"⚠️  Advertencia: No se pudo parsear JSON automáticamente. Error: {e}")
            contenido = []
        
        print(f"✅ Descubrimiento generado exitosamente ({len(contenido)} ideas)")
        return contenido[:10]  # Asegurar máximo 10
        
    except Exception as e:
        print(f"❌ Error al generar contenido de Descubrimiento: {e}")
        return []


def generar_contenido_consideracion(buyer_persona_texto: str, product_info: Dict[str, str]) -> List[Dict[str, str]]:
    """Genera 10 ideas de contenido de consideración para redes sociales pagas."""
    empresa = product_info.get('empresa', 'la empresa')
    
    prompt = f"""Teniendo en cuenta que mi perfil de cliente es:

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

Responde en formato JSON con un array de objetos, cada uno con las claves: "titulo", "gancho" y "concepto"."""

    print("\n🔄 Generando contenido: Consideración (10 ideas)...")
    
    try:
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=4096,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        respuesta_texto = message.content[0].text
        
        try:
            inicio = respuesta_texto.find('[')
            fin = respuesta_texto.rfind(']') + 1
            if inicio != -1 and fin > inicio:
                json_str = respuesta_texto[inicio:fin]
                contenido = json.loads(json_str)
                
                # Validar estructura
                for item in contenido:
                    if not all(k in item for k in ["titulo", "gancho", "concepto"]):
                        raise ValueError("Estructura de contenido incompleta")
            else:
                raise ValueError("No se encontró array JSON en la respuesta")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"⚠️  Advertencia: No se pudo parsear JSON automáticamente. Error: {e}")
            contenido = []
        
        print(f"✅ Consideración generada exitosamente ({len(contenido)} ideas)")
        return contenido[:10]  # Asegurar máximo 10
        
    except Exception as e:
        print(f"❌ Error al generar contenido de Consideración: {e}")
        return []


def generar_contenido_decision(buyer_persona_texto: str, product_info: Dict[str, str]) -> List[Dict[str, str]]:
    """Genera 10 ideas de contenido de decisión para redes sociales pagas."""
    empresa = product_info.get('empresa', 'la empresa')
    
    prompt = f"""Teniendo en cuenta que mi perfil de cliente es:

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

Responde en formato JSON con un array de objetos, cada uno con las claves: "titulo", "gancho" y "concepto"."""

    print("\n🔄 Generando contenido: Decisión (10 ideas)...")
    
    try:
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=4096,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        respuesta_texto = message.content[0].text
        
        try:
            inicio = respuesta_texto.find('[')
            fin = respuesta_texto.rfind(']') + 1
            if inicio != -1 and fin > inicio:
                json_str = respuesta_texto[inicio:fin]
                contenido = json.loads(json_str)
                
                # Validar estructura
                for item in contenido:
                    if not all(k in item for k in ["titulo", "gancho", "concepto"]):
                        raise ValueError("Estructura de contenido incompleta")
            else:
                raise ValueError("No se encontró array JSON en la respuesta")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"⚠️  Advertencia: No se pudo parsear JSON automáticamente. Error: {e}")
            contenido = []
        
        print(f"✅ Decisión generada exitosamente ({len(contenido)} ideas)")
        return contenido[:10]  # Asegurar máximo 10
        
    except Exception as e:
        print(f"❌ Error al generar contenido de Decisión: {e}")
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
    """Envía un webhook con los resultados del proceso de generación de contenido para redes sociales pagas.
    
    Args:
        webhook_url: URL del webhook a enviar
        resultado: Diccionario con los resultados del proceso
        output_file: Ruta del archivo JSON generado
        
    Returns:
        True si el webhook se envió exitosamente, False en caso contrario
    """
    try:
        contenido = resultado.get("contenido", {})
        
        # Estructurar el payload para el webhook
        payload = {
            "event": "paid_social_content_generation_completed",
            "status": "success",
            "timestamp": resultado.get("timestamp"),
            "output_file": output_file,
            "workflow": "generate_paid_social_content",
            "data": {
                "source_file": resultado.get("source_file"),
                "product_info": resultado.get("product_info", {}),
                "contenido": {
                    "descubrimiento": {
                        "count": len(contenido.get("descubrimiento", [])),
                        "items": convertir_array_a_objeto(contenido.get("descubrimiento", []), "idea")
                    },
                    "consideracion": {
                        "count": len(contenido.get("consideracion", [])),
                        "items": convertir_array_a_objeto(contenido.get("consideracion", []), "idea")
                    },
                    "decision": {
                        "count": len(contenido.get("decision", [])),
                        "items": convertir_array_a_objeto(contenido.get("decision", []), "idea")
                    },
                    "total_count": (
                        len(contenido.get("descubrimiento", [])) +
                        len(contenido.get("consideracion", [])) +
                        len(contenido.get("decision", []))
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
        description="Generador de Ideas de Contenido para Redes Sociales Pagas",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--input-file",
        required=True,
        help="Ruta al archivo JSON del buyer persona generado previamente"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Generador de Contenido para Redes Sociales Pagas")
    print("=" * 60)
    
    # Cargar buyer persona
    print(f"\n📂 Leyendo archivo: {args.input_file}")
    data = cargar_buyer_persona(args.input_file)
    
    buyer_persona = data["buyer_persona"]
    product_info = data["product_info"]
    source_file = data["source_file"]
    
    buyer_persona_texto = formatear_buyer_persona_texto(buyer_persona)
    
    print("\n" + "=" * 60)
    print("Iniciando generación de contenido...")
    print("=" * 60)
    
    try:
        # Generar contenido por etapa EN PARALELO
        print("\n🚀 Generando etapas de contenido en paralelo...")
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Enviar todas las tareas
            future_to_tipo = {
                executor.submit(generar_contenido_descubrimiento, buyer_persona_texto, product_info): "descubrimiento",
                executor.submit(generar_contenido_consideracion, buyer_persona_texto, product_info): "consideracion",
                executor.submit(generar_contenido_decision, buyer_persona_texto, product_info): "decision"
            }
            
            # Recopilar resultados conforme se completan
            contenido_resultado = {}
            for future in as_completed(future_to_tipo):
                tipo = future_to_tipo[future]
                try:
                    contenido = future.result()
                    contenido_resultado[tipo] = contenido
                except Exception as e:
                    print(f"❌ Error al generar contenido {tipo}: {e}")
                    contenido_resultado[tipo] = []
        
        print("\n✅ Todas las etapas de contenido han sido generadas")
        
        # Consolidar resultados
        resultado = {
            "timestamp": datetime.now().isoformat(),
            "source_file": source_file,
            "product_info": product_info,
            "contenido": contenido_resultado
        }
        
        # Guardar en archivo JSON
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f".tmp/paid_social_content_{timestamp_str}.json"
        
        os.makedirs(".tmp", exist_ok=True)
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)
        
        print("\n" + "=" * 60)
        print("✅ Proceso completado exitosamente")
        print("=" * 60)
        print(f"\nResultados guardados en: {output_file}")
        print(f"\nResumen:")
        print(f"  - Descubrimiento: {len(contenido_resultado.get('descubrimiento', []))} ideas")
        print(f"  - Consideración: {len(contenido_resultado.get('consideracion', []))} ideas")
        print(f"  - Decisión: {len(contenido_resultado.get('decision', []))} ideas")
        print(f"  - Total: {len(contenido_resultado.get('descubrimiento', [])) + len(contenido_resultado.get('consideracion', [])) + len(contenido_resultado.get('decision', []))} ideas")
        
        # Enviar webhook si está configurado
        if WEBHOOK_URL_PAID_SOCIAL_CONTENT:
            print(f"\n📡 Enviando webhook a {WEBHOOK_URL_PAID_SOCIAL_CONTENT}...")
            enviar_webhook(WEBHOOK_URL_PAID_SOCIAL_CONTENT, resultado, output_file)
        else:
            print("\nℹ️  WEBHOOK_URL_PAID_SOCIAL_CONTENT no configurado en .env - omitiendo envío de webhook")
        
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()



