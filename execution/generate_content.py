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
from typing import Dict, List, Any
from dotenv import load_dotenv
from anthropic import Anthropic

# Cargar variables de entorno
load_dotenv()

# Configuración
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")

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

Crea un resumen a modo de estudio del cliente, de las características de las personas que me compran y qué buscan en mi producto. Incluye al menos 10 de sus dolores, y al menos 10 beneficios que proporciona mi producto, así como los principales motivadores de compra.

Responde en formato JSON con la siguiente estructura:
{{
  "resumen": "resumen general del cliente",
  "dolores": ["dolor1", "dolor2", ...],
  "beneficios": ["beneficio1", "beneficio2", ...],
  "motivadores_compra": ["motivador1", "motivador2", ...]
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
                "dolores": [],
                "beneficios": [],
                "motivadores_compra": []
            }
        
        print("✅ Buyer persona generado exitosamente")
        return buyer_persona
        
    except Exception as e:
        print(f"❌ Error al generar buyer persona: {e}")
        raise


def generar_contenido(tipo: str, buyer_persona_texto: str, product_info: Dict[str, str]) -> List[Dict[str, str]]:
    """Genera contenido de un tipo específico usando Claude."""
    
    prompts = {
        "opinion_personal": f"""Teniendo en cuenta que mi perfil de cliente es:

{buyer_persona_texto}

Dame 10 ideas específicas de videos cortos para redes sociales dirigidos a mis clientes. La temática de estas ideas debe ser opinión personal (comentar noticia o tema polémico). Deben ser ideas muy interesantes. Deben lograr que la audiencia conecte conmigo y mi producto. Para cada idea dame el gancho que tendría al principio y una breve descripción del concepto de la idea.

Responde en formato JSON con un array de objetos, cada uno con las claves: "gancho" y "descripcion".""",

        "contraintuitivo": f"""Teniendo en cuenta que mi perfil de cliente es:

{buyer_persona_texto}

Dame 10 ideas específicas de videos cortos para redes sociales dirigidos a mis clientes. La temática de estas ideas debe ser contenido educativo con información contraintuitiva. Deben ser ideas muy interesantes. Deben lograr que la audiencia conecte conmigo y mi producto. Para cada idea dame el gancho que tendría al principio y una breve descripción del concepto de la idea.

Responde en formato JSON con un array de objetos, cada uno con las claves: "gancho" y "descripcion".""",

        "educativo_practico": f"""Teniendo en cuenta que mi perfil de cliente es:

{buyer_persona_texto}

Dame 10 ideas específicas de videos cortos para redes sociales dirigidos a mis clientes. La temática de estas ideas debe ser contenido educativo con información práctica muy útil. Deben ser ideas muy interesantes. Deben lograr que la audiencia conecte conmigo y mi producto. Para cada idea dame el gancho que tendría al principio y una breve descripción del concepto de la idea.

Responde en formato JSON con un array de objetos, cada uno con las claves: "gancho" y "descripcion".""",

        "historias_logros": f"""Teniendo en cuenta que mi perfil de cliente es:

{buyer_persona_texto}

Dame 10 ideas específicas de videos cortos para redes sociales dirigidos a mis clientes. La temática de estas ideas debe ser historias interesantes MÍAS (de quien crea el contenido - el profesional o empresa), y particularmente logros profesionales, casos exitosos que haya manejado, momentos de superación profesional, o logros significativos en mi carrera o negocio. Deben ser ideas muy interesantes que muestren mi experiencia, resultados y trayectoria. Deben lograr que la audiencia conecte conmigo y mi producto. Para cada idea dame el gancho que tendría al principio y una breve descripción del concepto de la idea.

Responde en formato JSON con un array de objetos, cada uno con las claves: "gancho" y "descripcion".""",

        "momentos_vulnerables": f"""Teniendo en cuenta que mi perfil de cliente es:

{buyer_persona_texto}

Dame 10 ideas específicas de videos cortos para redes sociales dirigidos a mis clientes. La temática de estas ideas debe ser momentos vulnerables MÍOS (de quien crea el contenido - el profesional o empresa), no de los clientes. Estos deben ser momentos personales, honestos y auténticos que muestren mi humanidad, mis dudas, mis errores, mis miedos o momentos difíciles relacionados con mi profesión, negocio o trayectoria. Deben ser ideas muy interesantes que generen conexión emocional y humanicen mi marca. Para cada idea dame el gancho que tendría al principio y una breve descripción del concepto de la idea.

Responde en formato JSON con un array de objetos, cada uno con las claves: "gancho" y "descripcion"."""
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
            contenido = [{"gancho": "Ver respuesta completa", "descripcion": respuesta_texto}]
        
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
        
        # Paso 2: Generar cada tipo de contenido
        tipos_contenido = [
            "opinion_personal",
            "contraintuitivo",
            "educativo_practico",
            "historias_logros",
            "momentos_vulnerables"
        ]
        
        contenido_resultado = {}
        for tipo in tipos_contenido:
            contenido_resultado[tipo] = generar_contenido(tipo, buyer_persona_texto, product_info)
        
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
        
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()


