# Base de Datos Factusol - Esquema Completo

Documentación completa de la estructura de la base de datos de Factusol.
Extraído de: `0022026.accdb` (Access Database)
Total de tablas: **170**

## Índice de Tablas

- [F_1KB](#f_1kb) (19 campos)
- [F_ACL](#f_acl) (8 campos)
- [F_ACT](#f_act) (2 campos)
- [F_AGE](#f_age) (52 campos)
- [F_ALB](#f_alb) (125 campos)
- [F_ALM](#f_alm) (11 campos)
- [F_ANP](#f_anp) (7 campos)
- [F_ANT](#f_ant) (12 campos)
- [F_ARC](#f_arc) (3 campos)
- [F_ART](#f_art) (81 campos)
- [F_BAN](#f_ban) (43 campos)
- [F_BLQ](#f_blq) (5 campos)
- [F_BUS](#f_bus) (9 campos)
- [F_CAF](#f_caf) (5 campos)
- [F_CAJ](#f_caj) (3 campos)
- [F_CAP](#f_cap) (54 campos)
- [F_CCC](#f_ccc) (11 campos)
- [F_CE1](#f_ce1) (4 campos)
- [F_CE2](#f_ce2) (4 campos)
- [F_CEG](#f_ceg) (4 campos)
- [F_CFG](#f_cfg) (4 campos)
- [F_CGA](#f_cga) (2 campos)
- [F_CHE](#f_che) (8 campos)
- [F_CHEIMG](#f_cheimg) (2 campos)
- [F_CHEIMG_OLD](#f_cheimg_old) (2 campos)
- [F_CHEMIO](#f_chemio) (5 campos)
- [F_CIN](#f_cin) (8 campos)
- [F_CLI](#f_cli) (201 campos)
- [F_CNP](#f_cnp) (8 campos)
- [F_CNS](#f_cns) (4 campos)
- [F_COB](#f_cob) (7 campos)
- [F_COM](#f_com) (8 campos)
- [F_DES](#f_des) (8 campos)
- [F_DVL](#f_dvl) (4 campos)
- [F_DVO](#f_dvo) (2 campos)
- [F_EAC](#f_eac) (4 campos)
- [F_EAN](#f_ean) (2 campos)
- [F_EMP](#f_emp) (50 campos)
- [F_ENS](#f_ens) (42 campos)
- [F_ENT](#f_ent) (94 campos)
- [F_ESI](#f_esi) (71 campos)
- [F_FAB](#f_fab) (117 campos)
- [F_FAC](#f_fac) (145 campos)
- [F_FAM](#f_fam) (11 campos)
- [F_FCO](#f_fco) (4 campos)
- [F_FMO](#f_fmo) (3 campos)
- [F_FPA](#f_fpa) (28 campos)
- [F_FRD](#f_frd) (95 campos)
- [F_FRE](#f_fre) (105 campos)
- [F_FTE](#f_fte) (12 campos)
- [F_GAG](#f_gag) (6 campos)
- [F_HOJ](#f_hoj) (6 campos)
- [F_HOR](#f_hor) (2 campos)
- [F_ING](#f_ing) (9 campos)
- [F_L34](#f_l34) (32 campos)
- [F_LAC](#f_lac) (16 campos)
- [F_LAG](#f_lag) (7 campos)
- [F_LAL](#f_lal) (30 campos)
- [F_LAN](#f_lan) (7 campos)
- [F_LCA](#f_lca) (11 campos)
- [F_LCH](#f_lch) (4 campos)
- [F_LCO](#f_lco) (18 campos)
- [F_LCR](#f_lcr) (14 campos)
- [F_LEN](#f_len) (22 campos)
- [F_LFA](#f_lfa) (29 campos)
- [F_LFB](#f_lfb) (28 campos)
- [F_LFC](#f_lfc) (8 campos)
- [F_LFD](#f_lfd) (22 campos)
- [F_LFL](#f_lfl) (8 campos)
- [F_LFM](#f_lfm) (8 campos)
- [F_LFR](#f_lfr) (22 campos)
- [F_LHO](#f_lho) (10 campos)
- [F_LMA](#f_lma) (11 campos)
- [F_LPA](#f_lpa) (8 campos)
- [F_LPC](#f_lpc) (29 campos)
- [F_LPD](#f_lpd) (12 campos)
- [F_LPF](#f_lpf) (14 campos)
- [F_LPG](#f_lpg) (4 campos)
- [F_LPH](#f_lph) (3 campos)
- [F_LPP](#f_lpp) (20 campos)
- [F_LPS](#f_lps) (23 campos)
- [F_LRD](#f_lrd) (8 campos)
- [F_LRE](#f_lre) (2 campos)
- [F_LRL](#f_lrl) (13 campos)
- [F_LRM](#f_lrm) (36 campos)
- [F_LRU](#f_lru) (4 campos)
- [F_LSA](#f_lsa) (7 campos)
- [F_LTA](#f_lta) (4 campos)
- [F_LTC](#f_ltc) (6 campos)
- [F_LTH](#f_lth) (8 campos)
- [F_LTR](#f_ltr) (8 campos)
- [F_MAS](#f_mas) (7 campos)
- [F_MAT](#f_mat) (6 campos)
- [F_MCK](#f_mck) (4 campos)
- [F_MEN](#f_men) (12 campos)
- [F_MVI](#f_mvi) (7 campos)
- [F_OBR](#f_obr) (46 campos)
- [F_ODE](#f_ode) (7 campos)
- [F_ODT](#f_odt) (3 campos)
- [F_OOB](#f_oob) (5 campos)
- [F_OPR](#f_opr) (5 campos)
- [F_ORD](#f_ord) (17 campos)
- [F_ORE](#f_ore) (7 campos)
- [F_PAG](#f_pag) (11 campos)
- [F_PCL](#f_pcl) (99 campos)
- [F_PDA](#f_pda) (54 campos)
- [F_PER](#f_per) (46 campos)
- [F_PPR](#f_ppr) (95 campos)
- [F_PRC](#f_prc) (5 campos)
- [F_PRE](#f_pre) (103 campos)
- [F_PRO](#f_pro) (96 campos)
- [F_Q34](#f_q34) (7 campos)
- [F_RDJ](#f_rdj) (3 campos)
- [F_RDO](#f_rdo) (11 campos)
- [F_REC](#f_rec) (24 campos)
- [F_REM](#f_rem) (9 campos)
- [F_REP](#f_rep) (12 campos)
- [F_RES](#f_res) (10 campos)
- [F_RET](#f_ret) (9 campos)
- [F_RIE](#f_rie) (7 campos)
- [F_RUT](#f_rut) (3 campos)
- [F_SAL](#f_sal) (3 campos)
- [F_SEC](#f_sec) (5 campos)
- [F_SFC](#f_sfc) (6 campos)
- [F_SFD](#f_sfd) (5 campos)
- [F_SFL](#f_sfl) (7 campos)
- [F_SLA](#f_sla) (7 campos)
- [F_SLB](#f_slb) (7 campos)
- [F_SLC](#f_slc) (5 campos)
- [F_SLD](#f_sld) (7 campos)
- [F_SLE](#f_sle) (7 campos)
- [F_SLF](#f_slf) (7 campos)
- [F_SLI](#f_sli) (6 campos)
- [F_SLP](#f_slp) (5 campos)
- [F_SLR](#f_slr) (7 campos)
- [F_SLT](#f_slt) (7 campos)
- [F_SLV](#f_slv) (5 campos)
- [F_SMS](#f_sms) (13 campos)
- [F_STC](#f_stc) (8 campos)
- [F_STM](#f_stm) (26 campos)
- [F_STO](#f_sto) (7 campos)
- [F_TAR](#f_tar) (4 campos)
- [F_TCA](#f_tca) (1 campos)
- [F_TCD](#f_tcd) (6 campos)
- [F_TCH](#f_tch) (10 campos)
- [F_TCL](#f_tcl) (2 campos)
- [F_TRA](#f_tra) (4 campos)
- [F_TRB](#f_trb) (6 campos)
- [F_TRN](#f_trn) (15 campos)
- [F_TRZ](#f_trz) (4 campos)
- [F_UME](#f_ume) (2 campos)
- [F_VAL](#f_val) (8 campos)
- [F_VER](#f_ver) (6 campos)
- [R_LPA](#r_lpa) (15 campos)
- [R_LPR](#r_lpr) (2 campos)
- [R_MAR](#r_mar) (2 campos)
- [R_PAR](#r_par) (46 campos)
- [R_TIN](#r_tin) (5 campos)
- [T_ATE](#t_ate) (41 campos)
- [T_CPU](#t_cpu) (6 campos)
- [T_DEP](#t_dep) (8 campos)
- [T_DOC](#t_doc) (7 campos)
- [T_LTE](#t_lte) (12 campos)
- [T_PER](#t_per) (3 campos)
- [T_TER](#t_ter) (15 campos)
- [T_TFI](#t_tfi) (5 campos)
- [T_TPV](#t_tpv) (81 campos)
- [T_TTF](#t_ttf) (20 campos)
- [T_TUR](#t_tur) (4 campos)
- [f_ant_lan](#f_ant_lan) (19 campos)

---

## F_1KB

**Registros:** 1

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `COD1KB` | Entero | 2 | ✓ | Código |
| `THU1KB` | Entero | 2 |  | Tipo de huella (0 = Empresa, 1 = Personal) |
| `CAM1KB` | Texto corto | 255 |  | Campos incluidos en la huella |
| `NIM1KB` | Entero | 2 |  | Nombre a imprimir (0 = Fiscal, 1 = Comercial) |
| `TIM1KB` | Entero | 2 |  | Tamaño de impresión (fijo o máximo) |
| `ANC1KB` | Moneda | 8 |  | Ancho de la huella |
| `ALT1KB` | Moneda | 8 |  | Alto de la huella |
| `TPU1KB` | Moneda | 8 |  | Tamaño del punto |
| `ALI1KB` | Entero | 2 |  | Alineación |
| `POX1KB` | Moneda | 8 |  | Posición X |
| `POY1KB` | Moneda | 8 |  | Posición Y |
| `SEG1KB` | Entero | 2 |  | Seguridad |
| `RVE1KB` | Entero | 2 |  | Ratio vertical |
| `NCE1KB` | Entero | 2 |  | Nivel de corrección de errores |
| `ROT1KB` | Entero | 2 |  | Rotación |
| `CPI1KB` | Entero largo | 4 |  | Color del pincel |
| `FTR1KB` | Entero | 2 |  | Fondo transparente |
| `CFO1KB` | Entero largo | 4 |  | Color del fondo |
| `RES1KB` | Entero | 2 |  | Resolución |

---

## F_ACL

**Registros:** 19

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODACL` | Entero largo | 4 | ✓ | Código |
| `CLIACL` | Entero largo | 4 |  | [F=hh:mm]Hora |
| `OPEACL` | Entero largo | 4 |  | [F=00000]Agente |
| `CAMACL` | Entero | 2 |  | [E]Campaña |
| `ESTACL` | Entero largo | 4 |  | [L=#0;Pendiente#1;En curso#2;Finalizada]Estado |
| `ACOACL` | Entero largo | 4 |  | Tipo de acción |
| `SEGACL` | Texto largo |  |  | Consulta |
| `PCOACL` | Texto corto | 50 |  | [F=hh:mm]Hora del fin de la acción |

---

## F_ACT

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODACT` | Texto corto | 4 | ✓ |  |
| `DESACT` | Texto corto | 50 |  | Descripción |

---

## F_AGE

**Registros:** 24

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODAGE` | Entero largo | 4 | ✓ | Código de agente |
| `TEMAGE` | Texto corto | 18 |  | Movil |
| `ZONAGE` | Texto corto | 40 |  | Zona |
| `IMPAGE` | Moneda | 8 |  | Comisión |
| `TCOAGE` | Texto corto | 1 |  | Tipo de contrato (0:Externo, 1:Plantilla) |
| `IVAAGE` | Entero | 2 |  | IVA |
| `IRPAGE` | Entero | 2 |  | Fecha de alta |
| `FAXAGE` | Texto corto | 25 |  | Fax |
| `EMAAGE` | Texto corto | 60 |  | E-Mail |
| `WEBAGE` | Texto corto | 60 |  | Web |
| `PAIAGE` | Texto corto | 50 |  | País |
| `PCOAGE` | Texto corto | 50 |  | Persona de contacto |
| `TEPAGE` | Texto corto | 30 |  | Teléfono particular |
| `CLAAGE` | Texto corto | 10 |  |  |
| `DNIAGE` | Texto corto | 18 |  | D.N.I. |
| `RUTAGE` | Texto corto | 3 |  | Ruta |
| `CUWAGE` | Texto corto | 50 |  | [E]Código de usuario Web |
| `CAWAGE` | Texto corto | 15 |  | [E]Clave de usuario Web |
| `SUWAGE` | Entero | 2 |  | [E][L=#;No#1;Sí]Dar acceso a internet |
| `MEWAGE` | Texto corto | 255 |  | [E]Mensaje emergente Web |
| `CPOAGE` | Texto corto | 10 |  | Cód. Postal |
| `PROAGE` | Texto corto | 40 |  | Provincia |
| `ENTAGE` | Texto corto | 4 |  |  |
| `OFIAGE` | Texto corto | 4 |  |  |
| `DCOAGE` | Texto corto | 2 |  |  |
| `CUEAGE` | Texto corto | 10 |  |  |
| `BANAGE` | Texto corto | 50 |  |  |
| `LISAGE` | Entero | 2 |  |  |
| `CONAGE` | Entero | 2 |  |  |
| `DOMAGE` | Texto corto | 100 |  | Domicilio |
| `NOMAGE` | Texto corto | 100 |  | Nombre |
| `NOCAGE` | Texto corto | 100 |  |  |
| `MEMAGE` | Texto corto | 100 |  |  |
| `OBSAGE` | Texto largo |  |  | Observaciones |
| `FORAGE` | Entero | 2 |  |  |
| `LFOAGE` | Texto corto | 50 |  |  |
| `OFOAGE` | Texto largo |  |  |  |
| `UREAGE` | Entero | 2 |  |  |
| `CURAGE` | Entero largo | 4 |  |  |
| `URLAGE` | Texto corto | 60 |  |  |
| `CATAGE` | Entero | 2 |  |  |
| `PUNAGE` | Moneda | 8 |  |  |
| `CVEAGE` | Moneda | 8 |  |  |
| `CREAGE` | Moneda | 8 |  |  |
| `PURAGE` | Moneda | 8 |  |  |
| `JEQAGE` | Entero | 2 |  | [L=#0;No#1;Sí]Jefe de equipo |
| `CSAAGE` | Moneda | 8 |  | Comisión sobre los demás agentes comerciales |
| `AGJAGE` | Entero largo | 4 |  | Código del agente que su jefe de equipo |
| `DMWAGE` | Entero | 2 |  |  |
| `FOTAGE` | Texto corto | 255 |  | [E]Fotografía |
| `POBAGE` | Texto corto | 30 |  | Población |
| `CTPAGE` | Texto corto | 255 |  | [E]Contraseña TpvSOL |

---

## F_ALB

**Registros:** 1604

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `TIPALB` | Texto corto | 1 | ✓ | Nº de serie |
| `CODALB` | Entero largo | 4 | ✓ | [F=000000]Código |
| `REFALB` | Texto corto | 50 |  | Fecha |
| `ESTALB` | Entero | 2 |  | [L=#0;Pte.#1;Facturado]Estado |
| `ALMALB` | Texto corto | 3 |  | Almacén |
| `AGEALB` | Entero largo | 4 |  | [F=00000]Agente |
| `PROALB` | Texto corto | 10 |  | Proveedor del cliente |
| `CLIALB` | Entero largo | 4 |  | [F=00000]Cliente |
| `CNOALB` | Texto corto | 100 |  | Nombre |
| `CDOALB` | Texto corto | 100 |  | Domicilio |
| `CPOALB` | Texto corto | 30 |  | Población |
| `CCPALB` | Texto corto | 10 |  | Cód. Postal |
| `CPRALB` | Texto corto | 40 |  | Provincia |
| `CNIALB` | Texto corto | 18 |  | N.I.F. |
| `TIVALB` | Entero | 2 |  | [L=#0;Con IVA#1;Sin IVA#2;Intracomunitario#3;Importación]Tipo de IVA |
| `REQALB` | Entero largo | 4 |  | [L=#0;No#1;Sí]Recargo de equivalencia |
| `TELALB` | Texto corto | 20 |  | Teléfono |
| `NET1ALB` | Moneda | 8 |  | Neto 1 |
| `NET2ALB` | Moneda | 8 |  | Neto 2 |
| `NET3ALB` | Moneda | 8 |  | Neto 3 |
| `PDTO1ALB` | Moneda | 8 |  | Porcentaje de descuento 1 |
| `PDTO2ALB` | Moneda | 8 |  | Porcentaje de descuento 2 |
| `PDTO3ALB` | Moneda | 8 |  | Porcentaje de descuento 3 |
| `IDTO1ALB` | Moneda | 8 |  | Importe de descuento 1 |
| `IDTO2ALB` | Moneda | 8 |  | Importe de descuento 2 |
| `IDTO3ALB` | Moneda | 8 |  | Importe de descuento 3 |
| `PPPA1ALB` | Moneda | 8 |  | Porcentaje de pronto pago 1 |
| `PPPA2ALB` | Moneda | 8 |  | Porcentaje de pronto pago 2 |
| `PPPA3ALB` | Moneda | 8 |  | Porcentaje de pronto pago 3 |
| `IPPA1ALB` | Moneda | 8 |  | Importe de pronto pago 1 |
| `IPPA2ALB` | Moneda | 8 |  | Importe de pronto pago 2 |
| `IPPA3ALB` | Moneda | 8 |  | Importe de pronto pago 3 |
| `PPOR1ALB` | Moneda | 8 |  | Porcentaje de portes 1 |
| `PPOR2ALB` | Moneda | 8 |  | Porcentaje de portes 2 |
| `PPOR3ALB` | Moneda | 8 |  | Porcentaje de portes 3 |
| `IPOR1ALB` | Moneda | 8 |  | Importe de portes 1 |
| `IPOR2ALB` | Moneda | 8 |  | Importe de portes 2 |
| `IPOR3ALB` | Moneda | 8 |  | Importe de portes 3 |
| `PFIN1ALB` | Moneda | 8 |  | Porcentaje de financiación 1 |
| `PFIN2ALB` | Moneda | 8 |  | Porcentaje de financiación 2 |
| `PFIN3ALB` | Moneda | 8 |  | Porcentaje de financiación 3 |
| `IFIN1ALB` | Moneda | 8 |  | Importe de financiación 1 |
| `IFIN2ALB` | Moneda | 8 |  | Importe de financiación 2 |
| `IFIN3ALB` | Moneda | 8 |  | Importe de financiación 3 |
| `BAS1ALB` | Moneda | 8 |  | Base imponible 1 |
| `BAS2ALB` | Moneda | 8 |  | Base imponible 2 |
| `BAS3ALB` | Moneda | 8 |  | Base imponible 3 |
| `PIVA1ALB` | Moneda | 8 |  | Porcentaje de impuestos 1 |
| `PIVA2ALB` | Moneda | 8 |  | Porcentaje de impuestos 2 |
| `PIVA3ALB` | Moneda | 8 |  | Porcentaje de impuestos 3 |
| `IIVA1ALB` | Moneda | 8 |  | Importe de impuestos 1 |
| `IIVA2ALB` | Moneda | 8 |  | Importe de impuestos 2 |
| `IIVA3ALB` | Moneda | 8 |  | Importe de impuestos 3 |
| `PREC1ALB` | Moneda | 8 |  | Porcentaje de recargo de equivalencia 1 |
| `PREC2ALB` | Moneda | 8 |  | Porcentaje de recargo de equivalencia 2 |
| `PREC3ALB` | Moneda | 8 |  | Porcentaje de recargo de equivalencia 3 |
| `IREC1ALB` | Moneda | 8 |  | Importe de recargo de equivalencia 1 |
| `IREC2ALB` | Moneda | 8 |  | Importe de recargo de equivalencia 2 |
| `IREC3ALB` | Moneda | 8 |  | Importe de recargo de equivalencia 3 |
| `PRET1ALB` | Moneda | 8 |  | Porcentaje de retención |
| `IRET1ALB` | Moneda | 8 |  | Importe de retención |
| `TOTALB` | Moneda | 8 |  | Total |
| `FOPALB` | Texto corto | 3 |  | Forma de pago |
| `PRTALB` | Entero | 2 |  | [L=#Pagados#1;Debidos]Portes |
| `TPOALB` | Texto corto | 30 |  | Portes (texto) |
| `OB1ALB` | Texto corto | 100 |  | Línea 1 de observaciones |
| `OB2ALB` | Texto corto | 100 |  | Línea 2 de observaciones |
| `OBRALB` | Entero | 2 |  | Código de la dirección de entrega |
| `REPALB` | Texto corto | 50 |  | Remitido por |
| `EMBALB` | Texto corto | 50 |  | Embalado por |
| `AATALB` | Texto corto | 50 |  | A la atención de |
| `REAALB` | Texto corto | 50 |  | Referencia |
| `PEDALB` | Texto corto | 30 |  | Fecha de su pedido |
| `COBALB` | Entero | 2 |  | [L=#0;Pte.#1;Cobrado#2;Cob. Parcial]Estado (cobros) |
| `TRAALB` | Entero largo | 4 |  | [L=#No traspasado#1;Traspasado]Traspasado a contabilidad |
| `IMPALB` | Texto corto | 1 |  | [E]Impresa |
| `TRNALB` | Entero | 2 |  | Transportista |
| `CISALB` | Texto corto | 20 |  | Nº de expedición 1 |
| `TRCALB` | Texto corto | 20 |  | Nº de expedición 2 |
| `PRIALB` | Texto largo |  |  | [E]Campo para anotaciones privadas del documento |
| `ASOALB` | Texto corto | 255 |  | [E]Documentos asociados al documento |
| `CBAALB` | Entero | 2 |  | Banco del cliente |
| `ENVALB` | Entero | 2 |  | [F=hh:mm]Hora |
| `COMALB` | Texto largo |  |  | [E]Comentarios después de las líneas de detalle |
| `USUALB` | Entero | 2 |  | Código del usuario que creó el documento |
| `USMALB` | Entero | 2 |  | Código del último usuario que modificó el documento |
| `FAXALB` | Texto corto | 25 |  | Fax |
| `EFEALB` | Moneda | 8 |  | [E]EFECTIVO COBRADO DEL DOCUMENTO (PARA TPV) |
| `CAMALB` | Moneda | 8 |  | [E]CAMBIO DEL DOCUMENTO (PARA TPV) |
| `NET4ALB` | Moneda | 8 |  | Neto (Exento de impuestos) |
| `PDTO4ALB` | Moneda | 8 |  | Porcentaje de descuento (Exento de impuestos) |
| `IDTO4ALB` | Moneda | 8 |  | Importe de descuento (Exento de impuestos) |
| `PPPA4ALB` | Moneda | 8 |  | Porcentaje de pronto pago (Exento de impuestos) |
| `IPPA4ALB` | Moneda | 8 |  | Importe de pronto pago (Exento de impuestos) |
| `PPOR4ALB` | Moneda | 8 |  | Porcentaje de portes (Exento de impuestos) |
| `IPOR4ALB` | Moneda | 8 |  | Importe de portes (Exento de impuestos) |
| `PFIN4ALB` | Moneda | 8 |  | Porcentaje de financiación (Exento de impuestos) |
| `IFIN4ALB` | Moneda | 8 |  | Importe de financiación (Exento de impuestos) |
| `BAS4ALB` | Moneda | 8 |  | Base (Exenta de impuestos) |
| `EMAALB` | Entero | 2 |  | [E]Enviado por e-mail |
| `PASALB` | Texto corto | 150 |  | [E]Permisos y contraseña del documento |
| `TPDALB` | Moneda | 8 |  | [E]Ticket, porcentaje de descuento |
| `TIDALB` | Moneda | 8 |  | [E]Ticket, importe de descuento |
| `CEMALB` | Texto corto | 255 |  | E-mail de destino |
| `CPAALB` | Texto corto | 50 |  | País del cliente |
| `BNOALB` | Texto corto | 40 |  | Nombre del banco |
| `BENALB` | Texto corto | 4 |  | Banco: Entidad |
| `BOFALB` | Texto corto | 4 |  | Banco: Oficina |
| `BDCALB` | Texto corto | 2 |  | Banco: DC |
| `BNUALB` | Texto corto | 10 |  | Banco: Cuenta |
| `TIVA1ALB` | Entero | 2 |  | [E]Tipo de iva al que pertenece el neto 1 (0 a 6) |
| `TIVA2ALB` | Entero | 2 |  | [E]Tipo de iva al que pertenece el neto 2 (0 a 6) |
| `TIVA3ALB` | Entero | 2 |  | [E]Tipo de iva al que pertenece el neto 3 (0 a 6) |
| `BIBALB` | Texto corto | 34 |  | Banco: Código IBAN |
| `BICALB` | Texto corto | 11 |  | Banco: Código BIC |
| `EFSALB` | Moneda | 8 |  | Entregado en segunda forma de pago (para TPV) |
| `EFVALB` | Moneda | 8 |  | Entregado en vales (para TPV) |
| `TPVIDALB` | Texto corto | 16 |  | Identicador de apertura de turno (para TPV) |
| `TERALB` | Entero | 2 |  | Terminal que lo creó (para TPV) |
| `TFIALB` | Entero largo | 4 |  | Tarjeta de fidelización usada |
| `TFAALB` | Moneda | 8 |  | Puntos/Saldo acumulado en esta venta |
| `DEPALB` | Entero | 2 |  | Código del dependiente de TPVSOL |
| `NASALB` | Texto corto | 15 |  | [E]Nota asociada al documento |
| `DEMALB` | Entero | 2 |  | Fecha última modificación |
| `EERALB` | Entero | 2 |  | [E]Estado envío RETO |

---

## F_ALM

**Registros:** 1

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODALM` | Texto corto | 3 | ✓ | Código |
| `NOMALM` | Texto corto | 50 |  | Nombre |
| `OBSALM` | Texto corto | 100 |  | Observaciones |
| `DIRALM` | Texto corto | 100 |  | Dirección |
| `CPOALM` | Texto corto | 10 |  | Código postal |
| `POBALM` | Texto corto | 30 |  | Población |
| `PROALM` | Texto corto | 40 |  | Provincia |
| `PCOALM` | Texto corto | 50 |  | Persona de contacto |
| `TELALM` | Texto corto | 50 |  | Teléfono |
| `FAXALM` | Texto corto | 25 |  | Fax |
| `EMAALM` | Texto corto | 60 |  | E-mail |

---

## F_ANP

**Registros:** 16588

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODANP` | Entero largo | 4 |  | Fecha |
| `PROANP` | Entero largo | 4 |  | [F=00000]Proveedor |
| `IMPANP` | Moneda | 8 |  | Importe |
| `ESTANP` | Entero | 2 |  | [L=#0;Sin aplicar#1;Aplicado]Estado |
| `TDOANP` | Texto corto | 1 |  | [E]TIPO DE DOCUMENTO AL QUE SE APLICO EL ANTICIPO |
| `CDOANP` | Entero largo | 4 |  | [E]CODIGO DE DOCUMENTO AL QUE SE APLICO EL ANTICIPO |
| `OBSANP` | Texto corto | 255 |  | Observaciones |

---

## F_ANT

**Registros:** 66756

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODANT` | Entero largo | 4 |  | Fecha |
| `CLIANT` | Entero largo | 4 |  | [F=00000]Cliente |
| `IMPANT` | Moneda | 8 |  | Importe |
| `ESTANT` | Entero | 2 |  | [L=#0;Sin aplicar#1;Aplicado]Estado |
| `DOCANT` | Entero | 2 |  | [E]Documento al que se le aplicó el anticipo, 0= Ninguno, 1=Factura, |
| `TDOANT` | Texto corto | 1 |  | [E]TIPO DE DOCUMENTO AL QUE SE APLICO EL ANTICIPO |
| `CDOANT` | Entero largo | 4 |  | [E]CODIGO DE DOCUMENTO AL QUE SE APLICO EL ANTICIPO |
| `SDOANT` | Entero largo | 4 |  | [E]SUBCÓDIGO DE DOCUMENTO AL QUE SE APLICÓ EL ANTICIPO, EN |
| `OBSANT` | Texto corto | 255 |  | Observaciones |
| `CRIANT` | Entero | 2 |  | Tipo: 0=Vale, 1=Anticipo efectivo, 2=Anticipo otros |
| `CAJANT` | Entero | 2 |  |  |
| `TPVIDANT` | Texto corto | 16 |  | Identicador de apertura de turno (para TPV) |

---

## F_ARC

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `ARTARC` | Texto corto | 13 | ✓ | Artículo |
| `CE1ARC` | Texto corto | 3 | ✓ | Talla |
| `CE2ARC` | Texto corto | 3 | ✓ | Color |

---

## F_ART

**Registros:** 14518

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODART` | Texto corto | 13 | ✓ | Código |
| `EANART` | Texto corto | 50 |  | Código EAN |
| `EQUART` | Texto corto | 18 |  | Equivalente |
| `CCOART` | Entero largo | 4 |  | Código corto |
| `FAMART` | Texto corto | 3 |  | Familia |
| `DESART` | Texto corto | 50 |  | Descripcion general |
| `DEEART` | Texto corto | 30 |  | [E]Descripción para etiquetas |
| `DETART` | Texto corto | 20 |  | [E]Descripción para tickes |
| `PHAART` | Entero largo | 4 |  | Proveedor habitual |
| `TIVART` | Entero | 2 |  | [L=#0;IVA1AUT#1;IVA2AUT#2;IVA3AUT#3;Exento]Tipo de IVA |
| `PCOART` | Moneda | 8 |  | Precio de costo |
| `DT0ART` | Moneda | 8 |  | Descuento 1 |
| `DT1ART` | Moneda | 8 |  | Descuento 2 |
| `DT2ART` | Moneda | 8 |  | Fecha de alta |
| `MDAART` | Moneda | 8 |  | Máximo descuento aplicable |
| `UBIART` | Texto corto | 30 |  | Ubicación en el almacén |
| `UELART` | Entero | 2 |  | Unidades en línea |
| `UPPART` | Moneda | 8 |  | Unidades por palets |
| `DIMART` | Texto corto | 30 |  | Dimensiones |
| `MEMART` | Texto largo |  |  | Mensaje emergente |
| `OBSART` | Texto largo |  |  | Observaciones |
| `NPUART` | Entero | 2 |  | [E]No permitir utilzar el art. |
| `NIAART` | Entero | 2 |  | [E]No imprimir en ningun listado |
| `COMART` | Entero largo | 4 |  | Art. compuesto |
| `CP1ART` | Texto corto | 25 |  | Campo Programable 1 |
| `CP2ART` | Texto corto | 25 |  | Campo Programable 2 |
| `CP3ART` | Texto corto | 25 |  | Campo Programable 3 |
| `REFART` | Texto corto | 30 |  | Referencia del proveedor |
| `DLAART` | Texto largo |  |  | Descripción larga |
| `IPUART` | Moneda | 8 |  | Importe de portes por unidad |
| `NCCART` | Texto corto | 10 |  | Cuenta contable para ventas |
| `CUCART` | Texto corto | 10 |  | Cuenta contable para compras |
| `CANART` | Moneda | 8 |  | Cantidad por defecto en las salidas |
| `IMGART` | Texto largo |  |  | [E]Imagen |
| `SUWART` | Entero | 2 |  | [E]Subir a internet |
| `DELART` | Texto largo |  |  | Descripción para los listados en la web |
| `DEWART` | Texto largo |  |  | Descripción web |
| `MEWART` | Texto corto | 255 |  | [E]Mensaje emergente web |
| `CSTART` | Entero | 2 |  | [E]Controlar stock (web) |
| `IMWART` | Texto corto | 100 |  | [E]Imagen web |
| `STOART` | Entero | 2 |  | Fecha de última modificación |
| `PESART` | Moneda | 8 |  | Peso |
| `FTEART` | Entero largo | 4 |  | Fabricante |
| `ACOART` | Texto corto | 13 |  | Artículo concatenado |
| `GARART` | Texto corto | 50 |  | Garantía |
| `UMEART` | Entero | 2 |  | Unidad de medida |
| `TMOART` | Entero | 2 |  | [L=#0;Sí#1;No]Traspasar el artículo a MovilSol |
| `CONART` | Texto corto | 120 |  | [E]Contraseña |
| `TIV2ART` | Entero largo | 4 |  | [L=#0;IVA1AUT#1;IVA2AUT#2;IVA3AUT#3;Exento]Tipo de IVA 2º periodo |
| `DE1ART` | Texto largo |  |  | Primera descripción auxiliar |
| `DE2ART` | Texto largo |  |  | Segunda descripción auxiliar |
| `DE3ART` | Texto largo |  |  | Tercera descripción auxiliar |
| `DFIART` | Moneda | 8 |  | % Descuento fijo en ventas |
| `RPUART` | Entero | 2 |  | [E]Artículo concatenado, tipo de precio |
| `RPFART` | Moneda | 8 |  | [E]Artículo concatenado, precio fijado |
| `RCUART` | Entero | 2 |  | [E]Artículo concatenado, cantidad a utilizar |
| `RCFART` | Moneda | 8 |  | [E]Artículo concatenado, cantidad a multiplicar |
| `MECART` | Texto largo |  |  | Mensaje emergente para compras |
| `DSCART` | Entero | 2 |  | Artículo descatalogado |
| `AMAART` | Entero | 2 |  | [L=#0;Sí#1;No]Artículo manual |
| `CAEART` | Moneda | 8 |  | Cantidad por defecto en las entradas |
| `UFSART` | Entero | 2 |  | Utilizar la descripción de la familia en sumatorios |
| `IMFART` | Doble | 8 |  | Fecha de la imagen |
| `PFIART` | Moneda | 8 |  | Puntos tarjeta fidelización |
| `MPTART` | Entero | 2 |  | Mostrar en panel táctil TPVSOL |
| `CP4ART` | Texto corto | 25 |  | Campo Programable 4 |
| `CP5ART` | Texto corto | 25 |  | Campo Programable 5 |
| `ORDART` | Entero largo | 4 |  | Indica el orden para la Tienda Virtual |
| `UEQART` | Texto corto | 20 |  | Unidad de medida equivalente |
| `DCOART` | Entero | 2 |  | Días máximos de conservación |
| `FAVART` | Texto corto | 1 |  | [E]Favorito |
| `DSTART` | Entero | 2 |  | Destacado |
| `VEWART` | Moneda | 8 |  | Ventas asociadas al artículo |
| `URAART` | Texto corto | 255 |  | URL amigable |
| `VMPART` | Moneda | 8 |  | Valoraciones medias |
| `UR1ART` | Texto corto | 255 |  | URL de información adicional 1 |
| `UR2ART` | Texto corto | 255 |  | URL de información adicional 2 |
| `UR3ART` | Texto corto | 255 |  | URL de información adicional 3 |
| `CN8ART` | Texto corto | 25 |  | Código estadistico Intrstat CN8 |
| `OCUART` | Entero | 2 |  | Ocultar en TPVSOL |
| `RSVART` | Entero | 2 |  | Gestionar reservas |

---

## F_BAN

**Registros:** 51

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODBAN` | Entero | 2 | ✓ | Código |
| `NOMBAN` | Texto corto | 40 |  | Nombre |
| `DOMBAN` | Texto corto | 40 |  | Domicilio |
| `POBBAN` | Texto corto | 30 |  | Población |
| `CPOBAN` | Texto corto | 10 |  | Cód. Postal |
| `PROBAN` | Texto corto | 40 |  | Provincia |
| `TELBAN` | Texto corto | 50 |  | Teléfono |
| `FAXBAN` | Texto corto | 12 |  | Fax |
| `DIRBAN` | Texto corto | 40 |  | Director |
| `TDIBAN` | Texto corto | 12 |  | Teléfono director |
| `INTBAN` | Texto corto | 40 |  | Interventor |
| `TINBAN` | Texto corto | 12 |  | Teléfono interventor |
| `COMBAN` | Texto corto | 40 |  | Comercial |
| `TCOBAN` | Texto corto | 12 |  | Teléfono comercial |
| `ENTBAN` | Texto corto | 4 |  | Entidad |
| `OFIBAN` | Texto corto | 4 |  | Oficina |
| `DCOBAN` | Texto corto | 2 |  | Dígitos de control |
| `CUEBAN` | Texto corto | 10 |  | Nº de cuenta |
| `TCUBAN` | Entero | 2 |  | Vencimiento de la póliza de crédito |
| `LIMBAN` | Moneda | 8 |  | Límite de la póliza de crédito |
| `IMPBAN` | Moneda | 8 |  | Fecha de alta |
| `CCOBAN` | Texto corto | 10 |  | Cuenta contable |
| `INEBAN` | Texto corto | 9 |  | Cód. Plaza INE |
| `CP19BAN` | Texto corto | 18 |  | Cuaderno 19. CIF Presentador. |
| `NP19BAN` | Texto corto | 40 |  | Cuaderno 19. Nombre Presentador. |
| `SP19BAN` | Texto corto | 3 |  | Cuaderno 19. Sufijo Presentador. |
| `CO19BAN` | Texto corto | 18 |  | Cuaderno 19. CIF Ordenante. |
| `NO19BAN` | Texto corto | 40 |  | Cuaderno 19. Nombre Ordenante. |
| `SO19BAN` | Texto corto | 3 |  | Cuaderno 19. Sufijo Ordenante. |
| `CP58BAN` | Texto corto | 18 |  | Cuaderno 58. CIF Presentador. |
| `NP58BAN` | Texto corto | 40 |  | Cuaderno 58. Nombre Presentador. |
| `SP58BAN` | Texto corto | 3 |  | Cuaderno 58. Sufijo Presentador. |
| `CO58BAN` | Texto corto | 18 |  | Cuaderno 58. CIF Ordenante. |
| `NO58BAN` | Texto corto | 40 |  | Cuaderno 58. Nombre Ordenante. |
| `SO58BAN` | Texto corto | 3 |  | Cuaderno 58. Sufijo Ordenante. |
| `CO34BAN` | Texto corto | 10 |  | Transferencias. Código Ordenante. |
| `NO34BAN` | Texto corto | 36 |  | Transferencias. Nombre Ordenante. |
| `DO34BAN` | Texto corto | 36 |  | Transferencias. Domicilio Ordenante. |
| `PL34BAN` | Texto corto | 36 |  | Transferencias. Nombre Ordenante. |
| `IBABAN` | Texto corto | 34 |  | Código IBAN |
| `BICBAN` | Texto corto | 11 |  | Código BIC |
| `RE34BAN` | Texto corto | 3 |  | Sufijo transferencias |
| `BTRBAN` | Entero | 2 |  | Incluir en factura electronica |

---

## F_BLQ

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `DOCBLQ` | Texto corto | 1 | ✓ | Documento (P=Presupuesto, C=Pedido, A=Albaran, F=Factura, ...) |
| `TDOBLQ` | Texto corto | 1 | ✓ | Serie del documento |
| `CDOBLQ` | Entero largo | 4 | ✓ | Código del documento |
| `USUBLQ` | Entero | 2 |  | Usuario |
| `NINBLQ` | Entero | 2 |  | Fecha y hora |

---

## F_BUS

**Registros:** 15489

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODBUS` | Entero largo | 4 |  | Código de la tabla |
| `NOMBUS` | Texto corto | 255 |  | Nombre |
| `DAT1BUS` | Texto corto | 255 |  | Dato 1 para búsquedas |
| `DAT2BUS` | Texto corto | 255 |  | Dato 2 para búsquedas |
| `DAT3BUS` | Texto corto | 255 |  | Dato 3 para búsquedas |
| `TIPBUS` | Texto corto | 50 |  | Tipo de fichero (F_CLI, F_PRO, F_ART, ETC.) |
| `CNUBUS` | Entero largo | 4 |  | Código del fichero asociado (numérico) |
| `CTEBUS` | Texto corto | 50 |  | Código del fichero asociado (texto) |
| `PNABUS` | Entero | 2 |  | Para identificar la actualización de los indices |

---

## F_CAF

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `AGECAF` | Entero largo | 4 | ✓ | Agente |
| `TIPCAF` | Entero largo | 4 | ✓ | [L=#0;Artículo#1;Familia]Tipo de descuento |
| `CODCAF` | Texto corto | 50 | ✓ | Artículo/familia |
| `COMCAF` | Moneda | 8 |  | Comisión |
| `TCOCAF` | Entero | 2 |  |  |

---

## F_CAJ

**Registros:** 243

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `NUMCAJ` | Entero largo | 4 |  | Fecha |
| `CAJCAJ` | Entero | 2 |  | Caja |
| `USNCAJ` | Entero | 2 |  | Seleccionar Documento Al Crear Nuevo Ticket (1 Si - 0 No) |

---

## F_CAP

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `LETCAP` | Texto corto | 1 | ✓ | Letra |
| `CODCAP` | Entero largo | 4 | ✓ | [F=000000]Código |
| `SUBCAP` | Entero largo | 4 | ✓ | Subcódigo |
| `ESTCAP` | Entero | 2 |  | [L=#0;Pte.#1;En curso#2;Terminado#3;Fact.#4;Fact.Parcial]Estado |
| `CLICAP` | Entero largo | 4 |  | [F=00000]Cliente |
| `DENCAP` | Texto corto | 50 |  | Denominación |
| `DESCAP` | Texto largo |  |  | Descripción |
| `LOCCAP` | Texto corto | 50 |  | Fecha de conclusión |
| `TTRCAP` | Entero | 2 |  | [L=#0;Administración#1;Presupuesto]Tipo de trabajo |
| `MATCAP` | Moneda | 8 |  | Materiales |
| `MOBCAP` | Moneda | 8 |  | Mano de obra |
| `PINCAP` | Moneda | 8 |  | Porcentaje de índice |
| `IINCAP` | Moneda | 8 |  | Importe índice |
| `COSCAP` | Moneda | 8 |  | Coste total |
| `PMACAP` | Moneda | 8 |  | Porcentaje de margen |
| `IMACAP` | Moneda | 8 |  | Margen |
| `PVECAP` | Moneda | 8 |  | Precio venta |
| `CAN1CAP` | Moneda | 8 |  | Cantidad de material 1 |
| `CAN2CAP` | Moneda | 8 |  | Cantidad de material 2 |
| `CAN3CAP` | Moneda | 8 |  | Cantidad de material 3 |
| `CAN4CAP` | Moneda | 8 |  | Cantidad de material 4 |
| `CAN5CAP` | Moneda | 8 |  | Cantidad de material 5 |
| `CAN6CAP` | Moneda | 8 |  | Cantidad de material 6 |
| `CAN7CAP` | Moneda | 8 |  | Cantidad de material 7 |
| `UME1CAP` | Texto corto | 4 |  | Unidad de medida 1 |
| `UME2CAP` | Texto corto | 4 |  | Unidad de medida 2 |
| `UME3CAP` | Texto corto | 4 |  | Unidad de medida 3 |
| `UME4CAP` | Texto corto | 4 |  | Unidad de medida 4 |
| `UME5CAP` | Texto corto | 4 |  | Unidad de medida 5 |
| `UME6CAP` | Texto corto | 4 |  | Unidad de medida 6 |
| `UME7CAP` | Texto corto | 4 |  | Unidad de medida 7 |
| `MAT1CAP` | Texto corto | 40 |  | Material 1 |
| `MAT2CAP` | Texto corto | 40 |  | Material 2 |
| `MAT3CAP` | Texto corto | 40 |  | Material 3 |
| `MAT4CAP` | Texto corto | 40 |  | Material 4 |
| `MAT5CAP` | Texto corto | 40 |  | Material 5 |
| `MAT6CAP` | Texto corto | 40 |  | Material 6 |
| `MAT7CAP` | Texto corto | 40 |  | Material 7 |
| `TOT1CAP` | Moneda | 8 |  | Total línea de material 1 |
| `TOT2CAP` | Moneda | 8 |  | Total línea de material 2 |
| `TOT3CAP` | Moneda | 8 |  | Total línea de material 3 |
| `TOT4CAP` | Moneda | 8 |  | Total línea de material 4 |
| `TOT5CAP` | Moneda | 8 |  | Total línea de material 5 |
| `TOT6CAP` | Moneda | 8 |  | Total línea de material 6 |
| `TOT7CAP` | Moneda | 8 |  | Total línea de material 7 |
| `NHPCAP` | Moneda | 8 |  | Número de horas presupuestadas |
| `DES1CAP` | Texto corto | 30 |  | Descripción de dibujo 1 |
| `DES2CAP` | Texto corto | 30 |  | Descripción de dibujo 2 |
| `UNI1CAP` | Moneda | 8 |  | Unidades 1 |
| `UNI2CAP` | Moneda | 8 |  | Unidades 2 |
| `PUN1CAP` | Moneda | 8 |  | Precio unitario 1 |
| `PUN2CAP` | Moneda | 8 |  | Precio unitario 2 |
| `TOT21CAP` | Moneda | 8 |  | Total dibujo 1 |
| `TOT22CAP` | Moneda | 8 |  | Total dibujo 2 |

---

## F_CCC

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CLICCC` | Entero largo | 4 | ✓ | [F=00000]Cliente |
| `CODCCC` | Entero | 2 | ✓ | Código |
| `ENTCCC` | Texto corto | 4 |  | Entidad |
| `OFICCC` | Texto corto | 4 |  | Oficina |
| `DCOCCC` | Texto corto | 2 |  | Dígitos de control |
| `CUECCC` | Texto corto | 10 |  | Nº de cuenta |
| `BANCCC` | Texto corto | 50 |  | Banco |
| `IBACCC` | Texto corto | 34 |  | Código IBAN |
| `BICCCC` | Texto corto | 11 |  | Código BIC |
| `MUTCCC` | Entero | 2 |  | Mandato de domiciliación. Utilizar |
| `MRECCC` | Texto corto | 35 |  | Mandato fecha |

---

## F_CE1

**Registros:** 45

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODCE1` | Texto corto | 3 | ✓ | Código |
| `DESCE1` | Texto corto | 50 |  | Descripción |
| `COLCE1` | Entero largo | 4 |  | [E]Color descriptivo |
| `ORDCE1` | Entero | 2 |  | [E]Orden |

---

## F_CE2

**Registros:** 27

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODCE2` | Texto corto | 3 | ✓ | Código |
| `DESCE2` | Texto corto | 50 |  | Descripción |
| `COLCE2` | Entero largo | 4 |  | [E]Color descriptivo |
| `ORDCE2` | Entero | 2 |  | [E]Orden |

---

## F_CEG

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODCEG` | Entero | 2 | ✓ | Código |
| `CE1CEG` | Texto corto | 3 | ✓ | Talla |
| `CE2CEG` | Texto corto | 3 | ✓ | Color |
| `DENCEG` | Texto corto | 50 |  | Denominación |

---

## F_CFG

**Registros:** 877

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODCFG` | Texto corto | 50 | ✓ |  |
| `NUMCFG` | Moneda | 8 |  |  |
| `TEXCFG` | Texto largo |  |  |  |
| `TIPCFG` | Entero | 2 |  |  |

---

## F_CGA

**Registros:** 11

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODCGA` | Texto corto | 3 | ✓ | Código |
| `DESCGA` | Texto corto | 50 |  | Descripción |

---

## F_CHE

**Registros:** 7864

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODCHE` | Entero largo | 4 | ✓ | Código |
| `LUGCHE` | Texto corto | 50 |  | Lugar de emisión |
| `IMPCHE` | Moneda | 8 |  | Fecha de vencimiento |
| `CLICHE` | Entero largo | 4 |  | [F=00000]Cliente |
| `BANCHE` | Entero | 2 |  | Banco |
| `CLACHE` | Texto corto | 50 |  | Claúsula |
| `CHECHE` | Texto corto | 50 |  | Clave del documento |
| `CNOCHE` | Texto corto | 255 |  | Nombre |

---

## F_CHEIMG

**Registros:** 5031

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODCHE` | Entero largo | 4 |  |  |
| `URLCHE` | Texto corto | 255 |  |  |

---

## F_CHEIMG_OLD

**Registros:** 8890

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODCHE` | Entero largo | 4 |  |  |
| `URLCHE` | Texto corto | 255 |  |  |

---

## F_CHEMIO

**Registros:** 108

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODCHE` | Entero largo | 4 |  |  |
| `BANCHE` | Entero largo | 4 |  |  |
| `CHECHE` | Texto corto | 100 |  |  |
| `IMPCHE` | Doble | 8 |  |  |
| `ESTCHE` | Texto corto | 1 |  |  |

---

## F_CIN

**Registros:** 14392

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `ALMCIN` | Texto corto | 3 | ✓ | Fecha |
| `ARTCIN` | Texto corto | 13 | ✓ | Artículo |
| `CE1CIN` | Texto corto | 3 | ✓ | Talla |
| `CE2CIN` | Texto corto | 3 | ✓ | Color |
| `UACCIN` | Moneda | 8 |  | Stock actual |
| `URECIN` | Moneda | 8 |  | Unidades contadas |
| `DACCIN` | Moneda | 8 |  | [E]Disponible antes de la consolidación |
| `DRECIN` | Moneda | 8 |  | [E]Disponible consolidado |

---

## F_CLI

**Registros:** 880

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODCLI` | Entero largo | 4 | ✓ | Código |
| `CCOCLI` | Entero largo | 4 |  | Código contable |
| `NIFCLI` | Texto corto | 18 |  | N.I.F. |
| `NOFCLI` | Texto corto | 100 |  | Nombre fiscal |
| `NOCCLI` | Texto corto | 100 |  | Nombre comercial |
| `DOMCLI` | Texto corto | 100 |  | Domicilio |
| `POBCLI` | Texto corto | 30 |  | Población |
| `CPOCLI` | Texto corto | 10 |  | Cód. Postal |
| `PROCLI` | Texto corto | 40 |  | Provincia |
| `TELCLI` | Texto corto | 50 |  | Teléfono |
| `FAXCLI` | Texto corto | 25 |  | Fax |
| `PCOCLI` | Texto corto | 50 |  | Persona de contacto |
| `AGECLI` | Entero largo | 4 |  | [F=00000]Agente comercial |
| `BANCLI` | Texto corto | 40 |  | Banco |
| `ENTCLI` | Texto corto | 4 |  | Entidad |
| `OFICLI` | Texto corto | 4 |  | Oficina |
| `DCOCLI` | Texto corto | 2 |  | Dígito de control |
| `CUECLI` | Texto corto | 10 |  | Nº de cuenta |
| `FPACLI` | Texto corto | 3 |  | Forma de pago |
| `FINCLI` | Moneda | 8 |  | Porcentaje de financiación |
| `PPACLI` | Moneda | 8 |  | Porcentaje de pronto pago |
| `TARCLI` | Entero largo | 4 |  | [E]Tarifa |
| `DP1CLI` | Entero | 2 |  | Día de pago 1 |
| `DP2CLI` | Entero | 2 |  | Día de pago 2 |
| `DP3CLI` | Entero | 2 |  | Día de pago 3 |
| `TCLCLI` | Texto corto | 3 |  | Tipo de cliente |
| `DT1CLI` | Moneda | 8 |  | Descuento 1 |
| `DT2CLI` | Moneda | 8 |  | Descuento 2 |
| `DT3CLI` | Moneda | 8 |  | Descuento 3 |
| `TESCLI` | Entero | 2 |  | [E]Tarifa especial; 0: No, 1:si |
| `CPRCLI` | Texto corto | 10 |  | Código de proveedor |
| `TPOCLI` | Entero | 2 |  | [L=#0;Pagados#1;Debidos]Portes |
| `PORCLI` | Texto corto | 30 |  | Portes (texto) |
| `IVACLI` | Entero | 2 |  | [L=#0;Con IVA#1;Sin IVA#2;Intracomunitario#3;Exportación]Tipo de IVA |
| `TIVCLI` | Entero | 2 |  | [L=#0;Sin asignar;#1;IVA1AUT#2;IVA2AUT#3;IVA3AUT#4;Exento]Porcentaje |
| `REQCLI` | Entero | 2 |  | Fecha de alta |
| `EMACLI` | Texto corto | 255 |  | E-mail |
| `WEBCLI` | Texto corto | 60 |  | Web |
| `MEMCLI` | Texto largo |  |  | Mensaje emergente |
| `OBSCLI` | Texto largo |  |  | Observaciones |
| `HORCLI` | Texto corto | 30 |  | Horario |
| `VDECLI` | Texto corto | 5 |  | Vacaciones (desde) |
| `VHACLI` | Texto corto | 5 |  | Vacaciones (hasta) |
| `CRFCLI` | Entero | 2 |  | [E]Crear recibo al factura |
| `NVCCLI` | Entero | 2 |  | [E]No vender a este cliente |
| `NFCCLI` | Entero | 2 |  | [E]No facturar a este cliente |
| `NICCLI` | Entero | 2 |  | [E]No imprimir este cliente |
| `MONCLI` | Entero | 2 |  | [E]0: Euros;1:Pesetas |
| `PAICLI` | Texto corto | 50 |  | País |
| `DOCCLI` | Entero | 2 |  | Nº de serie predeterminado |
| `DBACLI` | Texto corto | 50 |  | Dirección del banco |
| `PBACLI` | Texto corto | 50 |  | Población del banco |
| `SWFCLI` | Texto corto | 50 |  | IBAN del banco |
| `CO1CLI` | Texto largo |  |  | Concepto 1 de facturación |
| `CO2CLI` | Texto largo |  |  | Concepto 2 de facturación |
| `CO3CLI` | Texto largo |  |  | Concepto 3 de facturación |
| `CO4CLI` | Texto largo |  |  | Concepto 4 de facturación |
| `CO5CLI` | Texto largo |  |  | Concepto 5 de facturación |
| `IM1CLI` | Moneda | 8 |  | Importe 1 de facturación |
| `IM2CLI` | Moneda | 8 |  | Importe 2 de facturación |
| `IM3CLI` | Moneda | 8 |  | Importe 3 de facturación |
| `IM4CLI` | Moneda | 8 |  | Importe 4 de facturación |
| `IM5CLI` | Moneda | 8 |  | Importe 5 de facturación |
| `RUTCLI` | Texto corto | 3 |  | Ruta |
| `SWICLI` | Texto corto | 11 |  | SWIFT del banco |
| `GIRCLI` | Texto corto | 50 |  | Teléfonos de contacto |
| `CUWCLI` | Texto corto | 50 |  | [E]Código ususario web |
| `CAWCLI` | Texto corto | 15 |  | [E]Clave usuario web |
| `SUWCLI` | Entero | 2 |  | [E]Permitir su utilización en internet |
| `MEWCLI` | Texto corto | 255 |  | [E]Mensaje emergente web |
| `ESTCLI` | Entero largo | 4 |  | [L=#0;Sin seleccionar#1;Habitual#2;Esporádico#3;Dado de baja#4;En |
| `AR1CLI` | Texto corto | 13 |  | Artículo 1 de facturación |
| `AR2CLI` | Texto corto | 13 |  | Artículo 2 de facturación |
| `AR3CLI` | Texto corto | 13 |  | Artículo 3 de facturación |
| `AR4CLI` | Texto corto | 13 |  | Artículo 4 de facturación |
| `AR5CLI` | Texto corto | 13 |  | Artículo 5 de facturación |
| `FELCLI` | Entero largo | 4 |  | [E]FACTURA ELECTRÓNICA DEL CLIENTE, 0 = NO; 1 = SI |
| `TRACLI` | Entero | 2 |  | Transportista |
| `NCFCLI` | Entero | 2 |  | Fecha de nacimiento |
| `FOTCLI` | Texto corto | 255 |  | [E]Foto del cliente |
| `SKYCLI` | Texto corto | 60 |  | [E]Cuenta skype del cliente |
| `NO1CLI` | Texto corto | 50 |  | Nombre de la persona de contacto 1 |
| `TF1CLI` | Texto corto | 50 |  | Teléfono de la persona de contacto 1 |
| `EM1CLI` | Texto corto | 60 |  | E-mail de la persona de contacto 1 |
| `NO2CLI` | Texto corto | 50 |  | Nombre de la persona de contacto 2 |
| `TF2CLI` | Texto corto | 50 |  | Teléfono de la persona de contacto 2 |
| `EM2CLI` | Texto corto | 60 |  | E-mail de la persona de contacto 2 |
| `NO3CLI` | Texto corto | 50 |  | Nombre de la persona de contacto 3 |
| `TF3CLI` | Texto corto | 50 |  | Teléfono de la persona de contacto 3 |
| `EM3CLI` | Texto corto | 60 |  | E-mail de la persona de contacto 3 |
| `NO4CLI` | Texto corto | 50 |  | Nombre de la persona de contacto 4 |
| `TF4CLI` | Texto corto | 50 |  | Teléfono de la persona de contacto 4 |
| `EM4CLI` | Texto corto | 60 |  | E-mail de la persona de contacto 4 |
| `NO5CLI` | Texto corto | 50 |  | Nombre de la persona de contacto 5 |
| `TF5CLI` | Texto corto | 50 |  | Teléfono de la persona de contacto 5 |
| `EM5CLI` | Texto corto | 60 |  | E-mail de la persona de contacto 5 |
| `RETCLI` | Entero | 2 |  | [L=#0;No#1;Sí]Retención |
| `CTMCLI` | Entero | 2 |  | Divisa |
| `MNPCLI` | Entero | 2 |  | [L=#0;Sin |
| `IFICLI` | Entero largo | 4 |  | [L=#0;Ninguno;#1;NIF#2;NIF/IVA (NIF operador |
| `IMPCLI` | Entero largo | 4 |  | [L=#0;IVA#1;IGIC]Tipo de impuesto |
| `NCACLI` | Entero | 2 |  | [E]Número de copias de albaranes |
| `CAMCLI` | Moneda | 8 |  | Comisión por defecto para agentes |
| `CO6CLI` | Texto largo |  |  | Concepto 6 de facturación |
| `IM6CLI` | Moneda | 8 |  | Importe 6 de facturación |
| `AR6CLI` | Texto corto | 13 |  | Artículo 6 de facturación |
| `CO7CLI` | Texto largo |  |  | Concepto 7 de facturación |
| `IM7CLI` | Moneda | 8 |  | Importe 7 de facturación |
| `AR7CLI` | Texto corto | 13 |  | Artículo 7 de facturación |
| `CO8CLI` | Texto largo |  |  | Concepto 8 de facturación |
| `IM8CLI` | Moneda | 8 |  | Importe 8 de facturación |
| `AR8CLI` | Texto corto | 13 |  | Artículo 8 de facturación |
| `CO9CLI` | Texto largo |  |  | Concepto 9 de facturación |
| `IM9CLI` | Moneda | 8 |  | Importe 9 de facturación |
| `AR9CLI` | Texto corto | 13 |  | Artículo 9 de facturación |
| `CO10CLI` | Texto largo |  |  | Concepto 10 de facturación |
| `IM10CLI` | Moneda | 8 |  | Importe 10 de facturación |
| `AR10CLI` | Texto corto | 13 |  | Artículo 10 de facturación |
| `CO11CLI` | Texto largo |  |  | Concepto 11 de facturación |
| `IM11CLI` | Moneda | 8 |  | Importe 11 de facturación |
| `AR11CLI` | Texto corto | 13 |  | Artículo 11 de facturación |
| `CO12CLI` | Texto largo |  |  | Concepto 12 de facturación |
| `IM12CLI` | Moneda | 8 |  | Importe 12 de facturación |
| `AR12CLI` | Texto corto | 13 |  | Artículo 12 de facturación |
| `ME1CLI` | Entero largo | 4 |  | [L=#0;Sin |
| `ME2CLI` | Entero largo | 4 |  | [L=#0;Sin |
| `ME3CLI` | Entero largo | 4 |  | [L=#0;Sin |
| `ME4CLI` | Entero largo | 4 |  | [L=#0;Sin |
| `ME5CLI` | Entero largo | 4 |  | [L=#0;Sin |
| `ME6CLI` | Entero largo | 4 |  | [L=#0;Sin |
| `ME7CLI` | Entero largo | 4 |  | [L=#0;Sin |
| `ME8CLI` | Entero largo | 4 |  | [L=#0;Sin |
| `ME9CLI` | Entero largo | 4 |  | [L=#0;Sin |
| `ME10CLI` | Entero largo | 4 |  | [L=#0;Sin |
| `ME11CLI` | Entero largo | 4 |  | [L=#0;Sin |
| `ME12CLI` | Entero largo | 4 |  | [L=#0;Sin |
| `CASCLI` | Texto corto | 255 |  | Carpeta asociada al cliente |
| `EMOCLI` | Entero largo | 4 |  | Exportar a movilsol (0 = Si, 1 = No) |
| `PRECLI` | Moneda | 8 |  | % de retención |
| `DTCCLI` | Moneda | 8 |  | % dto. comercial |
| `EPETCLI` | Texto corto | 13 |  | EDI Código peticionario |
| `ERECCLI` | Texto corto | 13 |  | EDI Código receptor |
| `ECLICLI` | Texto corto | 13 |  | EDI Código cliente |
| `EPAGCLI` | Texto corto | 13 |  | Fecha de última modificación del cliente |
| `PGCCLI` | Texto corto | 3 |  | Cuenta del plan contable general a la que está asociado el cliente (430, |
| `RESCLI` | Texto corto | 200 |  | Rappels |
| `RFICLI` | Moneda | 8 |  | Rappel fijo |
| `PRACLI` | Texto corto | 30 |  | Pago de rappels |
| `ACTCLI` | Texto corto | 4 |  | Actividad |
| `ECOCLI` | Texto corto | 60 |  | E-mail comercial |
| `ECNCLI` | Texto corto | 60 |  | E-mail contabilidad |
| `EADCLI` | Texto corto | 60 |  | E-mail administración |
| `TWICLI` | Texto corto | 255 |  | Perfil de twitter |
| `A1KCLI` | Entero | 2 |  | 1kB |
| `MOVCLI` | Texto corto | 50 |  | Móvil |
| `CPFCLI` | Texto corto | 15 |  | N.C.P.P.F. |
| `RCCCLI` | Entero | 2 |  | Régimen especial del criterio de caja |
| `MUTCLI` | Entero | 2 |  | Mandato de domiciliación. Utilizar |
| `MRECLI` | Texto corto | 35 |  | Mandato fecha |
| `ACO1CLI` | Texto corto | 20 |  | O.Contable Código DIR3 |
| `ADO1CLI` | Texto corto | 100 |  | O.Contable Domicilio |
| `ACP1CLI` | Texto corto | 10 |  | O.Contable Código postal |
| `APO1CLI` | Texto corto | 30 |  | O.Contable Población |
| `APR1CLI` | Texto corto | 40 |  | O.Contable Provincia |
| `APA1CLI` | Texto corto | 50 |  | O.Contable País |
| `ACO2CLI` | Texto corto | 20 |  | O. Gestor Código DIR3 |
| `ADO2CLI` | Texto corto | 100 |  | O.Gestor Domicilio |
| `ACP2CLI` | Texto corto | 10 |  | O. Gestor Código postal |
| `APO2CLI` | Texto corto | 30 |  | O.Gestor Población |
| `APR2CLI` | Texto corto | 40 |  | O.Gestor Provincia |
| `APA2CLI` | Texto corto | 50 |  | O.Gestor País |
| `ACO3CLI` | Texto corto | 20 |  | U.Tramitadora Código DIR3 |
| `ADO3CLI` | Texto corto | 100 |  | U.Tramitadora Domicilio |
| `ACP3CLI` | Texto corto | 10 |  | U.Tramitadora Código postal |
| `APO3CLI` | Texto corto | 30 |  | U.Tramitadora Población |
| `APR3CLI` | Texto corto | 40 |  | U.Tramitadora Provincia |
| `APA3CLI` | Texto corto | 50 |  | U.Tramitadora País |
| `IEUCLI` | Entero | 2 |  | Iva en país de residencia |
| `ACO4CLI` | Texto corto | 20 |  | O.Comprador Código DIR3 |
| `ADO4CLI` | Texto corto | 100 |  | O.Comprador Domicilio |
| `ACP4CLI` | Texto corto | 10 |  | O.Comprador Código postal |
| `APO4CLI` | Texto corto | 30 |  | O.Comprador Población |
| `APR4CLI` | Texto corto | 40 |  | O.Comprador Provincia |
| `APA4CLI` | Texto corto | 50 |  | O.Comprador País |
| `BTRCLI` | Entero | 2 |  | Banco para transferencias |
| `CFECLI` | Entero | 2 |  | Configuración para generación de factura-e |
| `COPCLI` | Entero | 2 |  | Clave de operación |
| `MDFCLI` | Entero | 2 |  | Modelo de impresión para facturas |
| `APDCLI` | Entero | 2 |  | Aceptada la política de tratamiento de datos |
| `PECCLI` | Entero | 2 |  | Permitido el envío de e-mails comerciales |
| `MDACLI` | Entero largo | 4 |  | Modelo de impresión para albaranes |
| `TRECLI` | Entero | 2 |  | [E]Tipo de retención |
| `CVICLI` | Entero | 2 |  | [E]Clave de operación intracomunitaria |
| `FAVCLI` | Texto corto | 1 |  | [E]Favorito |
| `FCBCLI` | Texto corto | 255 |  | [E]Facebook |
| `ITGCLI` | Texto corto | 255 |  | [E]Instagram |
| `FEFCLI` | Entero | 2 |  | [E]Forma de entrega de las facturas |
| `ATVCLI` | Entero | 2 |  | [E]Aplicar tarifa por volumen |
| `DECCLI` | Entero | 2 |  | [E]Departamento contabilidad |
| `SDCCLI` | Entero | 2 |  | [E]Subdepartamento contabilidad |
| `CROCLI` | Texto corto | 20 |  | [E]Código ROPO |

---

## F_CNP

**Registros:** 9

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODCNP` | Entero | 2 | ✓ | Código |
| `TIPCNP` | Entero largo | 4 | ✓ | [L=#0;Cobros#1;Pagos]Tipo de contrapartida |
| `DESCNP` | Texto corto | 50 |  | Descripción |
| `CUECNP` | Texto corto | 10 |  | Cuenta contable |
| `CACCNP` | Entero | 2 |  | [E]Crear apunte en caja, 0 = no, 1 = si |
| `TDOCNP` | Entero | 2 |  | [E]Tipo de documento con el que se creará el apunte en caja |
| `ACACNP` | Entero | 2 |  | [E]Crear apunte a caja al utilizar la contrapartida (0 = No, 1 = Si) |
| `EFECNP` | Entero | 2 |  | [E]Efectivo |

---

## F_CNS

**Registros:** 34

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `ALMCNS` | Texto corto | 3 | ✓ | Fecha |
| `ARTCNS` | Texto corto | 13 | ✓ | Artículo |
| `NSECNS` | Texto corto | 50 |  | [E]FECHA DE CONSUMO PREFERENTE |
| `CANCNS` | Moneda | 8 |  | Unidades |

---

## F_COB

**Registros:** 1145

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODCOB` | Entero largo | 4 |  | Fecha |
| `IMPCOB` | Moneda | 8 |  | Importe |
| `CPTCOB` | Texto corto | 40 |  | Concepto |
| `CPACOB` | Entero | 2 |  | Contrapartida |
| `OBSCOB` | Texto largo |  |  | Observaciones |
| `TRACOB` | Entero largo | 4 |  | [L=#0;No traspasado#1;Traspasado]Traspasado a contabilidad |
| `TIPCOB` | Entero largo | 4 |  | [L=#0;Factura emitida#1;Albarán#2;Recibo#3;Factura recibida]Tipo de |

---

## F_COM

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODCOM` | Texto corto | 13 | ✓ | Código |
| `ARTCOM` | Texto corto | 13 | ✓ | Artículo |
| `DESCOM` | Texto corto | 50 |  | Descripción |
| `COSCOM` | Moneda | 8 |  | Precio de costo |
| `UNICOM` | Moneda | 8 |  | Unidades |
| `CE1COM` | Texto corto | 3 |  | Talla |
| `CE2COM` | Texto corto | 3 |  | Color |
| `ORDCOM` | Entero | 2 |  | Orden |

---

## F_DES

**Registros:** 2

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `TIPDES` | Texto corto | 5 | ✓ | Tipo de cliente |
| `ARFDES` | Texto corto | 13 | ✓ | Artículo / familia |
| `DESDES` | Texto corto | 50 |  | Descripción del artículo / familia |
| `FIJDES` | Texto corto | 1 |  | [E]No dejar modificar |
| `PORDES` | Moneda | 8 |  | Porcentaje |
| `TDEDES` | Entero | 2 |  | [L=#0;Porcentaje#1;Importe]Tipo |
| `IMPDES` | Moneda | 8 |  | Importe |
| `TFIDES` | Entero | 2 |  |  |

---

## F_DVL

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `ARTDVL` | Texto corto | 13 | ✓ | Codigo de articulo |
| `POSDVL` | Entero | 2 | ✓ | [E]Posición |
| `DESDVL` | Moneda | 8 | ✓ | Desde |
| `PDEDVL` | Moneda | 8 | ✓ | Precio/Descuento |

---

## F_DVO

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `ARTDVO` | Texto corto | 13 | ✓ | Codigo de articulo |
| `TIPDVO` | Entero | 2 | ✓ | [L=#0;Precio#1;Descuento]Tipo |

---

## F_EAC

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `ARTEAC` | Texto corto | 13 | ✓ | Artículo |
| `EANEAC` | Texto corto | 50 | ✓ | Código de barras |
| `CE1EAC` | Texto corto | 3 | ✓ | Talla |
| `CE2EAC` | Texto corto | 3 | ✓ | Color |

---

## F_EAN

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `ARTEAN` | Texto corto | 13 | ✓ | Artículo |
| `EANEAN` | Texto corto | 50 | ✓ | Código de barras |

---

## F_EMP

**Registros:** 2

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODEMP` | Texto corto | 3 | ✓ | Código |
| `NIFEMP` | Texto corto | 18 |  | N.I.F. |
| `DENEMP` | Texto corto | 100 |  | Denominación social |
| `NOMEMP` | Texto corto | 100 |  | Nombre comercial |
| `SIGEMP` | Texto corto | 2 |  | Sigla |
| `DOMEMP` | Texto corto | 100 |  | Domicilio |
| `NUMEMP` | Texto corto | 5 |  | Nº de calle |
| `ESCEMP` | Texto corto | 2 |  | Escalera |
| `PISEMP` | Texto corto | 2 |  | Piso |
| `PRTEMP` | Texto corto | 2 |  | Puerta |
| `POBEMP` | Texto corto | 30 |  | Población |
| `MUNEMP` | Texto corto | 5 |  | Municipio |
| `CPOEMP` | Texto corto | 10 |  | Cód. Postal |
| `PROEMP` | Texto corto | 40 |  | Provincia |
| `TELEMP` | Texto corto | 50 |  | Teléfono |
| `FAXEMP` | Texto corto | 15 |  | Fax |
| `EJEEMP` | Texto corto | 4 |  | [E]Ejercicio |
| `CLAEMP` | Texto corto | 120 |  | [E]Clave |
| `REGEMP` | Texto corto | 30 |  | Registro mercantil |
| `TOMEMP` | Texto corto | 10 |  | Tomo |
| `FOLEMP` | Texto corto | 10 |  | Folio |
| `HOJEMP` | Texto corto | 10 |  | Hoja |
| `INSEMP` | Texto corto | 10 |  | Inscripción |
| `EMAEMP` | Texto corto | 50 |  | E-mail |
| `WEBEMP` | Texto corto | 50 |  | Web |
| `MOVEMP` | Texto corto | 50 |  | Móvil |
| `ECOEMP` | Texto corto | 50 |  | E-mail comercial |
| `EADEMP` | Texto corto | 50 |  | E-mail administración |
| `ECBEMP` | Texto corto | 50 |  | E-mail contabilidad |
| `AGESEMP` | Entero | 2 |  | Aplicación de gestión |
| `AGETEMP` | Entero | 2 |  | Tipo de aplicación de gestión |
| `ACONEMP` | Entero | 2 |  | Aplicación de contabilidad |
| `ACOTEMP` | Entero | 2 |  | Tipo de aplicación de contabilidad |
| `ALABEMP` | Entero | 2 |  | Aplicación laboral |
| `ATPVEMP` | Entero | 2 |  | Aplicación TPV |
| `AC1EMP` | Entero | 2 |  | Actividad 1 de la empresa |
| `AC2EMP` | Entero | 2 |  | Actividad 2 de la empresa |
| `AC3EMP` | Entero | 2 |  | Actividad 3 de la empresa |
| `FJUEMP` | Entero | 2 |  | Forma jurídica de la empresa |
| `PCOEMP` | Texto corto | 50 |  | Persona de contacto |
| `EJEGEMP` | Texto corto | 4 |  | Ejercicio por defecto en gestión |
| `EJECEMP` | Texto corto | 4 |  | Ejercicio por defecto en contabilidad |
| `EJELEMP` | Texto corto | 4 |  | Ejercicio por defecto en laboral |
| `EJETEMP` | Texto corto | 4 |  | Ejercicio por defecto en tpv |
| `UVDEMP` | Entero | 2 |  | Utilizar varias direcciones |
| `EBAEMP` | Entero | 2 |  | Empresa en baja |
| `TRAEMP` | Entero largo | 4 |  |  |
| `TVEEMP` | Texto corto | 4 |  | Ejercicio de la tienda virtual |
| `TVCEMP` | Texto corto | 120 |  | Clave para la tienda virtual |
| `ACCEMP` | Entero | 2 |  | Acceso a la Empresa del usuario |

---

## F_ENS

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODENS` | Entero | 2 | ✓ | Código |
| `DESENS` | Texto corto | 50 |  | Descripción |
| `CO1ENS` | Texto corto | 25 |  | Descripción componente 1 |
| `FA1ENS` | Texto corto | 3 |  | Familia componente 1 |
| `CO2ENS` | Texto corto | 25 |  | Descripción componente 2 |
| `FA2ENS` | Texto corto | 3 |  | Familia componente 2 |
| `CO3ENS` | Texto corto | 25 |  | Descripción componente 3 |
| `FA3ENS` | Texto corto | 3 |  | Familia componente 3 |
| `CO4ENS` | Texto corto | 25 |  | Descripción componente 4 |
| `FA4ENS` | Texto corto | 3 |  | Familia componente 4 |
| `CO5ENS` | Texto corto | 25 |  | Descripción componente 5 |
| `FA5ENS` | Texto corto | 3 |  | Familia componente 5 |
| `CO6ENS` | Texto corto | 25 |  | Descripción componente 6 |
| `FA6ENS` | Texto corto | 3 |  | Familia componente 6 |
| `CO7ENS` | Texto corto | 25 |  | Descripción componente 7 |
| `FA7ENS` | Texto corto | 3 |  | Familia componente 7 |
| `CO8ENS` | Texto corto | 25 |  | Descripción componente 8 |
| `FA8ENS` | Texto corto | 3 |  | Familia componente 8 |
| `CO9ENS` | Texto corto | 25 |  | Descripción componente 9 |
| `FA9ENS` | Texto corto | 3 |  | Familia componente 9 |
| `CO10ENS` | Texto corto | 25 |  | Descripción componente 10 |
| `FA10ENS` | Texto corto | 3 |  | Familia componente 10 |
| `CO11ENS` | Texto corto | 25 |  | Descripción componente 11 |
| `FA11ENS` | Texto corto | 3 |  | Familia componente 11 |
| `CO12ENS` | Texto corto | 25 |  | Descripción componente 12 |
| `FA12ENS` | Texto corto | 3 |  | Familia componente 12 |
| `CO13ENS` | Texto corto | 25 |  | Descripción componente 13 |
| `FA13ENS` | Texto corto | 3 |  | Familia componente 13 |
| `CO14ENS` | Texto corto | 25 |  | Descripción componente 14 |
| `FA14ENS` | Texto corto | 3 |  | Familia componente 14 |
| `CO15ENS` | Texto corto | 25 |  | Descripción componente 15 |
| `FA15ENS` | Texto corto | 3 |  | Familia componente 15 |
| `CO16ENS` | Texto corto | 25 |  | Descripción componente 16 |
| `FA16ENS` | Texto corto | 3 |  | Familia componente 16 |
| `CO17ENS` | Texto corto | 25 |  | Descripción componente 17 |
| `FA17ENS` | Texto corto | 3 |  | Familia componente 17 |
| `CO18ENS` | Texto corto | 25 |  | Descripción componente 18 |
| `FA18ENS` | Texto corto | 3 |  | Familia componente 18 |
| `CO19ENS` | Texto corto | 25 |  | Descripción componente 19 |
| `FA19ENS` | Texto corto | 3 |  | Familia componente 19 |
| `CO20ENS` | Texto corto | 25 |  | Descripción componente 20 |
| `FA20ENS` | Texto corto | 3 |  | Familia componente 20 |

---

## F_ENT

**Registros:** 52

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `TIPENT` | Texto corto | 1 | ✓ | Nº de serie |
| `CODENT` | Entero largo | 4 | ✓ | [F=000000]Código |
| `REFENT` | Texto corto | 50 |  | Fecha |
| `PROENT` | Entero largo | 4 |  | [F=00000]Proveedor |
| `ESTENT` | Entero | 2 |  | [L=#0;Pte.#1;Fact.]Estado |
| `ALMENT` | Texto corto | 3 |  | Almacén |
| `ALBENT` | Texto corto | 20 |  | Albarán de entrada |
| `CLIENT` | Texto corto | 10 |  | Cliente del proveedor |
| `PNOENT` | Texto corto | 100 |  | Nombre |
| `PDOENT` | Texto corto | 100 |  | Domicilio |
| `PPOENT` | Texto corto | 30 |  | Población |
| `PCPENT` | Texto corto | 10 |  | Cód. Postal |
| `PPRENT` | Texto corto | 40 |  | Provincia |
| `PNIENT` | Texto corto | 18 |  | N.I.F. |
| `TIVENT` | Entero | 2 |  | [L=#0;Con IVA#1;Sin IVA#2;Intracomunitario#3;Importación]Tipo de IVA |
| `REQENT` | Entero largo | 4 |  | [L=#0;No#1;Sí]Recargo de equivalencia |
| `PTEENT` | Texto corto | 20 |  | Teléfono |
| `NET1ENT` | Moneda | 8 |  | Neto 1 |
| `NET2ENT` | Moneda | 8 |  | Neto 2 |
| `NET3ENT` | Moneda | 8 |  | Neto 3 |
| `PDTO1ENT` | Moneda | 8 |  | Porcentaje de descuento 1 |
| `PDTO2ENT` | Moneda | 8 |  | Porcentaje de descuento 2 |
| `PDTO3ENT` | Moneda | 8 |  | Porcentaje de descuento 3 |
| `IDTO1ENT` | Moneda | 8 |  | Importe de descuento 1 |
| `IDTO2ENT` | Moneda | 8 |  | Importe de descuento 2 |
| `IDTO3ENT` | Moneda | 8 |  | Importe de descuento 3 |
| `PPPA1ENT` | Moneda | 8 |  | Porcentaje de descuento 1 |
| `PPPA2ENT` | Moneda | 8 |  | Porcentaje de descuento 2 |
| `PPPA3ENT` | Moneda | 8 |  | Porcentaje de descuento 3 |
| `IPPA1ENT` | Moneda | 8 |  | Importe de pronto pago 1 |
| `IPPA2ENT` | Moneda | 8 |  | Importe de pronto pago 2 |
| `IPPA3ENT` | Moneda | 8 |  | Importe de pronto pago 3 |
| `PPOR1ENT` | Moneda | 8 |  | Porcentaje de portes 1 |
| `PPOR2ENT` | Moneda | 8 |  | Porcentaje de portes 2 |
| `PPOR3ENT` | Moneda | 8 |  | Porcentaje de portes 3 |
| `IPOR1ENT` | Moneda | 8 |  | Importe de portes 1 |
| `IPOR2ENT` | Moneda | 8 |  | Importe de portes 2 |
| `IPOR3ENT` | Moneda | 8 |  | Importe de portes 3 |
| `PFIN1ENT` | Moneda | 8 |  | Porcentaje de financiación 1 |
| `PFIN2ENT` | Moneda | 8 |  | Porcentaje de financiación 2 |
| `PFIN3ENT` | Moneda | 8 |  | Porcentaje de financiación 3 |
| `IFIN1ENT` | Moneda | 8 |  | Importe de financiación 1 |
| `IFIN2ENT` | Moneda | 8 |  | Importe de financiación 2 |
| `IFIN3ENT` | Moneda | 8 |  | Importe de financiación 3 |
| `BAS1ENT` | Moneda | 8 |  | Base imponible 1 |
| `BAS2ENT` | Moneda | 8 |  | Base imponible 2 |
| `BAS3ENT` | Moneda | 8 |  | Base imponible 3 |
| `PIVA1ENT` | Moneda | 8 |  | Porcentaje de impuestos 1 |
| `PIVA2ENT` | Moneda | 8 |  | Porcentaje de impuestos 2 |
| `PIVA3ENT` | Moneda | 8 |  | Porcentaje de impuestos 3 |
| `IIVA1ENT` | Moneda | 8 |  | Importe de impuestos 1 |
| `IIVA2ENT` | Moneda | 8 |  | Importe de impuestos 2 |
| `IIVA3ENT` | Moneda | 8 |  | Importe de impuestos 3 |
| `PREC1ENT` | Moneda | 8 |  | Porcentaje de recargo de equivalencia 1 |
| `PREC2ENT` | Moneda | 8 |  | Porcentaje de recrago de equivalencia 2 |
| `PREC3ENT` | Moneda | 8 |  | Porcentaje de recargo de equivalencia 3 |
| `IREC1ENT` | Moneda | 8 |  | Importe de recargo de equivalencia 1 |
| `IREC2ENT` | Moneda | 8 |  | Importe de recargo de equivalencia 2 |
| `IREC3ENT` | Moneda | 8 |  | Importe de recargo de equivalencia 3 |
| `PRET1ENT` | Moneda | 8 |  | Porcentaje de retención |
| `IRET1ENT` | Moneda | 8 |  | Importe de retención |
| `TOTENT` | Moneda | 8 |  | Total |
| `FOPENT` | Texto corto | 3 |  | Forma de pago |
| `PRTENT` | Entero | 2 |  | [L=#0;Pagados#1;Debidos]Portes |
| `TPOENT` | Texto corto | 30 |  | Portes (texto) |
| `OB1ENT` | Texto corto | 100 |  | Línea 1 de observaciones |
| `OB2ENT` | Texto corto | 100 |  | Línea 2 de observaciones |
| `TRAENT` | Texto corto | 50 |  | Fecha de entrega |
| `HORENT` | Texto corto | 50 |  | Hora de entrega |
| `GP1ENT` | Moneda | 8 |  | Gasto proporcional 1 |
| `GP2ENT` | Moneda | 8 |  | Gasto proporcional 2 |
| `GP3ENT` | Moneda | 8 |  | Gasto proporcional 3 |
| `GP4ENT` | Moneda | 8 |  | Gasto proporcional 4 |
| `COMENT` | Texto largo |  |  | [E]Comentarios después de las líneas de detalle |
| `USUENT` | Entero | 2 |  | Código del usuario que creó el documento |
| `USMENT` | Entero | 2 |  | Código del último usuario que modificó el documento |
| `NET4ENT` | Moneda | 8 |  | Neto (Exento de impuestos) |
| `PDTO4ENT` | Moneda | 8 |  | Porcentaje de descuento (Exento de impuestos) |
| `IDTO4ENT` | Moneda | 8 |  | Importe de descuento (Exento de impuestos) |
| `PPPA4ENT` | Moneda | 8 |  | Porcentaje de pronto pago (Exento de impuestos) |
| `IPPA4ENT` | Moneda | 8 |  | Importe de pronto pago (Exento de impuestos) |
| `PPOR4ENT` | Moneda | 8 |  | Porcentaje de portes (Exento de impuestos) |
| `IPOR4ENT` | Moneda | 8 |  | Importe de portes (Exento de impuestos) |
| `PFIN4ENT` | Moneda | 8 |  | Porcentaje de financiación (Exento de impuestos) |
| `IFIN4ENT` | Moneda | 8 |  | Importe de financiación (Exento de impuestos) |
| `BAS4ENT` | Moneda | 8 |  | Base (Exenta de impuestos) |
| `EMAENT` | Entero | 2 |  | [E]Enviado por e-mail |
| `PASENT` | Texto corto | 150 |  | [E]Permisos y contraseña del documento |
| `PEMENT` | Texto corto | 255 |  | E-mail de destino |
| `PPAENT` | Texto corto | 50 |  | País del proveedor |
| `TIVA1ENT` | Entero | 2 |  | [E]Tipo de iva al que pertenece el neto 1 (0 a 6) |
| `TIVA2ENT` | Entero | 2 |  | [E]Tipo de iva al que pertenece el neto 2 (0 a 6) |
| `TIVA3ENT` | Entero | 2 |  | Fecha última modificación |
| `EERENT` | Entero | 2 |  | [E]Estado envío RETO |

---

## F_ESI

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `DOCESI` | Entero | 2 | ✓ | Documento, 0=Factura emitida;1=Factura |
| `TIPESI` | Texto corto | 1 | ✓ | Serie |
| `CODESI` | Entero largo | 4 | ✓ | Código |
| `LINESI` | Entero | 2 | ✓ | Línea (para los cobros/pagos) |
| `POSESI` | Entero largo | 4 | ✓ | Posición |
| `DESESI` | Texto largo |  |  | Fecha de expedición |
| `REFESI` | Texto corto | 60 |  | Referencia factura recibida |
| `TOTESI` | Moneda | 8 |  | Importe total |
| `TDRESI` | Texto corto | 1 |  | Nº de serie documento rectificado |
| `CDRESI` | Entero largo | 4 |  | Código del documento rectificado |
| `BDRESI` | Moneda | 8 |  | Suma de bases imponibles del documento rectificativo |
| `IIDRESI` | Moneda | 8 |  | Suma de importes de impuestos del documento rectificativo |
| `CLIESI` | Entero largo | 4 |  | Cliente o proveedor |
| `NOMESI` | Texto corto | 100 |  | Razón social |
| `IFIESI` | Entero largo | 4 |  | [L=#0;NIF#1;NIF/IVA (NIF operador |
| `NIFESI` | Texto corto | 18 |  | N.I.F. |
| `PAIESI` | Texto corto | 50 |  | País del cliente |
| `BAS1ESI` | Moneda | 8 |  | Base imponible 1 |
| `BAS2ESI` | Moneda | 8 |  | Base imponible 2 |
| `BAS3ESI` | Moneda | 8 |  | Base imponible 3 |
| `BAS4ESI` | Moneda | 8 |  | Base imponible 4 |
| `PIVA1ESI` | Moneda | 8 |  | Porcentaje de impuestos 1 |
| `PIVA2ESI` | Moneda | 8 |  | Porcentaje de impuestos 2 |
| `PIVA3ESI` | Moneda | 8 |  | Porcentaje de impuestos 3 |
| `IIVA1ESI` | Moneda | 8 |  | Importe de impuestos 1 |
| `IIVA2ESI` | Moneda | 8 |  | Importe de impuestos 2 |
| `IIVA3ESI` | Moneda | 8 |  | Importe de impuestos 3 |
| `PREC1ESI` | Moneda | 8 |  | Porcentaje de recargo de equivalencia 1 |
| `PREC2ESI` | Moneda | 8 |  | Porcentaje de recargo de equivalencia 2 |
| `PREC3ESI` | Moneda | 8 |  | Porcentaje de recargo de equivalencia 3 |
| `IREC1ESI` | Moneda | 8 |  | Importe de recargo de equivalencia 1 |
| `IREC2ESI` | Moneda | 8 |  | Importe de recargo de equivalencia 2 |
| `IREC3ESI` | Moneda | 8 |  | Fecha de cobro |
| `ICOESI` | Moneda | 8 |  | Importe de cobro |
| `MCOESI` | Entero | 2 |  | Medio de cobro/pago |
| `DCOESI` | Texto corto | 34 |  | Cuenta o descripción del medio de cobro/pago |
| `ESTESI` | Entero | 2 |  | Estado: 0=Pendiente de enviar; 1=Enviada |
| `TACESI` | Entero largo | 4 |  | Hora de envío |
| `ESRESI` | Entero | 2 |  | Estado de registro de la factura: 0= Sin presentar, 1=Correcta, 2=Aceptada |
| `CERESI` | Entero | 2 |  | Código del error |
| `DERESI` | Texto corto | 255 |  | Descripción del error |
| `SINESI` | Entero | 2 |  | Situación del inmueble |
| `TFAESI` | Entero | 2 |  | Tipo de factura |
| `CREESI` | Entero | 2 |  | Fecha registro contable |
| `CDEESI` | Moneda | 8 |  | Cuota deducible |
| `IBIESI` | Texto corto | 255 |  | Fecha inicio utilización bien de inversión |
| `PBIESI` | Moneda | 8 |  | Prorrata anual definitiva del bien de inversión |
| `DGLESI` | Entero | 2 |  | Desglose: 0=Factura, 1=Tipo de operación |
| `TOPESI` | Entero | 2 |  | Tipo de operación: 0=Entrega de bienes, 1=Prestación de servicios |
| `RE2ESI` | Texto corto | 60 |  | Referencia factura final |
| `CSVESI` | Texto corto | 16 |  | Código Seguro de Verificación |
| `ISPESI` | Entero | 2 |  | Inversión Sujeto Pasivo |
| `TERESI` | Entero | 2 |  | Emitida por terceros |
| `IRLESI` | Moneda | 8 |  | Importe no sujeto por reglas de localización |
| `IAOESI` | Moneda | 8 |  | Importe no sujeto por art. 7, 14, otros |
| `TFRESI` | Entero largo | 4 |  | Tipo de factura rectificativa |
| `IRDRESI` | Moneda | 8 |  | Fecha de operación |
| `PERESI` | Entero largo | 4 |  | Periodo de presentación |
| `RDFESI` | Entero largo | 4 |  | Factura rectificativa por diferencia (0=NO, 1=SI) |
| `TENESI` | Entero | 2 |  | Emitida por tercero por exigencia normativa |
| `FSIESI` | Entero | 2 |  | Es factura simplificada Art. 7.2 y 7.3 |
| `SIDESI` | Entero | 2 |  | Sin identificación de destinatario |
| `CGEESI` | Entero | 2 |  | Es cambio a gran empresa |
| `CEXESI` | Entero largo | 4 |  | Causas de exención |
| `VDEESI` | Entero largo | 4 |  | Varios destinatarios: 0=No, 1=Si |
| `BI1ESI` | Entero | 2 |  | Bien de inversión 1 |
| `BI2ESI` | Entero | 2 |  | Bien de inversión 2 |
| `BI3ESI` | Entero | 2 |  | Bien de inversión 3 |
| `DPPESI` | Entero | 2 |  | Deducir en periodo posterior |
| `EDPESI` | Entero | 2 |  | Ejercicio de deducción posterior |
| `PDPESI` | Entero | 2 |  | Periodo de deducción posterior |

---

## F_FAB

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `TIPFAB` | Texto corto | 1 | ✓ | Nº de serie |
| `CODFAB` | Entero largo | 4 | ✓ | [F=000000]Código |
| `REFFAB` | Texto corto | 50 |  | Fecha |
| `ESTFAB` | Entero | 2 |  | [F=#0;Pte.#1;Pte. Parcial#2;Cobrada#3;Devuelta]Estado |
| `ALMFAB` | Texto corto | 3 |  | Almacén |
| `AGEFAB` | Entero largo | 4 |  | [F=00000]Agente |
| `PROFAB` | Texto corto | 10 |  | Proveedor del cliente |
| `CLIFAB` | Entero largo | 4 |  | [F=00000]Cliente |
| `CNOFAB` | Texto corto | 100 |  | Nombre |
| `CDOFAB` | Texto corto | 100 |  | Domicilio |
| `CPOFAB` | Texto corto | 30 |  | Población |
| `CCPFAB` | Texto corto | 10 |  | Cód. Postal |
| `CPRFAB` | Texto corto | 40 |  | Provincia |
| `CNIFAB` | Texto corto | 18 |  | N.I.F. |
| `TIVFAB` | Entero | 2 |  | [L=#0;Con IVA#1;Sin IVA#2;Intracomunitario#3;Importación]Tipo de IVA |
| `REQFAB` | Entero largo | 4 |  | [L=#0;No#1;Sí]Recargo de equivalencia |
| `TELFAB` | Texto corto | 20 |  | Teléfono |
| `NET1FAB` | Moneda | 8 |  | Neto 1 |
| `NET2FAB` | Moneda | 8 |  | Neto 2 |
| `NET3FAB` | Moneda | 8 |  | Neto 3 |
| `PDTO1FAB` | Moneda | 8 |  | Porcentaje de descuento 1 |
| `PDTO2FAB` | Moneda | 8 |  | Porcentaje de descuento 2 |
| `PDTO3FAB` | Moneda | 8 |  | Porcentaje de descuento 3 |
| `IDTO1FAB` | Moneda | 8 |  | Importe de descuento 1 |
| `IDTO2FAB` | Moneda | 8 |  | Importe de descuento 2 |
| `IDTO3FAB` | Moneda | 8 |  | Importe de descuento 3 |
| `PPPA1FAB` | Moneda | 8 |  | Porcentaje de pronto pago 1 |
| `PPPA2FAB` | Moneda | 8 |  | Porcentaje de pronto pago 2 |
| `PPPA3FAB` | Moneda | 8 |  | Porcentaje de pronto pago 3 |
| `IPPA1FAB` | Moneda | 8 |  | Importe de pronto pago 1 |
| `IPPA2FAB` | Moneda | 8 |  | Importe de pronto pago 2 |
| `IPPA3FAB` | Moneda | 8 |  | Importe de pronto pago 3 |
| `PPOR1FAB` | Moneda | 8 |  | Porcentaje de portes 1 |
| `PPOR2FAB` | Moneda | 8 |  | Porcentaje de portes 2 |
| `PPOR3FAB` | Moneda | 8 |  | Porcentaje de portes 3 |
| `IPOR1FAB` | Moneda | 8 |  | Importe de portes 1 |
| `IPOR2FAB` | Moneda | 8 |  | Importe de portes 2 |
| `IPOR3FAB` | Moneda | 8 |  | Importe de portes 3 |
| `PFIN1FAB` | Moneda | 8 |  | Porcentaje de financiación 1 |
| `PFIN2FAB` | Moneda | 8 |  | Porcentaje de financiación 2 |
| `PFIN3FAB` | Moneda | 8 |  | Porcentaje de financiación 3 |
| `IFIN1FAB` | Moneda | 8 |  | Importe de financiación 1 |
| `IFIN2FAB` | Moneda | 8 |  | Importe de financiación 2 |
| `IFIN3FAB` | Moneda | 8 |  | Importe de financiación 3 |
| `BAS1FAB` | Moneda | 8 |  | Base imponible 1 |
| `BAS2FAB` | Moneda | 8 |  | Base imponible 2 |
| `BAS3FAB` | Moneda | 8 |  | Base imponible 3 |
| `PIVA1FAB` | Moneda | 8 |  | Porcentaje de impuestos 1 |
| `PIVA2FAB` | Moneda | 8 |  | Porcentaje de impuestos 2 |
| `PIVA3FAB` | Moneda | 8 |  | Porcentaje de impuestos 3 |
| `IIVA1FAB` | Moneda | 8 |  | Importe de impuestos 1 |
| `IIVA2FAB` | Moneda | 8 |  | Importe de impuestos 2 |
| `IIVA3FAB` | Moneda | 8 |  | Importe de impuestos 3 |
| `PREC1FAB` | Moneda | 8 |  | Porcentaje de recargo de equivalencia 1 |
| `PREC2FAB` | Moneda | 8 |  | Porcentaje de recargo de equivalencia 2 |
| `PREC3FAB` | Moneda | 8 |  | Porcentaje de recargo de equivalencia 3 |
| `IREC1FAB` | Moneda | 8 |  | Importe de recargo de equivalencia 1 |
| `IREC2FAB` | Moneda | 8 |  | Importe de recargo de equivalencia 2 |
| `IREC3FAB` | Moneda | 8 |  | Importe de recargo de equivalencia 3 |
| `PRET1FAB` | Moneda | 8 |  | Porcentaje de retención |
| `IRET1FAB` | Moneda | 8 |  | Importe de retención |
| `TOTFAB` | Moneda | 8 |  | Total |
| `FOPFAB` | Texto corto | 3 |  | Forma de pago |
| `PRTFAB` | Entero | 2 |  | [L=#0;Pagados#1;Debidos]Portes |
| `TPOFAB` | Texto corto | 30 |  | Portes (texto) |
| `OB1FAB` | Texto corto | 100 |  | Línea 1 de observaciones |
| `OB2FAB` | Texto corto | 100 |  | Línea 2 de observaciones |
| `TDRFAB` | Texto corto | 1 |  | [E]Tipo del documento rectificado |
| `CDRFAB` | Entero largo | 4 |  | [E]Código del documento rectificado |
| `OBRFAB` | Entero | 2 |  | Código de la dirección de entrega |
| `REPFAB` | Texto corto | 50 |  | Remitido por |
| `EMBFAB` | Texto corto | 50 |  | Embalado por |
| `AATFAB` | Texto corto | 50 |  | A la atención de |
| `REAFAB` | Texto corto | 50 |  | Referencia |
| `PEDFAB` | Texto corto | 50 |  | Fecha de su pedido |
| `COBFAB` | Entero | 2 |  | [E]0:Pendiente,1:Girado |
| `CREFAB` | Entero | 2 |  | [E]Tipo de creacion |
| `TIRFAB` | Texto corto | 1 |  | [E]Tipo del recibo que se crea a partir de esta factura |
| `CORFAB` | Entero largo | 4 |  | [E]Codigo del recibo que se crea a partir de esta factura |
| `TRAFAB` | Entero | 2 |  | [L=#0;No traspasado#1;Traspasado]Traspasado a contabilidad |
| `VENFAB` | Texto corto | 255 |  | [E]Vencimientos de la factura |
| `PRIFAB` | Texto largo |  |  | [E]Campo para anotaciones privadas del documento |
| `ASOFAB` | Texto corto | 255 |  | [E]Documentos externos asociados al documento |
| `IMPFAB` | Texto corto | 1 |  | [E]Impresa |
| `CBAFAB` | Entero | 2 |  | [F=hh:mm]Hora de creación |
| `COMFAB` | Texto largo |  |  | [E]Comentarios para imprimir después de las líneas de detalle |
| `USUFAB` | Entero | 2 |  | Código del usuario que creó el documento |
| `USMFAB` | Entero | 2 |  | Código del último usuario que modificó el documento |
| `FAXFAB` | Texto corto | 25 |  | Fax |
| `NET4FAB` | Moneda | 8 |  | Neto (Exento de impuestos) |
| `PDTO4FAB` | Moneda | 8 |  | Porcentaje de descuento (Exento de impuestos) |
| `IDTO4FAB` | Moneda | 8 |  | Importe de descuento (Exento de impuestos) |
| `PPPA4FAB` | Moneda | 8 |  | Porcentaje de pronto pago (Exento de impuestos) |
| `IPPA4FAB` | Moneda | 8 |  | Importe de pronto pago (Exento de impuestos) |
| `PPOR4FAB` | Moneda | 8 |  | Porcentaje de portes (Exento de impuestos) |
| `IPOR4FAB` | Moneda | 8 |  | Importe de portes (Exento de impuestos) |
| `PFIN4FAB` | Moneda | 8 |  | Porcentaje de financiación (Exento de impuestos) |
| `IFIN4FAB` | Moneda | 8 |  | Importe de financiación (Exento de impuestos) |
| `BAS4FAB` | Moneda | 8 |  | Base (Exenta de impuestos) |
| `EMAFAB` | Entero | 2 |  | [E]Enviado por e-mail |
| `PASFAB` | Texto corto | 150 |  | [E]Permisos y contraseña del documento |
| `CEMFAB` | Texto corto | 255 |  | E-mail de destino |
| `CPAFAB` | Texto corto | 50 |  | País del cliente |
| `BNOFAB` | Texto corto | 40 |  | Nombre del banco |
| `BENFAB` | Texto corto | 4 |  | Banco: Entidad |
| `BOFFAB` | Texto corto | 4 |  | Banco: Oficina |
| `BDCFAB` | Texto corto | 2 |  | Banco: DC |
| `BNUFAB` | Texto corto | 10 |  | Banco: Cuenta |
| `TIVA1FAB` | Entero | 2 |  | [E]Tipo de iva al que pertenece el neto 1 (0 a 6) |
| `TIVA2FAB` | Entero | 2 |  | [E]Tipo de iva al que pertenece el neto 2 (0 a 6) |
| `TIVA3FAB` | Entero | 2 |  | [E]Tipo de iva al que pertenece el neto 3 (0 a 6) |
| `BIBFAB` | Texto corto | 34 |  | Banco: Código IBAN |
| `BICFAB` | Texto corto | 11 |  | Banco: Código BIC |
| `TPVIDFAB` | Texto corto | 16 |  | Identicador de apertura de turno (para TPV) |
| `TERFAB` | Entero | 2 |  | Terminal que lo creó (para TPV) |
| `EDRFAB` | Entero | 2 |  | Fecha última modificación |
| `EERFAB` | Entero | 2 |  | [E]Estado envío RETO |

---

## F_FAC

**Registros:** 1895

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `TIPFAC` | Texto corto | 1 | ✓ | Nº de serie |
| `CODFAC` | Entero largo | 4 | ✓ | [F=000000]Código |
| `REFFAC` | Texto corto | 50 |  | Fecha |
| `ESTFAC` | Entero | 2 |  | [L=#0;Pte.#1;Pte. Parcial#2;Cobrada#3;Devuelta#4;Anulada]Estado |
| `ALMFAC` | Texto corto | 3 |  | Almacén |
| `AGEFAC` | Entero largo | 4 |  | [F=00000]Agente |
| `PROFAC` | Texto corto | 10 |  | Proveedor del cliente |
| `CLIFAC` | Entero largo | 4 |  | [F=00000]Cliente |
| `CNOFAC` | Texto corto | 100 |  | Nombre |
| `CDOFAC` | Texto corto | 100 |  | Domicilio |
| `CPOFAC` | Texto corto | 30 |  | Población |
| `CCPFAC` | Texto corto | 10 |  | Cód. Postal |
| `CPRFAC` | Texto corto | 40 |  | Provincia |
| `CNIFAC` | Texto corto | 18 |  | N.I.F. |
| `TIVFAC` | Entero | 2 |  | [L=#0;Con IVA#1;Sin IVA#2;Intracomunitario#3;Exportación]Tipo de IVA |
| `REQFAC` | Entero largo | 4 |  | [L=#0;No#1;Sí]Recargo de equivalencia |
| `TELFAC` | Texto corto | 20 |  | Teléfono |
| `NET1FAC` | Moneda | 8 |  | Neto 1 |
| `NET2FAC` | Moneda | 8 |  | Neto 2 |
| `NET3FAC` | Moneda | 8 |  | Neto 3 |
| `PDTO1FAC` | Moneda | 8 |  | Porcentaje de descuento 1 |
| `PDTO2FAC` | Moneda | 8 |  | Porcentaje de descuento 2 |
| `PDTO3FAC` | Moneda | 8 |  | Porcentaje de descuento 3 |
| `IDTO1FAC` | Moneda | 8 |  | Importe de descuento 1 |
| `IDTO2FAC` | Moneda | 8 |  | Importe de descuento 2 |
| `IDTO3FAC` | Moneda | 8 |  | Importe de descuento 3 |
| `PPPA1FAC` | Moneda | 8 |  | Porcentaje de pronto pago 1 |
| `PPPA2FAC` | Moneda | 8 |  | Porcentaje de pronto pago 2 |
| `PPPA3FAC` | Moneda | 8 |  | Porcentaje de pronto pago 3 |
| `IPPA1FAC` | Moneda | 8 |  | Importe de pronto pago 1 |
| `IPPA2FAC` | Moneda | 8 |  | Importe de pronto pago 2 |
| `IPPA3FAC` | Moneda | 8 |  | Importe de pronto pago 3 |
| `PPOR1FAC` | Moneda | 8 |  | Porcentaje de portes 1 |
| `PPOR2FAC` | Moneda | 8 |  | Porcentaje de portes 2 |
| `PPOR3FAC` | Moneda | 8 |  | Porcentaje de portes 3 |
| `IPOR1FAC` | Moneda | 8 |  | Importe de portes 1 |
| `IPOR2FAC` | Moneda | 8 |  | Importe de portes 2 |
| `IPOR3FAC` | Moneda | 8 |  | Importe de portes 3 |
| `PFIN1FAC` | Moneda | 8 |  | Porcentaje de financiación 1 |
| `PFIN2FAC` | Moneda | 8 |  | Porcentaje de financiación 2 |
| `PFIN3FAC` | Moneda | 8 |  | Porcentaje de financiación 3 |
| `IFIN1FAC` | Moneda | 8 |  | Importe de financiación 1 |
| `IFIN2FAC` | Moneda | 8 |  | Importe de financiación 2 |
| `IFIN3FAC` | Moneda | 8 |  | Importe de financiación 3 |
| `BAS1FAC` | Moneda | 8 |  | Base imponible 1 |
| `BAS2FAC` | Moneda | 8 |  | Base imponible 2 |
| `BAS3FAC` | Moneda | 8 |  | Base imponible 3 |
| `PIVA1FAC` | Moneda | 8 |  | Porcentaje de impuestos 1 |
| `PIVA2FAC` | Moneda | 8 |  | Porcentaje de impuestos 2 |
| `PIVA3FAC` | Moneda | 8 |  | Porcentaje de impuestos 3 |
| `IIVA1FAC` | Moneda | 8 |  | Importe de impuestos 1 |
| `IIVA2FAC` | Moneda | 8 |  | Importe de impuestos 2 |
| `IIVA3FAC` | Moneda | 8 |  | Importe de impuestos 3 |
| `PREC1FAC` | Moneda | 8 |  | Porcentaje de recargo de equivalencia 1 |
| `PREC2FAC` | Moneda | 8 |  | Porcentaje de recargo de equivalencia 2 |
| `PREC3FAC` | Moneda | 8 |  | Porcentaje de recargo de equivalencia 3 |
| `IREC1FAC` | Moneda | 8 |  | Importe de recargo de equivalencia 1 |
| `IREC2FAC` | Moneda | 8 |  | Importe de recargo de equivalencia 2 |
| `IREC3FAC` | Moneda | 8 |  | Importe de recargo de equivalencia 3 |
| `PRET1FAC` | Moneda | 8 |  | Porcentaje de retención |
| `IRET1FAC` | Moneda | 8 |  | Importe de retención |
| `TOTFAC` | Moneda | 8 |  | Total |
| `FOPFAC` | Texto corto | 3 |  | Forma de pago |
| `PRTFAC` | Entero | 2 |  | [L=#0;Pagados#1;Debidos]Portes |
| `TPOFAC` | Texto corto | 30 |  | Portes (texto) |
| `OB1FAC` | Texto corto | 100 |  | Línea 1 de observaciones |
| `OB2FAC` | Texto corto | 100 |  | Línea 2 de observaciones |
| `TDRFAC` | Texto corto | 1 |  | Nº de serie documento rectificado |
| `CDRFAC` | Entero largo | 4 |  | [F=000000]Código del documento rectificado |
| `OBRFAC` | Entero | 2 |  | Código de la dirección de entrega |
| `REPFAC` | Texto corto | 50 |  | Remitido por |
| `EMBFAC` | Texto corto | 50 |  | Embalado por |
| `AATFAC` | Texto corto | 50 |  | A la antención de |
| `REAFAC` | Texto corto | 50 |  | Referencia |
| `PEDFAC` | Texto corto | 50 |  | Fecha de su pedido |
| `COBFAC` | Entero | 2 |  | [L=#0;Pendiente#1;Girado]Recibo |
| `CREFAC` | Entero | 2 |  | [E]Tipo de creacion |
| `TIRFAC` | Texto corto | 1 |  | [E]Tipo del recibo que se crea a partir de esta factura |
| `CORFAC` | Entero largo | 4 |  | [E]Codigo del recibo que se crea a partir de esta factura |
| `COPFAC` | Entero | 2 |  | Clave de operación |
| `TRAFAC` | Entero | 2 |  | [L=#0;No traspasado#1;Traspasado]Traspasado a contabilidad |
| `VENFAC` | Texto corto | 255 |  | [E]Vencimientos de la factura |
| `PRIFAC` | Texto largo |  |  | [E]CAMPO PARA ANOTACIONES PRIVADAS DEL DOCUMENTO |
| `ASOFAC` | Texto corto | 255 |  | [E]DOCUMENTOS EXTERNOS ASOCIADOS AL DOCUMENTO. |
| `IMPFAC` | Texto corto | 1 |  | [E]Impresa |
| `CBAFAC` | Entero | 2 |  | [F=HH:mm]Hora |
| `COMFAC` | Texto largo |  |  | [E]COMENTARIOS PARA IMPRIMIR AL FINAL DE LAS LÍNEAS DE DETALLE |
| `USUFAC` | Entero | 2 |  | Código del usuario que creó el documento |
| `USMFAC` | Entero | 2 |  | Código del último usuario que modificó el documento |
| `FAXFAC` | Texto corto | 25 |  | Fax |
| `IMGFAC` | Texto corto | 255 |  | [E]IMAGEN DE LA FACTURA |
| `EFEFAC` | Moneda | 8 |  | [E]EFECTIVO COBRADO DE LA FACTURA (PARA TPV) |
| `CAMFAC` | Moneda | 8 |  | [E]CAMBIO DE LA FACTURA |
| `TRNFAC` | Entero | 2 |  | [F=000]Código del transportista |
| `CISFAC` | Texto corto | 20 |  | Nº de expedición 1 (transporte) |
| `TRCFAC` | Texto corto | 20 |  | Nº de expedición 2 (transporte) |
| `NET4FAC` | Moneda | 8 |  | Neto (Exento de impuestos) |
| `PDTO4FAC` | Moneda | 8 |  | Porcentaje de descuento (Exento de impuestos) |
| `IDTO4FAC` | Moneda | 8 |  | Importe de descuento (Exento de impuestos) |
| `PPPA4FAC` | Moneda | 8 |  | Porcentaje de pronto pago (Exento de impuestos) |
| `IPPA4FAC` | Moneda | 8 |  | Importe de pronto pago (Exento de impuestos) |
| `PPOR4FAC` | Moneda | 8 |  | Porcentaje de portes (Exento de impuestos) |
| `IPOR4FAC` | Moneda | 8 |  | Importe de portes (Exento de impuestos) |
| `PFIN4FAC` | Moneda | 8 |  | Porcentaje de financiación (Exento de impuestos) |
| `IFIN4FAC` | Moneda | 8 |  | Importe de financiación (Exento de impuestos) |
| `BAS4FAC` | Moneda | 8 |  | Base (Exenta de impuestos) |
| `EMAFAC` | Entero | 2 |  | [E]Enviado por e-mail |
| `PASFAC` | Texto corto | 150 |  | [E]Permisos y contraseña del documento |
| `TPDFAC` | Moneda | 8 |  | [E]Ticket, porcentaje de descuento |
| `TIDFAC` | Moneda | 8 |  | [E]Ticket, importe de descuento |
| `A1KFAC` | Entero | 2 |  | Código 1KB: Actividad de la factura |
| `CEMFAC` | Texto corto | 255 |  | E-mail de destino |
| `CPAFAC` | Texto corto | 50 |  | País del cliente |
| `BNOFAC` | Texto corto | 40 |  | Nombre del banco |
| `BENFAC` | Texto corto | 4 |  | Banco: Entidad |
| `BOFFAC` | Texto corto | 4 |  | Banco: Oficina |
| `BDCFAC` | Texto corto | 2 |  | Banco: DC |
| `BNUFAC` | Texto corto | 10 |  | Banco: Cuenta |
| `TIVA1FAC` | Entero | 2 |  | [E]Tipo de iva al que pertenece el neto 1 (0 a 6) |
| `TIVA2FAC` | Entero | 2 |  | [E]Tipo de iva al que pertenece el neto 2 (0 a 6) |
| `TIVA3FAC` | Entero | 2 |  | [E]Tipo de iva al que pertenece el neto 3 (0 a 6) |
| `RCCFAC` | Entero | 2 |  | Régimen especial del criterio de caja |
| `BIBFAC` | Texto corto | 34 |  | Banco: Código IBAN |
| `BICFAC` | Texto corto | 11 |  | Banco: Código BIC |
| `EFSFAC` | Moneda | 8 |  | Entregado en segunda forma de pago (para TPV) |
| `EFVFAC` | Moneda | 8 |  | Entregado en vales (para TPV) |
| `CIEFAC` | Entero | 2 |  | Factura con impuestos en país de residencia |
| `GFEFAC` | Entero | 2 |  |  |
| `TIFFAC` | Entero | 2 |  |  |
| `TPVIDFAC` | Texto corto | 16 |  | Identicador de apertura de turno (para TPV) |
| `TERFAC` | Entero | 2 |  | Terminal que lo creó (para TPV) |
| `TFIFAC` | Entero largo | 4 |  | Tarjeta de fidelización usada |
| `TFAFAC` | Moneda | 8 |  | Puntos/Saldo acumulado en esta venta |
| `TREFAC` | Entero | 2 |  | [E]Tipo de retención |
| `CVIFAC` | Entero | 2 |  | [E]Clave de operación intracomunitaria |
| `DEPFAC` | Entero | 2 |  | Fecha de operación |
| `NASFAC` | Texto corto | 15 |  | [E]Nota asociada al documento |
| `EDRFAC` | Entero | 2 |  | [F=0000]Ejercicio del documento rectificado |
| `DEMFAC` | Entero | 2 |  | Fecha última modificación |
| `ITBFAC` | Texto corto | 39 |  | Identificador TicketBAI |
| `STBFAC` | Texto corto | 100 |  | [E]Signatura value (100 primeros caracteres) |
| `DECFAC` | Entero | 2 |  | [E]Departamento contabilidad |
| `SDCFAC` | Entero | 2 |  | [E]Subdepartamento contabilidad |
| `TRZFAC` | Texto largo |  |  | [E]Traza |
| `EERFAC` | Entero | 2 |  | [E]Estado envío RETO |

---

## F_FAM

**Registros:** 862

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODFAM` | Texto corto | 3 | ✓ | Código |
| `DESFAM` | Texto corto | 50 |  | Descripción |
| `SECFAM` | Texto corto | 3 |  | Sección |
| `TEXFAM` | Texto corto | 50 |  | Texto predefinido |
| `CUEFAM` | Texto corto | 10 |  | Cuenta contable (Ventas) |
| `CUCFAM` | Texto corto | 10 |  | Cuenta contable (Compras) |
| `SUWFAM` | Entero | 2 |  | [E]Imagen de la familia |
| `IMFFAM` | Doble | 8 |  | Fecha de la imagen |
| `MPTFAM` | Entero | 2 |  | Mostrar en el panel táctil de TPVSOL |
| `PFIFAM` | Moneda | 8 |  | Puntos tarjeta fidelización |
| `ORDFAM` | Entero largo | 4 |  | Indica el orden para la Tienda Virtual |

---

## F_FCO

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODFCO` | Entero largo | 4 |  | Fecha |
| `ALMFCO` | Texto corto | 3 |  | Almacén |
| `ESTFCO` | Entero | 2 |  | [L=#0;Pte.#;Fabricada]Estado |
| `OBSFCO` | Texto corto | 255 |  | [E] Observaciones |

---

## F_FMO

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODFMO` | Entero largo | 4 |  | Fecha |
| `TURFMO` | Texto corto | 30 |  | Turno |
| `TRAFMO` | Entero | 2 |  | Trabajador |

---

## F_FPA

**Registros:** 11

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODFPA` | Texto corto | 3 | ✓ | Código |
| `DESFPA` | Texto corto | 100 |  | Descripción |
| `VENFPA` | Entero | 2 |  | Nº de vencimientos |
| `PROFPA` | Entero | 2 |  | [E]1:vencimientos proporcionales |
| `DIA1FPA` | Texto corto | 3 |  | Días de vencimiento 1 |
| `DIA2FPA` | Texto corto | 3 |  | Días de vencimiento 2 |
| `DIA3FPA` | Texto corto | 3 |  | Días de vencimiento 3 |
| `DIA4FPA` | Texto corto | 3 |  | Días de vencimiento 4 |
| `DIA5FPA` | Texto corto | 3 |  | Días de vencimiento 5 |
| `DIA6FPA` | Texto corto | 3 |  | Días de vencimiento 6 |
| `PRO1FPA` | Moneda | 8 |  | Proporción de pago 1 |
| `PRO2FPA` | Moneda | 8 |  | Proporción de pago 2 |
| `PRO3FPA` | Moneda | 8 |  | Proporción de pago 3 |
| `PRO4FPA` | Moneda | 8 |  | Proporción de pago 4 |
| `PRO5FPA` | Moneda | 8 |  | Proporción de pago 5 |
| `PRO6FPA` | Moneda | 8 |  | Proporción de pago 6 |
| `SUWFPA` | Entero largo | 4 |  | [E]SUBIR A INTERNET |
| `DEWFPA` | Texto corto | 50 |  | [E]DESCRIPCIÓN WEB |
| `TIPFPA` | Entero | 2 |  | [E] |
| `EFEFPA` | Entero | 2 |  | [E]EFECTIVO 0=NO; 1= SI |
| `MESFPA` | Entero | 2 |  | [E]FORMA DE PAGO POR DIAS O POR MESES |
| `AUDFPA` | Entero | 2 |  | Ajustar al último día del mes |
| `CCOFPA` | Entero | 2 |  | Contrapartida por defecto para cobros |
| `CPAFPA` | Entero | 2 |  | Contrapartida por defecto para pagos |
| `CFEFPA` | Texto corto | 5 |  | Código de la forma de pago en el estándar Factura-e |
| `REMFPA` | Entero | 2 |  | [L=#0;No#1;Sí]Incluir esta forma de pago en procesos de remesado |
| `UETFPA` | Entero | 2 |  | [L=#0;No#1;Sí]Utilizar en TpvSOL |
| `BANFPA` | Entero | 2 |  | Banco |

---

## F_FRD

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `TIPFRD` | Texto corto | 1 | ✓ | Nº de serie |
| `CODFRD` | Entero largo | 4 | ✓ | [F=000000]Código |
| `FACFRD` | Texto corto | 50 |  | Código de factura |
| `REFFRD` | Texto corto | 50 |  | Fecha |
| `PROFRD` | Entero largo | 4 |  | [F=00000]Proveedor |
| `ESTFRD` | Entero | 2 |  | Estado |
| `CLIFRD` | Texto corto | 10 |  | Cliente del proveedor |
| `PNOFRD` | Texto corto | 100 |  | Nombre |
| `PDOFRD` | Texto corto | 100 |  | Domicilio |
| `PPOFRD` | Texto corto | 30 |  | Población |
| `PCPFRD` | Texto corto | 10 |  | Cód. Postal |
| `PPRFRD` | Texto corto | 40 |  | Provincia |
| `PNIFRD` | Texto corto | 18 |  | N.I.F. |
| `TIVFRD` | Entero | 2 |  | [L=#0;Con IVA#1;Sin IVA#2;Intracomunitario#3;Importación]Tipo de IVA |
| `REQFRD` | Entero largo | 4 |  | [L=#0;No#1;Sí]Recargo de equivalencia |
| `PTEFRD` | Texto corto | 20 |  | Teléfono |
| `NET1FRD` | Moneda | 8 |  | Neto 1 |
| `NET2FRD` | Moneda | 8 |  | Neto 2 |
| `NET3FRD` | Moneda | 8 |  | Neto 3 |
| `PDTO1FRD` | Moneda | 8 |  | Porcentaje de descuento 1 |
| `PDTO2FRD` | Moneda | 8 |  | Porcentaje de descuento 2 |
| `PDTO3FRD` | Moneda | 8 |  | Porcentaje de descuento 3 |
| `IDTO1FRD` | Moneda | 8 |  | Importe de descuento 1 |
| `IDTO2FRD` | Moneda | 8 |  | Importe de descuento 2 |
| `IDTO3FRD` | Moneda | 8 |  | Importe de descuento 3 |
| `PPPA1FRD` | Moneda | 8 |  | Porcentaje de pronto pago 1 |
| `PPPA2FRD` | Moneda | 8 |  | Porcentaje de pronto pago 2 |
| `PPPA3FRD` | Moneda | 8 |  | Porcentaje de pronto pago 3 |
| `IPPA1FRD` | Moneda | 8 |  | Importe de pronto pago 1 |
| `IPPA2FRD` | Moneda | 8 |  | Importe de pronto pago 2 |
| `IPPA3FRD` | Moneda | 8 |  | Importe de pronto pago 3 |
| `PPOR1FRD` | Moneda | 8 |  | Porcentaje de portes 1 |
| `PPOR2FRD` | Moneda | 8 |  | Porcentaje de portes 2 |
| `PPOR3FRD` | Moneda | 8 |  | Porcentaje de portes 3 |
| `IPOR1FRD` | Moneda | 8 |  | Importe de portes 1 |
| `IPOR2FRD` | Moneda | 8 |  | Importe de portes 2 |
| `IPOR3FRD` | Moneda | 8 |  | Importe de portes 3 |
| `PFIN1FRD` | Moneda | 8 |  | Porcentaje de financiación 1 |
| `PFIN2FRD` | Moneda | 8 |  | Porcentaje de financiación 2 |
| `PFIN3FRD` | Moneda | 8 |  | Porcentaje de financiación 3 |
| `IFIN1FRD` | Moneda | 8 |  | Importe de financiación 1 |
| `IFIN2FRD` | Moneda | 8 |  | Importe de financiación 2 |
| `IFIN3FRD` | Moneda | 8 |  | Importe de financiación 3 |
| `BAS1FRD` | Moneda | 8 |  | Base imponible 1 |
| `BAS2FRD` | Moneda | 8 |  | Base imponible 2 |
| `BAS3FRD` | Moneda | 8 |  | Base imponible 3 |
| `PIVA1FRD` | Moneda | 8 |  | Porcentaje de impuestos 1 |
| `PIVA2FRD` | Moneda | 8 |  | Porcentaje de impuestos 2 |
| `PIVA3FRD` | Moneda | 8 |  | Porcentaje de impuestos 3 |
| `IIVA1FRD` | Moneda | 8 |  | Importe de impuestos 1 |
| `IIVA2FRD` | Moneda | 8 |  | Importe de impuestos 2 |
| `IIVA3FRD` | Moneda | 8 |  | Importe de impuestos 3 |
| `PREC1FRD` | Moneda | 8 |  | Porcentaje de recargo de equivalencia 1 |
| `PREC2FRD` | Moneda | 8 |  | Porcentaje de recargo de equivalencia 2 |
| `PREC3FRD` | Moneda | 8 |  | Porcentaje de recargo de equivalencia 3 |
| `IREC1FRD` | Moneda | 8 |  | Importe de recargo de equivalencia 1 |
| `IREC2FRD` | Moneda | 8 |  | Importe de recargo de equivalencia 2 |
| `IREC3FRD` | Moneda | 8 |  | Importe de recargo de equivalencia 3 |
| `PRET1FRD` | Moneda | 8 |  | Porcentaje de retención |
| `IRET1FRD` | Moneda | 8 |  | Importe de retención |
| `TOTFRD` | Moneda | 8 |  | Total |
| `FOPFRD` | Texto corto | 3 |  | Forma de pago |
| `OB1FRD` | Texto corto | 100 |  | Línea 1 de observaciones |
| `OB2FRD` | Texto corto | 100 |  | Línea 2 de observaciones |
| `TRAFRD` | Texto corto | 50 |  | Fecha de entrega |
| `HORFRD` | Texto corto | 50 |  | Hora de entrega |
| `PRTFRD` | Entero | 2 |  | [L=#0;Pagados#1;Debidos]Portes |
| `TPOFRD` | Texto corto | 30 |  | Portes (texto) |
| `TPSFRD` | Entero | 2 |  | [L=#0;No traspasado#1;Traspasado]Traspasado a contabilidad |
| `VENFRD` | Texto corto | 255 |  | [E]Vencimientos de la factura recibida |
| `COMFRD` | Texto largo |  |  | [E]Comentarios después de las líneas de detalle |
| `TFDFRD` | Texto corto | 1 |  | [E]TIPO DE LA FACTURA DEVUELTA |
| `CFDFRD` | Entero largo | 4 |  | [E]CODIGO DE LA FACTURA DEVUELTA |
| `ALMFRD` | Texto corto | 3 |  | Almacén |
| `USUFRD` | Entero | 2 |  | Código del usuario que creó el documento |
| `USMFRD` | Entero | 2 |  | Código del último usuario que modificó el documento |
| `NET4FRD` | Moneda | 8 |  | Neto (Exento de impuestos) |
| `PDTO4FRD` | Moneda | 8 |  | Porcentaje de descuento (Exento de impuestos) |
| `IDTO4FRD` | Moneda | 8 |  | Importe de descuento (Exento de impuestos) |
| `PPPA4FRD` | Moneda | 8 |  | Porcentaje de pronto pago (Exento de impuestos) |
| `IPPA4FRD` | Moneda | 8 |  | Importe de pronto pago (Exento de impuestos) |
| `PPOR4FRD` | Moneda | 8 |  | Porcentaje de portes (Exento de impuestos) |
| `IPOR4FRD` | Moneda | 8 |  | Importe de portes (Exento de impuestos) |
| `PFIN4FRD` | Moneda | 8 |  | Porcentaje de financiación (Exento de impuestos) |
| `IFIN4FRD` | Moneda | 8 |  | Importe de financiación (Exento de impuestos) |
| `BAS4FRD` | Moneda | 8 |  | Base (Exenta de impuestos) |
| `EMAFRD` | Entero | 2 |  | [E]Enviado por e-mail |
| `PASFRD` | Texto corto | 150 |  | [E]Permisos y contraseña del documento |
| `PEMFRD` | Texto corto | 255 |  | E-mail de destino |
| `PPAFRD` | Texto corto | 50 |  | País del proveedor |
| `TIVA1FRD` | Entero | 2 |  | [E]Tipo de iva al que pertenece el neto 1 (0 a 6) |
| `TIVA2FRD` | Entero | 2 |  | [E]Tipo de iva al que pertenece el neto 2 (0 a 6) |
| `TIVA3FRD` | Entero | 2 |  | [E]Tipo de iva al que pertenece el neto 3 (0 a 6) |
| `EFDFRD` | Entero | 2 |  | Fecha última modificación |
| `EERFRD` | Entero | 2 |  | [E]Estado envío RETO |

---

## F_FRE

**Registros:** 317

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `TIPFRE` | Texto corto | 1 | ✓ | Nº de serie |
| `CODFRE` | Entero largo | 4 | ✓ | [F=000000]Código |
| `FACFRE` | Texto corto | 50 |  | Código de factura |
| `REFFRE` | Texto corto | 50 |  | Fecha |
| `PROFRE` | Entero largo | 4 |  | [F=00000]Proveedor |
| `ESTFRE` | Entero | 2 |  | [L=#0;Pte.#1;Pag. Parcial#2;Pagada]Estado |
| `CLIFRE` | Texto corto | 10 |  | Cliente del proveedor |
| `PNOFRE` | Texto corto | 100 |  | Nombre |
| `PDOFRE` | Texto corto | 100 |  | Domicilio |
| `PPOFRE` | Texto corto | 30 |  | Población |
| `PCPFRE` | Texto corto | 10 |  | Cód. Postal |
| `PPRFRE` | Texto corto | 40 |  | Provincia |
| `PNIFRE` | Texto corto | 18 |  | N.I.F. |
| `TIVFRE` | Entero | 2 |  | [L=#0;Con IVA#1;Sin IVA#2;Intracomunitario#3;Importación]Tipo de IVA |
| `REQFRE` | Entero largo | 4 |  | [L=#0;No#1;Sí]Recargo de equivalencia |
| `PTEFRE` | Texto corto | 20 |  | Teléfono |
| `NET1FRE` | Moneda | 8 |  | Neto 1 |
| `NET2FRE` | Moneda | 8 |  | Neto 2 |
| `NET3FRE` | Moneda | 8 |  | Neto 3 |
| `PDTO1FRE` | Moneda | 8 |  | Porcentaje de descuento 1 |
| `PDTO2FRE` | Moneda | 8 |  | Porcentaje de descuento 2 |
| `PDTO3FRE` | Moneda | 8 |  | Porcentaje de descuento 3 |
| `IDTO1FRE` | Moneda | 8 |  | Importe de descuento 1 |
| `IDTO2FRE` | Moneda | 8 |  | Importe de descuento 2 |
| `IDTO3FRE` | Moneda | 8 |  | Importe de descuento 3 |
| `PPPA1FRE` | Moneda | 8 |  | Porcentaje de pronto pago 1 |
| `PPPA2FRE` | Moneda | 8 |  | Porcentaje de pronto pago 2 |
| `PPPA3FRE` | Moneda | 8 |  | Porcentaje de pronto pago 3 |
| `IPPA1FRE` | Moneda | 8 |  | Importe de pronto pago 1 |
| `IPPA2FRE` | Moneda | 8 |  | Importe de pronto pago 2 |
| `IPPA3FRE` | Moneda | 8 |  | Importe de pronto pago 3 |
| `PPOR1FRE` | Moneda | 8 |  | Porcentaje de portes 1 |
| `PPOR2FRE` | Moneda | 8 |  | Porcentaje de portes 2 |
| `PPOR3FRE` | Moneda | 8 |  | Porcentaje de portes 3 |
| `IPOR1FRE` | Moneda | 8 |  | Importe de portes 1 |
| `IPOR2FRE` | Moneda | 8 |  | Importe de portes 2 |
| `IPOR3FRE` | Moneda | 8 |  | Importe de portes 3 |
| `PFIN1FRE` | Moneda | 8 |  | Porcentaje de financiación 1 |
| `PFIN2FRE` | Moneda | 8 |  | Porcentaje de financiación 2 |
| `PFIN3FRE` | Moneda | 8 |  | Porcentaje de financiación 3 |
| `IFIN1FRE` | Moneda | 8 |  | Importe de financiación 1 |
| `IFIN2FRE` | Moneda | 8 |  | Importe de financiación 2 |
| `IFIN3FRE` | Moneda | 8 |  | Importe de financiación 3 |
| `BAS1FRE` | Moneda | 8 |  | Base imponible 1 |
| `BAS2FRE` | Moneda | 8 |  | Base imponible 2 |
| `BAS3FRE` | Moneda | 8 |  | Base imponible 3 |
| `PIVA1FRE` | Moneda | 8 |  | Porcentaje de impuestos 1 |
| `PIVA2FRE` | Moneda | 8 |  | Porcentaje de impuestos 2 |
| `PIVA3FRE` | Moneda | 8 |  | Porcentaje de impuestos 3 |
| `IIVA1FRE` | Moneda | 8 |  | Importe de impuestos 1 |
| `IIVA2FRE` | Moneda | 8 |  | Importe de impuestos 2 |
| `IIVA3FRE` | Moneda | 8 |  | Importe de impuestos 3 |
| `PREC1FRE` | Moneda | 8 |  | Porcentaje de recargo de equivalencia 1 |
| `PREC2FRE` | Moneda | 8 |  | Porcentaje de recargo de equivalencia 2 |
| `PREC3FRE` | Moneda | 8 |  | Porcentaje de recargo de equivalencia 3 |
| `IREC1FRE` | Moneda | 8 |  | Importe de recargo de equivalencia 1 |
| `IREC2FRE` | Moneda | 8 |  | Importe de recargo de equivalencia 2 |
| `IREC3FRE` | Moneda | 8 |  | Importe de recargo de equivalencia 3 |
| `PRET1FRE` | Moneda | 8 |  | Porcentaje de retención |
| `IRET1FRE` | Moneda | 8 |  | Importe de retención |
| `TOTFRE` | Moneda | 8 |  | Total |
| `FOPFRE` | Texto corto | 3 |  | Forma de pago |
| `OB1FRE` | Texto corto | 100 |  | Línea 1 de observaciones |
| `OB2FRE` | Texto corto | 100 |  | Línea 2 de observaciones |
| `TRAFRE` | Texto corto | 50 |  | Fecha de entrega |
| `HORFRE` | Texto corto | 50 |  | Hora de entrega |
| `PRTFRE` | Entero | 2 |  | [L=#0;Pagados#1;Debidos]Portes |
| `TPOFRE` | Texto corto | 30 |  | Portes (texto) |
| `COPFRE` | Entero | 2 |  | Fecha de operación |
| `TPSFRE` | Entero | 2 |  | [L=#0;No traspasado#1;Traspasado]Traspasado a contabilidad |
| `VENFRE` | Texto corto | 255 |  | [E]Vencimientos de la factura recibida |
| `COMFRE` | Texto largo |  |  | [E]Comentarios después de las líneas de detalle |
| `DEDFRE` | Entero largo | 4 |  | [L=#0;Deducible#1;No deducible#2;Prorrata]Tipo |
| `USUFRE` | Entero | 2 |  | Código del usuario que creó el documento |
| `USMFRE` | Entero | 2 |  | Código del último ususario que modificó el documento |
| `ALMFRE` | Texto corto | 3 |  | Almacén |
| `NET4FRE` | Moneda | 8 |  | Neto (Exento de impuestos) |
| `PDTO4FRE` | Moneda | 8 |  | Porcentaje de descuento (Exento de impuestos) |
| `IDTO4FRE` | Moneda | 8 |  | Importe de descuento (Exento de impuestos) |
| `PPPA4FRE` | Moneda | 8 |  | Porcentaje de pronto pago (Exento de impuestos) |
| `IPPA4FRE` | Moneda | 8 |  | Importe de pronto pago (Exento de impuestos) |
| `PPOR4FRE` | Moneda | 8 |  | Porcentaje de portes (Exento de impuestos) |
| `IPOR4FRE` | Moneda | 8 |  | Importe de portes (Exento de impuestos) |
| `PFIN4FRE` | Moneda | 8 |  | Porcentaje de financiación (Exento de impuestos) |
| `IFIN4FRE` | Moneda | 8 |  | Importe de financiación (Exento de impuestos) |
| `BAS4FRE` | Moneda | 8 |  | Base (Exenta de impuestos) |
| `EMAFRE` | Entero | 2 |  | [E]Enviado por e-mail |
| `POAFRE` | Entero | 2 |  | [E]Tipo de proveedor (0 = Proveedor, 1 = Acreedor) |
| `BINFRE` | Entero | 2 |  | [L=#0;No#1;Sí]Bien de inversión |
| `PASFRE` | Texto corto | 150 |  | [E]Permisos y contraseña del documento |
| `IMGFRE` | Texto corto | 255 |  | [E]Imagen de la factura recibida |
| `PEMFRE` | Texto corto | 255 |  | E-mail de destino |
| `PPAFRE` | Texto corto | 50 |  | País del proveedor |
| `PDEFRE` | Moneda | 8 |  | Porcentaje de deducción de la factura |
| `TIVA1FRE` | Entero | 2 |  | [E]Tipo de iva al que pertenece el neto 1 (0 a 6) |
| `TIVA2FRE` | Entero | 2 |  | [E]Tipo de iva al que pertenece el neto 2 (0 a 6) |
| `TIVA3FRE` | Entero | 2 |  | [E]Tipo de iva al que pertenece el neto 3 (0 a 6) |
| `TREFRE` | Entero | 2 |  | [E]Tipo de retención de la factura recibida |
| `RCCFRE` | Entero | 2 |  | Régimen especial del criterio de caja |
| `TIFFRE` | Entero | 2 |  | Fecha registro contable |
| `CVIFRE` | Entero | 2 |  | Fecha última modificación |
| `DECFRE` | Entero | 2 |  | [E]Departamento contabilidad |
| `SDCFRE` | Entero | 2 |  | [E]Subdepartamento contabilidad |
| `TRZFRE` | Texto largo |  |  | [E]Traza |
| `EERFRE` | Entero | 2 |  | [E]Estado envío RETO |

---

## F_FTE

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODFTE` | Entero largo | 4 | ✓ | Código |
| `NOMFTE` | Texto corto | 50 |  | Nombre |
| `DOMFTE` | Texto corto | 50 |  | Domicilio |
| `CPOFTE` | Texto corto | 10 |  | Cód. Postal |
| `POBFTE` | Texto corto | 30 |  | Población |
| `PROFTE` | Texto corto | 40 |  | Provincia |
| `NIFFTE` | Texto corto | 18 |  | N.I.F. |
| `TELFTE` | Texto corto | 50 |  | Teléfono |
| `FAXFTE` | Texto corto | 25 |  | Fax |
| `WEBFTE` | Texto corto | 60 |  | Web |
| `EMAFTE` | Texto corto | 60 |  | E-mail |
| `OBSFTE` | Texto largo |  |  | Observaciones |

---

## F_GAG

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODGAG` | Entero largo | 4 | ✓ | Código |
| `AGEGAG` | Entero largo | 4 |  | Fecha |
| `CONGAG` | Texto corto | 50 |  | Concepto |
| `IMPGAG` | Moneda | 8 |  | Importe |
| `CCGGAG` | Texto corto | 3 |  | [E]Código del concepto de gasto del agente |
| `OBSGAG` | Texto largo |  |  | Observaciones |

---

## F_HOJ

**Registros:** 3

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `NOMHOJ` | Texto corto | 15 | ✓ | Nombre |
| `TEXHOJ` | Texto largo |  |  | Texto |
| `TIPHOJ` | Texto corto | 1 |  | [L=#0;Condiciones#1;Presentación]Tipo |
| `MIZHOJ` | Moneda | 8 |  | [E]Margen izquierdo |
| `MDEHOJ` | Moneda | 8 |  | [E]Margen derecho |
| `DESHOJ` | Texto corto | 100 |  | Descripción |

---

## F_HOR

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODHOR` | Entero largo | 4 |  | Fecha del parte |
| `TRAHOR` | Entero largo | 4 |  | Trabajador |

---

## F_ING

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODING` | Entero largo | 4 | ✓ | Código |
| `CAJING` | Entero | 2 |  | Fecha |
| `HORING` | Texto corto | 5 |  | Hora |
| `CONING` | Texto corto | 50 |  | Concepto |
| `IMPING` | Moneda | 8 |  | Importe |
| `CLIING` | Entero largo | 4 |  | Cliente |
| `TPVIDING` | Texto corto | 16 |  | ID apertura TPV |
| `CFAING` | Entero | 2 |  | [E]Apunte caja de FactuSOL |
| `PFAING` | Entero largo | 4 |  | [E]Posición apunte caja de FactuSOL |

---

## F_L34

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODL34` | Entero | 2 | ✓ | Código |
| `POSL34` | Entero | 2 | ✓ | [E]POSICION EN EL FICHERO |
| `REFL34` | Texto corto | 12 |  | Referencia |
| `IMPL34` | Moneda | 8 |  | Importe |
| `ENTL34` | Texto corto | 4 |  | Entidad |
| `OFIL34` | Texto corto | 4 |  | Oficina |
| `DCOL34` | Texto corto | 2 |  | Dígitos de control |
| `CUEL34` | Texto corto | 10 |  | Nº de cuenta |
| `CONL34` | Entero | 2 |  | [E]CONCEPTO DE LA TRANSFERENCIA (1 = NOMINA, 8 = PENSIÓN, 9 = |
| `NOML34` | Texto corto | 36 |  | Nombre del beneficiario |
| `DOML34` | Texto corto | 72 |  | Domiclio del beneficiario) |
| `CPOL34` | Texto corto | 10 |  | Cód. Postal del beneficiario |
| `PLAL34` | Texto corto | 26 |  | Plaza del beneficiario |
| `PROL34` | Texto corto | 36 |  | Provincia |
| `CO1L34` | Texto corto | 140 |  | Concepto 1 |
| `CO2L34` | Texto corto | 36 |  | Concepto 2 |
| `CCOL34` | Texto corto | 10 |  | Cuenta contable |
| `TIPL34` | Entero | 2 |  | Tipo de transferencia |
| `BICL34` | Texto corto | 11 |  | BIC |
| `TCUL34` | Texto corto | 1 |  | Identificador de la cuenta |
| `IDCL34` | Texto corto | 34 |  | Cuenta del beneficiario |
| `CGAL34` | Entero | 2 |  | Clave de gastos |
| `RBEL34` | Texto corto | 13 |  | Referencia para el beneficiario |
| `TTRL34` | Texto corto | 4 |  | Tipo de transferencia |
| `PTRL34` | Entero | 2 |  | Propósito de la transferencia (Otras transferencias SEPA) |
| `PAIL34` | Texto corto | 50 |  | País |
| `BCPL34` | Entero | 2 |  | Balanza de pagos. Clase de pago |
| `BCEL34` | Entero largo | 4 |  | Balanza de pagos. Código estadístico |
| `BPAL34` | Texto corto | 50 |  | Balanza de pagos. País |
| `BNIL34` | Texto corto | 9 |  | Balanza de pagos. NIF |
| `BNOL34` | Texto corto | 8 |  | Balanza de pagos. NOF |
| `BISL34` | Texto corto | 12 |  | Balanza de pagos. Código ISIN |

---

## F_LAC

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `TFALAC` | Texto corto | 1 | ✓ | Nº Serie |
| `CALLAC` | Entero largo | 4 | ✓ | [F=000000]Código |
| `LINLAC` | Entero largo | 4 |  | Fecha |
| `IMPLAC` | Moneda | 8 |  | Importe |
| `CPTLAC` | Texto corto | 40 |  | Concepto |
| `CPALAC` | Entero | 2 |  | [E]Contrapartida(De 0 a 9 : se selecciona de las 10 opciones de la tabla |
| `TRALAC` | Entero | 2 |  | [L=#0;No traspasado#1;Traspasado]Traspasado a contabilidad |
| `ANTLAC` | Entero largo | 4 |  | Anticipo |
| `TIPLAC` | Entero | 2 |  | [L=#0;Cobro#1;Devolución]Tipo |
| `FPALAC` | Texto corto | 3 |  | Forma de pago |
| `OBSLAC` | Texto largo |  |  | Observaciones |
| `MULLAC` | Entero largo | 4 |  | [E]CODIGO DEL COBRO MÚLTIPLE EN EL QUE FUE INCLUIDA ESTA LÍNEA |
| `CAJLAC` | Entero largo | 4 |  | [E]Caja |
| `PCALAC` | Entero largo | 4 |  | [E]Posición de la línea de caja |
| `TPVIDLAC` | Texto corto | 16 |  | Identificador de apertura de turno (para TPV) |
| `TERLAC` | Entero largo | 4 |  | Terminal que ha creado el cobro (para TPV) |

---

## F_LAG

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `AGELAG` | Entero largo | 4 | ✓ | Agente de la liquidación |
| `FILLAG` | Texto corto | 50 | ✓ | Filtros al obtener la liquidación |
| `VENLAG` | Moneda | 8 |  | Importe vendido por el agente |
| `JVELAG` | Moneda | 8 |  | Importe vendido por los agentes de su equipo |
| `COMLAG` | Moneda | 8 |  | Importe comisionado al agente |
| `JCOLAG` | Moneda | 8 |  | Fecha de pago |
| `OBSLAG` | Texto largo |  |  | Observaciones |

---

## F_LAL

**Registros:** 2517

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `TIPLAL` | Texto corto | 1 | ✓ | Nº de serie |
| `CODLAL` | Entero largo | 4 | ✓ | [F=000000]Código |
| `POSLAL` | Entero | 2 | ✓ | Posición de la línea de albarán |
| `ARTLAL` | Texto corto | 13 |  | Artículo |
| `DESLAL` | Texto largo |  |  | Descripción |
| `CANLAL` | Moneda | 8 |  | Descuento 3 |
| `PRELAL` | Moneda | 8 |  | Precio |
| `TOTLAL` | Moneda | 8 |  | Total |
| `IVALAL` | Entero | 2 |  | [L=#0;IVA1AUT#1;IVA2AUT#2;IVA3AUT#3;Exento]Porcentaje de IVA |
| `DOCLAL` | Texto corto | 1 |  | [E]Documento que lo creo: P :pesupuesto, C: Pedido de clientes E:Entrada |
| `DTPLAL` | Texto corto | 1 |  | [E]Tipo del documento que lo creo |
| `DCOLAL` | Entero largo | 4 |  | [E]Código de pedido de cliente que la creo |
| `COSLAL` | Moneda | 8 |  | Precio de costo al crear la línea |
| `BULLAL` | Moneda | 8 |  | Número de bultos |
| `COMLAL` | Moneda | 8 |  | Comisión del agente |
| `MEMLAL` | Texto largo |  |  | Comentarios |
| `EJELAL` | Texto corto | 4 |  | [E]Ejercicio del que proviene la validación de documento. |
| `ALTLAL` | Moneda | 8 |  | Alto |
| `ANCLAL` | Moneda | 8 |  | Ancho |
| `FONLAL` | Moneda | 8 |  | [E]Fecha de consumo preferente |
| `IINLAL` | Entero largo | 4 |  | [E]IVA INCLUIDO EN LA LÍNEA |
| `PIVLAL` | Moneda | 8 |  | [E]PRECIO IVA INCLUIDO EN LA LÍNEA |
| `TIVLAL` | Moneda | 8 |  | [E]TOTAL IVA INCLUIDO EN LA LÍNEA |
| `FIMLAL` | Entero | 2 |  | [E]FORMATO DE IMPRESIÓN DE LA LÍNEA DE DETALLE (0 = SIN FORMATO, |
| `CE1LAL` | Texto corto | 3 |  | Talla |
| `CE2LAL` | Texto corto | 3 |  | Color |
| `IMALAL` | Texto corto | 255 |  | Imagen asociada a la línea |
| `SUMLAL` | Texto corto | 30 |  | Sumatorio donde se debe acumular el valor |
| `NIMLAL` | Entero | 2 |  | [L=#0;Imprimir#1;No imprimir]No imprimir la línea |
| `TCOLAL` | Entero | 2 |  |  |

---

## F_LAN

**Registros:** 18651

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODANT` | Entero largo | 4 |  |  |
| `POSANT` | Entero largo | 4 |  |  |
| `LOTANT` | Texto corto | 100 |  |  |
| `CUPANT` | Texto corto | 100 |  |  |
| `IMPANT` | Doble | 8 |  |  |
| `PORANT` | Doble | 8 |  |  |
| `OPEANT` | Texto corto | 1 |  |  |

---

## F_LCA

**Registros:** 605

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CAJLCA` | Entero largo | 4 | ✓ | Código |
| `POSLCA` | Entero largo | 4 | ✓ | [E]Posición |
| `CONLCA` | Texto corto | 50 |  | Concepto |
| `DEBLCA` | Moneda | 8 |  | Debe |
| `HABLCA` | Moneda | 8 |  | Haber |
| `F6` | Texto corto | 255 |  |  |
| `F7` | Doble | 8 |  |  |
| `F8` | Doble | 8 |  |  |
| `F9` | Texto corto | 255 |  |  |
| `F10` | Moneda | 8 |  |  |
| `F11` | Moneda | 8 |  |  |

---

## F_LCH

**Registros:** 14849

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CHELCH` | Entero largo | 4 | ✓ | Código |
| `POSLCH` | Entero largo | 4 | ✓ | [E]Posición |
| `CONLCH` | Texto corto | 60 |  | Concepto |
| `IMPLCH` | Moneda | 8 |  | Importe |

---

## F_LCO

**Registros:** 1599

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `TFALCO` | Texto corto | 1 | ✓ | Nº Serie |
| `CFALCO` | Entero largo | 4 | ✓ | [F=000000]Código |
| `LINLCO` | Entero largo | 4 |  | Fecha |
| `IMPLCO` | Moneda | 8 |  | Importe |
| `CPTLCO` | Texto corto | 40 |  | Concepto |
| `CPALCO` | Entero | 2 |  | Código de contrapartida |
| `TRALCO` | Entero | 2 |  | [L=#0;No traspasado#1;Traspasado]Traspasado a contabilidad |
| `ANTLCO` | Entero largo | 4 |  | Anticipo |
| `TIPLCO` | Entero | 2 |  | [L=#0;Cobro#1;Devolución]Tipo |
| `FPALCO` | Texto corto | 3 |  | Forma de pago |
| `OBSLCO` | Texto largo |  |  | Observaciones |
| `MULLCO` | Entero largo | 4 |  | [E]CODIGO DEL COBRO MÚLTIPLE EN EL QUE FUE INCLUIDA ESTA LÍNEA |
| `CAJLCO` | Entero largo | 4 |  | [E]Caja |
| `PCALCO` | Entero largo | 4 |  | [E]Posición de la línea de caja |
| `TPVIDLCO` | Texto corto | 16 |  | Identificador de apertura de turno (para TPV) |
| `TERLCO` | Entero largo | 4 |  | Terminal que ha creado el cobro (para TPV) |
| `PROLCO` | Texto corto | 255 |  |  |
| `TIDLCO` | Texto corto | 50 |  |  |

---

## F_LCR

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `TRELCR` | Texto corto | 1 | ✓ | Nº de serie |
| `CRELCR` | Entero largo | 4 | ✓ | [F=000000]Código |
| `POSLCR` | Entero | 2 | ✓ | Nº de vencimiento |
| `LINLCR` | Entero largo | 4 |  | Fecha |
| `IMPLCR` | Moneda | 8 |  | Importe |
| `CPTLCR` | Texto corto | 40 |  | Concepto |
| `CPALCR` | Entero | 2 |  | [E]Contrapartida(De 0 a 9 : se seleeciona de las 10 opciones de la tabla |
| `TRALCR` | Entero | 2 |  | [L=#0;No traspasado#1;Traspasado]Traspasado a contabilidad |
| `ANTLCR` | Entero largo | 4 |  | Anticipo |
| `TIPLCR` | Entero | 2 |  | [L=#0;Cobro#1;Devolución]Tipo |
| `OBSLCR` | Texto largo |  |  | Observaciones |
| `MULLCR` | Entero largo | 4 |  | [E]CODIGO DEL COBRO MÚLTIPLE EN EL QUE FUE INCLUIDA ESTA LÍNEA |
| `CAJLCR` | Entero largo | 4 |  | [E]Caja |
| `PCALCR` | Entero largo | 4 |  | [E]Posición de la línea de caja |

---

## F_LEN

**Registros:** 209

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `TIPLEN` | Texto corto | 1 | ✓ | Nº de serie |
| `CODLEN` | Entero largo | 4 | ✓ | [F=000000]Código |
| `POSLEN` | Entero | 2 | ✓ | [E]Posición de la línea |
| `ARTLEN` | Texto corto | 13 |  | Artículo |
| `DESLEN` | Texto largo |  |  | Descripción |
| `CANLEN` | Moneda | 8 |  | Descuento 3 |
| `PRELEN` | Moneda | 8 |  | Precio |
| `TOTLEN` | Moneda | 8 |  | [L=#0;IVA1AUT#1;IVA2AUT#2;IVA3AUT#3;Exento]Porcentaje de IVA |
| `DOCLEN` | Texto corto | 1 |  | [E]Tipo de documento: V: Pedido de porveedores |
| `DTPLEN` | Texto corto | 1 |  | [E]Tipo de pedido de proveedor que la creo |
| `DCOLEN` | Entero largo | 4 |  | [E]Código de pedido de proveedor que la creo |
| `EJELEN` | Texto corto | 4 |  | [E]Ejercicio |
| `ALTLEN` | Moneda | 8 |  | Alto |
| `ANCLEN` | Moneda | 8 |  | Ancho |
| `FONLEN` | Moneda | 8 |  | Fondo |
| `BULLEN` | Moneda | 8 |  | Bultos |
| `MEMLEN` | Texto largo |  |  | [E]Fecha de consumo preferente |
| `FIMLEN` | Entero | 2 |  | [E]FORMATO DE IMPRESIÓN DE LA LÍNEA DE DETALLE (0 = SIN FORMATO, |
| `CE1LEN` | Texto corto | 3 |  | Talla |
| `CE2LEN` | Texto corto | 3 |  | Color |
| `IMALEN` | Texto corto | 255 |  | Imagen asociada a la línea |
| `SUMLEN` | Texto corto | 30 |  | Sumatorio donde se debe acumular el valor |

---

## F_LFA

**Registros:** 2982

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `TIPLFA` | Texto corto | 1 | ✓ | Nº de serie |
| `CODLFA` | Entero largo | 4 | ✓ | [F=000000]Código |
| `POSLFA` | Entero | 2 | ✓ | [E]Posicion |
| `ARTLFA` | Texto corto | 13 |  | Articulo |
| `DESLFA` | Texto largo |  |  | Descripción |
| `CANLFA` | Moneda | 8 |  | Descuento 3 |
| `PRELFA` | Moneda | 8 |  | Precio |
| `TOTLFA` | Moneda | 8 |  | [L=#0;IVA1AUT#1;IVA2AUT#2;IVA3AUT#3;Exento]Porcentaje de IVA |
| `DOCLFA` | Texto corto | 1 |  | [E]documento que la creo P:presupuesto, C:cliente,A:Albaran |
| `DTPLFA` | Texto corto | 1 |  | [E]Tipo del documento que lo creo |
| `DCOLFA` | Entero largo | 4 |  | [E]Código del documento que lo creo |
| `COSLFA` | Moneda | 8 |  | Precio de costo al crear la línea |
| `BULLFA` | Moneda | 8 |  | Bultos |
| `COMLFA` | Moneda | 8 |  | Comisión del agente |
| `MEMLFA` | Texto largo |  |  | Comentarios |
| `EJELFA` | Texto corto | 4 |  | [E]Ejercicio desde el que se valida |
| `ALTLFA` | Moneda | 8 |  | Alto |
| `ANCLFA` | Moneda | 8 |  | Ancho |
| `FONLFA` | Moneda | 8 |  | [E]Fecha de consumo preferente |
| `IINLFA` | Entero largo | 4 |  | [E]IVA INCLUIDO EN LA LÍNEA |
| `PIVLFA` | Moneda | 8 |  | [E]PRECIO IVA INCLUIDO EN LA LÍNEA |
| `TIVLFA` | Moneda | 8 |  | [E]TOTAL IVA INCLUIDO EN LA LÍNEA |
| `FIMLFA` | Entero | 2 |  | [E]FORMATO DE IMPRESIÓN DE LA LÍNEA DE DETALLE (0 = SIN FORMATO, |
| `CE1LFA` | Texto corto | 3 |  | Talla |
| `CE2LFA` | Texto corto | 3 |  | Color |
| `IMALFA` | Texto corto | 255 |  | Imagen asociada a la línea |
| `SUMLFA` | Texto corto | 30 |  | Sumatorio donde se debe acumular el valor |
| `NIMLFA` | Entero | 2 |  | [L=#0;Imprimir#1;No imprimir]No imprimir la línea |
| `TCOLFA` | Entero | 2 |  |  |

---

## F_LFB

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `TIPLFB` | Texto corto | 1 | ✓ | Nº de serie |
| `CODLFB` | Entero largo | 4 | ✓ | Código |
| `POSLFB` | Entero | 2 | ✓ | [E]Posicion |
| `ARTLFB` | Texto corto | 13 |  | Artículo |
| `DESLFB` | Texto largo |  |  | Descripción |
| `CANLFB` | Moneda | 8 |  | Descuento 3 |
| `PRELFB` | Moneda | 8 |  | Precio |
| `TOTLFB` | Moneda | 8 |  | [L=#0;IVA1AUT#1;IVA2AUT#2;IVA3AUT#3;Exento]Porcentaje de IVA |
| `DOCLFB` | Texto corto | 1 |  | [E]documento que la creo P:presupuesto, C:cliente,A:Albaran |
| `DTPLFB` | Texto corto | 1 |  | [E]Tipo del documento que lo creo |
| `DCOLFB` | Entero largo | 4 |  | [E]Código del documento que lo creo |
| `COSLFB` | Moneda | 8 |  | Precio de costo al crear la línea |
| `BULLFB` | Moneda | 8 |  | Bultos |
| `COMLFB` | Moneda | 8 |  | Comisión del agente |
| `MEMLFB` | Texto largo |  |  | Comentarios |
| `EJELFB` | Texto corto | 4 |  | [E]Ejercicio desde el que se valida |
| `ALTLFB` | Moneda | 8 |  | Alto |
| `ANCLFB` | Moneda | 8 |  | Ancho |
| `FONLFB` | Moneda | 8 |  | [E]Fecha de consumo preferente |
| `IINLFB` | Entero largo | 4 |  | [E]IVA INCLUIDO EN LA LÍNEA |
| `PIVLFB` | Moneda | 8 |  | [E]PRECIO IVA INCLUIDO EN LA LÍNEA |
| `TIVLFB` | Moneda | 8 |  | [E]TOTAL IVA INCLUIDO EN LA LÍNEA |
| `FIMLFB` | Entero | 2 |  | [E]FORMATO DE IMPRESIÓN DE LA LÍNEA DE DETALLE (0 = SIN FORMATO, |
| `CE1LFB` | Texto corto | 3 |  | Talla |
| `CE2LFB` | Texto corto | 3 |  | Color |
| `IMALFB` | Texto corto | 255 |  | Imagen asociada a la línea |
| `SUMLFB` | Texto corto | 30 |  | Sumatorio donde se debe acumular el valor |
| `TCOLFB` | Entero | 2 |  |  |

---

## F_LFC

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODLFC` | Entero largo | 4 | ✓ | Código |
| `POSLFC` | Entero largo | 4 | ✓ | [E]Linea de fabricacion |
| `ARTLFC` | Texto corto | 13 |  | Artículo |
| `DESLFC` | Texto corto | 50 |  | Descripción |
| `CANLFC` | Moneda | 8 |  | Unidades fabricadas |
| `OBSLFC` | Texto largo |  |  | Observaciones |
| `CE1LFC` | Texto corto | 3 |  | Talla |
| `CE2LFC` | Texto corto | 3 |  | Color |

---

## F_LFD

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `TIPLFD` | Texto corto | 1 | ✓ | Nº de serie |
| `CODLFD` | Entero largo | 4 | ✓ | [F=000000]Código |
| `POSLFD` | Entero | 2 | ✓ | [E]Posicion |
| `ARTLFD` | Texto corto | 13 |  | Artículo |
| `DESLFD` | Texto largo |  |  | Descripción |
| `CANLFD` | Moneda | 8 |  | Descuento 3 |
| `PRELFD` | Moneda | 8 |  | Precio |
| `TOTLFD` | Moneda | 8 |  | [L=#0;IVA1AUT#1;IVA2AUT#2;IVA3AUT#3;Exento]Porcentaje de IVA |
| `DTPLFD` | Texto corto | 1 |  | [E]Tipo de documento que la creo |
| `DCOLFD` | Entero largo | 4 |  | [E]Código del documento que la creo |
| `DOCLFD` | Texto corto | 1 |  | [E]Documento que la creo: P: pedido de proveedor, E:entrada |
| `EJELFD` | Texto corto | 4 |  | [E]Ejercicio |
| `ALTLFD` | Moneda | 8 |  | Alto |
| `ANCLFD` | Moneda | 8 |  | Ancho |
| `FONLFD` | Moneda | 8 |  | Fondo |
| `BULLFD` | Moneda | 8 |  | Bultos |
| `MEMLFD` | Texto largo |  |  | [E]Fecha de consumo preferente |
| `FIMLFD` | Entero | 2 |  | [E]FORMATO DE IMPRESIÓN DE LA LÍNEA DE DETALLE (0 = SIN FORMATO, |
| `CE1LFD` | Texto corto | 3 |  | Talla |
| `CE2LFD` | Texto corto | 3 |  | Color |
| `IMALFD` | Texto corto | 255 |  | Imagen asociada a la línea |
| `SUMLFD` | Texto corto | 30 |  | Sumatorio donde se debe acumular el valor |

---

## F_LFL

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODLFL` | Entero largo | 4 | ✓ | Código |
| `POSLFL` | Entero | 2 | ✓ | [E]Posición de la fabricación |
| `LINLFL` | Entero | 2 | ✓ | [E]Línea del componente |
| `ARTLFL` | Texto corto | 13 |  | Artículo |
| `CANLFL` | Moneda | 8 |  | Cantidad |
| `COSLFL` | Moneda | 8 |  | Precio de Costo |
| `CE1LFL` | Texto corto | 3 |  | Talla |
| `CE2LFL` | Texto corto | 3 |  | Color |

---

## F_LFM

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODLFM` | Entero largo | 4 | ✓ | Código |
| `POSLFM` | Entero | 2 | ✓ | [E]POSICION DE LA LÍNEA DE FABRICACIÓN DE MANO DE OBRA |
| `HORLFM` | Moneda | 8 |  | Nº de horas |
| `CONLFM` | Texto largo |  |  | Concepto |
| `THOLFM` | Entero | 2 |  | Tipo de hora |
| `PRELFM` | Moneda | 8 |  | Precio de la hora |
| `FABLFM` | Entero largo | 4 |  | [E]CÓDIGO DE LA FABRICACIÓN ENLAZADA |
| `LINLFM` | Entero largo | 4 |  | [E]LINEA DEL FABRICADO DE LA ORDEN |

---

## F_LFR

**Registros:** 1184

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `TIPLFR` | Texto corto | 1 | ✓ | Nº de serie |
| `CODLFR` | Entero largo | 4 | ✓ | [F=000000]Código |
| `POSLFR` | Entero | 2 | ✓ | [E]Posicion de la fact. de prov. |
| `ARTLFR` | Texto corto | 13 |  | Artículo |
| `DESLFR` | Texto largo |  |  | Descripción |
| `CANLFR` | Moneda | 8 |  | Descuento 3 |
| `PRELFR` | Moneda | 8 |  | Precio |
| `TOTLFR` | Moneda | 8 |  | [L=#0;IVA1AUT#1;IVA2AUT#2;IVA3AUT#3;Exento]Porcentaje de IVA |
| `DTPLFR` | Texto corto | 1 |  | [E]Tipo de documento que la creo |
| `DCOLFR` | Entero largo | 4 |  | [E]Código del documento que la creo |
| `DOCLFR` | Texto corto | 1 |  | [E]Documento que la creo: P: pedido de proveedor, E:entrada |
| `EJELFR` | Texto corto | 4 |  | [E]Ejercicio |
| `ALTLFR` | Moneda | 8 |  | Alto |
| `ANCLFR` | Moneda | 8 |  | Ancho |
| `FONLFR` | Moneda | 8 |  | Fondo |
| `BULLFR` | Moneda | 8 |  | Bultos |
| `MEMLFR` | Texto largo |  |  | [E]Fecha de consumo preferente |
| `FIMLFR` | Entero | 2 |  | [E]FORMATO DE IMPRESIÓN DE LA LÍNEA DE DETALLE (0 = SIN FORMATO, |
| `CE1LFR` | Texto corto | 3 |  | Talla |
| `CE2LFR` | Texto corto | 3 |  | Color |
| `IMALFR` | Texto corto | 255 |  | Imagen asociada a la línea |
| `SUMLFR` | Texto corto | 30 |  | Sumatorio donde se debe acumular el valor |

---

## F_LHO

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODLHO` | Entero largo | 4 | ✓ | [F=000000]Codigo |
| `POSLHO` | Entero | 2 | ✓ | [E]Posición |
| `OFLLHO` | Texto corto | 1 |  | Letra de la obra |
| `OFCLHO` | Entero largo | 4 |  | [F=000000]Código de la obra |
| `OFSLHO` | Entero largo | 4 |  | Subcódigo de la obra |
| `NHOLHO` | Moneda | 8 |  | Nº de horas |
| `PRELHO` | Moneda | 8 |  | Precio de la hora |
| `CCALHO` | Entero | 2 |  | [L=#0;Conforme#1;No conforme]Control de calidad |
| `THOLHO` | Entero | 2 |  | Tipo de hora |
| `CONLHO` | Texto largo |  |  | Concepto |

---

## F_LMA

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODLMA` | Entero largo | 4 | ✓ | [F=000000]Código |
| `POSLMA` | Entero | 2 | ✓ | [E]Posición |
| `ARTLMA` | Texto corto | 13 |  | Artículo |
| `PROLMA` | Entero largo | 4 |  | [F=00000]Proveedor |
| `OFLLMA` | Texto corto | 1 |  | Letra de la orden |
| `OFCLMA` | Entero largo | 4 |  | [F=000000]Código de la orden |
| `OFSLMA` | Entero largo | 4 |  | Subcódigo de la orden |
| `CANLMA` | Moneda | 8 |  | Cantidad |
| `UNILMA` | Texto corto | 6 |  | Unidad de medida |
| `PCOLMA` | Moneda | 8 |  | Precio de costo |
| `DESLMA` | Texto largo |  |  | Descripción del artículo |

---

## F_LPA

**Registros:** 327

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `ARTLPA` | Texto corto | 13 | ✓ | Artículo |
| `PROLPA` | Entero largo | 4 | ✓ | [F=00000]Proveedor |
| `PRELPA` | Moneda | 8 |  | Precio |
| `DT1LPA` | Moneda | 8 |  | Descuento 1 |
| `DT2LPA` | Moneda | 8 |  | Descuento 2 |
| `DT3LPA` | Moneda | 8 |  | Descuento 3 |
| `RESLPA` | Moneda | 8 |  | Resultado |
| `REFLPA` | Texto corto | 30 |  | Referencia |

---

## F_LPC

**Registros:** 2542

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `TIPLPC` | Texto corto | 1 | ✓ | Nº de serie |
| `CODLPC` | Entero largo | 4 | ✓ | [F=000000]Código |
| `POSLPC` | Entero | 2 | ✓ | [E]Posicion de la línea del ped. de cliente |
| `ARTLPC` | Texto corto | 13 |  | Artículo |
| `DESLPC` | Texto largo |  |  | Descripción |
| `CANLPC` | Moneda | 8 |  | Descuento 3 |
| `PRELPC` | Moneda | 8 |  | Precio |
| `TOTLPC` | Moneda | 8 |  | Total |
| `PENLPC` | Moneda | 8 |  | [L=#0;IVA1AUT#1;IVA2AUT#2;IVA3AUT#3;Exento]Porcentaje de IVA |
| `DOCLPC` | Texto corto | 1 |  | [E]Documento que lo creo P: presupuesto |
| `DTPLPC` | Texto corto | 1 |  | [E]Tipo del documento que lo creo |
| `DCOLPC` | Entero largo | 4 |  | [E]Código del documento que lo creo |
| `MEMLPC` | Texto largo |  |  | Comentarios |
| `EJELPC` | Texto corto | 4 |  | [E]Ejercicio |
| `ALTLPC` | Moneda | 8 |  | Alto |
| `ANCLPC` | Moneda | 8 |  | Ancho |
| `FONLPC` | Moneda | 8 |  | [E]Fecha de consumo preferente |
| `IINLPC` | Entero largo | 4 |  | [E]IVA INCLUIDO EN LA LÍNEA |
| `PIVLPC` | Moneda | 8 |  | [E]PRECIO IVA INCLUIDO EN LA LÍNEA |
| `TIVLPC` | Moneda | 8 |  | [E]TOTAL IVA INCLUIDO EN LA LÍNEA |
| `FIMLPC` | Entero | 2 |  | [E]FORMATO DE IMPRESIÓN DE LA LÍNEA DE DETALLE (0 = SIN FORMATO, |
| `COSLPC` | Moneda | 8 |  | Precio de costo al crear la línea |
| `BULLPC` | Moneda | 8 |  | Bultos |
| `CE1LPC` | Texto corto | 3 |  | Talla |
| `CE2LPC` | Texto corto | 3 |  | Color |
| `IMALPC` | Texto corto | 255 |  | Imagen asociada a la línea |
| `SUMLPC` | Texto corto | 30 |  | Sumatorio donde se debe acumular el valor |
| `ANULPC` | Moneda | 8 |  | Cantidad anulada |
| `NIMLPC` | Entero | 2 |  | [L=#0;Imprimir#1;No imprimir]No imprimir la línea |

---

## F_LPD

**Registros:** 18

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODLPD` | Entero | 2 | ✓ | Código |
| `POSLPD` | Entero | 2 | ✓ | [E]POSICION DE LA LÍNEA DE PDA |
| `DESLPD` | Texto corto | 50 |  | Descripción del documento |
| `DOCLPD` | Texto corto | 1 |  | Documento |
| `SERLPD` | Texto corto | 1 |  | Nº de serie |
| `NUELPD` | Entero | 2 |  | [E]PERMITIR CREAR DOCUMENTOS |
| `MODLPD` | Entero | 2 |  | [E]PERMITIR MODIFICAR DOCUMENTOS |
| `BORLPD` | Entero | 2 |  | [E]PERMITIR BORRAR DOCUMENTOS |
| `NEXLPD` | Entero largo | 4 |  | No exportar histórico |
| `CONLPD` | Entero | 2 |  |  |
| `COBLPD` | Entero | 2 |  |  |
| `MIMLPD` | Entero largo | 4 |  |  |

---

## F_LPF

**Registros:** 424

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `TFRLPF` | Texto corto | 1 | ✓ | Nº de serie |
| `CFRLPF` | Entero largo | 4 | ✓ | [F=000000]Código |
| `LINLPF` | Entero largo | 4 | ✓ | [E]Código de la línea |
| `IMPLPF` | Moneda | 8 |  | Fecha |
| `CPTLPF` | Texto corto | 40 |  | Concepto |
| `CPALPF` | Entero | 2 |  | [E]Contrapartida |
| `TRALPF` | Entero | 2 |  | [L=#0;No traspasado#1;Traspasado]Traspasado a contabilidad |
| `CAJLPF` | Entero largo | 4 |  | [E]Caja |
| `PCALPF` | Entero largo | 4 |  | [E]Posición de la línea de caja |
| `MULLPF` | Entero largo | 4 |  |  |
| `ANTLPF` | Entero | 2 |  |  |
| `OBSLPF` | Texto largo |  |  | Observaciones |
| `PROLPF` | Texto corto | 255 |  |  |
| `TIDLPF` | Texto corto | 50 |  |  |

---

## F_LPG

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `PAGLPG` | Entero largo | 4 | ✓ | Código |
| `POSLPG` | Entero largo | 4 | ✓ | [E]Posición |
| `CONLPG` | Texto corto | 60 |  | Concepto |
| `IMPLPG` | Moneda | 8 |  | Importe |

---

## F_LPH

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODLPH` | Entero largo | 4 | ✓ | Código de personal |
| `POSLPH` | Entero largo | 4 |  | Fecha hasta la que se aplica |
| `TCHLPH` | Entero largo | 4 |  | Control horario asociado |

---

## F_LPP

**Registros:** 344

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `TIPLPP` | Texto corto | 1 | ✓ | Nº de serie |
| `CODLPP` | Entero largo | 4 | ✓ | [F=000000]Código |
| `POSLPP` | Entero | 2 | ✓ | [E]Posición |
| `ARTLPP` | Texto corto | 13 |  | Artículo |
| `DESLPP` | Texto largo |  |  | Descripción |
| `CANLPP` | Moneda | 8 |  | Descuento 3 |
| `PRELPP` | Moneda | 8 |  | Precio |
| `TOTLPP` | Moneda | 8 |  | Total |
| `PENLPP` | Moneda | 8 |  | [L=#0;IVA1AUT#1;IVA2AUT#2;IVA3AUT#3;Exento]Porcentaje de IVA |
| `ESTLPP` | Texto corto | 1 |  | [E]Estado |
| `ALTLPP` | Moneda | 8 |  | Alto |
| `ANCLPP` | Moneda | 8 |  | Ancho |
| `FONLPP` | Moneda | 8 |  | Fondo |
| `BULLPP` | Moneda | 8 |  | Bultos |
| `MEMLPP` | Texto largo |  |  | [E]Fecha de consumo preferente |
| `FIMLPP` | Entero | 2 |  | [E]FORMATO DE IMPRESIÓN DE LA LÍNEA DE DETALLE (0 = SIN FORMATO, |
| `CE1LPP` | Texto corto | 3 |  | Talla |
| `CE2LPP` | Texto corto | 3 |  | Color |
| `IMALPP` | Texto corto | 255 |  | Imagen asociada a la línea |
| `SUMLPP` | Texto corto | 30 |  | Sumatorio donde se debe acumular el valor |

---

## F_LPS

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `TIPLPS` | Texto corto | 1 | ✓ | Nº de serie |
| `CODLPS` | Entero largo | 4 | ✓ | [F=000000]Código |
| `POSLPS` | Entero | 2 | ✓ | [E]Posición |
| `ARTLPS` | Texto corto | 13 |  | Artículo |
| `DESLPS` | Texto largo |  |  | Descripción |
| `CANLPS` | Moneda | 8 |  | Descuento 3 |
| `PRELPS` | Moneda | 8 |  | Precio |
| `TOTLPS` | Moneda | 8 |  | [L=#0;IVA1AUT#1;IVA2AUT#2;IVA3AUT#3;Exento]Porcentaje de IVA |
| `MEMLPS` | Texto largo |  |  | Comentarios |
| `ALTLPS` | Moneda | 8 |  | Alto |
| `ANCLPS` | Moneda | 8 |  | Ancho |
| `FONLPS` | Moneda | 8 |  | [E]Fecha de consumo preferente |
| `IINLPS` | Entero largo | 4 |  | [E]IVA INCLUIDO EN LA LÍNEA |
| `PIVLPS` | Moneda | 8 |  | [E]PRECIO IVA INCLUIDO EN LA LÍNEA |
| `TIVLPS` | Moneda | 8 |  | [E]TOTAL IVA INCLUIDO EN LA LÍNEA |
| `FIMLPS` | Entero | 2 |  | [E]FORMATO DE IMPRESIÓN DE LA LÍNEA DE DETALLE (0 = SIN FORMATO, |
| `COSLPS` | Moneda | 8 |  | Precio de costo al crear la línea |
| `CE1LPS` | Texto corto | 3 |  | Talla |
| `CE2LPS` | Texto corto | 3 |  | Color |
| `IMALPS` | Texto corto | 255 |  | Imagen asociada a la línea |
| `BULLPS` | Moneda | 8 |  | Nº de bultos |
| `SUMLPS` | Texto corto | 30 |  | Sumatorio donde se debe acumular el valor |
| `NIMLPS` | Entero | 2 |  | [L=#0;Imprimir#1;No imprimir]No imprimir la línea |

---

## F_LRD

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODLRD` | Entero largo | 4 | ✓ | Código |
| `POSLRD` | Entero | 2 | ✓ | Posición |
| `DIALRD` | Entero | 2 |  | Día |
| `HORLRD` | Moneda | 8 |  | Nº de horas ordinarias |
| `HEXLRD` | Moneda | 8 |  | Nº de horas extraordinarias |
| `HCOLRD` | Moneda | 8 |  | Nº de horas complementarias |
| `HJOLRD` | Moneda | 8 |  | Nº de horas jornada |
| `OBSLRD` | Texto corto | 255 |  | Observaciones |

---

## F_LRE

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `REPLRE` | Entero largo | 4 | ✓ | Representante |
| `PROLRE` | Entero largo | 4 | ✓ | [F=00000]Proveedor |

---

## F_LRL

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODLRL` | Entero largo | 4 | ✓ | Código |
| `POSLRL` | Entero | 2 | ✓ | Posición |
| `LINLRL` | Entero | 2 | ✓ | Línea |
| `TIPLRL` | Entero | 2 |  | [L=#0;Mañana#1;Tarde]Tipo |
| `HENLRL` | Texto corto | 10 |  | Horario. Entrada |
| `HSALRL` | Texto corto | 10 |  | Horario. Salida |
| `HSCLRL` | Texto corto | 10 |  | Horario. Salida comisión de servicios |
| `HFCLRL` | Texto corto | 10 |  | Horario. |
| `WENLRL` | Entero largo | 4 |  |  |
| `WSALRL` | Entero largo | 4 |  |  |
| `SANLRL` | Entero largo | 4 |  |  |
| `OBELRL` | Texto corto | 50 |  |  |
| `OBSLRL` | Texto corto | 50 |  |  |

---

## F_LRM

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODLRM` | Entero largo | 4 | ✓ | Código |
| `POSLRM` | Entero largo | 4 | ✓ | [E]Posición en la remesa |
| `CLILRM` | Entero largo | 4 |  | [F=00000]Cliente |
| `NOMLRM` | Texto corto | 100 |  | Nombre |
| `DOMLRM` | Texto corto | 100 |  | Domicilio |
| `CPOLRM` | Texto corto | 10 |  | Cód. Postal |
| `POBLRM` | Texto corto | 30 |  | Población |
| `PROLRM` | Texto corto | 40 |  | Provincia |
| `NIFLRM` | Texto corto | 18 |  | N.I.F. |
| `ENTLRM` | Texto corto | 4 |  | Entidad |
| `OFILRM` | Texto corto | 4 |  | Oficina |
| `DCOLRM` | Texto corto | 2 |  | Dígitos de control |
| `CUELRM` | Texto corto | 10 |  | Vencimiento |
| `CO1LRM` | Texto corto | 140 |  | Concepto 1 |
| `CO2LRM` | Texto corto | 50 |  | Concepto 2 |
| `CO3LRM` | Texto corto | 50 |  | Concepto 3 |
| `CO4LRM` | Texto corto | 50 |  | Concepto 4 |
| `IM1LRM` | Moneda | 8 |  | Importe 1 |
| `IM2LRM` | Moneda | 8 |  | Importe 2 |
| `IM3LRM` | Moneda | 8 |  | Importe 3 |
| `IM4LRM` | Moneda | 8 |  | Importe 4 |
| `TOTLRM` | Moneda | 8 |  | Total |
| `FTILRM` | Texto largo |  |  | [E]Documentos que originan la línea de la remesa |
| `FCOLRM` | Entero largo | 4 |  | [E]Código de la factura de la línea de remesa |
| `PAILRM` | Texto corto | 50 |  | País |
| `IBALRM` | Texto corto | 34 |  | IBAN |
| `BICLRM` | Texto corto | 11 |  | BIC |
| `MRELRM` | Texto corto | 35 |  | Mandato fecha |
| `MTILRM` | Texto corto | 4 |  | Mandato tipo |
| `PADLRM` | Texto corto | 4 |  | Propósito del adeudo |
| `BCPLRM` | Entero | 2 |  | Balanza de pagos. Clase de pago |
| `BCELRM` | Entero largo | 4 |  | Balanza de pagos. Código estadístico |
| `BPALRM` | Texto corto | 50 |  | Balanza de pagos. País |
| `BNILRM` | Texto corto | 9 |  | Balanza de pagos. NIF |
| `BNOLRM` | Texto corto | 8 |  | Balanza de pagos. NOF |
| `BISLRM` | Texto corto | 12 |  | Balanza de pagos. Código ISIN |

---

## F_LRU

**Registros:** 7

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODLRU` | Texto corto | 3 | ✓ | Código |
| `POSLRU` | Entero largo | 4 | ✓ | [E]Posición |
| `CLILRU` | Entero largo | 4 |  | [F=00000]Cliente |
| `OBRLRU` | Entero | 2 |  | Dirección de entrega del cliente |

---

## F_LSA

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODLSA` | Entero largo | 4 | ✓ | Código |
| `POSLSA` | Entero largo | 4 | ✓ | [E]Linea de fabricacion |
| `ARTLSA` | Texto corto | 13 |  | Artículo |
| `DESLSA` | Texto corto | 50 |  | Descripcion |
| `UNILSA` | Moneda | 8 |  | Unidades fabricadas |
| `CE1LSA` | Texto corto | 3 |  | Talla |
| `CE2LSA` | Texto corto | 3 |  | Color |

---

## F_LTA

**Registros:** 58081

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `TARLTA` | Entero largo | 4 | ✓ | Código |
| `ARTLTA` | Texto corto | 13 | ✓ | Artículo |
| `MARLTA` | Moneda | 8 |  | Margen |
| `PRELTA` | Moneda | 8 |  | Precio |

---

## F_LTC

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `TARLTC` | Entero | 2 | ✓ | Código |
| `ARTLTC` | Texto corto | 13 | ✓ | Artículo |
| `CE1LTC` | Texto corto | 3 | ✓ | Talla |
| `CE2LTC` | Texto corto | 3 | ✓ | Color |
| `MARLTC` | Moneda | 8 |  | Margen |
| `PRELTC` | Moneda | 8 |  | Precio |

---

## F_LTH

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODLTH` | Entero largo | 4 | ✓ | Código |
| `TIPLTH` | Entero largo | 4 | ✓ | Tipo de horario (0=Invierno o anual, 1=Verano) |
| `DIALTH` | Entero largo | 4 | ✓ | Día de la semana |
| `HENLTH` | Texto corto | 5 |  | Hora de entrada |
| `HSALTH` | Texto corto | 5 |  | Hora de salida |
| `HETLTH` | Texto corto | 5 |  | Hora de entrada (por la tarde) |
| `HSTLTH` | Texto corto | 5 |  | Hora de salida (por la tarde) |
| `HJOLTH` | Moneda | 8 |  |  |

---

## F_LTR

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `DOCLTR` | Entero largo | 4 | ✓ | Código |
| `LINLTR` | Entero largo | 4 | ✓ | [E]Línea de traspaso |
| `ARTLTR` | Texto corto | 13 |  | Artículo |
| `CANLTR` | Moneda | 8 |  | Cantidad |
| `LOTLTR` | Texto largo |  |  | [E]FECHA DE CONSUMO DE LA LINEA DE TRASPASO |
| `CE1LTR` | Texto corto | 3 |  | Talla |
| `CE2LTR` | Texto corto | 3 |  | Color |
| `BULLTR` | Moneda | 8 |  | Nº de bultos en el traspaso |

---

## F_MAS

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODMAS` | Texto corto | 35 | ✓ | Código (referencia) del mandato |
| `DESMAS` | Texto corto | 50 |  | Descripción del mandato |
| `CLIMAS` | Entero largo | 4 |  | Fecha de la firma del mandato |
| `TIPMAS` | Entero | 2 |  | Tipo de mandato (recurrente o único) |
| `ESTMAS` | Entero | 2 |  | Estado del mandato (Pendiente, en uso, utilizado) |
| `BANMAS` | Entero largo | 4 |  | Banco del mandato |
| `CUAMAS` | Entero | 2 |  | Tipo de cuaderno SEPA |

---

## F_MAT

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODMAT` | Entero largo | 4 |  | Fecha |
| `TRAMAT` | Entero largo | 4 |  | [F=00000]Trabajador |
| `ALMMAT` | Texto corto | 3 |  | Almacén |
| `TFAMAT` | Texto corto | 1 |  | [E]TIPO DE FACTURA O ALBARAN |
| `CFAMAT` | Entero largo | 4 |  | [E]CODIGO DE LA FACTURA O ALBARAN |
| `TDOMAT` | Entero | 2 |  | [E][L=#0;Factura#1;Albarán]Tipo de documento generado |

---

## F_MCK

**Registros:** 1

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODMCK` | Entero largo | 4 |  | Fecha del control |
| `AGEMCK` | Entero largo | 4 |  | Agente comercial |
| `KMIMCK` | Entero largo | 4 |  | Kilómetros inciales |
| `KMFMCK` | Entero largo | 4 |  | Kilómetros finales |

---

## F_MEN

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODMEN` | Entero largo | 4 |  | Fecha de fin |
| `ME1MEN` | Texto corto | 60 |  | Mensaje 1 |
| `FACMEN` | Byte | 1 |  | [E]factura |
| `ME2MEN` | Texto corto | 60 |  | Mensaje 2 |
| `ALBMEN` | Byte | 1 |  | [E]Albaran |
| `PPRMEN` | Byte | 1 |  | [E]Pedido Proveedor |
| `PCLMEN` | Byte | 1 |  | [E]Pedido cliente |
| `PREMEN` | Byte | 1 |  | [E]Presupuestos |
| `FABMEN` | Byte | 1 |  | [E]Abonos |
| `ME3MEN` | Texto corto | 60 |  | Mensaje 3 |
| `ME4MEN` | Texto corto | 60 |  | Mensaje 4 |
| `LOGMEN` | Texto corto | 255 |  | Logotipo a imprimir con el mensaje |

---

## F_MVI

**Registros:** 2

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODMVI` | Entero largo | 4 |  |  |
| `CLIMVI` | Entero largo | 4 |  |  |
| `AGEMVI` | Entero largo | 4 |  |  |
| `OBSMVI` | Texto largo |  |  |  |
| `MOTMVI` | Entero | 2 |  |  |
| `LOCMVI` | Texto corto | 50 |  |  |
| `OBRMVI` | Entero | 2 |  | Dirección de entrega del cliente |

---

## F_OBR

**Registros:** 5

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CLIOBR` | Entero largo | 4 | ✓ | [F=00000]Cliente |
| `CODOBR` | Entero | 2 | ✓ | Código |
| `NOMOBR` | Texto corto | 100 |  | Nombre |
| `DIROBR` | Texto corto | 100 |  | Dirección |
| `POBOBR` | Texto corto | 30 |  | Población |
| `CPOOBR` | Texto corto | 10 |  | Cód. Postal |
| `PROOBR` | Texto corto | 40 |  | Provincia |
| `TELOBR` | Texto corto | 40 |  | Teléfono |
| `PCOOBR` | Texto corto | 40 |  | Persona de contacto |
| `AGEOBR` | Entero largo | 4 |  | [F=00000]Agente |
| `FADOBR` | Entero | 2 |  | [E]DIRECCION DE OBRA POR DEFECTO; 0 = NO, 1 = ALBARANES, 2 = |
| `LLAOBR` | Texto corto | 1 |  | [E]LLAMANTE |
| `EMAOBR` | Texto corto | 60 |  | E-mail |
| `PAIOBR` | Texto corto | 50 |  | País |
| `REPOBR` | Entero | 2 |  | [E]Dirección predeterminada para la impresión de partes |
| `ACO1OBR` | Texto corto | 20 |  | O.Contable Código DIR3 |
| `ADO1OBR` | Texto corto | 100 |  | O.Contable Domicilio |
| `ACP1OBR` | Texto corto | 10 |  | O.Contable Código postal |
| `APO1OBR` | Texto corto | 30 |  | O.Contable Población |
| `APR1OBR` | Texto corto | 40 |  | O.Contable Provincia |
| `APA1OBR` | Texto corto | 50 |  | O.Contable País |
| `ACO2OBR` | Texto corto | 20 |  | O. Gestor Código DIR3 |
| `ADO2OBR` | Texto corto | 100 |  | O.Gestor Domicilio |
| `ACP2OBR` | Texto corto | 10 |  | O. Gestor Código postal |
| `APO2OBR` | Texto corto | 30 |  | O.Gestor Población |
| `APR2OBR` | Texto corto | 40 |  | O.Gestor Provincia |
| `APA2OBR` | Texto corto | 50 |  | O.Gestor País |
| `ACO3OBR` | Texto corto | 20 |  | U.Tramitadora Código DIR3 |
| `ADO3OBR` | Texto corto | 100 |  | U.Tramitadora Domicilio |
| `ACP3OBR` | Texto corto | 10 |  | U.Tramitadora Código postal |
| `APO3OBR` | Texto corto | 30 |  | U.Tramitadora Población |
| `APR3OBR` | Texto corto | 40 |  | U.Tramitadora Provincia |
| `APA3OBR` | Texto corto | 50 |  | U.Tramitadora País |
| `ACO4OBR` | Texto corto | 20 |  | O.Comprador Código DIR3 |
| `ADO4OBR` | Texto corto | 100 |  | O.Comprador Domicilio |
| `ACP4OBR` | Texto corto | 10 |  | O.Comprador Código postal |
| `APO4OBR` | Texto corto | 30 |  | O.Comprador Población |
| `APR4OBR` | Texto corto | 40 |  | O.Comprador Provincia |
| `APA4OBR` | Texto corto | 50 |  | O.Comprador País |
| `BTROBR` | Entero | 2 |  | Banco para transferencias |
| `EPETOBR` | Texto corto | 13 |  | EDI Código peticionario |
| `ERECOBR` | Texto corto | 13 |  | EDI Código receptor |
| `ECLIOBR` | Texto corto | 13 |  | EDI Código cliente |
| `EPAGOBR` | Texto corto | 13 |  | EDI Código pagador |
| `CROOBR` | Texto corto | 20 |  | [E]Código ROPO |
| `NIROBR` | Texto corto | 18 |  | [E]N.I.F. Destinatario RETO |

---

## F_ODE

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODODE` | Entero largo | 4 |  | Fecha de fin |
| `ARTODE` | Texto corto | 13 |  | Artículo |
| `NARODE` | Texto corto | 50 |  | Descripción del artículo |
| `DESODE` | Moneda | 8 |  | Descuento |
| `TFIODE` | Entero largo | 4 |  | Aplicar a |
| `CE1ODE` | Texto corto | 3 |  | Talla |
| `CE2ODE` | Texto corto | 3 |  | Color |

---

## F_ODT

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODODT` | Entero largo | 4 |  | Fecha de fin |
| `ARTODT` | Texto corto | 13 |  | Artículo |
| `NARODT` | Texto corto | 50 |  | Descripción del artículo |

---

## F_OOB

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODOOB` | Entero largo | 4 | ✓ | Código |
| `ARTOOB` | Texto corto | 13 |  | Artículo |
| `NAROOB` | Texto corto | 50 |  | Descripción del artículo |
| `PREOOB` | Moneda | 8 |  | Precio / Descuento |
| `TOFOOB` | Entero | 2 |  | [L=#0;Precio fijo#1;Descuento]Tipo |

---

## F_OPR

**Registros:** 1

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODOPR` | Entero largo | 4 |  | Fecha de fin |
| `ARTOPR` | Texto corto | 13 |  | Artículo |
| `NAROPR` | Texto corto | 50 |  | Descripción del artículo |
| `PREOPR` | Moneda | 8 |  | Precio |
| `TCLOPR` | Texto corto | 3 |  | Tipo de cliente |

---

## F_ORD

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `LETORD` | Texto corto | 1 | ✓ | Letra |
| `CODORD` | Entero largo | 4 | ✓ | [F=000000]Código |
| `ESTORD` | Entero | 2 |  | [L=#0;Pte.#1;En curso#2;Terminado#3;Fact.#4;Fact.Parcial]Estado |
| `CLIORD` | Entero largo | 4 |  | [F=00000]Cliente |
| `DENORD` | Texto corto | 50 |  | Denominación |
| `DESORD` | Texto largo |  |  | Descripción |
| `LOCORD` | Texto corto | 50 |  | Fecha de conclusión |
| `TTRORD` | Entero | 2 |  | [L=#0;Administración#1;Presupuesto]Tipo de trabajo |
| `MATORD` | Moneda | 8 |  | Importe materiales |
| `MOBORD` | Moneda | 8 |  | Importe mano de obra |
| `PINORD` | Moneda | 8 |  | Porcentaje de índice |
| `IINORD` | Moneda | 8 |  | Índice |
| `COSORD` | Moneda | 8 |  | Coste total |
| `PMAORD` | Moneda | 8 |  | Porcentaje de margen |
| `IMAORD` | Moneda | 8 |  | Margen |
| `PVEORD` | Moneda | 8 |  | Precio venta |
| `FACORD` | Texto corto | 255 |  | Nº de factura |

---

## F_ORE

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODORE` | Entero largo | 4 |  | Fecha de fin |
| `ARTORE` | Texto corto | 13 |  | Artículo |
| `NARORE` | Texto corto | 50 |  | Descripción del artículo |
| `AR1ORE` | Texto corto | 13 |  | Artículo regalo 1 |
| `NA1ORE` | Texto corto | 50 |  | Descripción artículo regalo 1 |
| `AR2ORE` | Texto corto | 13 |  | Artículo regalo 2 |
| `NA2ORE` | Texto corto | 50 |  | Descripción artículo regalo 2 |

---

## F_PAG

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODPAG` | Entero largo | 4 | ✓ | Código |
| `LUGPAG` | Texto corto | 50 |  | Lugar de emisión |
| `IMPPAG` | Moneda | 8 |  | Fecha de vencimiento |
| `PROPAG` | Entero largo | 4 |  | [F=00000]Proveedor/Acreedor |
| `BANPAG` | Entero | 2 |  | Banco |
| `CLAPAG` | Texto corto | 50 |  | Claúsula |
| `ESTPAG` | Entero | 2 |  | [E]0:Sin imprimir,1:Impreso,2:enviado |
| `CHEPAG` | Texto corto | 50 |  | Clave documento |
| `PNOPAG` | Texto corto | 100 |  | Nombre del proveedor |
| `TPAPAG` | Entero | 2 |  | 1=Pagaré;2=Cheque |
| `TRAPAG` | Entero | 2 |  | TRASPASADO A CONTABILIDAD |

---

## F_PCL

**Registros:** 1648

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `TIPPCL` | Texto corto | 1 | ✓ | Nº de serie |
| `CODPCL` | Entero largo | 4 | ✓ | [F=000000]Código |
| `REFPCL` | Texto corto | 50 |  | Fecha |
| `AGEPCL` | Entero largo | 4 |  | [F=00000]Agente |
| `PROPCL` | Texto corto | 10 |  | Proveedor del cliente |
| `CLIPCL` | Entero largo | 4 |  | [F=00000]Cliente |
| `CNOPCL` | Texto corto | 100 |  | Nombre |
| `CDOPCL` | Texto corto | 100 |  | Domicilio |
| `CPOPCL` | Texto corto | 30 |  | Población |
| `CCPPCL` | Texto corto | 10 |  | Cód. Postal |
| `CPRPCL` | Texto corto | 40 |  | Provincia |
| `CNIPCL` | Texto corto | 18 |  | N.I.F. |
| `TIVPCL` | Entero | 2 |  | [L=#0;Con IVA#1;Sin IVA#2;Intracomunitario#3;Importación]Tipo de IVA |
| `REQPCL` | Entero largo | 4 |  | [L=#No#1;Sí]Recargo de equivalencia |
| `TELPCL` | Texto corto | 20 |  | Teléfono |
| `ESTPCL` | Entero | 2 |  | [L=#0;Pte.#1;Pte. Parcial#2;Enviado#3;En almacén#4;Anulado]Estado |
| `ALMPCL` | Texto corto | 3 |  | Almacén |
| `NET1PCL` | Moneda | 8 |  | Neto 1 |
| `NET2PCL` | Moneda | 8 |  | Neto 2 |
| `NET3PCL` | Moneda | 8 |  | Neto 3 |
| `PDTO1PCL` | Moneda | 8 |  | Porcentaje de descuento 1 |
| `PDTO2PCL` | Moneda | 8 |  | Porcentaje de descuento 2 |
| `PDTO3PCL` | Moneda | 8 |  | Porcentaje de descuento 3 |
| `IDTO1PCL` | Moneda | 8 |  | Importe de descuento 1 |
| `IDTO2PCL` | Moneda | 8 |  | Importe de descuento 2 |
| `IDTO3PCL` | Moneda | 8 |  | Importe de descuento 3 |
| `PPPA1PCL` | Moneda | 8 |  | Porcentaje de pronto pago 1 |
| `PPPA2PCL` | Moneda | 8 |  | Porcentaje de pronto pago 2 |
| `PPPA3PCL` | Moneda | 8 |  | Porcentaje de pronto pago 3 |
| `IPPA1PCL` | Moneda | 8 |  | Importe de pronto pago 1 |
| `IPPA2PCL` | Moneda | 8 |  | Importe de pronto pago 2 |
| `IPPA3PCL` | Moneda | 8 |  | Importe de pronto pago 3 |
| `PPOR1PCL` | Moneda | 8 |  | Porcentaje de portes 1 |
| `PPOR2PCL` | Moneda | 8 |  | Porcentaje de portes 2 |
| `PPOR3PCL` | Moneda | 8 |  | Porcentaje de portes 3 |
| `IPOR1PCL` | Moneda | 8 |  | Importe de portes 1 |
| `IPOR2PCL` | Moneda | 8 |  | Importe de portes 2 |
| `IPOR3PCL` | Moneda | 8 |  | Importe de portes 3 |
| `PFIN1PCL` | Moneda | 8 |  | Porcentaje de financiación 1 |
| `PFIN2PCL` | Moneda | 8 |  | Porcentaje de financiación 2 |
| `PFIN3PCL` | Moneda | 8 |  | Porcentaje de financiación 3 |
| `IFIN1PCL` | Moneda | 8 |  | Importe de financiación 1 |
| `IFIN2PCL` | Moneda | 8 |  | Importe de financiación 2 |
| `IFIN3PCL` | Moneda | 8 |  | Importe de financiación 3 |
| `BAS1PCL` | Moneda | 8 |  | Base imponible 1 |
| `BAS2PCL` | Moneda | 8 |  | Base imponible 2 |
| `BAS3PCL` | Moneda | 8 |  | Base imponible 3 |
| `PIVA1PCL` | Moneda | 8 |  | Porcentaje de impuestos 1 |
| `PIVA2PCL` | Moneda | 8 |  | Porcentaje de impuestos 2 |
| `PIVA3PCL` | Moneda | 8 |  | Porcentaje de impuestos 3 |
| `IIVA1PCL` | Moneda | 8 |  | Importe de impuestos 1 |
| `IIVA2PCL` | Moneda | 8 |  | Importe de impuestos 2 |
| `IIVA3PCL` | Moneda | 8 |  | Importe de impuestos 3 |
| `PREC1PCL` | Moneda | 8 |  | Porcentaje de recargo de equivalencia 1 |
| `PREC2PCL` | Moneda | 8 |  | Porcentaje de recargo de equivalencia 2 |
| `PREC3PCL` | Moneda | 8 |  | Porcentaje de recargo de equivalencia 3 |
| `IREC1PCL` | Moneda | 8 |  | Importe de recargo de equivalencia 1 |
| `IREC2PCL` | Moneda | 8 |  | Importe de recargo de equivalencia 2 |
| `IREC3PCL` | Moneda | 8 |  | Importe de recargo de equivalencia 3 |
| `PRET1PCL` | Moneda | 8 |  | Porcentaje de retención |
| `IRET1PCL` | Moneda | 8 |  | Importe de retención |
| `TOTPCL` | Moneda | 8 |  | Total |
| `FOPPCL` | Texto corto | 3 |  | Forma de pago |
| `PENPCL` | Texto corto | 40 |  | Plazo de entrega |
| `PRTPCL` | Entero | 2 |  | [L=#0;Pagados#1;Debidos]Portes |
| `TPOPCL` | Texto corto | 30 |  | Portes (texto) |
| `OB1PCL` | Texto corto | 100 |  | Línea 1 de observaciones |
| `OB2PCL` | Texto corto | 100 |  | Línea 2 de observaciones |
| `OBRPCL` | Entero | 2 |  | Código de la dirección de entrega |
| `PPOPCL` | Texto corto | 40 |  | Pedido por |
| `PRIPCL` | Texto largo |  |  | [E]CAMPO PARA ANOTACIONES PRIVADAS DEL DOCUMENTO |
| `ASOPCL` | Texto corto | 255 |  | [E]DOCUMENTOS EXTERNOS ASOCIADOS AL DOCUMENTO. |
| `COMPCL` | Texto largo |  |  | [E]COMENTARIOS DESPUES DE LÍNEAS DE DETALLE |
| `USUPCL` | Entero | 2 |  | Código del usuario que creó el documento |
| `USMPCL` | Entero | 2 |  | Código del último usuario que creó el documento |
| `FAXPCL` | Texto corto | 25 |  | Fax |
| `NET4PCL` | Moneda | 8 |  | Neto (Exento de impuestos) |
| `PDTO4PCL` | Moneda | 8 |  | Porcentaje de descuento (Exento de impuestos) |
| `IDTO4PCL` | Moneda | 8 |  | Importe de descuento (Exento de impuestos) |
| `PPPA4PCL` | Moneda | 8 |  | Porcentaje de pronto pago (Exento de impuestos) |
| `IPPA4PCL` | Moneda | 8 |  | Importe de pronto pago (Exento de impuestos) |
| `PPOR4PCL` | Moneda | 8 |  | Porcentaje de portes (Exento de impuestos) |
| `IPOR4PCL` | Moneda | 8 |  | Importe de portes (Exento de impuestos) |
| `PFIN4PCL` | Moneda | 8 |  | Porcentaje de financiación (Exento de impuestos) |
| `IFIN4PCL` | Moneda | 8 |  | Importe de financiación (Exento de impuestos) |
| `BAS4PCL` | Moneda | 8 |  | Base imponible (Exento de impuestos) |
| `EMAPCL` | Entero | 2 |  | [E]Enviado por e-mail |
| `PASPCL` | Texto corto | 150 |  | [F=hh:mm]Hora |
| `CEMPCL` | Texto corto | 255 |  | E-mail de destino |
| `CPAPCL` | Texto corto | 50 |  | País del cliente |
| `INCPCL` | Entero | 2 |  | [L=#0;No#1;Sí]Pedido con incidencia |
| `TIVA1PCL` | Entero | 2 |  | [E]Tipo de iva al que pertenece el neto 1 (0 a 6) |
| `TIVA2PCL` | Entero | 2 |  | [E]Tipo de iva al que pertenece el neto 2 (0 a 6) |
| `TIVA3PCL` | Entero | 2 |  | [E]Tipo de iva al que pertenece el neto 3 (0 a 6) |
| `TRNPCL` | Entero | 2 |  | [F=000]Código del transportista |
| `TPVIDPCL` | Texto corto | 16 |  | Identicador de apertura de turno (para TPV) |
| `TERPCL` | Entero | 2 |  | Terminal que lo creó (para TPV) |
| `IMPPCL` | Texto corto | 1 |  | [E]Impresa |
| `CEWPCL` | Entero | 2 |  | Fecha última modificación |

---

## F_PDA

**Registros:** 5

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODPDA` | Entero largo | 4 | ✓ | Código |
| `DESPDA` | Texto corto | 50 |  | Descripción |
| `AGEPDA` | Entero largo | 4 |  | [F=00000]Agente |
| `NOMPDA` | Texto corto | 50 |  | Nombre de la empresa |
| `DENPDA` | Texto corto | 40 |  | Denominación social de la empresa |
| `DOMPDA` | Texto corto | 50 |  | Domicilio de la empresa |
| `CPOPDA` | Texto corto | 10 |  | Cód. Postal de la empresa |
| `POBPDA` | Texto corto | 50 |  | Población de la empresa |
| `PROPDA` | Texto corto | 20 |  | Provincia de la empresa |
| `NIFPDA` | Texto corto | 18 |  | N.I.F. de la empresa |
| `PTEPDA` | Texto corto | 3 |  | Prefijo (teléfono) de la empresa |
| `TELPDA` | Texto corto | 12 |  | Teléfono de la empresa |
| `PFAPDA` | Texto corto | 3 |  | Prefijo (fax) de la empresa |
| `FAXPDA` | Texto corto | 12 |  | Fax de la empresa |
| `PERPDA` | Texto corto | 255 |  | [E]Permisos |
| `PREPDA` | Entero | 2 |  | [E]CAMBIAR PRECIOS DE LA PDA |
| `DTOPDA` | Entero | 2 |  | [E]CAMBIAR DESCUENTO DEL CLIENTE |
| `ARTPDA` | Entero | 2 |  | [E]PERMITIR VENDER ARTÍCULOS SIN CODIFICAR |
| `STOPDA` | Entero | 2 |  | [E]PERMITIR VENDER SIN STOCK |
| `LOTPDA` | Entero | 2 |  | [E]SOLICITAR EL NÚMERO DE LOTE EN LAS LÍNEAS DE DETALLE |
| `ENVPDA` | Entero | 2 |  | [E]SOLICITAR LA FECHA DE ENVASADO EN LAS LÍNEAS DE DETALLE |
| `CONPDA` | Entero | 2 |  | [E]SOLICITAR LA FECHA DE CONSUMO EN LAS LÍNEAS DE DETALLE |
| `PHIPDA` | Entero | 2 |  | [E]PROFUNDIDAD EN EL HISTÓRICO DE MOVIMIENTOS |
| `ALMPDA` | Texto corto | 3 |  | Almacén |
| `TARPDA` | Entero largo | 4 |  | Tarifa de precios de artículos |
| `EFEPDA` | Entero largo | 4 |  | [E]ABRIR LA VENTANA DE EFECTIVO/CAMBIO AL CREAR UNA NOTA |
| `ECLPDA` | Entero largo | 4 |  | [E]EXPORTAR TODOS LOS CLIENTES A LA PDA |
| `AEXPDA` | Entero largo | 4 |  | [E]APLICACIÓN EN EXCLUSIVA |
| `VA1PDA` | Texto corto | 10 |  | Artículo 1 a mostrar |
| `VA2PDA` | Texto corto | 10 |  | Artículo 2 a mostrar |
| `VA3PDA` | Texto corto | 10 |  | Artículo 3 a mostrar |
| `VA4PDA` | Texto corto | 10 |  | Artículo 4 a mostrar |
| `VA5PDA` | Texto corto | 10 |  | Fecha |
| `CCOPDA` | Texto corto | 120 |  | [E]Contraseña |
| `SCLPDA` | Entero | 2 |  |  |
| `PENPDA` | Entero | 2 |  |  |
| `AR1PDA` | Texto corto | 13 |  |  |
| `AR2PDA` | Texto corto | 13 |  |  |
| `AR3PDA` | Texto corto | 13 |  |  |
| `AR4PDA` | Texto corto | 13 |  |  |
| `AR5PDA` | Texto corto | 13 |  |  |
| `AR6PDA` | Texto corto | 13 |  |  |
| `AR7PDA` | Texto corto | 13 |  |  |
| `AR8PDA` | Texto corto | 13 |  |  |
| `AR9PDA` | Texto corto | 13 |  |  |
| `AR10PDA` | Texto corto | 13 |  |  |
| `ACOPDA` | Entero | 2 |  |  |
| `TRNPDA` | Entero | 2 |  |  |
| `VSTPDA` | Entero | 2 |  | Valor de Stock al Exportar (0 Actual - 1 Disponible) |
| `NPCPDA` | Entero | 2 |  | No vender por debajo del precio de costo |
| `CDEPDA` | Texto corto | 120 |  |  |
| `NPFPDA` | Entero | 2 |  | No modificar la fecha de las notas en PREVENTA |
| `GCAPDA` | Entero | 2 |  | Gestionar el cobro de albaranes |
| `RGIPDA` | Entero | 2 |  | Reiniciar gestión al importar en PREVENTA |

---

## F_PER

**Registros:** 4

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODPER` | Entero | 2 | ✓ | Código |
| `NOMPER` | Texto corto | 40 |  | Nombre |
| `DOMPER` | Texto corto | 40 |  | Domicilio |
| `POBPER` | Texto corto | 30 |  | Población |
| `CPOPER` | Texto corto | 10 |  | Cód. Postal |
| `PROPER` | Texto corto | 40 |  | Provincia |
| `DNIPER` | Texto corto | 18 |  | D.N.I. |
| `TELPER` | Texto corto | 50 |  | Fecha de nacimiento |
| `OBSPER` | Texto largo |  |  | Observación |
| `NSSPER` | Texto corto | 25 |  | Nº Seguridad Social |
| `CATPER` | Texto corto | 50 |  | Categoría |
| `TICPER` | Texto corto | 40 |  | Próximo vto. contrato |
| `SUEPER` | Moneda | 8 |  | Sueldo bruto |
| `DEPPER` | Texto corto | 40 |  | Departamento |
| `ESTPER` | Texto corto | 1 |  | [L=#0;Alta#1;Baja]Estado |
| `PR0PER` | Moneda | 8 |  | Precio hora 1 |
| `PR1PER` | Moneda | 8 |  | Precio hora 2 |
| `PR2PER` | Moneda | 8 |  | Precio hora 3 |
| `PR3PER` | Moneda | 8 |  | Precio hora 4 |
| `PR4PER` | Moneda | 8 |  | Precio hora 5 |
| `PR5PER` | Moneda | 8 |  | Precio hora 6 |
| `PR6PER` | Moneda | 8 |  | Precio hora 7 |
| `PR7PER` | Moneda | 8 |  | Precio hora 8 |
| `PR8PER` | Moneda | 8 |  | Precio hora 9 |
| `PR9PER` | Moneda | 8 |  | Precio hora 10 |
| `ENTPER` | Texto corto | 4 |  | Entidad |
| `OFIPER` | Texto corto | 4 |  | Oficina |
| `DCOPER` | Texto corto | 2 |  | Dígitos de control |
| `CUEPER` | Texto corto | 10 |  | Nº de cuenta |
| `BANPER` | Texto corto | 50 |  | Banco |
| `SEXPER` | Entero | 2 |  | [L=#0;Hombre#1;Mujer]Sexo |
| `NHIPER` | Entero | 2 |  | Nº de hijos |
| `ECIPER` | Entero | 2 |  | [L=#0;Soltero/a#1;Casado/a#2;Divorciado/a#3;Viudo/a]Estado civil |
| `MAIPER` | Texto corto | 50 |  | E-mail |
| `CARPER` | Texto corto | 40 |  | Cargo |
| `IBAPER` | Texto corto | 34 |  | IBAN del banco |
| `BICPER` | Texto corto | 11 |  | BIC del banco |
| `RPRPER` | Entero | 2 |  |  |
| `COLPER` | Texto corto | 1 |  |  |
| `FOTPER` | Texto corto | 12 |  |  |
| `IMGPER` | Texto corto | 255 |  | Ruta de la imagen de la fotografía |
| `NFCPER` | Texto corto | 50 |  | Código NFC asociado |
| `PJOPER` | Moneda | 8 |  |  |
| `EANPER` | Texto corto | 13 |  | Código EAN |
| `CENPER` | Texto corto | 40 |  | Centro de trabajo |
| `ADWPER` | Entero | 2 |  |  |

---

## F_PPR

**Registros:** 91

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `TIPPPR` | Texto corto | 1 | ✓ | Nº de serie |
| `CODPPR` | Entero largo | 4 | ✓ | [F=000000]Código |
| `REFPPR` | Texto corto | 50 |  | Fecha |
| `PROPPR` | Entero largo | 4 |  | [F=00000]Proveedor |
| `ESTPPR` | Entero | 2 |  | [L=#0;Pte. de recibir#1;Pte parcial#2;Recibido]Estado |
| `ALMPPR` | Texto corto | 3 |  | Almacén |
| `CLIPPR` | Texto corto | 10 |  | Cliente del proveedor |
| `PNOPPR` | Texto corto | 100 |  | Nombre |
| `PDOPPR` | Texto corto | 100 |  | Domicilio |
| `PPOPPR` | Texto corto | 30 |  | Población |
| `PCPPPR` | Texto corto | 10 |  | Cód. Postal |
| `PPRPPR` | Texto corto | 40 |  | Provincia |
| `PNIPPR` | Texto corto | 18 |  | N.I.F. |
| `TIVPPR` | Entero | 2 |  | [L=#0;Con IVA#1;Sin IVA#2;Intracomunitario#3;Importación]Tipo de IVA |
| `REQPPR` | Entero largo | 4 |  | [L=#No#1;Sí]Recargo de equivalencia |
| `PTEPPR` | Texto corto | 20 |  | Teléfono |
| `NET1PPR` | Moneda | 8 |  | Neto 1 |
| `NET2PPR` | Moneda | 8 |  | Neto 2 |
| `NET3PPR` | Moneda | 8 |  | Neto 3 |
| `PDTO1PPR` | Moneda | 8 |  | Porcentaje de descuento 1 |
| `PDTO2PPR` | Moneda | 8 |  | Porcentaje de descuento 2 |
| `PDTO3PPR` | Moneda | 8 |  | Porcentaje de descuento 3 |
| `IDTO1PPR` | Moneda | 8 |  | Importe de descuento 1 |
| `IDTO2PPR` | Moneda | 8 |  | Importe de descuento 2 |
| `IDTO3PPR` | Moneda | 8 |  | Importe de descuento 3 |
| `PPPA1PPR` | Moneda | 8 |  | Porcentaje de pronto pago 1 |
| `PPPA2PPR` | Moneda | 8 |  | Porcentaje de pronto pago 2 |
| `PPPA3PPR` | Moneda | 8 |  | Porcentaje de pronto pago 3 |
| `IPPA1PPR` | Moneda | 8 |  | Importe de pronto pago 1 |
| `IPPA2PPR` | Moneda | 8 |  | Importe de pronto pago 2 |
| `IPPA3PPR` | Moneda | 8 |  | Importe de pronto pago 3 |
| `PPOR1PPR` | Moneda | 8 |  | Porcentaje de portes 1 |
| `PPOR2PPR` | Moneda | 8 |  | Porcentaje de portes 2 |
| `PPOR3PPR` | Moneda | 8 |  | Porcentaje de portes 3 |
| `IPOR1PPR` | Moneda | 8 |  | Importe de portes 1 |
| `IPOR2PPR` | Moneda | 8 |  | Importe de portes 2 |
| `IPOR3PPR` | Moneda | 8 |  | Importe de portes 3 |
| `PFIN1PPR` | Moneda | 8 |  | Porcentaje de financiación 1 |
| `PFIN2PPR` | Moneda | 8 |  | Porcentaje de financiación 2 |
| `PFIN3PPR` | Moneda | 8 |  | Porcentaje de financiación 3 |
| `IFIN1PPR` | Moneda | 8 |  | Importe de financiación 1 |
| `IFIN2PPR` | Moneda | 8 |  | Importe de financiación 2 |
| `IFIN3PPR` | Moneda | 8 |  | Importe de financiación 3 |
| `BAS1PPR` | Moneda | 8 |  | Base imponible 1 |
| `BAS2PPR` | Moneda | 8 |  | Base imponible 2 |
| `BAS3PPR` | Moneda | 8 |  | Base imponible 3 |
| `PIVA1PPR` | Moneda | 8 |  | Porcentaje de impuestos 1 |
| `PIVA2PPR` | Moneda | 8 |  | Porcentaje de impuestos 2 |
| `PIVA3PPR` | Moneda | 8 |  | Porcentaje de impuestos 3 |
| `IIVA1PPR` | Moneda | 8 |  | Importe de impuestos 1 |
| `IIVA2PPR` | Moneda | 8 |  | Importe de impuestos 2 |
| `IIVA3PPR` | Moneda | 8 |  | Importe de impuestos 3 |
| `PREC1PPR` | Moneda | 8 |  | Porcentaje de recargo de equivalencia 1 |
| `PREC2PPR` | Moneda | 8 |  | Porcentaje de recargo de equivalencia 2 |
| `PREC3PPR` | Moneda | 8 |  | Porcentaje de recargo de equivalencia 3 |
| `IREC1PPR` | Moneda | 8 |  | Importe de recargo de equivalencia 1 |
| `IREC2PPR` | Moneda | 8 |  | Importe de recargo de equivalencia 2 |
| `IREC3PPR` | Moneda | 8 |  | Importe de recargo de equivalencia 3 |
| `PRET1PPR` | Moneda | 8 |  | Porcentaje de retención 1 |
| `IRET1PPR` | Moneda | 8 |  | Importe de retención 1 |
| `TOTPPR` | Moneda | 8 |  | Total |
| `FOPPPR` | Texto corto | 3 |  | Forma de pago |
| `PENPPR` | Texto corto | 40 |  | Plazo de entrega |
| `AATPPR` | Texto corto | 50 |  | A la atención de |
| `PRTPPR` | Moneda | 8 |  | [L=#Pagados#1;Debidos]Portes |
| `TPOPPR` | Texto corto | 30 |  | Portes (texto) |
| `OB1PPR` | Texto corto | 100 |  | Línea 1 de observaciones |
| `OB2PPR` | Texto corto | 100 |  | Línea 2 de observaciones |
| `ENVPPR` | Entero | 2 |  | [E]ENVIADO AL FICHERO DE COMPRAS |
| `COMPPR` | Texto largo |  |  | [E]COMENTARIOS DESPUÉS DE LÍNEAS DE DETALLE |
| `EDOPPR` | Texto corto | 50 |  | Domicilio de la empresa |
| `ECPPPR` | Texto corto | 10 |  | Cód. Postal de la empresa |
| `EPOPPR` | Texto corto | 30 |  | Población de la empresa |
| `EPRPPR` | Texto corto | 40 |  | Provincia de la empresa |
| `ETEPPR` | Texto corto | 20 |  | Teléfono de la empresa |
| `USUPPR` | Entero | 2 |  | Código del usuario que creó el documento |
| `USMPPR` | Entero | 2 |  | Código del último usuario que modificó el documento |
| `NET4PPR` | Moneda | 8 |  | Neto (Exento de impuestos) |
| `PDTO4PPR` | Moneda | 8 |  | Porcentaje de descuento (Exento de impuestos) |
| `IDTO4PPR` | Moneda | 8 |  | Importe de descuento (Exento de impuestos) |
| `PPPA4PPR` | Moneda | 8 |  | Porcentaje de pronto pago (Exento de impuestos) |
| `IPPA4PPR` | Moneda | 8 |  | Importe de pronto pago (Exento de impuestos) |
| `PPOR4PPR` | Moneda | 8 |  | Porcentaje de portes (Exento de impuestos) |
| `IPOR4PPR` | Moneda | 8 |  | Importe de portes (Exento de impuestos) |
| `PFIN4PPR` | Moneda | 8 |  | Porcentaje de financiación (Exento de impuestos) |
| `IFIN4PPR` | Moneda | 8 |  | Importe de financiación (Exento de impuestos) |
| `BAS4PPR` | Moneda | 8 |  | Base (Exenta de impuestos) |
| `EMAPPR` | Entero | 2 |  | [E]Enviado por e-mail |
| `PASPPR` | Texto corto | 150 |  | [E]Permisos y contraseña del documento |
| `PEMPPR` | Texto corto | 255 |  | E-mail de destino |
| `PPAPPR` | Texto corto | 50 |  | País del proveedor |
| `INCPPR` | Entero | 2 |  | [L=#0;No#1;Sí]Pedido con incidencia |
| `TIVA1PPR` | Entero | 2 |  | [E]Tipo de iva al que pertenece el neto 1 (0 a 6) |
| `TIVA2PPR` | Entero | 2 |  | [E]Tipo de iva al que pertenece el neto 2 (0 a 6) |
| `TIVA3PPR` | Entero | 2 |  | Fecha última modificación |

---

## F_PRC

**Registros:** 1

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CLIPRC` | Entero largo | 4 |  | [F=00000]Cliente |
| `ARTPRC` | Texto corto | 13 |  | Artículo |
| `PREPRC` | Moneda | 8 |  | Precio/Descuento |
| `TIPPRC` | Entero | 2 |  | [L=#0;Importe de venta#1;% Descuento]Tipo |
| `AOFPRC` | Entero | 2 |  | [L=#0;Artículo#1;Familia]Aplicar descuento sobre artículo o familia |

---

## F_PRE

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `TIPPRE` | Texto corto | 1 | ✓ | Nº de serie |
| `CODPRE` | Entero largo | 4 | ✓ | [F=000000]Código |
| `REFPRE` | Texto corto | 50 |  | Fecha |
| `AGEPRE` | Entero largo | 4 |  | [F=00000]Agente |
| `PROPRE` | Texto corto | 10 |  | Proveedor del cliente |
| `CLIPRE` | Entero largo | 4 |  | [F=00000]Cliente |
| `CNOPRE` | Texto corto | 100 |  | Nombre |
| `CDOPRE` | Texto corto | 100 |  | Domicilio |
| `CPOPRE` | Texto corto | 30 |  | Población |
| `CCPPRE` | Texto corto | 10 |  | Cód. Postal |
| `CPRPRE` | Texto corto | 40 |  | Provincia |
| `CNIPRE` | Texto corto | 18 |  | N.I.F. |
| `TIVPRE` | Entero | 2 |  | [L=#0;Con IVA#1;Sin IVA#2;Intracomunitario#3;Importación]Tipo de IVA |
| `REQPRE` | Entero largo | 4 |  | [L=#0;No#1;Sí]Recargo de equivalencia |
| `TELPRE` | Texto corto | 20 |  | Teléfono |
| `ALMPRE` | Texto corto | 3 |  | Almacén |
| `NET1PRE` | Moneda | 8 |  | Neto 1 |
| `NET2PRE` | Moneda | 8 |  | Neto 2 |
| `NET3PRE` | Moneda | 8 |  | Neto 3 |
| `PDTO1PRE` | Moneda | 8 |  | Porcentaje de descuento 1 |
| `PDTO2PRE` | Moneda | 8 |  | Porcentaje de descuento 2 |
| `PDTO3PRE` | Moneda | 8 |  | Porcentaje de descuento 3 |
| `IDTO1PRE` | Moneda | 8 |  | Importe de descuento 1 |
| `IDTO2PRE` | Moneda | 8 |  | Importe de descuento 2 |
| `IDTO3PRE` | Moneda | 8 |  | Importe de descuento 3 |
| `PPPA1PRE` | Moneda | 8 |  | Porcentaje de pronto pago 1 |
| `PPPA2PRE` | Moneda | 8 |  | Porcentaje de pronto pago 2 |
| `PPPA3PRE` | Moneda | 8 |  | Porcentaje de pronto pago 3 |
| `IPPA1PRE` | Moneda | 8 |  | Importe de pronto pago 1 |
| `IPPA2PRE` | Moneda | 8 |  | Importe de pronto pago 2 |
| `IPPA3PRE` | Moneda | 8 |  | Importe de pronto pago 3 |
| `PPOR1PRE` | Moneda | 8 |  | Porcentaje de portes 1 |
| `PPOR2PRE` | Moneda | 8 |  | Porcentaje de portes 2 |
| `PPOR3PRE` | Moneda | 8 |  | Porcentaje de portes 3 |
| `IPOR1PRE` | Moneda | 8 |  | Importe de portes 1 |
| `IPOR2PRE` | Moneda | 8 |  | Importe de portes 2 |
| `IPOR3PRE` | Moneda | 8 |  | Importe de portes 3 |
| `PFIN1PRE` | Moneda | 8 |  | Porcentaje de financiación 1 |
| `PFIN2PRE` | Moneda | 8 |  | Porcentaje de financiación 2 |
| `PFIN3PRE` | Moneda | 8 |  | Porcentaje de financiación 3 |
| `IFIN1PRE` | Moneda | 8 |  | Importe de financiación 1 |
| `IFIN2PRE` | Moneda | 8 |  | Importe de financiación 2 |
| `IFIN3PRE` | Moneda | 8 |  | Importe de financiación 3 |
| `BAS1PRE` | Moneda | 8 |  | Base imponible 1 |
| `BAS2PRE` | Moneda | 8 |  | Base imponible 2 |
| `BAS3PRE` | Moneda | 8 |  | Base imponible 3 |
| `PIVA1PRE` | Moneda | 8 |  | Porcentaje de impuestos 1 |
| `PIVA2PRE` | Moneda | 8 |  | Porcentaje de impuestos 2 |
| `PIVA3PRE` | Moneda | 8 |  | Porcentaje de impuestos 3 |
| `IIVA1PRE` | Moneda | 8 |  | Importe de impuestos 1 |
| `IIVA2PRE` | Moneda | 8 |  | Importe de impuestos 2 |
| `IIVA3PRE` | Moneda | 8 |  | Importe de impuestos 3 |
| `PREC1PRE` | Moneda | 8 |  | Porcentaje de recargo de equivalencia 1 |
| `PREC2PRE` | Moneda | 8 |  | Porcentaje de recargo de equivalencia 2 |
| `PREC3PRE` | Moneda | 8 |  | Porcentaje de recargo de equivalencia 3 |
| `IREC1PRE` | Moneda | 8 |  | Importe de recargo de equivalencia 1 |
| `IREC2PRE` | Moneda | 8 |  | Importe de recargo de equivalencia 2 |
| `IREC3PRE` | Moneda | 8 |  | Importe de recargo de equivalencia 3 |
| `PRET1PRE` | Moneda | 8 |  | Porcentaje de retención |
| `IRET1PRE` | Moneda | 8 |  | Importe de retención |
| `TOTPRE` | Moneda | 8 |  | Total |
| `FOPPRE` | Texto corto | 3 |  | Forma de pago |
| `PENPRE` | Texto corto | 100 |  | Plazo de entrega |
| `TVAPRE` | Texto corto | 50 |  | Tiempo de validez |
| `PRTPRE` | Entero | 2 |  | [L=#0;Pagados#1;Debidos]Portes |
| `TPOPRE` | Texto corto | 30 |  | Portes (texto) |
| `OB1PRE` | Texto corto | 100 |  | Línea 1 de observaciones |
| `OB2PRE` | Texto corto | 100 |  | Línea 2 de observaciones |
| `OBRPRE` | Entero | 2 |  | Código de la dirección de entrega |
| `ESTPRE` | Entero | 2 |  | [L=#0;Pte.#1;Aceptado#2;Rechazado#3;Enviado]Estado |
| `IPRPRE` | Entero largo | 4 |  | [E][L=#0;No#1;Sí]Imprimir presupuesto |
| `I1HPRE` | Entero largo | 4 |  | [E][L=#0;No#1;Sí]Imprimir hoja de condiciones |
| `IFPPRE` | Entero | 2 |  | [E]Imprimir factura proforma |
| `I2HPRE` | Entero largo | 4 |  | [E][L=#0;No#1;Sí]Imprimir hoja de presentación |
| `I1NPRE` | Texto corto | 15 |  | [E]Código de la hoja de condiciones |
| `I2NPRE` | Texto corto | 15 |  | [E]Código de la hoja de presentación |
| `PRIPRE` | Texto largo |  |  | [E]Anotaciones privadas del documento |
| `ASOPRE` | Texto corto | 255 |  | [E]Documentos externos asociados al documento |
| `COMPRE` | Texto largo |  |  | [E]Comentarios después de las líneas de detalle |
| `USUPRE` | Entero | 2 |  | Código del usuario que creó el documento |
| `USMPRE` | Entero | 2 |  | Código del último usuario que modificó el documento |
| `FAXPRE` | Texto corto | 25 |  | Fax |
| `IMGPRE` | Texto corto | 255 |  | [E]Imagen de la factura |
| `NET4PRE` | Moneda | 8 |  | Neto (Exento de impuestos) |
| `PDTO4PRE` | Moneda | 8 |  | Porcentaje de descuento (Exento de impuestos) |
| `IDTO4PRE` | Moneda | 8 |  | Importe de descuento (Exento de impuestos) |
| `PPPA4PRE` | Moneda | 8 |  | Porcentaje de pronto pago (Exento de impuestos) |
| `IPPA4PRE` | Moneda | 8 |  | Importe de pronto pago (Exento de impuestos) |
| `PPOR4PRE` | Moneda | 8 |  | Porcentaje de portes (Exento de impuestos) |
| `IPOR4PRE` | Moneda | 8 |  | Importe de portes (Exento de impuestos) |
| `PFIN4PRE` | Moneda | 8 |  | Porcentaje de financiación (Exento de impuestos) |
| `IFIN4PRE` | Moneda | 8 |  | Importe de financiación (Exento de impuestos) |
| `BAS4PRE` | Moneda | 8 |  | Base (Exenta de impuestos) |
| `EMAPRE` | Entero | 2 |  | [E]Enviado por e-mail |
| `PASPRE` | Texto corto | 150 |  | [F=hh:mm]Hora |
| `CARPRE` | Texto corto | 255 |  | Carpeta asociada |
| `CEMPRE` | Texto corto | 255 |  | E-mail de destino |
| `CPAPRE` | Texto corto | 50 |  | País del cliente |
| `TIVA1PRE` | Entero | 2 |  | [E]Tipo de iva al que pertenece el neto 1 (0 a 6) |
| `TIVA2PRE` | Entero | 2 |  | [E]Tipo de iva al que pertenece el neto 2 (0 a 6) |
| `TIVA3PRE` | Entero | 2 |  | [E]Tipo de iva al que pertenece el neto 3 (0 a 6) |
| `TPVIDPRE` | Texto corto | 16 |  | Identicador de apertura de turno (para TPV) |
| `TERPRE` | Entero | 2 |  | Fecha última modificación |

---

## F_PRO

**Registros:** 235

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODPRO` | Entero largo | 4 | ✓ | [F=00000]Código |
| `CCOPRO` | Entero largo | 4 |  | Código contabilidad |
| `TIPPRO` | Entero | 2 |  | [L=#0;Proveedor#1;Acreedor]Tipo |
| `NIFPRO` | Texto corto | 18 |  | N.I.F. |
| `NOFPRO` | Texto corto | 100 |  | Nombre fiscal |
| `NOCPRO` | Texto corto | 100 |  | Nombre comercial |
| `DOMPRO` | Texto corto | 100 |  | Domicilio |
| `POBPRO` | Texto corto | 30 |  | Población |
| `CPOPRO` | Texto corto | 10 |  | Cód. Postal |
| `PROPRO` | Texto corto | 40 |  | Provincia |
| `TELPRO` | Texto corto | 30 |  | Teléfono |
| `FAXPRO` | Texto corto | 25 |  | Fax |
| `PCOPRO` | Texto corto | 50 |  | Persona de contacto |
| `BANPRO` | Texto corto | 40 |  | Banco |
| `ENTPRO` | Texto corto | 4 |  | Entidad |
| `OFIPRO` | Texto corto | 4 |  | Oficina |
| `DCOPRO` | Texto corto | 2 |  | Dígitos de control |
| `CUEPRO` | Texto corto | 10 |  | Nº de cuenta |
| `FPAPRO` | Texto corto | 3 |  | Forma de pago |
| `SAPPRO` | Entero | 2 |  | Aprovisionamiento (Semanas) |
| `DAPPRO` | Entero | 2 |  | Aprovisionamiento (Días) |
| `TARPRO` | Texto corto | 30 |  | [E]Tarifa |
| `DT1PRO` | Moneda | 8 |  | Descuento 1 |
| `DT2PRO` | Moneda | 8 |  | Descuento 2 |
| `DT3PRO` | Moneda | 8 |  | Descuento 3 |
| `CCLPRO` | Texto corto | 10 |  | Código de cliente |
| `TPOPRO` | Entero | 2 |  | [L=#0;Pagados#1;Debidos]Portes |
| `PORPRO` | Texto corto | 30 |  | Portes (texto) |
| `IVAPRO` | Entero | 2 |  | [L=#0;Con IVA#1;Sin IVA#2;Intracomunitario#3;Importación]Tipo de IVA |
| `RESPRO` | Texto corto | 200 |  | Rappels |
| `RFIPRO` | Moneda | 8 |  | Rappel fijo |
| `PRAPRO` | Texto corto | 30 |  | Fecha de alta |
| `WEBPRO` | Texto corto | 50 |  | Web |
| `EMAPRO` | Texto corto | 255 |  | E-mail |
| `OBSPRO` | Texto largo |  |  | Observaciones |
| `HORPRO` | Texto corto | 30 |  | Horario |
| `VDEPRO` | Texto corto | 5 |  | Vacaciones (desde) |
| `VHAPRO` | Texto corto | 5 |  | Vacaciones (hasta) |
| `NVAPRO` | Entero | 2 |  | [E]No vender articulos a este proveedro |
| `NRPPRO` | Entero | 2 |  | [E]No realizar pagos a este proveedor |
| `NIPPRO` | Entero | 2 |  | [E]No imprimir en los listados |
| `PAIPRO` | Texto corto | 50 |  | País |
| `SWFPRO` | Texto corto | 50 |  | IBAN del banco |
| `TLXPRO` | Texto corto | 50 |  | Telex |
| `DBAPRO` | Texto corto | 50 |  | Domicilio del banco |
| `PBAPRO` | Texto corto | 50 |  | Población del banco |
| `REQPRO` | Entero | 2 |  | [L=#0;No#1;Sí]Recargo de equivalencia |
| `CCEPRO` | Texto corto | 10 |  | Cuenta contable de compras |
| `DP1PRO` | Entero | 2 |  | Dia de pago 1 del proveedor |
| `DP2PRO` | Entero | 2 |  | Dia de pago 2 del proveedor |
| `DP3PRO` | Entero | 2 |  | Dia de pago 3 del proveedor |
| `SWIPRO` | Texto corto | 11 |  | SWIFT del banco |
| `MEMPRO` | Texto largo |  |  | Mensaje emergente |
| `RETPRO` | Moneda | 8 |  | Porcentaje de retención |
| `NO1PRO` | Texto corto | 50 |  | Nombre de la persona de contacto 1 |
| `TF1PRO` | Texto corto | 50 |  | Teléfono de la persona de contacto 1 |
| `EM1PRO` | Texto corto | 60 |  | E-mail de la persona de contacto 1 |
| `NO2PRO` | Texto corto | 50 |  | Nombre de la persona de contacto 2 |
| `TF2PRO` | Texto corto | 50 |  | Teléfono de la persona de contacto 2 |
| `EM2PRO` | Texto corto | 60 |  | E-mail de la persona de contacto 2 |
| `NO3PRO` | Texto corto | 50 |  | Nombre de la persona de contacto 3 |
| `TF3PRO` | Texto corto | 50 |  | Teléfono de la persona de contacto 3 |
| `EM3PRO` | Texto corto | 60 |  | E-mail de la persona de contacto 3 |
| `NO4PRO` | Texto corto | 50 |  | Nombre de la persona de contacto 4 |
| `TF4PRO` | Texto corto | 50 |  | Teléfono de la persona de contacto 4 |
| `EM4PRO` | Texto corto | 60 |  | E-mail de la persona de contacto 4 |
| `NO5PRO` | Texto corto | 50 |  | Nombre de la presona de contacto 5 |
| `TF5PRO` | Texto corto | 50 |  | Teléfono de la persona de contacto 5 |
| `EM5PRO` | Texto corto | 60 |  | E-mail de la persona de contacto 5 |
| `DOCPRO` | Entero largo | 4 |  | Nº de serie predeterminado |
| `IFIPRO` | Entero largo | 4 |  | [L=#0;NIF#1;NIF/IVA (NIF operador |
| `IMPPRO` | Entero largo | 4 |  | [L=#0;IVA#1;IGIC]Tipo de impuesto |
| `HOMPRO` | Entero largo | 4 |  | Homologado |
| `PWEPRO` | Texto corto | 50 |  | Contraseña web |
| `CUWPRO` | Texto corto | 50 |  | Usuario web |
| `CASPRO` | Texto corto | 255 |  | Carpeta asociada al proveedor |
| `CTMPRO` | Entero | 2 |  | Divisa del proveedor |
| `PPAPRO` | Moneda | 8 |  | % Pronto pago |
| `TIVPRO` | Entero | 2 |  | [L=#0;Sin asignar;#1;IVA1AUT#2;IVA2AUT#3;IVA3AUT#4;Exento]Porcentaje |
| `TWIPRO` | Texto corto | 255 |  |  |
| `FCBPRO` | Texto corto | 255 |  |  |
| `MOVPRO` | Texto corto | 50 |  |  |
| `RCCPRO` | Entero | 2 |  |  |
| `REPPRO` | Entero largo | 4 |  | Representante |
| `COPPRO` | Entero | 2 |  | Clave de operación |
| `APDPRO` | Entero | 2 |  | Aceptada la política de tratamiento de datos |
| `PECPRO` | Entero | 2 |  | Permitido el envío de e-mails comerciales |
| `TREPRO` | Entero | 2 |  | [E]Tipo de retención |
| `CVIPRO` | Entero | 2 |  | [E]Clave de operación intracomunitaria |
| `FAVPRO` | Texto corto | 1 |  | [E]Favorito |
| `SKYPRO` | Texto corto | 60 |  | [E]Cuenta skype del cliente |
| `ITGPRO` | Texto corto | 255 |  | [E]Instagram |
| `MDPPRO` | Entero | 2 |  | Modelo de impresión para pedidos |
| `DECPRO` | Entero | 2 |  | [E]Departamento contabilidad |
| `SDCPRO` | Entero | 2 |  | [E]Subdepartamento contabilidad |
| `CROPRO` | Texto corto | 20 |  | [E]Código ROPO |

---

## F_Q34

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODQ34` | Entero | 2 |  | Fecha de emisión |
| `BANQ34` | Entero | 2 |  | Banco |
| `ESTQ34` | Entero | 2 |  | [L=#0;Pendiente#1;Enviada]Estado |
| `DCAQ34` | Entero | 2 |  | [L=#0;Sin relación#1;Con relación]Gastos |
| `GASQ34` | Entero | 2 |  | [L=#0;Por cuneta del ordenante#1;Por cuenta del |
| `TRAQ34` | Entero | 2 |  | Traspasada a contabilidad |
| `DESQ34` | Texto corto | 50 |  | Descripción |

---

## F_RDJ

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODRDJ` | Entero largo | 4 | ✓ | Código |
| `PERRDJ` | Entero | 2 |  | Trabajador |
| `MESRDJ` | Entero | 2 |  | Mes |

---

## F_RDO

**Registros:** 30

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODRDO` | Entero largo | 4 | ✓ | Código de la relación de documentos |
| `DORRDO` | Texto corto | 3 |  | Documento origen (C=Pedido cliente, A=Albarán...) |
| `TORRDO` | Texto corto | 1 |  | Serie del documento origen |
| `CORRDO` | Entero largo | 4 |  | Código del documento origen |
| `PORRDO` | Entero largo | 4 |  | Posición en el documento origen |
| `LORRDO` | Entero largo | 4 |  | Línea dentro de la posición del documento origen (futuro uso - para |
| `DDERDO` | Texto corto | 3 |  | Documento destino (V=Pedido proveedor, E=Entrada, A=Albarán...) |
| `TDERDO` | Texto corto | 1 |  | Serie del documento destino |
| `CDERDO` | Entero largo | 4 |  | Código del documento destino |
| `PDERDO` | Entero largo | 4 |  | Posición en el documento destino |
| `LDERDO` | Entero largo | 4 |  | Línea dentro de la posición del documento destino (futuro uso - para |

---

## F_REC

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `TIPREC` | Texto corto | 1 | ✓ | Nº de serie |
| `CODREC` | Entero largo | 4 | ✓ | [F=000000]Código |
| `POSREC` | Entero | 2 | ✓ | Nº de vencimiento |
| `LOCREC` | Texto corto | 30 |  | Lugar de expedición |
| `IMPREC` | Moneda | 8 |  | Fecha de vencimiento |
| `CO1REC` | Texto corto | 60 |  | Concepto 1 |
| `CO2REC` | Texto corto | 60 |  | Concepto 2 |
| `ENTREC` | Texto corto | 40 |  | Nombre de la entidad |
| `CC1REC` | Texto corto | 4 |  | Entidad |
| `CC2REC` | Texto corto | 4 |  | Oficina |
| `DCCREC` | Texto corto | 2 |  | Dígitos de control |
| `CUEREC` | Texto corto | 18 |  | Nº de cuenta |
| `ESTREC` | Entero | 2 |  | [L=#0;Pte.#1;Cobrado#2;Cobrado parcial]Estado |
| `CLIREC` | Entero largo | 4 |  | [F=00000]Cliente |
| `NOMREC` | Texto corto | 100 |  | Nombre |
| `DOMREC` | Texto corto | 100 |  | Dirección |
| `POBREC` | Texto corto | 50 |  | Población |
| `PRVREC` | Texto corto | 30 |  | Provincia |
| `CPOREC` | Texto corto | 10 |  | Cód. Postal |
| `NIFREC` | Texto corto | 18 |  | N.I.F. |
| `DEVREC` | Entero | 2 |  |  |
| `REMREC` | Entero | 2 |  |  |
| `IBAREC` | Texto corto | 34 |  |  |
| `BICREC` | Texto corto | 11 |  |  |

---

## F_REM

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODREM` | Entero largo | 4 |  | Fecha de emisión |
| `BANREM` | Entero | 2 |  | Banco |
| `TOTREM` | Moneda | 8 |  | Total |
| `ESTREM` | Entero | 2 |  | Fecha de cargo |
| `TRAREM` | Entero largo | 4 |  | [L=#0;No traspasada#1;Traspasada]Traspasada a contabilidad |
| `CGEREM` | Entero | 2 |  |  |
| `TIPREM` | Entero | 2 |  |  |
| `UFCREM` | Entero | 2 |  |  |
| `FINREM` | Entero | 2 |  | Financiada |

---

## F_REP

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODREP` | Entero largo | 4 | ✓ | Código |
| `NOMREP` | Texto corto | 40 |  | Nombre |
| `DOMREP` | Texto corto | 40 |  | Domicilio |
| `POBREP` | Texto corto | 30 |  | Población |
| `CPOREP` | Texto corto | 10 |  | Cód. Postal |
| `PROREP` | Texto corto | 40 |  | Provincia |
| `DNIREP` | Texto corto | 18 |  | D.N.I |
| `CARREP` | Texto corto | 40 |  | Cargo |
| `TEOREP` | Texto corto | 40 |  | Teléfonos oficina |
| `TEPREP` | Texto corto | 18 |  | Teléfono particular |
| `EMAREP` | Texto corto | 40 |  | E-mail |
| `OBSREP` | Texto largo |  |  | Observaciones |

---

## F_RES

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODRES` | Entero largo | 4 |  | Hora de fin |
| `DURRES` | Texto corto | 12 |  | Duración |
| `CLIRES` | Entero largo | 4 |  | Cliente que hace la reserva |
| `ARTRES` | Texto corto | 13 |  | Artículo reservado |
| `CANRES` | Moneda | 8 |  | Cantidad |
| `PRERES` | Moneda | 8 |  | Precio |
| `TOTRES` | Moneda | 8 |  | Total |
| `FACRES` | Entero largo | 4 |  | Está facturado |
| `TFARES` | Texto corto | 1 |  | Serie de la factura |
| `CFARES` | Entero | 2 |  | Número de la factura |

---

## F_RET

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODRET` | Entero largo | 4 | ✓ | Código |
| `CAJRET` | Entero | 2 |  | Fecha |
| `HORRET` | Texto corto | 5 |  | Hora |
| `CONRET` | Texto corto | 50 |  | Concepto |
| `IMPRET` | Moneda | 8 |  | Importe |
| `PRORET` | Entero largo | 4 |  | Proveedor |
| `TPVIDRET` | Texto corto | 16 |  | ID apertura TPV |
| `CFARET` | Entero | 2 |  | [E]Apunte caja de FactuSOL |
| `PFARET` | Entero largo | 4 |  | [E]Posición apunte caja de FactuSOL |

---

## F_RIE

**Registros:** 131

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CLIRIE` | Entero largo | 4 | ✓ | [F=00000]Cliente |
| `IMPRIE` | Moneda | 8 |  | Importe |
| `ASERIE` | Entero | 2 |  | [E]¿Asegurado? |
| `NPORIE` | Texto corto | 50 |  | Fecha de finalización |
| `CONRIE` | Texto corto | 100 |  |  |
| `IMARIE` | Moneda | 8 |  |  |
| `OBSRIE` | Texto corto | 255 |  | Observaciones |

---

## F_RUT

**Registros:** 2

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODRUT` | Texto corto | 3 | ✓ | Código |
| `DESRUT` | Texto corto | 50 |  | Descripción |
| `AGERUT` | Entero largo | 4 |  | [E]Agente |

---

## F_SAL

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODSAL` | Entero largo | 4 |  | Fecha |
| `ALMSAL` | Texto corto | 3 |  | Almacén |
| `OBSSAL` | Texto corto | 50 |  | Observaciones |

---

## F_SEC

**Registros:** 10

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODSEC` | Texto corto | 3 | ✓ | Código |
| `DESSEC` | Texto corto | 50 |  | Descripción |
| `SUWSEC` | Entero largo | 4 |  | [E]Imagen de la sección |
| `MPTSEC` | Entero | 2 |  | Mostrar en el panel táctil de TPVSOL |
| `ORDSEC` | Entero largo | 4 |  | Indica el orden para la Tienda Virtual |

---

## F_SFC

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODSFC` | Entero largo | 4 | ✓ | [E]CODIGO DEL DOCUMENTO ORIGEN |
| `POSSFC` | Entero largo | 4 | ✓ | [E]POSICION DENTRO DE LAS LÍNEAS DE FABRICACIÓN |
| `NSESFC` | Texto corto | 50 |  | Fecha de consumo preferente |
| `CANSFC` | Moneda | 8 |  | Fecha |
| `ALMSFC` | Texto corto | 3 |  | Almacén |
| `ARTSFC` | Texto corto | 13 |  | Artículo |

---

## F_SFD

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODSFD` | Entero largo | 4 | ✓ | [E]CODIGO DEL DOCUMENTO ORIGEN |
| `POSSFD` | Entero largo | 4 | ✓ | [E]POSICION DENTRO DE LAS LÍNEAS DE DETALLE |
| `LINSFD` | Entero largo | 4 | ✓ | [E]LÍNEA DE FABRICACIÓN DENTRO DE LA POSICIÓN |
| `NSESFD` | Texto corto | 50 |  | Fecha de consumo preferente |
| `CANSFD` | Moneda | 8 |  | Cantidad |

---

## F_SFL

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODSFL` | Entero largo | 4 | ✓ | [E]CODIGO DEL DOCUMENTO ORIGEN |
| `POSSFL` | Entero largo | 4 | ✓ | [E]POSICION DENTRO DE LAS LÍNEAS DE FABRICACIÓN |
| `LINSFL` | Entero | 2 | ✓ | [E]LINEA DEL COMPONENTE |
| `NSESFL` | Texto corto | 50 |  | Fecha de consumo preferente |
| `CANSFL` | Moneda | 8 |  | Fecha |
| `ALMSFL` | Texto corto | 3 |  | Almacén |
| `ARTSFL` | Texto corto | 13 |  | Artículo |

---

## F_SLA

**Registros:** 13

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `TIPSLA` | Texto corto | 1 | ✓ | Serie del albarán |
| `CODSLA` | Entero largo | 4 | ✓ | Código del albarán |
| `POSSLA` | Entero largo | 4 | ✓ | Posición de la línea de detalle |
| `NSESLA` | Texto corto | 50 |  | Fecha de consumo preferente |
| `CANSLA` | Moneda | 8 |  | [E]Fecha |
| `ALMSLA` | Texto corto | 3 |  | [E]Almacén |
| `ARTSLA` | Texto corto | 13 |  | [E]Artículo |

---

## F_SLB

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `TIPSLB` | Texto corto | 1 | ✓ | Serie del abono |
| `CODSLB` | Entero largo | 4 | ✓ | Código del abono |
| `POSSLB` | Entero largo | 4 | ✓ | Posición de la línea de detalle |
| `NSESLB` | Texto corto | 50 |  | Fecha de consumo preferente |
| `CANSLB` | Moneda | 8 |  | [E]Fecha |
| `ALMSLB` | Texto corto | 3 |  | [E]Almacén |
| `ARTSLB` | Texto corto | 13 |  | [E]Artículo |

---

## F_SLC

**Registros:** 2

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `TIPSLC` | Texto corto | 1 | ✓ | Serie del pedido de cliente |
| `CODSLC` | Entero largo | 4 | ✓ | Código del pedido de cliente |
| `POSSLC` | Entero largo | 4 | ✓ | Posición de la línea de detalle |
| `NSESLC` | Texto corto | 50 |  | Fecha de consumo preferente |
| `CANSLC` | Moneda | 8 |  | Cantidad |

---

## F_SLD

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `TIPSLD` | Texto corto | 1 | ✓ | Serie de la devolución |
| `CODSLD` | Entero largo | 4 | ✓ | Código de la devolución |
| `POSSLD` | Entero largo | 4 | ✓ | Posición de la línea de detalle |
| `NSESLD` | Texto corto | 50 |  | Fecha de consumo preferente |
| `CANSLD` | Moneda | 8 |  | [E]Fecha |
| `ALMSLD` | Texto corto | 3 |  | [E]Almacén |
| `ARTSLD` | Texto corto | 13 |  | [E]Artículo |

---

## F_SLE

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `TIPSLE` | Texto corto | 1 | ✓ | Serie de la entrada |
| `CODSLE` | Entero largo | 4 | ✓ | Código de la entrada |
| `POSSLE` | Entero largo | 4 | ✓ | Posición de la línea de detalle |
| `NSESLE` | Texto corto | 50 |  | Fecha de consumo preferente |
| `CANSLE` | Moneda | 8 |  | [E]Fecha |
| `ALMSLE` | Texto corto | 3 |  | [E]Almacén |
| `ARTSLE` | Texto corto | 13 |  | [E]Artículo |

---

## F_SLF

**Registros:** 13

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `TIPSLF` | Texto corto | 1 | ✓ | Serie de la factura |
| `CODSLF` | Entero largo | 4 | ✓ | Código de la factura |
| `POSSLF` | Entero largo | 4 | ✓ | Posición de la línea de detalle |
| `NSESLF` | Texto corto | 50 |  | Fecha de consumo preferente |
| `CANSLF` | Moneda | 8 |  | [E]Fecha |
| `ALMSLF` | Texto corto | 3 |  | [E]Almacén |
| `ARTSLF` | Texto corto | 13 |  | [E]Artículo |

---

## F_SLI

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODSLI` | Entero largo | 4 | ✓ | [E]CODIGO DEL DOCUMENTO ORIGEN |
| `POSSLI` | Entero largo | 4 | ✓ | [E]LÍNEA DE DETALLE |
| `NSESLI` | Texto corto | 50 |  | Fecha de consumo preferente |
| `CANSLI` | Moneda | 8 |  | Fecha |
| `ALMSLI` | Texto corto | 3 |  | Almacén |
| `ARTSLI` | Texto corto | 13 |  | Artículo |

---

## F_SLP

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `TIPSLP` | Texto corto | 1 | ✓ | Serie del presupuesto |
| `CODSLP` | Entero largo | 4 | ✓ | Código del presupuesto |
| `POSSLP` | Entero largo | 4 | ✓ | Posición de la línea de detalle |
| `NSESLP` | Texto corto | 50 |  | Fecha de consumo preferente |
| `CANSLP` | Moneda | 8 |  | Cantidad |

---

## F_SLR

**Registros:** 1

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `TIPSLR` | Texto corto | 1 | ✓ | Serie de la factura recibida |
| `CODSLR` | Entero largo | 4 | ✓ | Código de la factura recibida |
| `POSSLR` | Entero largo | 4 | ✓ | Posición de la línea de detalle |
| `NSESLR` | Texto corto | 50 |  | Fecha de consumo preferente |
| `CANSLR` | Moneda | 8 |  | [E]Fecha |
| `ALMSLR` | Texto corto | 3 |  | [E]Almacén |
| `ARTSLR` | Texto corto | 13 |  | [E]Artículo |

---

## F_SLT

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `DOCSLT` | Entero largo | 4 | ✓ | [E]CODIGO DEL DOCUMENTO ORIGEN |
| `LINSLT` | Entero largo | 4 | ✓ | [E]POSICION DENTRO DE LAS LÍNEAS DE DETALLE |
| `NSESLT` | Texto corto | 50 |  | Fecha de consumo preferente |
| `CANSLT` | Moneda | 8 |  | Fecha |
| `ALMSLT` | Texto corto | 3 |  | Almacén |
| `ALDSLT` | Texto corto | 255 |  | Almacén destino |
| `ARTSLT` | Texto corto | 13 |  | Artículo |

---

## F_SLV

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `TIPSLV` | Texto corto | 1 | ✓ | Serie del pedido a proveedor |
| `CODSLV` | Entero largo | 4 | ✓ | Código del pedido a proveedor |
| `POSSLV` | Entero largo | 4 | ✓ | Posición de la línea de detalle |
| `NSESLV` | Texto corto | 50 |  | Fecha de consumo preferente |
| `CANSLV` | Moneda | 8 |  | Cantidad |

---

## F_SMS

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODSMS` | Entero largo | 4 |  | [F=hh:mm]Hora |
| `CONSMS` | Texto largo |  |  | Texto |
| `DESSMS` | Texto largo |  |  | Destinatarios |
| `USUSMS` | Entero | 2 |  | Código usuario que envió el SMS |
| `ACUSMS` | Entero | 2 |  | [E]SOLICITO ACUSO DE RECIBO 0= NO, 1 = SI |
| `REMSMS` | Entero | 2 |  | [E]HORA PROGRAMADA PARA EL ENVÍO |
| `ASUSMS` | Texto largo |  |  | Asunto del MMS |
| `FICSMS` | Texto largo |  |  | [E]FICHERO ADJUNTO AL MMS |
| `ESTSMS` | Entero | 2 |  | [E]ESTADO DEL ENVÍO |
| `PARSMS` | Texto corto | 100 |  | [E] |
| `TDESMS` | Entero | 2 |  | [E]TIPO DE DESTINATARIO DEL SMS, 0=MANUAL, 1 = CLIENTE, 2 = |
| `CIDSMS` | Texto corto | 50 |  | Codigo SMS en la plataforma |
| `RPESMS` | Texto corto | 11 |  |  |

---

## F_STC

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `ARTSTC` | Texto corto | 13 | ✓ | Artículo |
| `ALMSTC` | Texto corto | 3 | ✓ | Almacén |
| `CE1STC` | Texto corto | 3 | ✓ | Talla |
| `CE2STC` | Texto corto | 3 | ✓ | Color |
| `MINSTC` | Moneda | 8 |  | Stock mínimo |
| `MAXSTC` | Moneda | 8 |  | Stock máximo |
| `ACTSTC` | Moneda | 8 |  | Stock actual |
| `DISSTC` | Moneda | 8 |  | Stock disponible |

---

## F_STM

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `ARTSTM` | Texto corto | 13 | ✓ | [E] |
| `ALMSTM` | Texto corto | 3 | ✓ | [E] |
| `A01STM` | Moneda | 8 |  | [E] |
| `D01STM` | Moneda | 8 |  | [E] |
| `A02STM` | Moneda | 8 |  | [E] |
| `D02STM` | Moneda | 8 |  | [E] |
| `A03STM` | Moneda | 8 |  | [E] |
| `D03STM` | Moneda | 8 |  | [E] |
| `A04STM` | Moneda | 8 |  | [E] |
| `D04STM` | Moneda | 8 |  | [E] |
| `A05STM` | Moneda | 8 |  | [E] |
| `D05STM` | Moneda | 8 |  | [E] |
| `A06STM` | Moneda | 8 |  | [E] |
| `D06STM` | Moneda | 8 |  | [E] |
| `A07STM` | Moneda | 8 |  | [E] |
| `D07STM` | Moneda | 8 |  | [E] |
| `A08STM` | Moneda | 8 |  | [E] |
| `D08STM` | Moneda | 8 |  | [E] |
| `A09STM` | Moneda | 8 |  | [E] |
| `D09STM` | Moneda | 8 |  | [E] |
| `A10STM` | Moneda | 8 |  | [E] |
| `D10STM` | Moneda | 8 |  | [E] |
| `A11STM` | Moneda | 8 |  | [E] |
| `D11STM` | Moneda | 8 |  | [E] |
| `A12STM` | Moneda | 8 |  | [E] |
| `D12STM` | Moneda | 8 |  | [E] |

---

## F_STO

**Registros:** 14521

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `ARTSTO` | Texto corto | 13 | ✓ | Artículo |
| `ALMSTO` | Texto corto | 3 | ✓ | Almacén |
| `MINSTO` | Moneda | 8 |  | Stock mínimo |
| `MAXSTO` | Moneda | 8 |  | Stock máximo |
| `ACTSTO` | Moneda | 8 |  | Stock actual |
| `DISSTO` | Moneda | 8 |  | Stock disponible |
| `UBISTO` | Texto corto | 30 |  | Ubicación en el almacén |

---

## F_TAR

**Registros:** 4

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODTAR` | Entero largo | 4 | ✓ | Código |
| `DESTAR` | Texto corto | 50 |  | Descripción |
| `MARTAR` | Moneda | 8 |  | Margen |
| `IVATAR` | Entero largo | 4 |  | [E]Incluir impuesto |

---

## F_TCA

**Registros:** 365

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CAMTCA` | Doble | 8 |  | Tipo de cambio |

---

## F_TCD

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODTCD` | Entero largo | 4 | ✓ | Código |
| `DESTCD` | Texto corto | 50 |  | Fecha |
| `HENTCD` | Texto corto | 5 |  | Hora de entrada |
| `HSATCD` | Texto corto | 5 |  | Hora de salida |
| `HETTCD` | Texto corto | 5 |  | Hora de entrada (por la tarde) |
| `HSTTCD` | Texto corto | 5 |  | Hora de salida (por la tarde) |

---

## F_TCH

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODTCH` | Entero largo | 4 | ✓ | Código |
| `DESTCH` | Texto corto | 50 |  | Fecha hasta la que está en vigor |
| `VERTCH` | Entero largo | 4 |  | Aplicar horario de verano (0 = No, 1 = Si) |
| `VDDTCH` | Entero largo | 4 |  | Verano desde día |
| `VDMTCH` | Entero largo | 4 |  | Verano desde mes |
| `VHDTCH` | Entero largo | 4 |  | Verano hasta día |
| `VHMTCH` | Entero largo | 4 |  | Verano hasta mes |
| `HEXTCH` | Entero largo | 4 |  | Permitir horas extras (0=No, 1=Horas extras fuerza mayor, 2=Horas extra, |
| `FENTCH` | Entero largo | 4 |  | Flexibilidad (números de minutos: 5, 10, 15, 20...) |
| `THOTCH` | Entero largo | 4 |  | Tipo de horario (Jornada diaria, Jornada flexible) |

---

## F_TCL

**Registros:** 4

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODTCL` | Texto corto | 3 | ✓ | Código |
| `DESTCL` | Texto corto | 50 |  | Descripción |

---

## F_TRA

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `DOCTRA` | Entero largo | 4 |  | Fecha |
| `AORTRA` | Texto corto | 3 |  | Almacén de origen |
| `ADETRA` | Texto corto | 3 |  | Almacén de destino |
| `COMTRA` | Texto largo |  |  | Comentarios |

---

## F_TRB

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `PROTRB` | Texto corto | 255 | ✓ | Producto |
| `TIDTRB` | Texto corto | 50 |  | Fecha del valor |
| `IMPTRB` | Moneda | 8 |  | Importe |
| `SALTRB` | Moneda | 8 |  | Saldo |
| `DESTRB` | Texto corto | 255 |  | Descripción |
| `CATTRB` | Entero largo | 4 |  | Categoría |

---

## F_TRN

**Registros:** 1

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODTRN` | Entero | 2 | ✓ | Código |
| `NOMTRN` | Texto corto | 40 |  | Nombre |
| `DOMTRN` | Texto corto | 40 |  | Domicilio |
| `POBTRN` | Texto corto | 30 |  | Población |
| `CPOTRN` | Texto corto | 10 |  | Cód. Postal |
| `PROTRN` | Texto corto | 40 |  | Provincia |
| `DNITRN` | Texto corto | 18 |  | D.N.I. |
| `TELTRN` | Texto corto | 18 |  | Teléfono |
| `FAXTRN` | Texto corto | 25 |  | Fax |
| `PCOTRN` | Texto corto | 50 |  | Persona de contacto |
| `PAITRN` | Texto corto | 50 |  | País |
| `EMATRN` | Texto corto | 60 |  | E-mail |
| `WEBTRN` | Texto corto | 60 |  | Web |
| `OBSTRN` | Texto largo |  |  | Observaciones |
| `UWETRN` | Entero largo | 4 |  | Utilizar en la web |

---

## F_TRZ

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODTRZ` | Entero largo | 4 | ✓ |  |
| `TIPTRZ` | Entero largo | 4 | ✓ |  |
| `NUMTRZ` | Texto corto | 50 |  |  |
| `DATTRZ` | Texto largo |  |  |  |

---

## F_UME

**Registros:** 1

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODUME` | Entero | 2 | ✓ | Código |
| `DESUME` | Texto corto | 50 |  | Descripción |

---

## F_VAL

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `ARTVAL` | Texto corto | 13 | ✓ | Código del artículo |
| `POSVAL` | Entero largo | 4 |  | [F=hh:mm]Hora |
| `TITVAL` | Texto corto | 255 |  | Titulo |
| `COMVAL` | Texto largo |  |  | Comentario |
| `VCLVAL` | Entero | 2 |  | Valoración del cliente |
| `VISVAL` | Entero | 2 |  | Visible |
| `APRVAL` | Entero | 2 |  | Comentario aprovado |
| `CLIVAL` | Entero | 2 |  | Código del cliente que hace la valoración |

---

## F_VER

**Registros:** 1

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODVER` | Entero largo | 4 |  | Código |
| `VERVER` | Entero | 2 |  | Versión |
| `EVEVER` | Entero | 2 |  | Edición verano, si o no |
| `REVVER` | Entero | 2 |  | Revisión |
| `MODVER` | Entero | 2 |  | Modificación |
| `SEGVER` | Entero | 2 |  | Seguridad |

---

## R_LPA

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `PARLPA` | Entero largo | 4 | ✓ | Código de parte |
| `POSLPA` | Entero | 2 | ✓ | Posición |
| `ARTLPA` | Texto corto | 13 |  | Artículo |
| `DARLPA` | Texto largo |  |  | Descripción |
| `CANLPA` | Moneda | 8 |  | Cantidad |
| `PRELPA` | Moneda | 8 |  | Precio |
| `DT1LPA` | Moneda | 8 |  | Descuento 1 |
| `DT2LPA` | Moneda | 8 |  | Descuento 2 |
| `DT3LPA` | Moneda | 8 |  | Descuento 3 |
| `TOTLPA` | Moneda | 8 |  | Total |
| `COMLPA` | Moneda | 8 |  | Comisión |
| `IVALPA` | Entero | 2 |  | [L=#0;IVA1AUT#1;IVA2AUT#2;IVA3AUT#3;Exento]Tipo de IVA |
| `BULLPA` | Entero largo | 4 |  | Nº de bultos |
| `COSLPA` | Moneda | 8 |  | Costo |
| `NSELPA` | Texto largo |  |  | Nº de serie |

---

## R_LPR

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODLPR` | Texto corto | 3 | ✓ | Código de producto |
| `DESLPR` | Texto corto | 50 |  | Descripción de producto |

---

## R_MAR

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODMAR` | Texto corto | 3 | ✓ | Código de marca |
| `DESMAR` | Texto corto | 50 |  | Nombre de la marca |

---

## R_PAR

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODPAR` | Entero largo | 4 |  | Fecha de entrada |
| `TIPPAR` | Entero | 2 |  | [L=#0;Tipo 1#1;Tipo 2#2;Tipo 3#3;Tipo 4#4;Tipo 5#5;Tipo 6#6;Tipo |
| `ESTPAR` | Entero | 2 |  | [L=#0;Estado 1#1;Estado 2#2;Estado 3#3;Estado 4#4;Estado 5#5;Estado |
| `CLIPAR` | Entero largo | 4 |  | [F=00000]Cliente |
| `PCOPAR` | Texto corto | 30 |  | Persona de contacto |
| `TELPAR` | Texto corto | 26 |  | Teléfono |
| `OBSPAR` | Texto corto | 100 |  | Observaciones |
| `ZONPAR` | Texto corto | 30 |  | Hora prevista visita |
| `TECPAR` | Entero | 2 |  | Técnico |
| `TAPPAR` | Texto corto | 3 |  | Producto |
| `MARPAR` | Texto corto | 3 |  | Marca |
| `MODPAR` | Texto corto | 50 |  | Modelo |
| `NSEPAR` | Texto corto | 50 |  | Fecha fin de garantía |
| `AVEPAR` | Texto largo |  |  | Síntoma de la avería |
| `PREPAR` | Entero | 2 |  | [L=#0;No#1;Sí]Solicita presupuesto previo |
| `GARPAR` | Entero | 2 |  | [L=#0;No#1;Sí]Reparación en garantía |
| `TINPAR` | Texto corto | 3 |  | Tipo de intervención |
| `NPOPAR` | Texto corto | 30 |  | Nº de póliza |
| `TRAPAR` | Texto largo |  |  | Trabajo realizado |
| `REPPAR` | Entero | 2 |  | [L=#0;No#1;Sí]Reparado en taller |
| `INTPAR` | Entero | 2 |  | [L=#0;No#1;Sí]Intervención terminada |
| `PIEPAR` | Moneda | 8 |  | Presupuesto. Piezas |
| `MOBPAR` | Moneda | 8 |  | Presupuesto. Mano de obra |
| `TPRPAR` | Moneda | 8 |  | Presupuesto. Total |
| `NHOPAR` | Moneda | 8 |  | Trabajo, hasta |
| `TPIPAR` | Moneda | 8 |  | Importe piezas |
| `MAOPAR` | Moneda | 8 |  | Importemano de obra |
| `DISPAR` | Moneda | 8 |  | Importe disposición de servicio |
| `TALPAR` | Moneda | 8 |  | Importe transporte / almacenaje |
| `BASPAR` | Moneda | 8 |  | Base imponible |
| `PIVPAR` | Moneda | 8 |  | Porcentaje de IVA |
| `IIVPAR` | Moneda | 8 |  | Importe de IVA |
| `TOTPAR` | Moneda | 8 |  | Fecha de salida |
| `FACPAR` | Entero | 2 |  | [L=#0;No#1;Sí]Facturado |
| `CNIPAR` | Texto corto | 18 |  | NIF |
| `CNOPAR` | Texto corto | 100 |  | Nombre |
| `CDOPAR` | Texto corto | 100 |  | Domicilio |
| `CCPPAR` | Texto corto | 10 |  | Código postal |
| `CPOPAR` | Texto corto | 30 |  | Población |
| `CPRPAR` | Texto corto | 40 |  | Provincia |
| `FAXPAR` | Texto corto | 25 |  | Fax |
| `EMAPAR` | Texto corto | 60 |  | E-mail |
| `PRECPAR` | Moneda | 8 |  | Porcentaje de recargo |
| `IRECPAR` | Moneda | 8 |  | Importe de recargo |
| `DOCPAR` | Texto corto | 50 |  | Documento en que se facturó o albaraneó el parte |
| `OBRPAR` | Entero | 2 |  | Dirección de entrega |

---

## R_TIN

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODTIN` | Texto corto | 3 | ✓ | Código |
| `DESTIN` | Texto corto | 50 |  | Descripción |
| `CMOTIN` | Entero | 2 |  | [L=#0;No#1;Sí]Cobrar mano de obra |
| `CMATIN` | Entero | 2 |  | [L=#0;No#1;Sí]Cobrar materiales |
| `CDSTIN` | Entero | 2 |  | [L=#0;No#1;Sí]Cobrar disposición de servicio |

---

## T_ATE

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `TERATE` | Entero largo | 4 | ✓ | TERMINAL |
| `TURATE` | Entero largo | 4 | ✓ | FECHA |
| `IDEATE` | Texto corto | 16 |  | IDENTIFICADOR |
| `SINATE` | Moneda | 8 |  | SALDO INICIAL |
| `EFEATE` | Moneda | 8 |  | EFECTIVO |
| `ANUATE` | Entero largo | 4 |  | TICKETS ANULADOS |
| `MODATE` | Entero largo | 4 |  | TICKETS MODIFICADOS |
| `BI0ATE` | Entero | 2 |  | BILLETES 500 EN CAJA |
| `BI1ATE` | Entero | 2 |  | BILLETES 200 EN CAJA |
| `BI2ATE` | Entero | 2 |  | BILLETES 100 EN CAJA |
| `BI3ATE` | Entero | 2 |  | BILLETES 50 EN CAJA |
| `BI4ATE` | Entero | 2 |  | BILLETES 20 EN CAJA |
| `BI5ATE` | Entero | 2 |  | BILLETES 10 EN CAJA |
| `BI6ATE` | Entero | 2 |  | BILLETES 5 EN CAJA |
| `MO0ATE` | Entero | 2 |  | MONEDAS 2 EN CAJA |
| `MO1ATE` | Entero | 2 |  | MONEDAS 1 EN CAJA |
| `MO2ATE` | Entero | 2 |  | MONEDAS 0,50 EN CAJA |
| `MO3ATE` | Entero | 2 |  | MONEDAS 0,20 EN CAJA |
| `MO4ATE` | Entero | 2 |  | MONEDAS 0,10 EN CAJA |
| `MO5ATE` | Entero | 2 |  | MONEDAS 0,05 EN CAJA |
| `MO6ATE` | Entero | 2 |  | MONEDAS 0,02 EN CAJA |
| `MO7ATE` | Entero | 2 |  | MONEDAS 0,01 EN CAJA |
| `BIA0ATE` | Entero | 2 |  | BILLETES 500 EN CAJA PROXIMA APERTURA |
| `BIA1ATE` | Entero | 2 |  | BILLETES 200 EN CAJA PROXIMA APERTURA |
| `BIA2ATE` | Entero | 2 |  | BILLETES 100 EN CAJA PROXIMA APERTURA |
| `BIA3ATE` | Entero | 2 |  | BILLETES 50 EN CAJA PROXIMA APERTURA |
| `BIA4ATE` | Entero | 2 |  | BILLETES 20 EN CAJA PROXIMA APERTURA |
| `BIA5ATE` | Entero | 2 |  | BILLETES 10 EN CAJA PROXIMA APERTURA |
| `BIA6ATE` | Entero | 2 |  | BILLETES 5 EN CAJA PROXIMA APERTURA |
| `MOA0ATE` | Entero | 2 |  | MONEDAS 2 EN CAJA PROXIMA APERTURA |
| `MOA1ATE` | Entero | 2 |  | MONEDAS 1 EN CAJA PROXIMA APERTURA |
| `MOA2ATE` | Entero | 2 |  | MONEDAS 0,50 EN CAJA PROXIMA APERTURA |
| `MOA3ATE` | Entero | 2 |  | MONEDAS 0,20 EN CAJA PROXIMA APERTURA |
| `MOA4ATE` | Entero | 2 |  | MONEDAS 0,10 EN CAJA PROXIMA APERTURA |
| `MOA5ATE` | Entero | 2 |  | MONEDAS 0,05 EN CAJA PROXIMA APERTURA |
| `MOA6ATE` | Entero | 2 |  | MONEDAS 0,02 EN CAJA PROXIMA APERTURA |
| `MOA7ATE` | Entero | 2 |  | MONEDAS 0,01 EN CAJA PROXIMA APERTURA |
| `EFEAATE` | Moneda | 8 |  | EFECTIVO PROXIMA APERTURA |
| `NCIATE` | Entero | 2 |  | NÚMERO DE CIERRES |
| `HOAATE` | Texto corto | 8 |  | HORA DE APERTURA |
| `HOCATE` | Texto corto | 8 |  | HORA DE CIERRE |

---

## T_CPU

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODCPU` | Entero largo | 4 |  | Fecha |
| `PUCCPU` | Moneda | 8 |  | Puntos canjeados |
| `OBSCPU` | Texto corto | 255 |  | Observaciones |
| `TDOCPU` | Texto corto | 1 |  | Tipo de documento relacionado: F=Factura, A=Albaran |
| `SDOCPU` | Texto corto | 1 |  | Serie del documento relacionado |
| `CDOCPU` | Entero largo | 4 |  | Código del documento relacionado |

---

## T_DEP

**Registros:** 1

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODDEP` | Entero | 2 | ✓ |  |
| `NOMDEP` | Texto corto | 40 |  |  |
| `PERDEP` | Entero | 2 |  | [E]Imagen del dependiente |
| `CLADEP` | Texto corto | 120 |  |  |
| `CCLDEP` | Entero | 2 |  |  |
| `ESTDEP` | Entero | 2 |  | Estado del dependiente (0 - Inactivo, 1 - Activo) |
| `AGEDEP` | Entero | 2 |  | Agente |
| `IDIDEP` | Entero | 2 |  | Idioma del dependiente (0=Sin seleccionar, 1 = Castellano, 2 = Catalán) |

---

## T_DOC

**Registros:** 3

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODDOC` | Entero | 2 | ✓ |  |
| `NOMDOC` | Texto corto | 50 |  |  |
| `DOCDOC` | Texto corto | 1 |  |  |
| `TIPDOC` | Entero | 2 |  |  |
| `FSIDOC` | Entero | 2 |  | Tipo factura simplificada S.I.I. |
| `SFIDOC` | Entero largo | 4 |  | Solicitar firma |
| `COPDOC` | Entero | 2 |  | Clave de operación si el tipo de documento es factura |

---

## T_LTE

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODLTE` | Entero | 2 | ✓ | Código del terminal |
| `DOCLTE` | Entero | 2 | ✓ | Tipo de documento |
| `PUSLTE` | Entero | 2 |  | Permitir su uso |
| `PIMLTE` | Entero | 2 |  | Pregunta imprimir |
| `MODLTE` | Entero | 2 |  | Modo de impresión: 0=Ticket; 1=Modelo predefinido;2=Ejecutable externo |
| `COPLTE` | Entero | 2 |  | Número de copias |
| `TFSLTE` | Texto corto | 50 |  | Texto identificativo del documento |
| `CMOLTE` | Entero largo | 4 |  | Modelo de impresión |
| `CM2LTE` | Entero largo | 4 |  | Modelo de impresión para la segunda impresión |
| `FICLTE` | Texto corto | 255 |  | Fichero ejecutable externo |
| `IUMLTE` | Entero | 2 |  | Impresora a utilizar en el modelo: 0=La de Tpv, 1=La del modelo de |
| `ITBLTE` | Entero | 2 |  | Imprimir Ticket BAI |

---

## T_PER

**Registros:** 1

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODPER` | Entero | 2 | ✓ | Código del perfil de acceso |
| `DESPER` | Texto corto | 40 |  | Descripción del perfil de acceso |
| `CADPER` | Texto corto | 255 |  | Cadena de permisos |

---

## T_TER

**Registros:** 1

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODTER` | Entero | 2 | ✓ |  |
| `DESTER` | Texto corto | 50 |  |  |
| `CLATER` | Texto corto | 8 |  |  |
| `DOCTER` | Entero | 2 |  |  |
| `DEPTER` | Entero largo | 4 |  |  |
| `TPVTER` | Entero largo | 4 |  |  |
| `ESTTER` | Entero largo | 4 |  |  |
| `SINTER` | Moneda | 8 |  |  |
| `EFETER` | Moneda | 8 |  |  |
| `ANUTER` | Entero largo | 4 |  |  |
| `MODTER` | Entero largo | 4 |  |  |
| `TURTER` | Entero largo | 4 |  | Turno actual |
| `HOATER` | Texto corto | 8 |  | Hora de apertura |
| `ABTTER` | Entero | 2 |  | Ancho botones táctiles secc/fam/art |
| `LBTTER` | Entero | 2 |  | Alto botones táctiles secc/fam/art |

---

## T_TFI

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODTFI` | Entero largo | 4 | ✓ | Código |
| `TTFTFI` | Entero largo | 4 |  | Tipo de tarjeta de fidelización |
| `IDETFI` | Texto corto | 13 |  | Id. Tarjeta |
| `CLITFI` | Entero largo | 4 |  | Valida Hasta |
| `TOTTFI` | Moneda | 8 |  | Total acumulado |

---

## T_TPV

**Registros:** 1

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODTPV` | Entero | 2 | ✓ | Código del punto de venta |
| `DESTPV` | Texto corto | 50 |  | Descripción del punto de venta |
| `CLITPV` | Entero largo | 4 |  | Código del cliente por defecto |
| `FPATPV` | Texto corto | 255 |  | Forma de pago por defecto |
| `ALMTPV` | Texto corto | 255 |  | Almacén por defecto |
| `TLITPV` | Entero | 2 |  | Mostrar texto cuando no haya ningún ticket activo |
| `PLITPV` | Texto corto | 255 |  | Primera linea del texto |
| `SLITPV` | Texto corto | 255 |  | Segunda linea del texto |
| `CTI1TPV` | Entero | 2 |  | Tickets - Tipo de impresión para la cabecera 1 |
| `CTL1TPV` | Entero | 2 |  | Tickets - Tipo de letra para la cabecera 1 |
| `CTT1TPV` | Texto corto | 255 |  | Tickets - Texto para la cabecera 1 |
| `CTI2TPV` | Entero | 2 |  | Tickets - Tipo de impresión para la cabecera 2 |
| `CTL2TPV` | Entero | 2 |  | Tickets - Tipo de letra para la cabecera 2 |
| `CTT2TPV` | Texto corto | 255 |  | Tickets - Texto para la cabecera 2 |
| `CTI3TPV` | Entero | 2 |  | Tickets - Tipo de impresión para la cabecera 3 |
| `CTL3TPV` | Entero | 2 |  | Tickets - Tipo de letra para la cabecera 3 |
| `CTT3TPV` | Texto corto | 255 |  | Tickets - Texto para la cabecera 3 |
| `CTI4TPV` | Entero | 2 |  | Tickets - Tipo de impresión para la cabecera 4 |
| `CTL4TPV` | Entero | 2 |  | Tickets - Tipo de letra para la cabecera 4 |
| `CTT4TPV` | Texto corto | 255 |  | Tickets - Texto para la cabecera 4 |
| `CTI5TPV` | Entero | 2 |  | Tickets - Tipo de impresión para la cabecera 5 |
| `CTL5TPV` | Entero | 2 |  | Tickets - Tipo de letra para la cabecera 5 |
| `CTT5TPV` | Texto corto | 255 |  | Tickets - Texto para la cabecera 5 |
| `LOGTPV` | Texto corto | 255 |  | Tickets - Logotipo para la cabecera |
| `ANGTPV` | Entero largo | 4 |  | Tickets - Ancho del logotipo |
| `ALGTPV` | Entero largo | 4 |  | Tickets - Alto del logotipo |
| `PXGTPV` | Entero largo | 4 |  | Tickets - Eje X para el logotipo |
| `PYGTPV` | Entero largo | 4 |  | Tickets - Eje Y para el logotipo |
| `ICCTPV` | Entero | 2 |  | Tickets - Imprimir cabecera del cliente |
| `PTI1TPV` | Entero | 2 |  | Tickets - Tipo de impresión para el pie 1 |
| `PTL1TPV` | Entero | 2 |  | Tickets - Tipo de letra para el pie 1 |
| `PTT1TPV` | Texto corto | 255 |  | Tickets - Texto para el pie 1 |
| `PTI2TPV` | Entero | 2 |  | Tickets - Tipo de impresión para el pie 2 |
| `PTL2TPV` | Entero | 2 |  | Tickets - Tipo de letra para el pie 2 |
| `PTT2TPV` | Texto corto | 255 |  | Tickets - Texto para el pie 2 |
| `PTI3TPV` | Entero | 2 |  | Tickets - Tipo de impresión para el pie 3 |
| `PTL3TPV` | Entero | 2 |  | Tickets - Tipo de letra para el pie 3 |
| `PTT3TPV` | Texto corto | 255 |  | Tickets - Texto para el pie 3 |
| `PTI4TPV` | Entero | 2 |  | Tickets - Tipo de impresión para el pie 4 |
| `PTL4TPV` | Entero | 2 |  | Tickets - Tipo de letra para el pie 4 |
| `PTT4TPV` | Texto corto | 255 |  | Tickets - Texto para el pie 4 |
| `PTI5TPV` | Entero | 2 |  | Tickets - Tipo de impresión para el pie 5 |
| `PTL5TPV` | Entero | 2 |  | Tickets - Tipo de letra para el pie 5 |
| `PTT5TPV` | Texto corto | 255 |  | Tickets - Texto para el pie 5 |
| `PTI6TPV` | Entero | 2 |  | Tickets - Tipo de impresión para el pie 6 |
| `PTL6TPV` | Entero | 2 |  | Tickets - Tipo de letra para el pie 6 |
| `PTT6TPV` | Texto corto | 255 |  | Tickets - Texto para el pie 6 |
| `PTI7TPV` | Entero | 2 |  | Tickets - Tipo de impresión para el pie 7 |
| `PTL7TPV` | Entero | 2 |  | Tickets - Tipo de letra para el pie 7 |
| `PTT7TPV` | Texto corto | 255 |  | Tickets - Texto para el pie 7 |
| `PTI8TPV` | Entero | 2 |  | Tickets - Tipo de impresión para el pie 8 |
| `PTL8TPV` | Entero | 2 |  | Tickets - Tipo de letra para el pie 8 |
| `PTT8TPV` | Texto corto | 255 |  | Tickets - Texto para el pie 8 |
| `PTI9TPV` | Entero | 2 |  | Tickets - Tipo de impresión para el pie 9 |
| `PTL9TPV` | Entero | 2 |  | Tickets - Tipo de letra para el pie 9 |
| `PTT9TPV` | Texto corto | 255 |  | Tickets - Texto para el pie 9 |
| `PTI10TPV` | Entero | 2 |  | Tickets - Tipo de impresión para el pie 10 |
| `PTL10TPV` | Entero | 2 |  | Tickets - Tipo de letra para el pie 10 |
| `PTT10TPV` | Texto corto | 255 |  | Tickets - Texto para el pie 10 |
| `CTIV1TPV` | Entero | 2 |  | Vales - Tipo de impresión para la cabecera 1 |
| `CTTV1TPV` | Texto corto | 255 |  | Vales - Texto de impresión para la cabecera 1 |
| `CTIV2TPV` | Entero | 2 |  | Vales - Tipo de impresión para la cabecera 2 |
| `CTTV2TPV` | Texto corto | 255 |  | Vales - Texto de impresión para la cabecera 2 |
| `CTIV3TPV` | Entero | 2 |  | Vales - Tipo de impresión para la cabecera 3 |
| `CTTV3TPV` | Texto corto | 255 |  | Vales - Texto de impresión para la cabecera 3 |
| `CTIV4TPV` | Entero | 2 |  | Vales - Tipo de impresión para la cabecera 4 |
| `CTTV4TPV` | Texto corto | 255 |  | Vales - Texto de impresión para la cabecera 4 |
| `CTIV5TPV` | Entero | 2 |  | Vales - Tipo de impresión para la cabecera 5 |
| `CTTV5TPV` | Texto corto | 255 |  | Vales - Texto de impresión para la cabecera 5 |
| `PTIV1TPV` | Entero | 2 |  | Vales - Tipo de impresión para el pie 1 |
| `PTTV1TPV` | Texto corto | 255 |  | Vales - Texto de impresión para el pie 1 |
| `PTIV2TPV` | Entero | 2 |  | Vales - Tipo de impresión para el pie 2 |
| `PTTV2TPV` | Texto corto | 255 |  | Vales - Texto de impresión para el pie 2 |
| `PTIV3TPV` | Entero | 2 |  | Vales - Tipo de impresión para el pie 3 |
| `PTTV3TPV` | Texto corto | 255 |  | Vales - Texto de impresión para el pie 3 |
| `PTIV4TPV` | Entero | 2 |  | Vales - Tipo de impresión para el pie 4 |
| `PTTV4TPV` | Texto corto | 255 |  | Vales - Texto de impresión para el pie 4 |
| `IEVTPV` | Entero | 2 |  | Imprimir cabecera con los datos de la empresa |
| `TRDTPV` | Entero | 2 |  | Traducir textos documentos |
| `ITRTPV` | Entero | 2 |  | Imprimir texto Ticket Regalo |
| `SCPTPV` | Entero | 2 |  | Solicitar código postal |

---

## T_TTF

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODTTF` | Entero largo | 4 | ✓ | Código |
| `NOMTTF` | Texto corto | 100 |  | Nombre de la tarjeta |
| `ATATTF` | Entero | 2 |  | Aplicar una tarifa |
| `TARTTF` | Entero | 2 |  | Tarifa |
| `ATETTF` | Entero | 2 |  | Aplicar tarifa especial de precios |
| `ACETTF` | Entero | 2 |  | Aplicar condiciones especiales de un cliente |
| `CLITTF` | Entero largo | 4 |  | Cliente |
| `ADTTTF` | Entero | 2 |  | Aplicar los descuentos de un tipo de cliente |
| `TCLTTF` | Texto corto | 3 |  | Tipo de cliente |
| `ADFTTF` | Entero | 2 |  | Aplicar un descuento fijo |
| `DTFTTF` | Moneda | 8 |  | Porcentaje descuento fijo |
| `FOATTF` | Entero | 2 |  | Forma de acumular: 0=Porcentaje de venta; 1=Por familia/artículo |
| `PACTTF` | Moneda | 8 |  | Porcentaje a acumular |
| `TACTTF` | Entero | 2 |  | Tipo de acumulado: 0=Puntos; 1=Saldo; 2=Personalizar |
| `UDATTF` | Entero | 2 |  | Utilizar decimales en el acumulado |
| `IAVTTF` | Entero | 2 |  | Imprimir en el ticket los puntos/saldos acumulados de esa venta |
| `IATTTF` | Entero | 2 |  | Imprimir en el ticket los puntos/saldos acumulados de la tarjeta |
| `COBTTF` | Entero | 2 |  | Permitir canjear como parte del cobro de un ticket |
| `LIMTTF` | Entero | 2 |  | Acumular solo en ventas superiores a |
| `IMMTTF` | Entero | 2 |  | Importe mínimo de la venta |

---

## T_TUR

**Registros:** 0

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `CODTUR` | Entero | 2 | ✓ | Código |
| `DESTUR` | Texto corto | 100 |  | Descripción |
| `HINTUR` | Texto corto | 30 |  | Hora inicial |
| `HFITUR` | Texto corto | 30 |  | Hora final |

---

## f_ant_lan

**Registros:** 10248

| Campo | Tipo | Tamaño | Requerido | Descripción |
|-------|------|--------|-----------|-------------|
| `regant` | Doble | 8 |  |  |
| `codant` | Doble | 8 |  |  |
| `codant1` | Doble | 8 |  |  |
| `cliant` | Doble | 8 |  |  |
| `posant` | Doble | 8 |  |  |
| `lotant` | Doble | 8 |  |  |
| `cupant` | Doble | 8 |  |  |
| `impant` | Doble | 8 |  |  |
| `porant` | Doble | 8 |  |  |
| `opeant` | Texto corto | 255 |  |  |
| `estant` | Doble | 8 |  |  |
| `docant` | Doble | 8 |  |  |
| `tdoant` | Doble | 8 |  |  |
| `cdoant` | Doble | 8 |  |  |
| `sdoant` | Doble | 8 |  |  |
| `obsant` | Texto corto | 255 |  |  |
| `criant` | Doble | 8 |  |  |
| `cajant` | Doble | 8 |  |  |
| `tpvidant` | Texto corto | 255 |  |  |

---
