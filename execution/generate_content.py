#!/usr/bin/env python3
"""
Script para generar contenido orgánico para clientes.
Genera un buyer persona y 5 tipos de contenido usando Claude API.
"""

import os
import json
import sys
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from anthropic import Anthropic
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# Cargar variables de entorno
load_dotenv()

# Configuración
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
WEBHOOK_URL_ORGANIC_CONTENT = os.getenv("WEBHOOK_URL_ORGANIC_CONTENT")  # Opcional

if not CLAUDE_API_KEY:
    print("ERROR: CLAUDE_API_KEY no está configurada en .env")
    sys.exit(1)

# Inicializar cliente de Claude
client = Anthropic(api_key=CLAUDE_API_KEY)


def solicitar_input(mensaje: str, requerido: bool = True) -> str:
    """Solicita input al usuario con validación."""
    while True:
        respuesta = input(f"{mensaje}: ").strip()
        if respuesta or not requerido:
            return respuesta
        print("Este campo es requerido. Por favor, ingresa un valor.")


def generar_buyer_persona(product_info: Dict[str, str]) -> Dict[str, Any]:
    """Genera el perfil del buyer persona usando Claude."""
    prompt = f"""Soy {product_info['empresa']}, {product_info['tipo_empresa']}, y vendo {product_info['producto']}, en {product_info['ubicacion']} y mi principal cliente son {product_info['cliente_principal']}. 

Crea un resumen a modo de estudio del cliente, de las características de las personas que me compran y qué buscan en mi producto. 

IMPORTANTE: Debes incluir EXACTAMENTE 10 dolores, EXACTAMENTE 10 beneficios y EXACTAMENTE 10 motivadores de compra. No más, no menos.

Responde en formato JSON con la siguiente estructura:
{{
  "resumen": "resumen general del cliente",
  "dolores": ["dolor1", "dolor2", "dolor3", "dolor4", "dolor5", "dolor6", "dolor7", "dolor8", "dolor9", "dolor10"],
  "beneficios": ["beneficio1", "beneficio2", "beneficio3", "beneficio4", "beneficio5", "beneficio6", "beneficio7", "beneficio8", "beneficio9", "beneficio10"],
  "motivadores_compra": ["motivador1", "motivador2", "motivador3", "motivador4", "motivador5", "motivador6", "motivador7", "motivador8", "motivador9", "motivador10"]
}}
"""

    print("\n🔄 Generando perfil del buyer persona...")
    
    try:
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=4096,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        respuesta_texto = message.content[0].text
        
        # Intentar parsear JSON de la respuesta
        try:
            # Buscar JSON en la respuesta (puede venir con markdown)
            inicio = respuesta_texto.find('{')
            fin = respuesta_texto.rfind('}') + 1
            if inicio != -1 and fin > inicio:
                json_str = respuesta_texto[inicio:fin]
                buyer_persona = json.loads(json_str)
            else:
                raise ValueError("No se encontró JSON en la respuesta")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"⚠️  Advertencia: No se pudo parsear JSON automáticamente. Usando respuesta completa como resumen.")
            buyer_persona = {
                "resumen": respuesta_texto,
                "dolores": [""] * 10,
                "beneficios": [""] * 10,
                "motivadores_compra": [""] * 10
            }
        
        # Asegurar que siempre hay exactamente 10 de cada uno
        # Si la IA generó más, tomar solo los primeros 10
        # Si generó menos, rellenar con strings vacíos
        if "dolores" in buyer_persona:
            dolores = buyer_persona["dolores"]
            buyer_persona["dolores"] = (dolores[:10] + [""] * (10 - len(dolores)))[:10]
        else:
            buyer_persona["dolores"] = [""] * 10
            
        if "beneficios" in buyer_persona:
            beneficios = buyer_persona["beneficios"]
            buyer_persona["beneficios"] = (beneficios[:10] + [""] * (10 - len(beneficios)))[:10]
        else:
            buyer_persona["beneficios"] = [""] * 10
            
        if "motivadores_compra" in buyer_persona:
            motivadores = buyer_persona["motivadores_compra"]
            buyer_persona["motivadores_compra"] = (motivadores[:10] + [""] * (10 - len(motivadores)))[:10]
        else:
            buyer_persona["motivadores_compra"] = [""] * 10
        
        print("✅ Buyer persona generado exitosamente (10 dolores, 10 beneficios, 10 motivadores)")
        return buyer_persona
        
    except Exception as e:
        print(f"❌ Error al generar buyer persona: {e}")
        raise


def generar_contenido(tipo: str, buyer_persona_texto: str, product_info: Dict[str, str]) -> List[Dict[str, str]]:
    """Genera contenido de un tipo específico usando Claude."""
    
    prompts = {
        "opinion_personal": f"""Teniendo en cuenta que mi perfil de cliente es:

{buyer_persona_texto}

Dame 10 ideas específicas de videos cortos para redes sociales dirigidos a mis clientes. La temática de estas ideas debe ser opinión personal (comentar noticia o tema polémico). Deben ser ideas muy interesantes. Deben lograr que la audiencia conecte conmigo y mi producto. Para cada idea dame un título descriptivo, el gancho que tendría al principio y una breve descripción del concepto de la idea.

Responde en formato JSON con un array de objetos, cada uno con las claves: "titulo", "gancho" y "descripcion".""",

        "contraintuitivo": f"""Teniendo en cuenta que mi perfil de cliente es:

{buyer_persona_texto}

Dame 10 ideas específicas de videos cortos para redes sociales dirigidos a mis clientes. La temática de estas ideas debe ser contenido educativo con información contraintuitiva. Deben ser ideas muy interesantes. Deben lograr que la audiencia conecte conmigo y mi producto. Para cada idea dame un título descriptivo, el gancho que tendría al principio y una breve descripción del concepto de la idea.

Responde en formato JSON con un array de objetos, cada uno con las claves: "titulo", "gancho" y "descripcion".""",

        "educativo_practico": f"""Teniendo en cuenta que mi perfil de cliente es:

{buyer_persona_texto}

Dame 10 ideas específicas de videos cortos para redes sociales dirigidos a mis clientes. La temática de estas ideas debe ser contenido educativo con información práctica muy útil. Deben ser ideas muy interesantes. Deben lograr que la audiencia conecte conmigo y mi producto. Para cada idea dame un título descriptivo, el gancho que tendría al principio y una breve descripción del concepto de la idea.

Responde en formato JSON con un array de objetos, cada uno con las claves: "titulo", "gancho" y "descripcion".""",

        "historias_logros": f"""Teniendo en cuenta que mi perfil de cliente es:

{buyer_persona_texto}

Dame 10 ideas específicas de videos cortos para redes sociales dirigidos a mis clientes. La temática de estas ideas debe ser historias interesantes MÍAS (de quien crea el contenido - el profesional o empresa), y particularmente logros profesionales, casos exitosos que haya manejado, momentos de superación profesional, o logros significativos en mi carrera o negocio. Deben ser ideas muy interesantes que muestren mi experiencia, resultados y trayectoria. Deben lograr que la audiencia conecte conmigo y mi producto. Para cada idea dame un título descriptivo, el gancho que tendría al principio y una breve descripción del concepto de la idea.

Responde en formato JSON con un array de objetos, cada uno con las claves: "titulo", "gancho" y "descripcion".""",

        "momentos_vulnerables": f"""Teniendo en cuenta que mi perfil de cliente es:

{buyer_persona_texto}

Dame 10 ideas específicas de videos cortos para redes sociales dirigidos a mis clientes. La temática de estas ideas debe ser momentos vulnerables MÍOS (de quien crea el contenido - el profesional o empresa), no de los clientes. Estos deben ser momentos personales, honestos y auténticos que muestren mi humanidad, mis dudas, mis errores, mis miedos o momentos difíciles relacionados con mi profesión, negocio o trayectoria. Deben ser ideas muy interesantes que generen conexión emocional y humanicen mi marca. Para cada idea dame un título descriptivo, el gancho que tendría al principio y una breve descripción del concepto de la idea.

Responde en formato JSON con un array de objetos, cada uno con las claves: "titulo", "gancho" y "descripcion"."""
    }
    
    tipo_labels = {
        "opinion_personal": "Opinión Personal",
        "contraintuitivo": "Contraintuitivo",
        "educativo_practico": "Educativo Práctico",
        "historias_logros": "Historias y Logros",
        "momentos_vulnerables": "Momentos Vulnerables"
    }
    
    if tipo not in prompts:
        raise ValueError(f"Tipo de contenido desconocido: {tipo}")
    
    print(f"\n🔄 Generando contenido: {tipo_labels[tipo]}...")
    
    try:
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=4096,
            messages=[
                {"role": "user", "content": prompts[tipo]}
            ]
        )
        
        respuesta_texto = message.content[0].text
        
        # Intentar parsear JSON de la respuesta
        try:
            # Buscar JSON array en la respuesta
            inicio = respuesta_texto.find('[')
            fin = respuesta_texto.rfind(']') + 1
            if inicio != -1 and fin > inicio:
                json_str = respuesta_texto[inicio:fin]
                contenido = json.loads(json_str)
            else:
                raise ValueError("No se encontró array JSON en la respuesta")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"⚠️  Advertencia: No se pudo parsear JSON automáticamente para {tipo_labels[tipo]}")
            # Intentar crear estructura básica desde el texto
            contenido = [{"titulo": "Ver respuesta completa", "gancho": "Ver respuesta completa", "descripcion": respuesta_texto}]
        
        print(f"✅ {tipo_labels[tipo]} generado exitosamente ({len(contenido)} ideas)")
        return contenido
        
    except Exception as e:
        print(f"❌ Error al generar contenido {tipo_labels[tipo]}: {e}")
        # Retornar lista vacía en caso de error para no detener el proceso
        return []


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


def convertir_array_a_objeto(array: List[Any], prefijo: str = "item", limite: int = None) -> Dict[str, Any]:
    """Convierte un array en un objeto con claves numeradas para facilitar mapeo en n8n.
    
    Args:
        array: Lista a convertir
        prefijo: Prefijo para las claves (por defecto "item")
        limite: Número máximo de elementos a incluir. Si se proporciona, siempre devuelve exactamente este número de elementos
        
    Returns:
        Diccionario con claves como "item_1", "item_2", etc.
    """
    if not array:
        if limite:
            # Si hay límite pero no hay array, crear objeto con valores vacíos
            return {f"{prefijo}_{i+1}": "" for i in range(limite)}
        return {}
    
    # Limitar el array si se especifica un límite
    if limite:
        # Tomar solo los primeros 'limite' elementos y asegurar que siempre haya 'limite' elementos
        array_limitado = list(array[:limite])
        # Si hay menos elementos que el límite, rellenar con strings vacíos
        while len(array_limitado) < limite:
            array_limitado.append("")
        return {f"{prefijo}_{i+1}": item for i, item in enumerate(array_limitado)}
    
    return {f"{prefijo}_{i+1}": item for i, item in enumerate(array)}


def enviar_webhook(webhook_url: str, resultado: Dict[str, Any], output_file: str) -> bool:
    """Envía un webhook con los resultados del proceso.
    
    Args:
        webhook_url: URL del webhook a enviar
        resultado: Diccionario con los resultados del proceso
        output_file: Ruta del archivo JSON generado
        
    Returns:
        True si el webhook se envió exitosamente, False en caso contrario
    """
    try:
        buyer_persona_data = resultado.get("buyer_persona", {})
        contenido_data = resultado.get("contenido", {})
        
        # Estructurar el payload para el webhook
        payload = {
            "event": "content_generation_completed",
            "status": "success",
            "timestamp": resultado.get("timestamp"),
            "output_file": output_file,
            "workflow": "generate_organic_content",
            "data": {
                "product_info": resultado.get("product_info", {}),
                "buyer_persona": {
                    "resumen": buyer_persona_data.get("resumen", ""),
                    "dolores_count": len(buyer_persona_data.get("dolores", [])),
                    "beneficios_count": len(buyer_persona_data.get("beneficios", [])),
                    "motivadores_count": len(buyer_persona_data.get("motivadores_compra", [])),
                    "dolores": convertir_array_a_objeto(buyer_persona_data.get("dolores", []), "dolor", limite=10),
                    "beneficios": convertir_array_a_objeto(buyer_persona_data.get("beneficios", []), "beneficio", limite=10),
                    "motivadores_compra": convertir_array_a_objeto(buyer_persona_data.get("motivadores_compra", []), "motivador", limite=10)
                },
                "contenido": {
                    "tipos": {
                        "opinion_personal": {
                            "count": len(contenido_data.get("opinion_personal", [])),
                            "ideas": convertir_array_a_objeto(contenido_data.get("opinion_personal", []), "idea")
                        },
                        "contraintuitivo": {
                            "count": len(contenido_data.get("contraintuitivo", [])),
                            "ideas": convertir_array_a_objeto(contenido_data.get("contraintuitivo", []), "idea")
                        },
                        "educativo_practico": {
                            "count": len(contenido_data.get("educativo_practico", [])),
                            "ideas": convertir_array_a_objeto(contenido_data.get("educativo_practico", []), "idea")
                        },
                        "historias_logros": {
                            "count": len(contenido_data.get("historias_logros", [])),
                            "ideas": convertir_array_a_objeto(contenido_data.get("historias_logros", []), "idea")
                        },
                        "momentos_vulnerables": {
                            "count": len(contenido_data.get("momentos_vulnerables", [])),
                            "ideas": convertir_array_a_objeto(contenido_data.get("momentos_vulnerables", []), "idea")
                        }
                    },
                    "total_ideas": sum(
                        len(contenido_data.get(tipo, []))
                        for tipo in ["opinion_personal", "contraintuitivo", "educativo_practico", 
                                    "historias_logros", "momentos_vulnerables"]
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
        description="Generador de Contenido Orgánico para Clientes",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--empresa", help="Nombre de la empresa o Persona")
    parser.add_argument("--tipo-empresa", dest="tipo_empresa", help="Qué es la empresa")
    parser.add_argument("--producto", help="Qué vendes en esta campaña")
    parser.add_argument("--ubicacion", help="En dónde lo vendes")
    parser.add_argument("--cliente-principal", dest="cliente_principal", help="Principal Cliente")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Generador de Contenido Orgánico para Clientes")
    print("=" * 60)
    
    # Recopilar información del producto
    if args.empresa and args.tipo_empresa and args.producto and args.ubicacion and args.cliente_principal:
        # Usar argumentos de línea de comandos
        product_info = {
            "empresa": args.empresa,
            "tipo_empresa": args.tipo_empresa,
            "producto": args.producto,
            "ubicacion": args.ubicacion,
            "cliente_principal": args.cliente_principal
        }
        print("\nUsando datos proporcionados como argumentos.\n")
    else:
        # Modo interactivo
        print("\nPor favor, proporciona la siguiente información:\n")
        product_info = {
            "empresa": solicitar_input("Nombre de la empresa o Persona"),
            "tipo_empresa": solicitar_input("Qué es la empresa"),
            "producto": solicitar_input("Qué vendes en esta campaña"),
            "ubicacion": solicitar_input("En dónde lo vendes"),
            "cliente_principal": solicitar_input("Principal Cliente")
        }
    
    print("\n" + "=" * 60)
    print("Iniciando generación de contenido...")
    print("=" * 60)
    
    try:
        # Paso 1: Generar buyer persona
        buyer_persona = generar_buyer_persona(product_info)
        buyer_persona_texto = formatear_buyer_persona_texto(buyer_persona)
        
        # Paso 2: Generar cada tipo de contenido EN PARALELO
        tipos_contenido = [
            "opinion_personal",
            "contraintuitivo",
            "educativo_practico",
            "historias_logros",
            "momentos_vulnerables"
        ]
        
        print("\n🚀 Generando tipos de contenido en paralelo...")
        contenido_resultado = {}
        
        # Usar ThreadPoolExecutor para ejecutar en paralelo
        with ThreadPoolExecutor(max_workers=5) as executor:
            # Enviar todas las tareas
            future_to_tipo = {
                executor.submit(generar_contenido, tipo, buyer_persona_texto, product_info): tipo
                for tipo in tipos_contenido
            }
            
            # Recopilar resultados conforme se completan
            for future in as_completed(future_to_tipo):
                tipo = future_to_tipo[future]
                try:
                    contenido = future.result()
                    contenido_resultado[tipo] = contenido
                except Exception as e:
                    print(f"❌ Error al generar contenido {tipo}: {e}")
                    contenido_resultado[tipo] = []
        
        print("\n✅ Todos los tipos de contenido han sido generados")
        
        # Paso 3: Consolidar resultados
        resultado = {
            "timestamp": datetime.now().isoformat(),
            "product_info": product_info,
            "buyer_persona": buyer_persona,
            "contenido": contenido_resultado
        }
        
        # Paso 4: Guardar en archivo JSON
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f".tmp/content_output_{timestamp_str}.json"
        
        os.makedirs(".tmp", exist_ok=True)
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)
        
        print("\n" + "=" * 60)
        print("✅ Proceso completado exitosamente")
        print("=" * 60)
        print(f"\nResultados guardados en: {output_file}")
        print(f"\nResumen:")
        print(f"  - Buyer persona: ✓")
        for tipo in tipos_contenido:
            cantidad = len(contenido_resultado.get(tipo, []))
            print(f"  - {tipo}: {cantidad} ideas")
        
        # Paso 5: Enviar webhook si está configurado
        if WEBHOOK_URL_ORGANIC_CONTENT:
            print(f"\n📡 Enviando webhook a {WEBHOOK_URL_ORGANIC_CONTENT}...")
            enviar_webhook(WEBHOOK_URL_ORGANIC_CONTENT, resultado, output_file)
        else:
            print("\nℹ️  WEBHOOK_URL_ORGANIC_CONTENT no configurado en .env - omitiendo envío de webhook")
        
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()


