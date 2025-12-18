#!/usr/bin/env python3
"""
Script para generar una campaña completa de Google Ads.
Organiza keywords por intención de búsqueda y genera anuncios y extensiones.
"""

import os
import json
import sys
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
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


def cargar_json(file_path: str) -> Optional[Dict[str, Any]]:
    """Carga un archivo JSON si existe."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as e:
        print(f"⚠️  Advertencia: Error al leer {file_path}: {e}")
        return None


def extraer_informacion(buyer_persona_file: Optional[str], blog_articles_file: Optional[str]) -> Dict[str, Any]:
    """Extrae y consolida información de los archivos proporcionados."""
    product_info = None
    buyer_persona = None
    articulos = None
    
    # Intentar cargar buyer persona
    if buyer_persona_file:
        data = cargar_json(buyer_persona_file)
        if data:
            product_info = data.get("product_info")
            buyer_persona = data.get("buyer_persona")
    
    # Intentar cargar artículos de blog
    if blog_articles_file:
        data = cargar_json(blog_articles_file)
        if data:
            # Si no tenemos product_info, tomarlo de aquí
            if not product_info:
                product_info = data.get("product_info")
            articulos = data.get("articulos")
    
    # Validar que tenemos al menos product_info mínimo
    if not product_info:
        raise ValueError("No se pudo extraer product_info de ningún archivo. Proporciona al menos uno de los archivos.")
    
    return {
        "product_info": product_info,
        "buyer_persona": buyer_persona,
        "articulos": articulos
    }


def formatear_buyer_persona_texto(buyer_persona: Optional[Dict[str, Any]]) -> str:
    """Formatea el buyer persona como texto para prompts."""
    if not buyer_persona:
        return "No disponible"
    
    texto = f"Resumen del cliente: {buyer_persona.get('resumen', 'N/A')}\n\n"
    
    if buyer_persona.get('dolores'):
        texto += "Dolores:\n"
        for dolor in buyer_persona['dolores'][:5]:  # Limitar para no exceder tokens
            texto += f"- {dolor}\n"
        texto += "\n"
    
    if buyer_persona.get('beneficios'):
        texto += "Beneficios:\n"
        for beneficio in buyer_persona['beneficios'][:5]:
            texto += f"- {beneficio}\n"
    
    return texto


def extraer_keywords_de_articulos(articulos: Optional[Dict[str, Any]], etapa: str) -> List[str]:
    """Extrae keywords de artículos de una etapa específica."""
    keywords = []
    if not articulos or etapa not in articulos:
        return keywords
    
    for articulo in articulos[etapa]:
        if "keyword_principal" in articulo:
            keywords.append(articulo["keyword_principal"])
        if "keywords_secundarias" in articulo:
            keywords.extend(articulo["keywords_secundarias"])
    
    return keywords


def generar_keywords_informativas(product_info: Dict[str, str], buyer_persona_texto: str, keywords_articulos: List[str]) -> List[Dict[str, str]]:
    """Genera keywords de intención informativa."""
    keywords_texto = "\n".join(f"- {kw}" for kw in keywords_articulos[:10]) if keywords_articulos else "Ninguna disponible"
    
    prompt = f"""Basándote en la información del negocio y las keywords de artículos de blog, genera 15-20 keywords de intención INFORMATIVA para Google Ads. Estas keywords son para personas que buscan información sobre el problema o la solución, no están listas para comprar aún.

Empresa: {product_info.get('empresa', 'N/A')}
Producto/Servicio: {product_info.get('producto', 'N/A')}
Ubicación: {product_info.get('ubicacion', 'N/A')}

Keywords de artículos de Descubrimiento:
{keywords_texto}

Perfil del buyer persona:
{buyer_persona_texto}

Las keywords deben ser:
- Términos informativos: "qué es", "cómo funciona", "síntomas de", "problemas de", "por qué"
- Relacionadas con los dolores/problemas del buyer persona
- No comerciales (no incluir "precio", "costo", "comprar")
- Variaciones naturales que usaría alguien buscando información

Para cada keyword, sugiere el match type más apropiado (PHRASE o BROAD_MODIFIER).

Responde en formato JSON con un array de objetos, cada uno con las claves: "keyword" y "match_type"."""

    print("\n🔄 Generando keywords: Intención Informativa...")
    
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
                keywords = json.loads(json_str)
                print(f"✅ Keywords informativas generadas ({len(keywords)} keywords)")
                return keywords[:20]  # Limitar a 20
            else:
                raise ValueError("No se encontró array JSON")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"⚠️  Advertencia: Error al parsear keywords informativas: {e}")
            return []
    except Exception as e:
        print(f"❌ Error al generar keywords informativas: {e}")
        return []


def generar_keywords_transaccionales(product_info: Dict[str, str], buyer_persona_texto: str, keywords_articulos: List[str]) -> List[Dict[str, str]]:
    """Genera keywords de intención transaccional."""
    keywords_texto = "\n".join(f"- {kw}" for kw in keywords_articulos[:10]) if keywords_articulos else "Ninguna disponible"
    
    prompt = f"""Basándote en la información del negocio y las keywords de artículos de blog, genera 15-20 keywords de intención TRANSACCIONAL para Google Ads. Estas keywords son para personas que están listas para comprar o contratar el servicio.

Empresa: {product_info.get('empresa', 'N/A')}
Producto/Servicio: {product_info.get('producto', 'N/A')}
Ubicación: {product_info.get('ubicacion', 'N/A')}

Keywords de artículos de Consideración y Decisión:
{keywords_texto}

Las keywords deben ser:
- Términos comerciales: "precio de", "costo de", "dónde hacer", "mejor lugar para", "cuánto cuesta"
- Incluir el nombre del producto/servicio
- Incluir ubicación cuando sea relevante
- Mostrar intención de compra o contratación

Para cada keyword, sugiere el match type más apropiado (EXACT o PHRASE).

Responde en formato JSON con un array de objetos, cada uno con las claves: "keyword" y "match_type"."""

    print("\n🔄 Generando keywords: Intención Transaccional...")
    
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
                keywords = json.loads(json_str)
                print(f"✅ Keywords transaccionales generadas ({len(keywords)} keywords)")
                return keywords[:20]
            else:
                raise ValueError("No se encontró array JSON")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"⚠️  Advertencia: Error al parsear keywords transaccionales: {e}")
            return []
    except Exception as e:
        print(f"❌ Error al generar keywords transaccionales: {e}")
        return []


def generar_keywords_navegacionales(product_info: Dict[str, str]) -> List[Dict[str, str]]:
    """Genera keywords de intención navegacional (marca)."""
    empresa = product_info.get('empresa', '')
    ubicacion = product_info.get('ubicacion', '')
    producto = product_info.get('producto', '')
    
    prompt = f"""Genera 10-15 keywords de intención NAVEGACIONAL para Google Ads. Estas keywords son para personas que buscan específicamente la marca o empresa.

Empresa: {empresa}
Ubicación: {ubicacion}
Producto/Servicio: {producto}

Las keywords deben incluir:
- Nombre de la empresa: "{empresa}"
- Empresa + ubicación: "{empresa} {ubicacion}"
- Empresa + producto: "{empresa} {producto}"
- Variaciones del nombre de la empresa
- Búsquedas de marca específica

Para cada keyword, sugiere el match type más apropiado (EXACT o PHRASE).

Responde en formato JSON con un array de objetos, cada uno con las claves: "keyword" y "match_type"."""

    print("\n🔄 Generando keywords: Intención Navegacional...")
    
    try:
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=2048,
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
                keywords = json.loads(json_str)
                print(f"✅ Keywords navegacionales generadas ({len(keywords)} keywords)")
                return keywords[:15]
            else:
                raise ValueError("No se encontró array JSON")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"⚠️  Advertencia: Error al parsear keywords navegacionales: {e}")
            return []
    except Exception as e:
        print(f"❌ Error al generar keywords navegacionales: {e}")
        return []


def generar_anuncios_grupo(product_info: Dict[str, str], buyer_persona_texto: str, keywords: List[Dict[str, str]], tipo_intencion: str) -> List[Dict[str, Any]]:
    """Genera anuncios para un grupo de keywords específico."""
    keywords_ejemplo = ", ".join([kw["keyword"] for kw in keywords[:5]])
    
    prompt = f"""Basándote en la información del negocio, genera 3-5 variaciones de anuncios Responsive Search Ads para Google Ads.

Empresa: {product_info.get('empresa', 'N/A')}
Producto/Servicio: {product_info.get('producto', 'N/A')}
Ubicación: {product_info.get('ubicacion', 'N/A')}
Tipo de intención: {tipo_intencion}

Keywords del grupo (ejemplos):
{keywords_ejemplo}

Perfil del buyer persona:
{buyer_persona_texto}

Para cada anuncio, proporciona:
- Headlines: 5-8 variaciones (máximo 30 caracteres cada una)
  * Deben incluir keywords relevantes
  * Deben incluir beneficios principales
  * Deben incluir call-to-action
- Descriptions: 3-4 variaciones (máximo 90 caracteres cada una)
  * Deben expandir beneficios
  * Deben incluir diferenciadores
  * Deben incluir call-to-action
- Final URL sugerida (puede ser placeholder si no hay URL real)
- Path1 y Path2 sugeridos para tracking

Responde en formato JSON con un array de objetos, cada uno con las claves: "headlines" (array), "descriptions" (array), "final_url" (string), "path1" (string), "path2" (string)."""

    print(f"  🔄 Generando anuncios para grupo {tipo_intencion}...")
    
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
                anuncios = json.loads(json_str)
                print(f"  ✅ {len(anuncios)} anuncios generados")
                return anuncios[:5]
            else:
                raise ValueError("No se encontró array JSON")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"  ⚠️  Advertencia: Error al parsear anuncios: {e}")
            return []
    except Exception as e:
        print(f"  ❌ Error al generar anuncios: {e}")
        return []


def generar_extensiones(product_info: Dict[str, str], buyer_persona: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Genera extensiones de anuncios."""
    beneficios = buyer_persona.get('beneficios', []) if buyer_persona else []
    beneficios_texto = "\n".join(f"- {b}" for b in beneficios[:5]) if beneficios else "No disponibles"
    
    prompt = f"""Basándote en la información del negocio, genera extensiones de anuncios para Google Ads.

Empresa: {product_info.get('empresa', 'N/A')}
Producto/Servicio: {product_info.get('producto', 'N/A')}
Ubicación: {product_info.get('ubicacion', 'N/A')}
Tipo de empresa: {product_info.get('tipo_empresa', 'N/A')}

Beneficios clave:
{beneficios_texto}

Genera:

1. Sitelinks (4-6):
   - Enlaces a páginas importantes (servicios, sobre nosotros, contacto, blog, etc.)
   - Título descriptivo (máximo 25 caracteres)
   - Descripción corta opcional (máximo 35 caracteres)
   - URL sugerida

2. Callouts (4-6):
   - Beneficios clave o diferenciadores
   - Máximo 25 caracteres cada uno

3. Structured Snippets:
   - Organizados por categorías estándar (Tipos de servicio, Características, etc.)
   - Lista de valores para cada categoría

Responde en formato JSON con un objeto que tenga las claves: "sitelinks" (array), "callouts" (array), "structured_snippets" (objeto con headers y values)."""

    print("\n🔄 Generando extensiones de anuncios...")
    
    try:
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=2048,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        respuesta_texto = message.content[0].text
        
        try:
            inicio = respuesta_texto.find('{')
            fin = respuesta_texto.rfind('}') + 1
            if inicio != -1 and fin > inicio:
                json_str = respuesta_texto[inicio:fin]
                extensiones = json.loads(json_str)
                print("✅ Extensiones generadas")
                return extensiones
            else:
                raise ValueError("No se encontró objeto JSON")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"⚠️  Advertencia: Error al parsear extensiones: {e}")
            return {"sitelinks": [], "callouts": [], "structured_snippets": {}}
    except Exception as e:
        print(f"❌ Error al generar extensiones: {e}")
        return {"sitelinks": [], "callouts": [], "structured_snippets": {}}


def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(
        description="Generador de Campaña Google Ads Completa",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--buyer-persona-file",
        help="Ruta al archivo JSON del buyer persona (opcional)"
    )
    parser.add_argument(
        "--blog-articles-file",
        help="Ruta al archivo JSON de artículos de blog (opcional)"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Generador de Campaña Google Ads Completa")
    print("=" * 60)
    
    # Extraer información
    try:
        data = extraer_informacion(args.buyer_persona_file, args.blog_articles_file)
        product_info = data["product_info"]
        buyer_persona = data["buyer_persona"]
        articulos = data["articulos"]
        
        print(f"\n📊 Información extraída:")
        print(f"  - Empresa: {product_info.get('empresa', 'N/A')}")
        print(f"  - Producto: {product_info.get('producto', 'N/A')}")
        print(f"  - Ubicación: {product_info.get('ubicacion', 'N/A')}")
        print(f"  - Buyer persona: {'✓' if buyer_persona else '✗'}")
        print(f"  - Artículos: {'✓' if articulos else '✗'}")
        
    except Exception as e:
        print(f"❌ Error al extraer información: {e}")
        sys.exit(1)
    
    buyer_persona_texto = formatear_buyer_persona_texto(buyer_persona)
    
    print("\n" + "=" * 60)
    print("Iniciando generación de campaña...")
    print("=" * 60)
    
    try:
        # Extraer keywords de artículos
        keywords_descubrimiento = extraer_keywords_de_articulos(articulos, "descubrimiento")
        keywords_consideracion = extraer_keywords_de_articulos(articulos, "consideracion")
        keywords_decision = extraer_keywords_de_articulos(articulos, "decision")
        keywords_articulos_info = keywords_descubrimiento
        keywords_articulos_trans = keywords_consideracion + keywords_decision
        
        # Generar keywords por intención
        keywords_info = generar_keywords_informativas(product_info, buyer_persona_texto, keywords_articulos_info)
        keywords_trans = generar_keywords_transaccionales(product_info, buyer_persona_texto, keywords_articulos_trans)
        keywords_nav = generar_keywords_navegacionales(product_info)
        
        # Organizar en grupos de anuncios
        ad_groups = []
        
        if keywords_info:
            anuncios_info = generar_anuncios_grupo(product_info, buyer_persona_texto, keywords_info, "Informativo")
            ad_groups.append({
                "name": f"Intención Informativa - {product_info.get('producto', 'Producto')}",
                "keywords": keywords_info,
                "ads": anuncios_info
            })
        
        if keywords_trans:
            anuncios_trans = generar_anuncios_grupo(product_info, buyer_persona_texto, keywords_trans, "Transaccional")
            ad_groups.append({
                "name": f"Intención Transaccional - {product_info.get('producto', 'Producto')}",
                "keywords": keywords_trans,
                "ads": anuncios_trans
            })
        
        if keywords_nav:
            anuncios_nav = generar_anuncios_grupo(product_info, buyer_persona_texto, keywords_nav, "Navegacional")
            ad_groups.append({
                "name": f"Intención Navegacional - {product_info.get('empresa', 'Marca')}",
                "keywords": keywords_nav,
                "ads": anuncios_nav
            })
        
        # Generar extensiones
        extensiones = generar_extensiones(product_info, buyer_persona)
        
        # Estructurar campaña
        ubicacion = product_info.get('ubicacion', '')
        producto = product_info.get('producto', 'Producto')
        campaign_name = f"Campaña {producto} {ubicacion}"
        
        resultado = {
            "timestamp": datetime.now().isoformat(),
            "source_files": {
                "buyer_persona": args.buyer_persona_file or None,
                "blog_articles": args.blog_articles_file or None
            },
            "product_info": product_info,
            "campaign": {
                "name": campaign_name,
                "type": "SEARCH",
                "settings": {
                    "locations": [ubicacion] if ubicacion else [],
                    "languages": ["es"],
                    "budget_suggestion": "Ajustar según mercado y objetivos",
                    "bid_strategy": "CPC manual (recomendado inicialmente)"
                },
                "ad_groups": ad_groups,
                "extensions": extensiones
            }
        }
        
        # Guardar en archivo JSON
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f".tmp/google_ads_campaign_{timestamp_str}.json"
        
        os.makedirs(".tmp", exist_ok=True)
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)
        
        print("\n" + "=" * 60)
        print("✅ Proceso completado exitosamente")
        print("=" * 60)
        print(f"\nResultados guardados en: {output_file}")
        print(f"\nResumen de la campaña:")
        print(f"  - Nombre: {campaign_name}")
        print(f"  - Grupos de anuncios: {len(ad_groups)}")
        total_keywords = sum(len(ag["keywords"]) for ag in ad_groups)
        total_ads = sum(len(ag["ads"]) for ag in ad_groups)
        print(f"  - Total keywords: {total_keywords}")
        print(f"  - Total anuncios: {total_ads}")
        print(f"  - Extensiones: ✓")
        
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

