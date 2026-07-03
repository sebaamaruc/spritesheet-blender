# Handoff

Ultima actualizacion: 2026-07-03

Hay handoff activo para continuar la planificacion del reinicio V2.

## Situacion

El usuario aprobo guardar un master plan para reiniciar `spritesheet-blender` como addon V2 mantenible, distribuible y extensible. El master plan aprobado vive en `docs/plans/reinicio-v2-master-plan.md`.

Este master plan no debe ejecutarse como plan monolitico. Cada fase o subfase que se beneficie de precision debe tener un plan especifico antes de ejecutarse. No implementar codigo ni limpiar archivos desde el master plan directamente.

La Fase 1 fue ejecutada y validada en `docs/plans/reinicio-v2-fase-1-preservacion.md`. El estado trackeado previo quedo preservado por Git en la rama `archive/generated-addon-v1` y el tag anotado `archive/generated-addon-v1-2026-07-03`.

La Fase 2 fue ejecutada y validada en `docs/plans/reinicio-v2-fase-2-documentacion-base.md`. La documentacion operativa V2 vigente quedo separada en:

- `docs/specs/product_requirements.md`
- `docs/specs/mvp_v2.md`
- `docs/architecture/addon_architecture.md`
- `docs/design/visual_selector_strategy.md`
- `docs/specs/validation_plan.md`

El MVP historico original fue preservado en `docs/archive/mvp-original.md`. `docs/specs/mvp.md` quedo como puntero historico/no operativo.

La Fase 3 fue ejecutada y validada en `docs/plans/reinicio-v2-fase-3-limpieza-arbol-activo.md`. El addon V1, tests legacy, scratch y residuos locales fueron retirados del arbol activo. Las metas V1 de `docs/source/goals.md` y `docs/source/goals.proposed.md` fueron archivadas en `docs/archive/source-goals-v1.md` y `docs/archive/source-goals-proposed-v1.md`.

La Fase 4 fue ejecutada y validada en `docs/plans/reinicio-v2-fase-4-scaffold-addon-v2.md`. Existe scaffold V2 minimo en `spritesheet_frame_selector/` con manifest, registro centralizado, preferencias, propiedad minima de escena y panel minimo. Validaron `compileall`, import/register/unregister con mock minimo de `bpy`, y Blender background real con Blender 5.1.1. Queda pendiente solo validacion manual GUI del panel.

## Proxima Accion Recomendada

Crear `docs/plans/reinicio-v2-fase-5-vertical-slices.md` como plan rector propuesto.

No implementar features de producto hasta tener plan rector de Fase 5 y subplan especifico aprobado.
