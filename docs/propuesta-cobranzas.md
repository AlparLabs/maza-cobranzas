# AlparData Implementación Odoo

## 🚀 Propuesta: Módulo de Cobranzas de Caja — Electricidad Maza

**Cliente:** Electricidad Maza SRL · **Atención:** Claudio y Simón · **Fecha:** Julio 2026

---

## 1. Propósito del Proyecto

Electricidad Maza opera con dos canales de venta que comparten los mismos medios de cobro físicos (posnet Payway, QR de Mercado Pago, efectivo de la caja):

- **Venta mostrador**: transcurre por el Punto de Venta y se cobra en la caja.
- **Venta industrial**: cotización → orden de venta → factura → entrega → cobranza en cuenta corriente (transferencia, cheque, o pago en la caja del mostrador).

El problema detectado en la operación diaria: cuando un cliente del canal industrial paga su factura en la caja (QR, tarjeta, efectivo), ese cobro se mezcla con la venta de mostrador y **la rendición del cierre de caja no cierra contra los lotes** de Mercado Pago y Payway.

El objetivo es que la cajera pueda **cobrar facturas de venta industrial con la misma facilidad que una venta de mostrador**, que cada cobro quede trazado por canal, y que el cierre diario consolide ambos mundos.

---

## 2. Lo que ya está resuelto (sin costo adicional)

Como parte del acompañamiento venimos trabajando el cierre de caja en el tablero online, que hoy ya resuelve la **consolidación y trazabilidad** del cierre:

- ✅ **Conciliación de lote diaria**: tabla Mostrador + Cobranza industria por concepto unificado (Efectivo, Mercado Pago, Transferencia MP, Payway, Cheques, Bancos). El lote de MP del día cierra contra un solo número.
- ✅ **Cierre de caja completo**: cobros por método con cantidad de operaciones, retiros de efectivo, devoluciones de NC separadas en sus tres casos (reintegro en dinero / reverso por el método original / saldo a cuenta del cliente), comprobantes emitidos (facturas vs NC) y **saldo neto en dinero** de la caja.
- ✅ **Cartera de cheques de terceros**: ya funciona nativa en Odoo (recibir diferidos → cartera → depositar o endosar a proveedores). Hoy: 47 cheques por $326M correctamente registrados.
- ✅ Estado de cuenta corriente por cliente con antigüedad de saldos y saldos a favor.

> **Tip AlparData:** antes de desarrollar, siempre agotamos lo nativo. La carga del cobro industrial ya se puede hacer hoy con "Registrar pago" desde la factura — lo que proponemos abajo es hacerla **más simple y a prueba de errores** para el ritmo de una caja.

---

## 3. Fase 1: Módulo "Cobranzas de Caja" (MVP)

Una pantalla única, pensada para la cajera, dentro de Odoo:

1. **Buscar el cliente** → ve su saldo de cuenta corriente y sus facturas pendientes.
2. **Elegir qué cobra**: una o varias facturas puntuales, **o** imputar al saldo de la cuenta.
3. **Elegir cómo cobra**, con los mismos conceptos del mostrador:
   - Efectivo · Mercado Pago (QR) · Transferencia · Tarjeta (posnet Payway)
   - **Cheque físico o Echeq diferido** → carga número, banco y vencimiento, y el cheque queda automáticamente en la **cartera de terceros** (para luego depositar o endosar).
4. El cobro queda registrado con **etiqueta de canal** (mostrador / caja-industria / administración), que es lo que permite que el cierre de lote del tablero cierre solo.

**Incluye:**
- Perfil de acceso "Cajera" (puede cobrar; no puede tocar contabilidad).
- Se usan los **mismos diarios y métodos de cobro que el PDV** (mismo posnet, mismo QR, mismo efectivo): la separación entre canales la da la etiqueta de canal de cada cobro, sin duplicar configuración.
- Integración con el tablero de cierre: la conciliación de lote leerá la etiqueta de canal.
- Capacitación a Sabrina, Verónica y Nathalie.

**Fuera de alcance de esta fase:** modificar el frontend del Punto de Venta (es la pieza más frágil de Odoo en cada actualización; no hace falta tocarla para resolver el problema).

---

## 4. Modalidad de trabajo

1. **Desarrollo y pruebas en entorno de test** (rama de staging de Odoo SH, con copia de los datos reales): validamos con las cajeras el flujo completo sin riesgo para producción.
2. **UAT con casos reales**: un cierre de caja de punta a punta contra los lotes de MP y Payway del día.
3. **Puesta en producción + acompañamiento** las primeras dos semanas de uso.

📅 **Cronograma estimado:** 2–3 semanas desde el kick-off (1 semana de desarrollo, 1 de pruebas en test con las cajeras, puesta en marcha).

---

## 5. Inversión

Honorarios según cotización adjunta. Como siempre, el entorno de prueba, los ajustes del tablero de cierre y la capacitación de los usuarios están incluidos — para AlparData no son "extras": son lo que hace que Odoo se use bien.

---

*AlparData · Joaquín Tojo · joaquin@alpardata.com.ar*
