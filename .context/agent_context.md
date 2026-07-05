# Agent Context

PCS-Version: 1
PCS-Template-Version: 1.0.0
Ultima actualizacion: 2026-07-05
Actualizado por: Codex

## Resumen Actual

El usuario decidio reiniciar `spritesheet-blender` como addon V2 mantenible, distribuible y extensible. El addon generado actual no debe repararse incrementalmente como base principal. Debe preservarse por Git, normalizarse la documentacion base y reconstruirse desde una arquitectura limpia.

El plan gobernante aprobado es `docs/plans/reinicio-v2-master-plan.md`. Este master plan no es ejecutable de forma monolitica: cada fase o subfase que se beneficie de precision debe tener un plan especifico aprobado antes de ejecutarse.

## Tarea Activa

Validar en Blender GUI el plan `docs/plans/reinicio-v2-fase-6a-hito3-selector-scroll.md`, implementado para corregir M6: thumbnails ocultos sin scroll en el selector visual.

## Proximo Paso Recomendado

Ejecutar en Blender GUI la validacion de scroll: abrir un clip con mas frames que celdas visibles, usar rueda dentro del panel para ver frames posteriores, confirmar que el click/toggle afecta el frame correcto y que la rueda fuera del panel sigue pasando al viewport. Despues resolver V5 de `docs/plans/reinicio-v2-fase-6a-validacion-hito1-selector-modal-lifecycle.md`.

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
- Subplanes implementados de Fase 5: archivados en `docs/archive/`
- Auditoria tecnica post-Fase 5: fuente vigente para Fase 6
- Fase 6 correcciones de auditoria tecnica: plan rector aprobado; D1 y D2 confirmadas por el usuario
- Fase 6a selector modal y lifecycle runtime: hito 1 implementado para C1, C2 y B5; validacion Blender pendiente
- Fase 6a validacion hito 1 selector modal/lifecycle: validaciones automaticas y Blender background pasadas; validacion GUI V2-V5 pendiente
- Fase 6a hito 3 selector scroll: implementado para M6; validacion Blender GUI pendiente
- Fase 6b0 preview desde camara efectiva: validada por el usuario
- Fase 7 validacion final y distribucion: plan propuesto, diferido hasta validar Fase 6
- Ejecucion de reinicio V2: pendiente de planes especificos por fase

## Archivos Relevantes Ahora

- `AGENTS.md`
- `.context/agent_context.md`
- `.context/index.md`
- `.context/handoff.md`
- `.context/decisions.md`
- `docs/plans/reinicio-v2-master-plan.md`
- `docs/technical-audit.md`
- `docs/plans/reinicio-v2-fase-6-correcciones-auditoria-tecnica.md`
- `docs/plans/reinicio-v2-fase-6a-selector-modal-lifecycle.md`
- `docs/plans/reinicio-v2-fase-6a-validacion-hito1-selector-modal-lifecycle.md`
- `docs/plans/reinicio-v2-fase-6a-hito3-selector-scroll.md`
- `docs/plans/reinicio-v2-fase-6b0-preview-camera-viewport.md`
- `docs/plans/reinicio-v2-fase-7-validacion-distribucion.md`
- `docs/archive/reinicio-v2-fase-1-preservacion.md`
- `docs/archive/reinicio-v2-fase-2-documentacion-base.md`
- `docs/archive/reinicio-v2-fase-3-limpieza-arbol-activo.md`
- `docs/archive/reinicio-v2-fase-4-scaffold-addon-v2.md`
- `docs/archive/reinicio-v2-fase-5-vertical-slices.md`
- `docs/archive/reinicio-v2-fase-5-workspace-root-vertical-slices.md`
- `docs/archive/reinicio-v2-fase-5a-data-model-persistencia.md`
- `docs/archive/reinicio-v2-fase-5a-workspace-data-model-persistencia.md`
- `docs/archive/reinicio-v2-fase-5b-gestion-clips.md`
- `docs/archive/reinicio-v2-fase-5b-workspace-clip-management.md`
- `docs/archive/reinicio-v2-fase-5c-preview-cache.md`
- `docs/archive/reinicio-v2-fase-5c-workspace-preview-cache.md`
- `docs/archive/reinicio-v2-fase-5c1-auditoria-decisiones-workspace-root.md`
- `docs/archive/reinicio-v2-fase-5d-visual-selector-minimo.md`
- `docs/archive/reinicio-v2-fase-5e-playback-preview.md`
- `docs/archive/reinicio-v2-fase-5e1-spike-selector-modal-preview-modes.md`
- `docs/archive/reinicio-v2-fase-5e1-selector-playback-ux.md`
- `docs/archive/reinicio-v2-fase-5f-render-final-workspace-aware.md`
- `docs/archive/reinicio-v2-fase-5g-export-spritesheet-json.md`
- `spritesheet_frame_selector/export/layout.py`
- `spritesheet_frame_selector/export/metadata.py`
- `spritesheet_frame_selector/export/composer.py`
- `spritesheet_frame_selector/operators/export.py`
- `tests/test_export_layout_metadata.py`
- `spritesheet_frame_selector/core/render_state.py`
- `spritesheet_frame_selector/core/validation.py`
- `spritesheet_frame_selector/render/renderer.py`
- `tests/test_render_state.py`
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

`docs/plans/reinicio-v2-fase-6a-hito3-selector-scroll.md`

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
- Fase 6 D1: eliminar el subsistema de render cache final para MVP.
- Fase 6 D2: prohibir frames negativos en MVP agregando `min=0` a `frame_start`/`frame_end`.
- Fase 6b0: previews `SOLID`/`MATERIAL` deben forzar temporalmente Camera View del `VIEW_3D` usado por `render.opengl(view_context=True)` para respetar la camara efectiva sin perder el shading de viewport.

## Riesgos Abiertos

- Fase 7 puede descubrir bugs de packaging/lifecycle que requieran correcciones menores antes de distribuir.
- `docs/technical-audit.md` detecto hallazgos criticos/altos que deben corregirse o clasificarse antes de distribucion.
- Blender background dentro del sandbox crashea antes de ejecutar Python; fuera del sandbox fue rechazado por politica del entorno actual en validaciones previas.
- La limpieza automatica de `__pycache__` generados por validacion fue rechazada por politica del entorno; no se intento una via alternativa.

## Bloqueos

Ninguno detectado para ejecutar la auditoria workspace-root.

## Validaciones Pendientes

- Validar en Blender GUI `docs/plans/reinicio-v2-fase-6a-hito3-selector-scroll.md`.
- Resolver V5 de `docs/plans/reinicio-v2-fase-6a-validacion-hito1-selector-modal-lifecycle.md`.
