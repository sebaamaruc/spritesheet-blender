# Agent Context

PCS-Version: 1
PCS-Template-Version: 1.0.0
Ultima actualizacion: 2026-07-04
Actualizado por: Codex

## Resumen Actual

El usuario decidio reiniciar `spritesheet-blender` como addon V2 mantenible, distribuible y extensible. El addon generado actual no debe repararse incrementalmente como base principal. Debe preservarse por Git, normalizarse la documentacion base y reconstruirse desde una arquitectura limpia.

El plan gobernante aprobado es `docs/plans/reinicio-v2-master-plan.md`. Este master plan no es ejecutable de forma monolitica: cada fase o subfase que se beneficie de precision debe tener un plan especifico aprobado antes de ejecutarse.

## Tarea Activa

Revisar y aprobar el plan propuesto de Fase 6 validacion/distribucion.

## Proximo Paso Recomendado

Revisar `docs/plans/reinicio-v2-fase-6-validacion-distribucion.md`. Si el usuario lo aprueba, persistirlo como plan activo aprobado antes de ejecutarlo.

## Estado

- PCS bootstrap: completado
- Contexto inicial del proyecto: completado
- Auditoria tecnica post-Workspace V1: historica
- Master plan de reinicio V2: aprobado
- Fase 1 preservacion del estado actual: validada
- Fase 2 documentacion base V2: validada
- Fase 3 limpieza del arbol activo: validada
- Fase 4 scaffold limpio del addon V2: validada
- Fase 5 rector vertical slices original: reemplazado parcialmente por workspace-root
- Fase 5 workspace-root rector: aprobado
- Fase 5a data model y persistencia original: validada, reemplazada por workspace-root
- Fase 5b gestion de clips original: validada, reemplazada por workspace-root
- Fase 5c preview cache original: validada, reemplazada por workspace-root
- Fase 5c.1 auditoria workspace-root: validada
- Fase 5a workspace-root data model y persistencia: validada
- Fase 5b workspace-root gestion de workspaces y clips: validada
- Fase 5c workspace-root preview cache: validada
- Fase 5d workspace-root selector visual minimo: validada
- Fase 5e workspace-root playback preview: validada
- Spike selector modal y preview modes: validado
- Fase 5e1 selector/playback UX: validada; quedan ajustes menores de UI no bloqueantes para pulido futuro
- Fase 5f render final workspace-aware: funcionalidad validada por usuario; flujo publico separado reemplazado por opcion integrada en 5g
- Fase 5g export spritesheet y JSON: validada por usuario, incluidas correcciones UI/naming/atajos
- Fase 6 validacion final y distribucion: plan propuesto
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
- `docs/plans/reinicio-v2-fase-5-vertical-slices.md`
- `docs/plans/reinicio-v2-fase-5-workspace-root-vertical-slices.md`
- `docs/plans/reinicio-v2-fase-5a-data-model-persistencia.md`
- `docs/plans/reinicio-v2-fase-5a-workspace-data-model-persistencia.md`
- `docs/plans/reinicio-v2-fase-5b-workspace-clip-management.md`
- `docs/plans/reinicio-v2-fase-5c-workspace-preview-cache.md`
- `docs/plans/reinicio-v2-fase-5d-visual-selector-minimo.md`
- `docs/plans/reinicio-v2-fase-5e-playback-preview.md`
- `docs/plans/reinicio-v2-fase-5e1-spike-selector-modal-preview-modes.md`
- `docs/plans/reinicio-v2-fase-5e1-selector-playback-ux.md`
- `docs/plans/reinicio-v2-fase-5f-render-final-workspace-aware.md`
- `docs/plans/reinicio-v2-fase-5g-export-spritesheet-json.md`
- `spritesheet_frame_selector/export/layout.py`
- `spritesheet_frame_selector/export/metadata.py`
- `spritesheet_frame_selector/export/composer.py`
- `spritesheet_frame_selector/operators/export.py`
- `tests/test_export_layout_metadata.py`
- `spritesheet_frame_selector/core/render_state.py`
- `spritesheet_frame_selector/core/validation.py`
- `spritesheet_frame_selector/render/renderer.py`
- `tests/test_render_state.py`
- `docs/plans/reinicio-v2-fase-5b-gestion-clips.md`
- `docs/plans/reinicio-v2-fase-5c-preview-cache.md`
- `docs/plans/reinicio-v2-fase-5c1-auditoria-decisiones-workspace-root.md`
- `docs/specs/workspace_root_decisions.md`
- `docs/specs/workspace_root_refactor_evaluation.md`
- `docs/specs/selector_modal_preview_modes_spike.md`
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

Sin plan activo ejecutable. Plan propuesto pendiente de revision: `docs/plans/reinicio-v2-fase-6-validacion-distribucion.md`

## Decisiones Vigentes Relevantes

- `DEC-0001`: PCS persiste contexto operativo en el repositorio.
- Reinicio V2: preservar estado actual por Git, limpiar el arbol activo despues de preservacion, reconstruir desde documentacion y arquitectura V2.
- Los planes de fase/subfase son los unicos ejecutables; el master plan gobierna orden, restricciones y criterios.
- Fase 2: `docs/specs/mvp.md` quedo historico/no operativo; el contrato vigente de producto y MVP vive en los documentos V2.
- Fase 3: el addon V1, tests legacy, scratch y residuos locales fueron retirados del arbol activo; el estado V1 solo debe consultarse desde Git/archive si hace falta.
- Fase 4: existe scaffold V2 minimo; no contiene features de producto fuera del lifecycle basico.
- Fase 5a: existe modelo persistente V2 con clips, frames, export settings y estado de escena.
- Fase 5b: existe gestion basica de clips con operadores Add/Remove/Duplicate/Select, UIList nativa, panel de edicion y persistencia validada en Blender background.
- Fase 5c: existe preview cache por clip con Generate/Refresh/Clear, cache key estable, paths administrados y persistencia de seleccion validada en Blender background.
- Fase 5e: existe playback preview runtime sobre previews cacheados y seleccion persistente, con Play/Pause/Stop, timer unico y cleanup en unregister.
- Fase 5a/5b/5c originales se conservan como historial validado, pero fueron reemplazadas como base vigente por workspace-root.
- Fase 5a workspace-root: modelo persistente validado con `Scene.spritesheet_state.workspaces`.
- DEC-0006: workspace es raiz de dominio en V2; 5a/5b/5c quedan sujetos a revision antes de continuar con selector visual.
- DEC-0007: docs V2 ya declaran workspace-root como contrato operativo.
- DEC-0008: preview/render/export deben resolver camara y collections efectivas desde workspace + clip.
- DEC-0009: rehacer Fase 5 desde scaffold para workspace-root.
- DEC-0010: antes de render final se debe corregir selector/playback con superficie modal/custom, `selector_mode` persistente y preview modes persistentes.

## Riesgos Abiertos

- Fase 6 puede descubrir bugs de packaging/lifecycle que requieran correcciones menores antes de distribuir.
- Blender background dentro del sandbox crashea antes de ejecutar Python; fuera del sandbox fue rechazado por politica del entorno actual en validaciones previas.
- La limpieza automatica de `__pycache__` generados por validacion fue rechazada por politica del entorno; no se intento una via alternativa.

## Bloqueos

Ninguno detectado para ejecutar la auditoria workspace-root.

## Validaciones Pendientes

- Revisar/aprobar `docs/plans/reinicio-v2-fase-6-validacion-distribucion.md`.
