# Agent Context

PCS-Version: 1
PCS-Template-Version: 1.0.0
Ultima actualizacion: 2026-07-03
Actualizado por: Codex

## Resumen Actual

El usuario decidio reiniciar `spritesheet-blender` como addon V2 mantenible, distribuible y extensible. El addon generado actual no debe repararse incrementalmente como base principal. Debe preservarse por Git, normalizarse la documentacion base y reconstruirse desde una arquitectura limpia.

El plan gobernante aprobado es `docs/plans/reinicio-v2-master-plan.md`. Este master plan no es ejecutable de forma monolitica: cada fase o subfase que se beneficie de precision debe tener un plan especifico aprobado antes de ejecutarse.

## Tarea Activa

Preparar el plan rector de Fase 5: implementacion por vertical slices.

## Proximo Paso Recomendado

Crear `docs/plans/reinicio-v2-fase-5-vertical-slices.md` como plan propuesto detallado. No implementar slices ni features de producto hasta que ese plan y/o el subplan correspondiente sean aprobados explicitamente.

## Estado

- PCS bootstrap: completado
- Contexto inicial del proyecto: completado
- Auditoria tecnica post-Workspace V1: historica
- Master plan de reinicio V2: aprobado
- Fase 1 preservacion del estado actual: validada
- Fase 2 documentacion base V2: validada
- Fase 3 limpieza del arbol activo: validada
- Fase 4 scaffold limpio del addon V2: validada
- Ejecucion de reinicio V2: pendiente de planes especificos por fase

## Archivos Relevantes Ahora

- `AGENTS.md`
- `.context/agent_context.md`
- `.context/index.md`
- `.context/handoff.md`
- `.context/decisions.md`
- `docs/plans/reinicio-v2-master-plan.md`
- `docs/plans/reinicio-v2-fase-1-preservacion.md`
- `docs/plans/reinicio-v2-fase-2-documentacion-base.md`
- `docs/plans/reinicio-v2-fase-3-limpieza-arbol-activo.md`
- `docs/plans/reinicio-v2-fase-4-scaffold-addon-v2.md`
- `spritesheet_frame_selector/`
- `docs/specs/PROJECT_VISION.md`
- `docs/specs/mvp.md`
- `docs/specs/product_requirements.md`
- `docs/specs/mvp_v2.md`
- `docs/architecture/addon_architecture.md`
- `docs/design/visual_selector_strategy.md`
- `docs/specs/validation_plan.md`
- `docs/archive/mvp-original.md`
- `docs/archive/source-goals-v1.md`
- `docs/archive/source-goals-proposed-v1.md`
- `docs/archive/audit_report.md`

## Plan Activo

`docs/plans/reinicio-v2-master-plan.md`

## Decisiones Vigentes Relevantes

- `DEC-0001`: PCS persiste contexto operativo en el repositorio.
- Reinicio V2: preservar estado actual por Git, limpiar el arbol activo despues de preservacion, reconstruir desde documentacion y arquitectura V2.
- Los planes de fase/subfase son los unicos ejecutables; el master plan gobierna orden, restricciones y criterios.
- Fase 2: `docs/specs/mvp.md` quedo historico/no operativo; el contrato vigente de producto y MVP vive en los documentos V2.
- Fase 3: el addon V1, tests legacy, scratch y residuos locales fueron retirados del arbol activo; el estado V1 solo debe consultarse desde Git/archive si hace falta.
- Fase 4: existe scaffold V2 minimo; no contiene features de producto fuera del lifecycle basico.

## Riesgos Abiertos

- Falta validacion manual GUI del panel minimo en Blender; la validacion background de import/register/unregister ya paso.
- Fase 5 debe respetar vertical slices y no saltar directamente a features amplias.

## Bloqueos

Ninguno detectado para preparar el plan propuesto de Fase 5.

## Validaciones Pendientes

- Preparar y aprobar `docs/plans/reinicio-v2-fase-5-vertical-slices.md` antes de implementar features de producto.
