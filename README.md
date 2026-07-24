# Maza · Cobranzas de Caja

Módulo Odoo 19 para Electricidad Maza: cobranza rápida de facturas de venta
industrial desde la caja del mostrador. Ver la propuesta en
[`docs/propuesta-cobranzas.md`](docs/propuesta-cobranzas.md).

## Estado

**v0.1 — esqueleto MVP, SIN probar en un Odoo real.** Escrito contra la
estructura relevada de la instancia de Maza (Odoo SH 19, l10n_ar +
l10n_latam_check). Necesita validarse en staging antes de mostrar.

## Qué hace

- Menú `Contabilidad ▸ Clientes ▸ Cobranza de Caja` (grupo "Cobranzas de Caja")
- Wizard: cliente → saldo + facturas pendientes → facturas puntuales o al
  saldo → método de cobro → Cobrar.
- Cobro normal: crea `account.payment` posteado y concilia contra las
  facturas elegidas (por orden de vencimiento).
- Cobro con cheque: abre el formulario nativo de pago prefilleado con el
  método `new_third_party_checks` → la cajera carga número/banco/vencimiento
  y el cheque queda en la cartera de terceros (nada reimplementado).
- Campo nuevo `maza_canal` en `account.payment` (mostrador / caja_industria /
  administración) → es lo que va a leer el tablero de cierre para la
  conciliación de lote por canal.

## Cómo subirlo a staging (Odoo SH)

1. Pedir acceso al repo GitHub del proyecto Odoo SH de Maza.
2. Crear rama `staging-cobranzas` desde `main` y copiar la carpeta
   `maza_caja_cobranzas/` a la raíz del repo (o al dir de addons custom).
3. Push → Odoo SH construye automáticamente un entorno de staging con copia
   de la base de producción.
4. En staging: Apps ▸ actualizar lista ▸ instalar "Maza · Cobranzas de Caja".
5. Asignar el grupo "Cobranzas de Caja" a Sabrina, Verónica y Nathalie.
6. Probar los 3 flujos: factura puntual / al saldo / cheque diferido.

## Uso como submódulo git

Este repo contiene el addon `maza_caja_cobranzas/` en la raíz (estilo repo de
addons OCA). Para consumirlo desde otro proyecto Odoo:

```bash
git submodule add git@github.com:santi-tojo/maza-cobranzas.git addons/maza-cobranzas
git submodule update --init --recursive
```

Luego agregar `addons/maza-cobranzas` al `addons_path` de Odoo (o dejar que
Odoo SH lo descubra si el submódulo cuelga de la raíz del repo del proyecto).

## Decisión de diseño: mismos diarios que el PDV

**NO se crean diarios nuevos.** Las cobranzas industriales usan los MISMOS
diarios y métodos que el punto de venta (mismo posnet → Banco Macro, mismo
QR → Mercado Pago, mismo Efectivo): el posnet y el QR son físicamente
compartidos entre canales. La separación mostrador/industria la da el campo
`maza_canal` de cada pago — no la configuración contable.

## Pendientes conocidos (para la fase de pruebas)

- [ ] Validar los `implied_ids` del grupo (que la cajera no vea de más).
- [ ] Ajustar el tablero de cierre para leer `maza_canal` cuando haya datos.
- [ ] Revisar nombres de campos en v19 real (`memo` vs `ref`) al instalar.
- [ ] Cobro parcial de una factura puntual: hoy concilia hasta agotar el
      importe (comportamiento estándar) — confirmar con las cajeras.
