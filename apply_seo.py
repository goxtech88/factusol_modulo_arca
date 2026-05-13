"""
Inyecta SEO + JSON-LD + meta tags optimizados en las 9 paginas v3.

Para cada pagina:
1. <title> optimizado con keywords
2. <meta name="description"> larga (150-160 chars) con keywords
3. <meta name="keywords">
4. <meta name="author"> Gonzalo Sarubilo
5. <link rel="canonical">
6. <meta property="og:*">
7. <meta name="twitter:*">
8. <script type="application/ld+json"> con schema apropiado por contexto
"""
import re
from pathlib import Path

LOGO = "https://goxtech.com.ar/arca_factusol/api/uploads/site/logo_main-1778620488.png"
BASE = "https://goxtech.com.ar"

# Schema base de Organization + Person (founder) reutilizable
PERSON_REF = {
    "@type": "Person",
    "@id": f"{BASE}/gonzalo-sarubilo/#person",
    "name": "Gonzalo Sarubilo",
    "jobTitle": "Fundador y consultor tecnológico",
    "url": f"{BASE}/gonzalo-sarubilo/",
    "email": "gonzalo@goxtech.com.ar",
    "telephone": "+5493541651038",
    "worksFor": {"@id": f"{BASE}/#organization"},
}

ORG_BASE = {
    "@type": "Organization",
    "@id": f"{BASE}/#organization",
    "name": "Goxtech",
    "legalName": "Goxtech",
    "url": BASE,
    "logo": LOGO,
    "founder": {"@id": f"{BASE}/gonzalo-sarubilo/#person"},
    "email": "gonzalo@goxtech.com.ar",
    "telephone": "+5493541651038",
    "address": {
        "@type": "PostalAddress",
        "addressLocality": "Córdoba",
        "addressRegion": "Córdoba",
        "addressCountry": "AR",
    },
    "sameAs": [],
    "areaServed": "AR",
}


def build_page_seo(page_key: str):
    """Devuelve (title, description, keywords, canonical, json_ld, breadcrumb)"""
    cfg = PAGES[page_key]
    canonical = f"{BASE}{cfg['path']}"
    breadcrumb = {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Inicio", "item": BASE + "/"},
        ] + (
            [{"@type": "ListItem", "position": 2, "name": cfg['breadcrumb']}]
            if cfg.get('breadcrumb') else []
        )
    }
    return cfg, canonical, breadcrumb


PAGES = {
    "home": {
        "path": "/",
        "title": "Goxtech — Factusol Argentina (gratis), facturación electrónica AFIP y Power BI",
        "description": "Consultoría tecnológica argentina. Implementación de Factusol gratis (Evolution), Módulo ARCA Sync para facturación electrónica AFIP, tableros Power BI y Tienda Nube. Por Gonzalo Sarubilo, profesional autorizado.",
        "keywords": "factusol argentina gratis, facturación electrónica argentina factusol gratis, módulo ARCA, Goxtech, Gonzalo Sarubilo, AFIP factusol, factusol AFIP gratis, factusol evolution argentina, consultoría tecnológica PyMEs argentina",
        "og_type": "website",
        "schema_main": {
            "@type": "WebSite",
            "@id": f"{BASE}/#website",
            "url": BASE,
            "name": "Goxtech",
            "description": "Consultoría tecnológica argentina especializada en Factusol y facturación electrónica AFIP/ARCA",
            "publisher": {"@id": f"{BASE}/#organization"},
            "inLanguage": "es-AR",
        },
        "extra_schemas": [{
            "@type": "ProfessionalService",
            "@id": f"{BASE}/#service",
            "name": "Goxtech",
            "image": LOGO,
            "url": BASE,
            "telephone": "+5493541651038",
            "email": "gonzalo@goxtech.com.ar",
            "priceRange": "$",
            "address": ORG_BASE["address"],
            "areaServed": {"@type": "Country", "name": "Argentina"},
            "founder": {"@id": f"{BASE}/gonzalo-sarubilo/#person"},
            "serviceType": ["Factusol Argentina", "Facturación electrónica AFIP", "Power BI", "Tienda Nube"],
        }],
    },
    "factusol": {
        "path": "/factusol/",
        "title": "Factusol Argentina gratis — Implementación, soporte y módulos custom | Goxtech",
        "description": "Factusol Evolution gratis adaptado a Argentina: facturación electrónica AFIP, multi-PV, multi-moneda. Implementación, migración, capacitación y soporte. +8 años con PyMEs argentinas.",
        "keywords": "factusol argentina gratis, factusol evolution argentina, factusol AFIP, factusol gratis, implementación factusol Córdoba, soporte factusol argentina, factusol facturación electrónica",
        "breadcrumb": "Factusol",
        "og_type": "website",
        "schema_main": {
            "@type": "Service",
            "@id": f"{BASE}/factusol/#service",
            "name": "Implementación de Factusol en Argentina",
            "description": "Servicio de implementación, parametrización, migración y soporte de Factusol Evolution (versión gratuita) adaptado a la operación argentina: AFIP, IVA, multi-PV, importadores, exportadores.",
            "provider": {"@id": f"{BASE}/#organization"},
            "areaServed": {"@type": "Country", "name": "Argentina"},
            "serviceType": "Implementación de ERP",
            "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "ARS",
                "description": "Factusol Evolution es gratuito. Goxtech cobra por implementación y soporte."
            }
        },
        "extra_schemas": [{
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": "¿Existe Factusol gratis en Argentina?",
                    "acceptedAnswer": {"@type": "Answer", "text": "Sí. Factusol Evolution es la versión gratuita de Sage. Tiene limitaciones de clientes y artículos pero es totalmente funcional para PyMEs chicas y medianas. Goxtech lo implementa adaptado a la operación argentina (AFIP, IVA, multi-PV) y suma el Módulo ARCA Sync gratuito para facturación electrónica."}
                },
                {
                    "@type": "Question",
                    "name": "¿Cuánto sale implementar Factusol en Argentina?",
                    "acceptedAnswer": {"@type": "Answer", "text": "La licencia de Factusol Evolution es gratis. Goxtech cobra por el servicio de implementación, parametrización inicial, migración de datos legacy, capacitación y soporte continuo. El presupuesto se ajusta a la operación: una PyME chica entre 4 y 6 semanas con valores accesibles."}
                },
                {
                    "@type": "Question",
                    "name": "¿Factusol funciona con facturación electrónica AFIP?",
                    "acceptedAnswer": {"@type": "Answer", "text": "Sí, con el Módulo ARCA Sync de Goxtech. Validás la factura desde Factusol y el CAE más QR más código de barras vuelve automáticamente al sistema en menos de 10 segundos. Sin Token Fiscal, sin doble tipeo. Soporta facturas A, B, C, M, E."}
                },
                {
                    "@type": "Question",
                    "name": "¿Cuántos puntos de venta soporta Factusol?",
                    "acceptedAnswer": {"@type": "Answer", "text": "Hasta 99 puntos de venta con numeradores independientes. El Módulo ARCA gestiona los CAE de cada PV por separado."}
                },
                {
                    "@type": "Question",
                    "name": "¿Es multi-usuario en red?",
                    "acceptedAnswer": {"@type": "Answer", "text": "Sí. La base se comparte en red (servidor o NAS) con permisos por usuario. Si la operación crece, se puede migrar la base a SQL Server."}
                },
                {
                    "@type": "Question",
                    "name": "¿Quién atiende Factusol oficialmente en Argentina?",
                    "acceptedAnswer": {"@type": "Answer", "text": "Sage Factusol opera desde España. El soporte oficial está limitado para Argentina. Goxtech, dirigida por Gonzalo Sarubilo, es implementador autorizado en Argentina con más de 8 años de experiencia. Cubre lo que el soporte oficial no cubre, las adaptaciones argentinas y los módulos custom."}
                }
            ]
        }],
    },
    "modulo-arca": {
        "path": "/modulo-arca/",
        "title": "Módulo ARCA Sync — Facturación electrónica Argentina Factusol gratis | Goxtech",
        "description": "Módulo gratuito de facturación electrónica AFIP/ARCA para Factusol. Emite facturas A/B/C/M/E con CAE en 10 segundos. Sin Token Fiscal, sin doble tipeo. RG 1361 compatible. Registrate gratis con CUIT.",
        "keywords": "factura electrónica argentina factusol gratis, módulo ARCA factusol, ARCA sync, facturación electrónica AFIP factusol, CAE factusol gratis, módulo AFIP factusol, WSFEv1 factusol, RG 1361 factusol",
        "breadcrumb": "Módulo ARCA",
        "og_type": "website",
        "schema_main": {
            "@type": "SoftwareApplication",
            "@id": f"{BASE}/modulo-arca/#software",
            "name": "Módulo ARCA Sync",
            "applicationCategory": "BusinessApplication",
            "applicationSubCategory": "Facturación electrónica",
            "operatingSystem": "Windows 10, Windows 11",
            "description": "Puente entre Factusol y AFIP/ARCA para emisión de facturación electrónica con CAE, QR y código de barras. Plan gratuito y plan mensual.",
            "softwareVersion": "1.7",
            "datePublished": "2026-04-01",
            "publisher": {"@id": f"{BASE}/#organization"},
            "creator": {"@id": f"{BASE}/gonzalo-sarubilo/#person"},
            "offers": [
                {
                    "@type": "Offer",
                    "name": "Plan gratis (registro por CUIT)",
                    "price": "0",
                    "priceCurrency": "ARS",
                    "availability": "https://schema.org/InStock",
                    "url": f"{BASE}/arca_factusol/",
                },
                {
                    "@type": "Offer",
                    "name": "Plan mensual",
                    "priceCurrency": "ARS",
                    "availability": "https://schema.org/InStock",
                    "url": f"{BASE}/arca_factusol/",
                }
            ],
            "featureList": [
                "Emisión de facturas A, B, C, M, E",
                "CAE automático en 10 segundos",
                "QR AFIP y código de barras",
                "Multi-PV (hasta 99 puntos de venta)",
                "Multi-usuario en red",
                "RG 1361 (duplicado electrónico)",
                "Sin Token Fiscal",
                "Integración nativa con Factusol",
                "Exportación CABECERA y DETALLE.txt",
            ],
        },
    },
    "power-bi": {
        "path": "/power-bi/",
        "title": "Tableros Power BI a medida en Argentina — DAX en español | Goxtech",
        "description": "Tableros Power BI conectados a Factusol, MySQL, SQL Server o Tienda Nube. Modelo semántico DAX argentino (separador ;). Ventas, Cuentas a Cobrar, Stock. Por Gonzalo Sarubilo.",
        "keywords": "power bi argentina, tableros power bi factusol, dashboards power bi a medida, DAX español argentino, Power BI Tienda Nube, consultoría Power BI Córdoba",
        "breadcrumb": "Power BI",
        "og_type": "website",
        "schema_main": {
            "@type": "Service",
            "@id": f"{BASE}/power-bi/#service",
            "name": "Implementación de tableros Power BI a medida",
            "description": "Conexión de ERPs (Factusol, MySQL, SQL Server, Tienda Nube, Gestión Nube) a Power BI con modelo semántico documentado en DAX en español argentino.",
            "provider": {"@id": f"{BASE}/#organization"},
            "areaServed": {"@type": "Country", "name": "Argentina"},
        },
    },
    "consultoria": {
        "path": "/consultoria/",
        "title": "Consultoría tecnológica para PyMEs argentinas — Goxtech",
        "description": "Servicios concretos: Tienda Nube, Gestión Nube, Meta Ads, Infraestructura Proxmox, desarrollos custom Python. Partner oficial. Por Gonzalo Sarubilo.",
        "keywords": "consultoría tecnológica argentina, Tienda Nube partner oficial, Gestión Nube, Meta Ads PyME, Proxmox argentina, Goxtech Labs",
        "breadcrumb": "Consultoría",
        "og_type": "website",
        "schema_main": {
            "@type": "Service",
            "@id": f"{BASE}/consultoria/#service",
            "name": "Consultoría tecnológica para PyMEs argentinas",
            "provider": {"@id": f"{BASE}/#organization"},
            "areaServed": {"@type": "Country", "name": "Argentina"},
        },
    },
    "industrias": {
        "path": "/industrias/",
        "title": "Industrias atendidas — Indumentaria, construcción, distribuidores | Goxtech",
        "description": "Sectores con casos reales: indumentaria con Gestión Moda, construcción con cuenta corriente compleja, distribuidores con app móvil, importadores multi-moneda, fábricas con escandallos.",
        "keywords": "factusol indumentaria, factusol construcción, factusol distribuidor, factusol importador, gestión moda argentina, ERP corralones",
        "breadcrumb": "Industrias",
        "og_type": "website",
    },
    "descargas": {
        "path": "/descargas/",
        "title": "Descargas — Módulo ARCA, Power BI y herramientas Goxtech",
        "description": "Catálogo de descargas: Módulo ARCA Sync para Factusol (gratis con CUIT), tableros Power BI base, utilidades para PyMEs argentinas.",
        "keywords": "descargar módulo ARCA, descargar factusol AFIP, Power BI dashboards descargar",
        "breadcrumb": "Descargas",
        "og_type": "website",
    },
    "contacto": {
        "path": "/contacto/",
        "title": "Contacto Goxtech — WhatsApp +54 9 3541 65-1038 | Gonzalo Sarubilo",
        "description": "Contactá a Goxtech. WhatsApp y email directo. Consultoría inicial gratuita de 30 minutos. Córdoba, Argentina. Atención remota en todo el país.",
        "keywords": "contacto Goxtech, Gonzalo Sarubilo whatsapp, consultor factusol Córdoba contacto",
        "breadcrumb": "Contacto",
        "og_type": "website",
        "schema_main": {
            "@type": "ContactPage",
            "@id": f"{BASE}/contacto/#contactpage",
            "name": "Contacto Goxtech",
            "url": f"{BASE}/contacto/",
            "mainEntity": {"@id": f"{BASE}/#organization"},
        },
    },
    "resenas": {
        "path": "/resenas/",
        "title": "Reseñas reales — Clientes activos Goxtech | Factusol, ARCA, Power BI",
        "description": "Testimonios de clientes activos de Goxtech. PyMEs argentinas que usan Factusol, Módulo ARCA Sync, Power BI y servicios de Tienda Nube. Sin filtros, cargado desde el CMS.",
        "keywords": "reseñas Goxtech, testimonios factusol argentina, clientes factusol AFIP",
        "breadcrumb": "Reseñas",
        "og_type": "website",
    },
}


def build_head_block(key: str) -> str:
    """Devuelve el bloque <head> a inyectar entre <head> y </head>."""
    cfg = PAGES[key]
    canonical = f"{BASE}{cfg['path']}"

    breadcrumb_items = [{"@type": "ListItem", "position": 1, "name": "Inicio", "item": BASE + "/"}]
    if cfg.get('breadcrumb'):
        breadcrumb_items.append({"@type": "ListItem", "position": 2, "name": cfg['breadcrumb']})

    # @graph con organization + person + main schema + breadcrumb + extras
    graph = [ORG_BASE, PERSON_REF]
    if cfg.get("schema_main"):
        graph.append(cfg["schema_main"])
    for ex in cfg.get("extra_schemas", []):
        graph.append(ex)
    graph.append({"@type": "BreadcrumbList", "itemListElement": breadcrumb_items})

    import json
    json_ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=2)

    return f"""<!-- SEO meta -->
<meta name="description" content="{cfg['description']}">
<meta name="keywords" content="{cfg['keywords']}">
<meta name="author" content="Gonzalo Sarubilo">
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
<meta name="geo.region" content="AR-X">
<meta name="geo.placename" content="Córdoba">
<link rel="canonical" href="{canonical}">

<!-- Open Graph -->
<meta property="og:type" content="{cfg.get('og_type','website')}">
<meta property="og:title" content="{cfg['title']}">
<meta property="og:description" content="{cfg['description']}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{LOGO}">
<meta property="og:image:alt" content="Goxtech — {cfg.get('breadcrumb', 'Consultoría tecnológica argentina')}">
<meta property="og:locale" content="es_AR">
<meta property="og:site_name" content="Goxtech">

<!-- Twitter -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{cfg['title']}">
<meta name="twitter:description" content="{cfg['description']}">
<meta name="twitter:image" content="{LOGO}">

<!-- Schema.org -->
<script type="application/ld+json">
{json_ld}
</script>
"""


PAGE_FILES = {
    "home": "home-v3.html",
    "factusol": "factusol-v3.html",
    "modulo-arca": "modulo-arca-v3.html",
    "power-bi": "power-bi-v3.html",
    "consultoria": "consultoria-v3.html",
    "industrias": "industrias-v3.html",
    "descargas": "descargas-v3.html",
    "contacto": "contacto-v3.html",
    "resenas": "resenas-v3.html",
}


def apply(file_path: Path, key: str):
    src = file_path.read_text(encoding="utf-8")
    cfg = PAGES[key]

    # 1. Reemplazar <title>
    new_title = cfg["title"]
    src = re.sub(r'<title>[^<]*</title>', f'<title>{new_title}</title>', src, count=1)

    # 2. Eliminar todos los meta description/keywords/author/canonical/og:/twitter:/JSON-LD anteriores
    patterns_to_remove = [
        r'<meta name="description"[^>]*>',
        r'<meta name="keywords"[^>]*>',
        r'<meta name="author"[^>]*>',
        r'<meta name="robots"[^>]*>',
        r'<meta name="geo\.[^"]+?"[^>]*>',
        r'<link rel="canonical"[^>]*>',
        r'<meta property="og:[^"]+"[^>]*>',
        r'<meta name="twitter:[^"]+"[^>]*>',
        r'<!-- SEO meta -->.*?(?=<!--|<link|<script|</head>)',
        r'<!-- Open Graph -->.*?(?=<!--|<link|<script|</head>)',
        r'<!-- Twitter -->.*?(?=<!--|<link|<script|</head>)',
        r'<!-- Schema(\.org)? -->.*?</script>',
        r'<!-- OG[^>]*-->',
    ]
    for pat in patterns_to_remove:
        src = re.sub(pat, '', src, flags=re.DOTALL)

    # Eliminar TODOS los script JSON-LD antiguos
    src = re.sub(r'<script type="application/ld\+json">.*?</script>', '', src, flags=re.DOTALL)

    # 3. Insertar el nuevo head block antes de </head>
    head_block = build_head_block(key)
    src = src.replace("</head>", head_block + "\n</head>", 1)

    # 4. Limpiar líneas vacías excesivas
    src = re.sub(r'\n\n\n+', '\n\n', src)

    file_path.write_text(src, encoding="utf-8")
    return len(src)


base = Path("web_register")
for key, fname in PAGE_FILES.items():
    p = base / fname
    if not p.exists():
        print(f"SKIP {fname}")
        continue
    size = apply(p, key)
    print(f"{fname} ({key}): {size:,} bytes")
