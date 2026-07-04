# Evaluacion Tecnica W3 - Refactor Vs Reinicio Workspace-Root

Estado: vigente como decision tecnica
Autoridad: `docs/plans/reinicio-v2-fase-5c1-auditoria-decisiones-workspace-root.md`
Fecha: 2026-07-03

## Proposito

Este documento ejecuta W3 del plan `docs/plans/reinicio-v2-fase-5c1-auditoria-decisiones-workspace-root.md`.

Compara dos rutas para adaptar la V2 actual al contrato workspace-root:

- refactorizar la implementacion actual 5a/5b/5c;
- volver al scaffold limpio de Fase 4 y rehacer 5a/5b/5c como slices workspace-root.

No implementa cambios de codigo. Define la recomendacion tecnica para W4.

## Fuentes Revisadas

- `docs/specs/workspace_root_decisions.md`
- `docs/specs/mvp_v2.md`
- `docs/architecture/addon_architecture.md`
- `docs/specs/validation_plan.md`
- `spritesheet_frame_selector/properties.py`
- `spritesheet_frame_selector/registration.py`
- `spritesheet_frame_selector/operators/clips.py`
- `spritesheet_frame_selector/operators/preview.py`
- `spritesheet_frame_selector/ui/panels.py`
- `spritesheet_frame_selector/ui/lists.py`
- `spritesheet_frame_selector/core/clip_state.py`
- `spritesheet_frame_selector/core/cache.py`
- `spritesheet_frame_selector/core/paths.py`
- `spritesheet_frame_selector/core/frame_sync.py`
- `spritesheet_frame_selector/core/frame_math.py`
- `spritesheet_frame_selector/preview/generator.py`
- `tests/test_clip_state.py`
- `tests/test_preview_cache.py`
- `tests/test_frame_math.py`
- Commit scaffold Fase 4: `77bda46`

## Decision

Recomendacion tecnica: rehacer 5a/5b/5c desde el scaffold limpio de Fase 4, reaprovechando selectivamente helpers puros y patrones validados.

No conviene hacer un refactor incremental de la implementacion actual porque el cambio de `Scene.spritesheet_state.clips` a `Scene.spritesheet_state.workspaces -> active_workspace -> clips` atraviesa el modelo, operadores, UI, preview cache, tests y validaciones Blender. El refactor tocaria casi todos los archivos de 5a/5b/5c y crearia una capa temporal de compatibilidad sin valor para el MVP V2.

## Resumen De Impacto

| Area | Estado Actual | Cambio Necesario | Reutilizacion | Veredicto |
|---|---|---|---|---|
| `properties.py` | `SpriteSheetSceneState` contiene `clips`, `active_clip_index`, `export_settings`. | Agregar `SpriteSheetWorkspace`, `SpriteSheetIncludedCollection`; mover clips/export settings bajo workspace; agregar overrides. | Baja. `SpriteSheetFrameItem`, parte de `SpriteSheetClip` y `SpriteSheetExportSettings` sirven como plantilla. | Rehacer. |
| `registration.py` | Registra frame, export, clip, scene state, UIList, operadores clips/preview, panel. | Nuevo orden dependiente: included collection, frame, export, clip, workspace, scene state, UILists workspace/clip, operadores workspace/clip/preview. | Media. Patron defensivo de registro sirve. | Rehacer lista y dependencias. |
| `operators/clips.py` | Opera sobre `state.clips`. | Operar sobre workspace activo; validar workspace ausente; soportar reorder y `include_in_export`. | Media-baja. Nombres, duplicacion e indices son utiles, pero hay que mover ownership. | Reescribir adaptadores. |
| `operators/preview.py` | Obtiene clip activo desde state global; cache path por clip id; cache key no incluye workspace ni collections efectivas. | Resolver workspace+clip activos; exigir camera/collections efectivas; cache por workspace id/clip id/key; incluir inputs efectivos. | Media. Sync y clear state son reutilizables. | Reescribir operador, conservar helpers. |
| `ui/panels.py` | Panel unico con lista global de clips. | UI de workspace, selector/lista de workspaces, defaults, lista de clips del workspace, overrides, export settings por workspace. | Baja. Estructura actual es demasiado pequeña y acoplada al modelo antiguo. | Rehacer. |
| `ui/lists.py` | Solo `SPRITESHEET_UL_clips`. | Agregar UIList de workspaces; adaptar clip list a owner workspace; incluir include/reorder si aplica. | Media. Patron UIList nativo sirve. | Rehacer con patron similar. |
| `core/clip_state.py` | Helpers asumen objeto con `clips` y `active_clip_index`. | Generalizar o crear `workspace_state.py` para state/workspace/clip activo; duplicacion de workspace. | Media. `next_clip_name` y parte de `duplicate_clip_data` sirven. | Extraer/reusar, no arrastrar tal cual. |
| `core/frame_math.py` | Puro. | Sin cambios relevantes. | Alta. | Conservar. |
| `core/frame_sync.py` | Puro sobre clip.frames. | Sin cambios relevantes salvo tests workspace-aware. | Alta. | Conservar. |
| `core/cache.py` | Cache key usa clip id/rango/step/preview/camera name. | Incluir workspace id, clip id, camera efectiva y collections efectivas; no usar `scene.camera` fallback. | Media. API y tests sirven, payload cambia. | Adaptar. |
| `core/paths.py` | Root + folder por clip id/cache key. | Folder por workspace id/clip id/cache key. | Alta. | Adaptar minimo. |
| `preview/generator.py` | Usa `clip.camera or scene.camera`; no aplica visibilidad por collections. | Recibir camera efectiva y collections efectivas; aplicar/restaurar visibility; no fallback silencioso. | Media-baja. Restauracion de render/frame sirve. | Reescribir firma y contexto. |
| Tests actuales | Cubren helpers 5a/5b/5c sin workspace. | Deben cubrir workspaces, defaults, overrides, visibility y persistencia por workspace. | Media para frame math/frame sync/cache. | Rehacer suite de slices. |
| Validaciones Blender background | Validaron persistencia global de clips y preview por clip. | Deben validar save/reopen de workspace-root, camera/default collections, overrides y cache workspace-aware. | Baja-media como scripts de referencia. | Reescribir validaciones. |

## Analisis De Rutas

### Ruta A: Refactorizar La V2 Actual

Ventajas:

- Conserva archivos y tests existentes.
- Reaprovecha directamente operadores add/remove/duplicate y preview.
- Puede parecer mas rapida en el corto plazo si se minimiza el cambio visual.

Costos:

- `properties.py` cambia su estructura central y fuerza migrar todos los consumidores.
- Los operadores actuales usan `state.clips` directamente; habria que introducir helpers de contexto y modificar cada operador.
- El panel actual esta construido alrededor de una lista global de clips; practicamente se reescribe.
- Preview cache actual no conoce workspace, camera efectiva ni collections efectivas.
- Tests actuales darian falsa seguridad si se mantienen sin reescribir.
- Para no romper estados temporales habria que sostener compatibilidad interna con el modelo viejo, pero V2 es reinicio limpio y no necesita migracion V1.

Riesgo principal:

- Arrastrar arquitectura transicional. El codigo quedaria como mezcla de 5a/5b/5c antigua y workspace-root nuevo, justo lo que se intento evitar al reiniciar el addon.

### Ruta B: Volver Al Scaffold Fase 4 Y Rehacer Slices Workspace-Root

Ventajas:

- La base Fase 4 ya tiene lifecycle limpio: manifest, registro centralizado, preferencias, propiedad raiz y panel minimo.
- Permite redisenar 5a como data model correcto desde el inicio.
- Evita mantener compatibilidad temporal con `state.clips`.
- Fuerza tests y validaciones a nacer contra el contrato correcto.
- Mantiene el principio del reinicio V2: no conservar codigo solo por costo hundido.

Costos:

- Hay que reimplementar trabajo ya validado en 5a/5b/5c.
- Se deben recrear subplanes workspace-root.
- Requiere mover cuidadosamente solo patrones/helper utiles para no copiar malas decisiones.

Riesgo principal:

- Perder tiempo si se descartan helpers puros que ya estan correctos. Este riesgo se mitiga declarando explicitamente que se pueden reaprovechar `frame_math`, `frame_sync`, partes de `paths/cache`, patrones de registro y tests adaptados.

## Piezas Que Conviene Conservar O Reaprovechar

- `core/frame_math.py`: conservar casi sin cambios.
- `core/frame_sync.py`: conservar casi sin cambios porque opera sobre `clip.frames`.
- Patron de `registration.py`: registro centralizado, `_registered_classes`, unregister defensivo.
- Patron de ids estables en clips.
- `core.paths.preview_cache_root()` y sanitizacion de path parts.
- Criterio de clear cache: limpiar rutas/cache pero preservar frames y seleccion.
- Tests de frame math.
- Partes de tests de preview cache sobre que el cache key no depende del nombre visible.

## Piezas Que No Conviene Arrastrar Tal Cual

- `SpriteSheetSceneState.clips`.
- `SpriteSheetSceneState.export_settings`.
- Operadores que leen o escriben `state.clips`.
- Panel principal basado en lista global de clips.
- Preview que usa `clip.camera or scene.camera`.
- Cache folder solo por `clip.id`.
- Cache key sin workspace ni collections efectivas.
- Tests que modelan `state = SimpleNamespace(clips=..., active_clip_index=...)` como raiz final.

## Decision De Implementacion Para W4

W4 debe replanificar Fase 5 con nuevos subplanes workspace-root. Recomendacion de estructura:

1. `reinicio-v2-fase-5a-workspace-data-model-persistencia.md`
   - Crear modelo root correcto: scene state, workspace, included collection, clip, frames, export settings.
   - Validar persistencia save/reopen.

2. `reinicio-v2-fase-5b-workspace-clip-management.md`
   - Gestion de workspaces y clips: add/remove/duplicate/select/reorder.
   - UIList de workspaces y clips.
   - Defaults de workspace y overrides de clip.

3. `reinicio-v2-fase-5c-workspace-preview-cache.md`
   - Preview cache workspace-aware.
   - Camera efectiva, collections efectivas y visibility reversible.
   - Cache por workspace id/clip id/cache key.

4. Subplan tecnico previo o dentro de 5c para investigar render nativo:
   - Comparar OpenGL viewport, render still en Workbench/EEVEE Next y fallback background.
   - No reintroducir WorldSwap sin evidencia.

5. Recién despues planificar `5d visual selector minimo`.

## Manejo De Planes 5a/5b/5c Existentes

Los planes `docs/plans/reinicio-v2-fase-5a-data-model-persistencia.md`, `docs/plans/reinicio-v2-fase-5b-gestion-clips.md` y `docs/plans/reinicio-v2-fase-5c-preview-cache.md` no deben borrarse.

En W4 deben marcarse como reemplazados u obsoletos por workspace-root, o archivarse segun reglas PCS, preservando su contenido historico. Hasta W4, permanecen como historial validado pero no como base arquitectonica vigente.

## Criterio De Cierre De W3

W3 queda cumplida con esta decision:

- ruta elegida: rehacer desde scaffold limpio de Fase 4;
- piezas reutilizables identificadas;
- piezas a descartar identificadas;
- W4 puede crear/reemplazar subplanes 5a/5b/5c workspace-root;
- 5d permanece detenido.
