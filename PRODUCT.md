# PRODUCT.md — Goxtech web v3

## Quién somos
Goxtech es una consultora tecnológica argentina (Córdoba) que vende software y servicios técnicos a PyMEs. Dos productos propios (Módulo ARCA Sync, Tableros Power BI base) y cuatro líneas de servicio (Factusol, Tienda Nube + Gestión Nube, Meta Ads, Infraestructura). Partner oficial certificado de Tienda Nube, Gestión Nube y Gestión Moda.

## Audiencia objetivo
- **Dueño/a de PyME argentina** (10-200 empleados): usa Factusol o un ERP comparable, tiene problemas concretos con facturación electrónica AFIP, sincronización de stock, reportes que no le sirven para decidir.
- **Encargado de sistemas / contador interno**: técnico, evalúa proveedores por capacidad real, no por venta. Aprecia ver código revisable, snippets concretos, FAQs explícitas.
- **Decision-maker estratégico (CFO / director comercial)**: lee landing por encima, busca KPIs concretos y prueba social. Confía en lo que ve documentado.

Idioma: castellano argentino. No castellano neutro. Usar "vos" no "tú", "WhatsApp" no "WA", separador decimal coma, miles con punto, pesos en ARS, separador DAX `;`.

## Tono y voz
- **Directo, sin humo de venta.** "Software que resuelve, no que promete." Lenguaje técnico cuando aplica, coloquial cuando aporta confianza.
- **Evidencia, no promesas.** Cada claim se respalda con un snippet (DAX, `pyodbc`, código de barras AFIP), un dato concreto (10s por factura, +8 años, RG 1361) o un campo real de la DB (`BNOFAC=CAE`, `PEDFAC=nro`).
- **Argentino concreto.** Usar nombres locales (ARCA, AFIP, Tienda Nube, Mercado Pago, Factusol Evolution, CUIT, factura A/B/C/M/E).
- **Sin buzzwords.** Evitar "transformación digital", "soluciones integrales", "innovación", "disruptivo". Si un texto puede aparecer en cualquier consultora genérica, reescribirlo.

## Anti-referencias (lo que NO somos)
- ❌ Consultoras de "transformación digital" con stock photos de manos saludándose
- ❌ Landings de SaaS sin precio y sin código visible
- ❌ Páginas con "+1000 clientes felices" sin nombre, sin caso, sin testimonio verificable
- ❌ Diseño dark-tech genérico (rojo/morado/cyan, gradientes neón)
- ❌ Decisiones "depende" sin alcance ni precio
- ❌ Botones "Schedule a demo" en castellano formal — usar "Agendá una consultoría", "Hablemos por WhatsApp"

## Referencias positivas
- Linear.app — claridad jerárquica, sin decoración inútil
- Vercel.com — uso de monoespaciada para detalles técnicos
- Documentación de Stripe — combinación de texto explicativo + code blocks
- Anthropic.com — uso de eyebrows mono, jerarquía tipográfica simple

## Principios estratégicos
1. **El código es parte del producto.** Mostrar el `<script>`, el snippet `pyodbc`, la medida DAX. Es honestidad técnica y trae a la audiencia técnica.
2. **La descarga / el WhatsApp son siempre el siguiente paso.** Cada página termina en CTA WhatsApp con texto pre-llenado al contexto.
3. **Mismo menú, mismo footer, mismo CTA en todas las páginas.** Coherencia es confianza.
4. **Performance sobre belleza.** HTML self-contained, sin frameworks pesados, Lucide via CDN, fuentes Google preconectadas, paths del backend con timestamp para cache.
5. **Honesto con los límites.** Si no tenemos casos en un sector, decimos "no es nuestro fuerte" en vez de inventar. Reseñas anonimizadas si el cliente no autorizó nombre.

## Inventario actual (web pública)
- `/` Home — hero stats + 2 productos + 6 servicios + stack + proceso + industrias + reseñas
- `/factusol/` — landing del ERP español adaptado a AR
- `/modulo-arca/` — producto propio: facturación electrónica AFIP integrada a Factusol
- `/power-bi/` — tableros base + DAX argentino
- `/consultoria/` — 6 service-blocks con anchors
- `/industrias/` — 6 sectores (indumentaria, construcción, distribuidores, importadores, fábricas, inmobiliaria)
- `/descargas/` — catálogo dinámico desde `/admin/downloads`
- `/contacto/` — channel-cards + form a `/contacts` + FAQ
- `/resenas/` — grid dinámico desde `/admin/reviews`
- `/admin/` — backoffice unificado (9 secciones)

## Métricas de éxito
- Tiempo a primer WhatsApp / consulta concreta: < 30 segundos desde landing
- Conversión de "Descargar gratis" → registro CUIT: > 25%
- Conversión de licencia free → mensual: > 8% en 90 días
- Bounce rate en landings producto: < 50%
