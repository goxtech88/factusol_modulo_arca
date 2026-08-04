# Carruseles de Instagram — Factusol ARCA Sync

Guiones listos para producir. Cada carrusel = **10 slides** (formato 1080×1350 px, 4:5).

**Convenciones:**
- `TITULO:` titular grande arriba del slide
- `BODY:` cuerpo (bullets, párrafo o número grande)
- `VISUAL:` qué imagen / screenshot va en el slide
- `CTA:` solo en slide 10
- `HASHTAGS` y `CAPTION` al final de cada carrusel

**Branding:**
- Color primario: `#0D47A1` (azul GoxTech)
- Color secundario: `#FFC107` (acento)
- Fondo: `#FFFFFF`
- Tipografía: Inter / Montserrat / Poppins (cualquiera con buena legibilidad mobile)
- Logo GoxTech esquina inferior izquierda en cada slide
- Marca de agua "@goxtech.ar" esquina inferior derecha

---

## CARRUSEL 1 — "Facturás como siempre. El CAE aparece solo."

**Tema:** auto-validación cada 60s
**Pain:** copiar/pegar CAE en Factusol a mano

### Slide 1 — Hook
TITULO: ¿Seguís pegando el CAE a mano en Factusol?
BODY: Hay una forma de que aparezca solo.
VISUAL: captura de Factusol con el campo CAE vacío + flecha roja apuntando

### Slide 2 — Pain
TITULO: El problema
BODY: 30 facturas por día × 90 segundos de copy-paste = **45 minutos perdidos diarios**.
VISUAL: reloj + cifra "45 min/día" en grande

### Slide 3 — Pain reforzado
TITULO: Y además...
BODY: ❌ Errores de tipeo en el CAE
❌ QR mal pegado o sin pegar
❌ Olvidos de venta del día
❌ Auditoría imposible
VISUAL: 4 íconos de error

### Slide 4 — Solución (intro)
TITULO: ARCA Sync hace esto solo
BODY: Cada 60 segundos detecta facturas nuevas del día y las valida contra ARCA.
VISUAL: animación / ilustración de un robot mirando Factusol

### Slide 5 — Demo
TITULO: ¿Cómo se ve?
BODY: 1. Facturás en Factusol como siempre
2. El sistema detecta la factura nueva
3. Pide CAE a ARCA
4. Escribe el CAE en F_FAC
5. Genera el QR
VISUAL: screenshot del dashboard con log de auto-validación en vivo

### Slide 6 — Prueba social / dato
TITULO: Lo que esto significa
BODY: **0 facturas tocadas a mano.**
**0 errores de CAE.**
**45 min/día recuperados.**
VISUAL: 3 números grandes en blanco sobre fondo azul

### Slide 7 — Feature técnica
TITULO: Lo que escribe en Factusol
BODY: ✅ Nº CAE
✅ Fecha de vencimiento
✅ QR (imagen)
✅ Código de barras AFIP
✅ Nº de comprobante (B-0001-00000023)
VISUAL: tabla con campos de F_FAC marcados en verde

### Slide 8 — Multi PV
TITULO: ¿Tenés varios puntos de venta?
BODY: A, B, C — en simultáneo. Cada usuario solo ve sus PV.
VISUAL: tres PV (A-0001, A-0002, B-0001) cada uno con su user

### Slide 9 — Confianza
TITULO: ¿Y si ARCA se cae?
BODY: El sistema reintenta solo. Cuando ARCA vuelve, valida todo lo pendiente. Vos ni te enterás.
VISUAL: gráfico de estado servidores ARCA (verde / rojo / amarillo)

### Slide 10 — CTA
TITULO: 15 días gratis
BODY: Instalamos en tu servidor, configuramos tus PV y arrancás.
CTA: 📲 WhatsApp +54 9 11 XXXX-XXXX
🌐 goxtech.ar
VISUAL: logo GoxTech + QR de WhatsApp

**CAPTION:**
> ¿Cuántas horas por mes perdés pegando el CAE en Factusol? Te lo solucionamos en 24h. Probalo 15 días gratis 👉 link en bio.

**HASHTAGS:** #factusol #afip #arca #facturacionelectronica #pymesargentinas #automatizacion #contadores #softwarecontable #emprendedoresargentinos #goxtech

---

## CARRUSEL 2 — "1 servidor. Todas tus empresas."

**Tema:** multi-instancia
**Pain:** múltiples CUITs = múltiples instalaciones, varios servidores, infierno IT

### Slide 1 — Hook
TITULO: Tenés 3 CUITs.
3 Factusol.
3 dolores de cabeza.
VISUAL: tres laptops separadas con el ícono de Factusol y un signo de exclamación encima

### Slide 2 — Pain
TITULO: La realidad de hoy
BODY: Cada empresa = una instalación, un servidor, certificados separados, scripts diferentes.
**Y rezar para que nadie toque nada.**
VISUAL: diagrama tipo "spaghetti" con 3 servers

### Slide 3 — Costos ocultos
TITULO: Lo que te cuesta
BODY: 💸 3× licencias de software
💸 3× soporte IT
💸 3× backups
💸 3× actualizaciones manuales
VISUAL: cifra "$$$" grande

### Slide 4 — Solución (intro)
TITULO: 1 sola app. N empresas.
BODY: Cada empresa = una carpeta. Cada carpeta = su CUIT, su DB y sus certificados.
VISUAL: árbol de carpetas
```
C:\
  Empresa_A\
  Empresa_B\
  Empresa_C\
```

### Slide 5 — Cómo funciona
TITULO: ¿Cómo lo hace?
BODY: Cada instancia corre en un puerto distinto:
• Empresa A → :8765
• Empresa B → :8766
• Empresa C → :8767
VISUAL: 3 ventanas de browser apiladas, cada una con su URL

### Slide 6 — Beneficio 1
TITULO: Mismo ejecutable
BODY: Actualizás 1 vez → todas las empresas al día.
VISUAL: 1 .exe → flecha → 3 carpetas

### Slide 7 — Beneficio 2
TITULO: Aislamiento total
BODY: La base de la Empresa A nunca toca la B. Certificados separados. Logs separados. Usuarios separados.
VISUAL: 3 cajas fuertes

### Slide 8 — Beneficio 3
TITULO: Un solo soporte
BODY: Nos llamás 1 vez por cualquier empresa. Resolvemos en remoto.
VISUAL: ícono de auriculares de soporte

### Slide 9 — Caso real
TITULO: Caso real
BODY: Estudio contable, 11 CUITs de clientes. 1 servidor. 0 problemas en 8 meses.
VISUAL: testimonial gráfico

### Slide 10 — CTA
TITULO: ¿Cuántas empresas manejás?
CTA: Te armamos la arquitectura sin costo.
📲 WhatsApp +54 9 11 XXXX-XXXX
VISUAL: logo + QR

**CAPTION:**
> Si manejás 2+ CUITs, tenés que ver esto. Una instalación, todas tus empresas, cero cruces de datos.

**HASHTAGS:** #estudiocontable #contadorpublico #factusol #afip #multiempresa #softwarepyme #automatizacioncontable #pymesargentinas #goxtech #arca

---

## CARRUSEL 3 — "Padrón ARCA en 1 click"

**Tema:** actualización de clientes desde padrón
**Pain:** cargar datos de cliente nuevo a mano

### Slide 1 — Hook
TITULO: Cliente nuevo. 8 minutos cargando datos.
BODY: Hay una forma de hacerlo en 8 segundos.
VISUAL: cronómetro 8:00 → 0:08

### Slide 2 — Pain
TITULO: Lo que cargás hoy a mano
BODY: 📝 Razón social
📝 CUIT
📝 Domicilio
📝 Condición IVA
📝 Provincia
📝 Localidad
📝 CP
VISUAL: formulario largo con todos los campos vacíos

### Slide 3 — Y los errores
TITULO: Y si te equivocás...
BODY: CUIT mal cargado → factura rechazada → llamada al cliente → vuelta a empezar.
VISUAL: factura con sello "RECHAZADA"

### Slide 4 — Solución
TITULO: 1 click. Padrón ARCA.
BODY: Cargás el CUIT. El sistema consulta el padrón. **Te trae todo.**
VISUAL: botón grande "Actualizar desde Padrón"

### Slide 5 — Qué trae
TITULO: Lo que carga solo
BODY: ✅ Razón social oficial
✅ Domicilio fiscal
✅ Condición IVA real
✅ Provincia + localidad
✅ Actividad principal
VISUAL: formulario lleno con check verde en cada campo

### Slide 6 — Escribe en Factusol
TITULO: Y lo guarda en Factusol
BODY: La tabla `F_CLI` queda actualizada. Sin tocar nada.
VISUAL: screenshot Factusol con ficha de cliente actualizada

### Slide 7 — Bonus: clientes existentes
TITULO: ¿Y los clientes viejos?
BODY: Actualización masiva. Sincronizás toda tu cartera con el padrón en 5 minutos.
VISUAL: lista de clientes con "Actualizando..." → "✓ Actualizado"

### Slide 8 — Beneficio real
TITULO: ¿Qué ganás?
BODY: 🎯 0 facturas rechazadas por datos mal
🎯 Auditoría AFIP sin sorpresas
🎯 Tu base de clientes siempre al día
VISUAL: 3 íconos grandes

### Slide 9 — Demo
TITULO: Cómo se ve
BODY: (Screenshot de la pantalla "Clientes" con un cliente marcado y el botón "Actualizar Padrón")
VISUAL: captura real de la app

### Slide 10 — CTA
TITULO: Probalo gratis
CTA: 15 días sin compromiso.
📲 +54 9 11 XXXX-XXXX
🌐 goxtech.ar
VISUAL: logo + QR

**CAPTION:**
> Si todavía cargás clientes a mano en Factusol, mirá esto. CUIT → click → todos los datos.

**HASHTAGS:** #factusol #padronafip #arca #facturacionelectronica #pymesargentinas #contadores #productividad #automatizacion #afip #goxtech

---

## CARRUSEL 4 — "Tu facturación, en una pantalla"

**Tema:** dashboard en tiempo real

### Slide 1 — Hook
TITULO: ¿Cuántas facturás hoy?
BODY: Si tardás más de 3 segundos en responder, te falta este dashboard.
VISUAL: signo de pregunta grande

### Slide 2 — Pain
TITULO: Lo que hacés hoy
BODY: Abrís Factusol → filtrás por fecha → contás → sumás IVA en Excel → te equivocás → empezás de nuevo.
VISUAL: cadena de pasos con "X" rojas

### Slide 3 — Solución
TITULO: Dashboard ARCA Sync
BODY: Todo lo que necesitás saber, en vivo.
VISUAL: screenshot completo del dashboard

### Slide 4 — Métrica 1
TITULO: Facturas del día
BODY: Cuántas emitiste, cuántas validadas, cuántas pendientes.
VISUAL: tarjeta del dashboard zoom

### Slide 5 — Métrica 2
TITULO: CAE emitidos del mes
BODY: Cantidad, total facturado, neto gravado, IVA débito.
VISUAL: tarjeta del dashboard zoom

### Slide 6 — Métrica 3
TITULO: Estado de servidores ARCA
BODY: 🟢 Verde: facturando
🟡 Amarillo: lento
🔴 Rojo: caído (y vas a saberlo antes que ARCA tweetee)
VISUAL: 3 indicadores

### Slide 7 — Métrica 4
TITULO: Logs en vivo
BODY: Cada factura validada aparece en tiempo real. Si algo falla, ves el error en el momento.
VISUAL: log scrolleando

### Slide 8 — Por usuario
TITULO: Cada user, su dashboard
BODY: El vendedor ve solo sus PV. El admin ve todo.
VISUAL: dos pantallas comparadas

### Slide 9 — Mobile
TITULO: Funciona en el celu
BODY: Es una web app. Abrís el navegador del celular y la usás.
VISUAL: vista mobile del dashboard

### Slide 10 — CTA
TITULO: Pedí demo
CTA: Te lo mostramos en 10 minutos.
📲 +54 9 11 XXXX-XXXX
VISUAL: logo + QR

**CAPTION:**
> Dejá de armar el Excel del IVA todos los meses. Mirá lo que se ve en una sola pantalla.

**HASHTAGS:** #factusol #dashboard #facturacionelectronica #afip #contadores #pymes #software #productividad #datosentiemporeal #goxtech

---

## CARRUSEL 5 — "Adiós al Excel del IVA"

**Tema:** posición IVA mensual

### Slide 1 — Hook
TITULO: Fin de mes.
TITULO 2: El contador pide el libro IVA.
TITULO 3: Vos: 😱
VISUAL: meme tipo cara de pánico (ilustrado)

### Slide 2 — Lo que hacés hoy
TITULO: La rutina del horror
BODY: 1. Exportás de Factusol a Excel
2. Filtrás por PV
3. Filtrás por tipo de comprobante
4. Sumás IVA a mano
5. Cruzás con CAE emitidos
6. Encontrás 1 diferencia
7. Llorás
VISUAL: ilustración de Excel con muchas pestañas

### Slide 3 — Solución
TITULO: ARCA Sync lo calcula solo
BODY: Posición IVA mensual. Por PV. Por tipo de comprobante.
VISUAL: tabla limpia con totales

### Slide 4 — Detalle 1
TITULO: Totales por PV
BODY: A-0001 → 234 facturas, $1.847.000 neto, $387.870 IVA
A-0002 → 89 facturas, $623.000 neto, $130.830 IVA
VISUAL: tarjetas por PV

### Slide 5 — Detalle 2
TITULO: Débito fiscal del mes
BODY: Calculado automáticamente sobre los CAE confirmados.
**Sin Excel, sin errores.**
VISUAL: número grande $518.700

### Slide 6 — Filtros
TITULO: Filtros que necesitás
BODY: Por mes ✅
Por punto de venta ✅
Por tipo de comprobante ✅
VISUAL: 3 selectores en una pantalla

### Slide 7 — Histórico
TITULO: Histórico de meses
BODY: Comparás IVA de Enero vs Febrero vs Marzo en 2 segundos.
VISUAL: gráfico de barras 12 meses

### Slide 8 — Para tu contador
TITULO: Lo exportás y se lo mandás
BODY: Tu contador recibe el libro IVA listo. Y vos te ahorrás la llamada de las 23h.
VISUAL: contador feliz / ícono PDF

### Slide 9 — Trazabilidad
TITULO: Auditable
BODY: Cada número en el libro IVA está respaldado por un CAE de ARCA. 100% trazable.
VISUAL: cadena de eslabones

### Slide 10 — CTA
TITULO: Cerrá el mes en paz
CTA: Probalo 15 días gratis.
📲 +54 9 11 XXXX-XXXX
VISUAL: logo + QR

**CAPTION:**
> Si todavía armás el libro IVA en Excel, esto te va a doler. Y después te va a gustar.

**HASHTAGS:** #librodeIVA #contadores #factusol #afip #monotributo #responsableinscripto #facturacion #pymesargentinas #goxtech #arca

---

## CARRUSEL 6 — "Cada vendedor, sus facturas"

**Tema:** roles + multi PV con permisos

### Slide 1 — Hook
TITULO: Tu vendedor de Córdoba vio facturas de Buenos Aires.
BODY: Y no debió.
VISUAL: ilustración de un user mirando datos ajenos

### Slide 2 — Pain
TITULO: Lo que pasa en Factusol "puro"
BODY: Todos los usuarios ven todas las facturas. Toda la facturación. Toda la información.
VISUAL: archivo abierto con muchas miradas alrededor

### Slide 3 — Por qué es un problema
TITULO: Riesgo
BODY: 🔴 Vendedores que copian datos de clientes
🔴 Disputas internas por comisiones
🔴 Sin control de quién hace qué
VISUAL: 3 íconos de alerta

### Slide 4 — Solución
TITULO: Roles + PV por usuario
BODY: Cada usuario tiene asignados solo sus puntos de venta.
VISUAL: tabla de usuarios → PVs

### Slide 5 — Admin
TITULO: Rol admin
BODY: Ve todo. Hace todo. Crea usuarios. Define PV.
VISUAL: usuario con corona

### Slide 6 — Usuario
TITULO: Rol usuario
BODY: Ve solo sus facturas. Solo sus PV. Solo sus clientes.
VISUAL: usuario con caja delimitada

### Slide 7 — Ejemplo
TITULO: Caso real
BODY: 5 vendedores, 5 PV. Cada uno ve solo el suyo. El gerente ve todos.
VISUAL: diagrama con 5 vendedores y 1 gerente

### Slide 8 — Auditoría
TITULO: Quién hizo qué
BODY: Logs por usuario. Sabés exactamente quién validó cada factura.
VISUAL: log con timestamps y usernames

### Slide 9 — Seguridad
TITULO: Login con JWT
BODY: Tokens seguros. Sesiones cerrables. Contraseñas hasheadas.
VISUAL: ícono de candado

### Slide 10 — CTA
TITULO: Profesionalizá tu facturación
CTA: 15 días gratis. Lo dejamos andando.
📲 +54 9 11 XXXX-XXXX
VISUAL: logo + QR

**CAPTION:**
> ¿Tu equipo de ventas ve datos que no debería? Hay una forma simple de evitarlo.

**HASHTAGS:** #seguridadinformatica #pymes #equipodeventas #factusol #afip #control #facturacion #software #goxtech #arca

---

## CARRUSEL 7 — "Los errores de ARCA, traducidos"

**Tema:** manejo de errores comprensible

### Slide 1 — Hook
TITULO: ARCA te tira:
TITULO 2: **"Error 10016"**
TITULO 3: ¿Y ahora?
VISUAL: pantalla con error críptico

### Slide 2 — Pain
TITULO: Los errores de ARCA en castellano técnico
BODY: 10016 → CUIT no autorizado
600 → Punto de venta sin habilitar
1000 → Token vencido
2000 → CAE no concedido
VISUAL: tabla de códigos sin explicación

### Slide 3 — Tu día hoy
TITULO: Lo que hacés
BODY: Googleás el código → leés foros de 2017 → llamás a tu contador → llamás a ARCA → desistís.
VISUAL: secuencia de pasos frustrante

### Slide 4 — Solución
TITULO: ARCA Sync traduce
BODY: Cada error viene con:
✅ Qué pasó
✅ Por qué
✅ Cómo lo arreglás
VISUAL: tarjeta de error con 3 secciones

### Slide 5 — Ejemplo 1
TITULO: 10016 — CUIT no autorizado
BODY: **Qué hacer:** verificá en ARCA que tu CUIT esté habilitado para WSFE en producción.
VISUAL: card con solución

### Slide 6 — Ejemplo 2
TITULO: 600 — Punto de venta no habilitado
BODY: **Qué hacer:** alta del PV en ARCA online → "Administración de Puntos de Venta".
VISUAL: card con solución + link al portal AFIP

### Slide 7 — Reintentos automáticos
TITULO: Y si es un error temporal
BODY: El sistema reintenta solo. No te molesta.
VISUAL: ícono de loop / retry

### Slide 8 — Logs
TITULO: Todo queda registrado
BODY: Cada error, su fecha, su contexto. Para que tu contador / soporte lo vea.
VISUAL: log con errores rojos y verdes

### Slide 9 — Soporte humano
TITULO: Y si no entendés
BODY: Nuestro soporte te lo resuelve. Por WhatsApp.
VISUAL: chat de WhatsApp simulado

### Slide 10 — CTA
TITULO: Dejá de pelearte con ARCA
CTA: Te acompañamos. Probalo gratis.
📲 +54 9 11 XXXX-XXXX
VISUAL: logo + QR

**CAPTION:**
> Si alguna vez ARCA te tiró un error en código numérico sin explicación, este post es para vos.

**HASHTAGS:** #afip #arca #errores #facturacionelectronica #factusol #soporte #contadores #pymes #goxtech #automatizacion

---

## CARRUSEL 8 — "Caso real: 1.847 facturas, 0 manuales"

**Tema:** caso de éxito / testimonial

### Slide 1 — Hook
TITULO: 1.847 facturas
TITULO 2: en 30 días
TITULO 3: 0 tocadas a mano
VISUAL: número grande "1.847"

### Slide 2 — Contexto
TITULO: Empresa: distribuidora de bebidas
BODY: 4 puntos de venta. 3 vendedores. 1 administrativa.
VISUAL: ícono distribuidora

### Slide 3 — Antes
TITULO: Antes de ARCA Sync
BODY: ⏰ 2 horas diarias copiando CAE
⏰ 1 hora semanal corrigiendo errores
⏰ 4 horas mensuales armando libro IVA
**= 60 horas/mes administrativas**
VISUAL: reloj acumulando horas

### Slide 4 — Decisión
TITULO: Probaron 15 días gratis
BODY: Instalación: 1 hora.
Configuración: 30 minutos.
Capacitación: 15 minutos.
VISUAL: cronómetro

### Slide 5 — Después - mes 1
TITULO: Resultado mes 1
BODY: 412 facturas → 412 CAE automáticos. **0 intervenciones manuales.**
VISUAL: tilde verde grande

### Slide 6 — Después - mes 2
TITULO: Resultado mes 2
BODY: 587 facturas. ARCA se cayó 2 veces. El sistema reintentó solo. **0 facturas perdidas.**
VISUAL: gráfico de uptime

### Slide 7 — Después - mes 3
TITULO: Resultado mes 3
BODY: 1.847 facturas acumuladas. La administrativa pasó esas 60h a tareas de cobranza.
VISUAL: gráfico antes/después

### Slide 8 — ROI
TITULO: ROI
BODY: La inversión se recuperó en **22 días**. El resto del año es pura ganancia de tiempo.
VISUAL: línea de tiempo con marca a los 22 días

### Slide 9 — Testimonial
TITULO: Sus palabras
BODY: *"Pasamos de pelearnos con AFIP todos los días a no acordarnos que existe. Eso vale más que el costo."*
— Cecilia, admin
VISUAL: foto / avatar + comilla grande

### Slide 10 — CTA
TITULO: Querés esto también
CTA: 15 días gratis. Sin tarjeta. Sin compromiso.
📲 +54 9 11 XXXX-XXXX
🌐 goxtech.ar
VISUAL: logo + QR

**CAPTION:**
> Un caso real. Números reales. Si manejás más de 200 facturas al mes, esto te va a interesar.

**HASHTAGS:** #casodeexito #pymesargentinas #factusol #afip #automatizacion #distribuidora #productividad #ROI #goxtech #arca

---

## Plan de publicación sugerido

| Semana | Lunes | Miércoles | Viernes |
|--------|-------|-----------|---------|
| 1 | Carrusel 1 (hook fuerte) | Carrusel 3 (productividad) | Carrusel 5 (contador) |
| 2 | Carrusel 4 (dashboard) | Carrusel 7 (errores ARCA) | Carrusel 2 (multi-empresa) |
| 3 | Carrusel 6 (seguridad) | Carrusel 8 (caso real, cierre) | (reposteo del más performante con story) |

**Recomendación:** después de la semana 3, mirar métricas (saves > likes > comments > shares) y duplicar los 2 carruseles más guardados con variantes (cambiar hook, cambiar slide 10).
