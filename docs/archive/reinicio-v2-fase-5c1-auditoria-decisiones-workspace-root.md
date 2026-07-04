# Plan Fase 5c.1 - Auditoria De Decisiones V1 Y Workspace Root

Estado: aprobado
Autoridad: usuario
Modo de ejecucion: ejecutar sin replanificar
Estado De Ejecucion: validado
Referencia superior: `docs/plans/reinicio-v2-master-plan.md`
Plan rector afectado: `docs/plans/reinicio-v2-fase-5-vertical-slices.md`

## Resumen

Pausar el avance a Fase 5d para auditar las decisiones de V1 no trasladadas a los documentos V2, confirmar cuales deben entrar al producto, y redisenar el modelo V2 con workspace como raiz antes de implementar selector visual, playback, render o export.

Decision ya tomada por el usuario:

- Workspace es raiz de dominio en V2.
- No continuar con 5d hasta estudiar impacto.
- Evaluar si la V2 actual puede refactorizarse o si conviene volver al scaffold limpio de Fase 4 y rehacer 5a/5b/5c con workspace-root.

## Proceso Por Fases

### Fase W1 - Auditoria De Decisiones V1

Objetivo:

- Revisar `archive/generated-addon-v1`, `docs/archive/`, `.context/decisions.md` historico y tests V1.
- Extraer decisiones de producto/arquitectura que no esten en docs V2.
- Clasificarlas como:
  - incorporar en V2;
  - descartar;
  - diferir;
  - investigar antes de decidir.

Decisiones ya preclasificadas por el usuario:

- Incorporar workspace como raiz.
- Mantener export settings como fuente unica, pero bajo workspace.
- Reanalizar UI de selector de workspaces; `template_list rows=1` de V1 es aceptable solo si sigue siendo la mejor opcion.
- Analizar default camera/default collections de workspace y overrides por clip.
- Confirmar visibilidad por collections como requisito fuerte para preview/render.
- Incorporar inclusion/exclusion de clips para export.
- Incorporar orden manual de clips.
- Incorporar duplicacion de workspace, pero redisenarla porque V1 no funcionaba bien.
- Incorporar preview/render segun visibilidad efectiva.
- Reinvestigar solucion de preview/material look; probar render nativo si corresponde.
- Incorporar JSON multi-clip secuencial.
- Mantener validaciones de export estrictas.
- Mantener PNG sequence opcional.
- Mantener warnings de dimensiones.

Criterio de termino:

- Documento de auditoria con tabla de decisiones V1 aceptadas, descartadas, diferidas e investigables.

### Fase W2 - Rediseno Documental Workspace-Root

Objetivo:

- Actualizar docs vigentes para reflejar workspace-root:
  - `docs/specs/mvp_v2.md`
  - `docs/architecture/addon_architecture.md`
  - `docs/specs/validation_plan.md`
  - si aplica, `docs/design/visual_selector_strategy.md`
- Registrar decisiones nuevas o reemplazadas en `.context/decisions.md`.

Modelo objetivo preliminar:

```text
Scene
  spritesheet_state: SpriteSheetSceneState

SpriteSheetSceneState
  schema_version
  workspaces: Collection[SpriteSheetWorkspace]
  active_workspace_index

SpriteSheetWorkspace
  id
  name
  default_camera
  default_collections
  clips
  active_clip_index
  export_settings

SpriteSheetClip
  id
  name
  include_in_export
  frame_start
  frame_end
  frame_step
  fps
  use_camera_override
  camera
  use_collection_override
  included_collections
  preview_size
  frames
  active_frame_index
  cache_key
  cache_folder
  cache_dirty
  last_preview_note
```

Criterio de termino:

- Docs V2 dejan de describir `Scene.spritesheet_state.clips` como raiz operativa.
- Workspace-root queda como contrato de producto y arquitectura.

### Fase W3 - Evaluacion Tecnica Refactor Vs Reinicio

Objetivo:

- Comparar dos rutas:
  - refactorizar la V2 actual 5a/5b/5c;
  - volver al scaffold limpio de Fase 4 y rehacer 5a/5b/5c.
- Medir impacto sobre:
  - `properties.py`;
  - `registration.py`;
  - operadores de clips/preview;
  - helpers de cache/path/frame sync;
  - panel/UIList;
  - tests actuales;
  - validaciones Blender background.

Recomendacion esperada:

- Si el refactor toca casi todos los archivos de 5a/5b/5c y requiere mantener compatibilidad temporal sin valor, preferir reinicio desde Fase 4.
- Si helpers puros y tests pueden reaprovecharse limpiamente, proponer refactor controlado.

Criterio de termino:

- Decision explicita documentada: `refactorizar` o `rehacer desde scaffold`.

### Fase W4 - Replanificacion De Vertical Slices

Objetivo:

- Reemplazar o complementar los subplanes 5a/5b/5c con versiones workspace-root.
- Detener 5d hasta que el nuevo 5a workspace-root, gestion workspace/clip y preview-cache workspace-aware esten validados.

Criterio de termino:

- PCS apunta al primer plan ejecutable de reconstruccion workspace-root.

## Reglas

- No implementar selector visual en esta fase.
- No refactorizar codigo en esta fase salvo instruccion explicita posterior.
- No borrar planes 5a/5b/5c; si quedan obsoletos, deben archivarse o marcarse como reemplazados segun reglas PCS.
- No copiar codigo V1 como base; V1 solo informa decisiones, riesgos y criterios.
- Las decisiones aceptadas deben registrarse como decisiones V2, no quedar solo en el chat.

## Validaciones

- Confirmar que `docs/plans/reinicio-v2-fase-5d-visual-selector-minimo.md` no se crea ni se ejecuta durante esta fase.
- Confirmar que PCS deja como siguiente accion ejecutar esta auditoria workspace-root.
- Confirmar que `.context/decisions.md` registra la decision de workspace como raiz.
- Confirmar que `git status --short --ignored` muestra solo cambios documentales/PCS esperados ademas de cambios ya existentes de fases previas.

## Criterio De Termino

La Fase 5c.1 termina cuando:

- existe auditoria documentada de decisiones V1;
- docs V2 se actualizan o queda plan aprobado para actualizarlos;
- se decide refactor vs reinicio desde scaffold;
- PCS apunta al siguiente plan ejecutable correcto;
- 5d permanece detenido hasta resolver workspace-root.

## Proximo Paso Inmediato

Ejecutar `docs/plans/reinicio-v2-fase-5a-workspace-data-model-persistencia.md`.

## Progreso De Ejecucion

- 2026-07-03: W1 ejecutada y validada. Entregable: `docs/specs/workspace_root_decisions.md`.
- 2026-07-03: W2 ejecutada y validada. Documentos actualizados: `docs/specs/mvp_v2.md`, `docs/architecture/addon_architecture.md`, `docs/specs/validation_plan.md`, `docs/design/visual_selector_strategy.md`, `.context/decisions.md`.
- 2026-07-03: W3 ejecutada y validada. Decision: rehacer 5a/5b/5c desde scaffold limpio de Fase 4; detalles en `docs/specs/workspace_root_refactor_evaluation.md`.
- 2026-07-03: W4 ejecutada y validada. Nuevo rector: `docs/plans/reinicio-v2-fase-5-workspace-root-vertical-slices.md`. Primer plan ejecutable: `docs/plans/reinicio-v2-fase-5a-workspace-data-model-persistencia.md`.
- Pendiente: ejecutar 5a workspace-root.
