# Plan Fase 5b Workspace-Root - Gestion De Workspaces Y Clips

Estado: aprobado
Autoridad: usuario
Modo de ejecucion: ejecutar sin replanificar
Estado De Ejecucion: validado
Referencia superior: `docs/plans/reinicio-v2-master-plan.md`
Plan rector: `docs/plans/reinicio-v2-fase-5-workspace-root-vertical-slices.md`

## Resumen

Implementar gestion basica de workspaces y clips sobre el modelo persistente workspace-root validado en `docs/plans/reinicio-v2-fase-5a-workspace-data-model-persistencia.md`.

El objetivo es que el usuario pueda crear, eliminar, duplicar, seleccionar y reordenar workspaces/clips desde el panel `SpriteSheet`, configurar defaults del workspace y overrides basicos del clip, sin implementar preview cache, selector visual, playback, render, composer ni export.

## Precondiciones

- Fase 5a workspace-root validada.
- `Scene.spritesheet_state.workspaces -> active_workspace -> clips -> frames` existe y persiste.
- Los planes originales 5a/5b/5c se consideran historial reemplazado, no base vigente.

## Cambios Clave

### Operadores De Workspace

Agregar `spritesheet_frame_selector/operators/workspaces.py` con:

- `SPRITESHEET_OT_workspace_add`
- `SPRITESHEET_OT_workspace_remove`
- `SPRITESHEET_OT_workspace_duplicate`
- `SPRITESHEET_OT_workspace_select`
- `SPRITESHEET_OT_workspace_move`
- `SPRITESHEET_OT_workspace_default_collection_add`
- `SPRITESHEET_OT_workspace_default_collection_remove`

Reglas:

- `Add Workspace` crea `id` unico, nombre incremental y selecciona el nuevo workspace.
- `Remove Workspace` no falla con lista vacia y ajusta `active_workspace_index`.
- `Duplicate Workspace` genera ids nuevos para workspace y clips, copia settings/defaults/seleccion, pero limpia cache como estado valido.
- `Move Workspace` reordena y mantiene indice activo correcto.
- No crear previews ni archivos.

### Operadores De Clips

Actualizar o reemplazar `spritesheet_frame_selector/operators/clips.py` para operar sobre workspace activo:

- `SPRITESHEET_OT_clip_add`
- `SPRITESHEET_OT_clip_remove`
- `SPRITESHEET_OT_clip_duplicate`
- `SPRITESHEET_OT_clip_select`
- `SPRITESHEET_OT_clip_move`
- `SPRITESHEET_OT_clip_included_collection_add`
- `SPRITESHEET_OT_clip_included_collection_remove`

Reglas:

- Operadores usan `active_workspace`, no `state.clips`.
- `Add Clip` crea `id` unico, nombre incremental, `include_in_export=True` y selecciona el clip nuevo.
- `Remove Clip` ajusta `workspace.active_clip_index`.
- `Duplicate Clip` genera nuevo `id`, copia configuracion/frames/seleccion y limpia cache.
- `Move Clip` respeta orden manual dentro del workspace.
- Operadores deben manejar sin traceback ausencia de escena, state, workspace activo, clip activo e indices fuera de rango.

### Helpers Puros

Agregar o adaptar helpers en `spritesheet_frame_selector/core/workspace_state.py` y/o `spritesheet_frame_selector/core/clip_state.py`:

- `active_workspace_or_none(state)`
- `clamp_active_workspace_index(state)`
- `active_clip_or_none(workspace)`
- `clamp_active_clip_index(workspace)`
- `next_item_name(existing_names, base)`
- `duplicate_clip_data(source, target)`
- `duplicate_workspace_data(source, target)`
- helpers para limpiar cache derivado al duplicar

Los helpers no deben usar `bpy.context`.

### UIList Y Panel

Agregar o adaptar `spritesheet_frame_selector/ui/lists.py`:

- `SPRITESHEET_UL_workspaces`
- `SPRITESHEET_UL_clips`

Actualizar `spritesheet_frame_selector/ui/panels.py`:

- selector/lista de workspaces;
- botones Add/Remove/Duplicate/Move para workspaces;
- campos del workspace activo:
  - `name`
  - `default_camera`
  - `default_collections`
  - resumen de export settings, sin exportar;
- lista de clips del workspace activo;
- botones Add/Remove/Duplicate/Move para clips;
- campos del clip activo:
  - `name`
  - `include_in_export`
  - `frame_start`
  - `frame_end`
  - `frame_step`
  - `fps`
  - `preview_size`
  - `use_camera_override`
  - `camera` si override activo
  - `use_collection_override`
  - `included_collections` si override activo;
- resumen de frames esperados, frames guardados y seleccionados;
- mensajes claros si no hay workspace o clip activo.

La UI no debe hacer IO, crear carpetas, generar previews ni limpiar cache desde `draw()`.

### Registro

Actualizar `spritesheet_frame_selector/registration.py`:

- registrar UILists y operadores despues de `PropertyGroup`;
- mantener unregister en orden inverso;
- preservar doble ciclo `register()`/`unregister()`.

## Reglas De Implementacion

- No copiar codigo V1 como base.
- No recuperar modelo `Scene.spritesheet_state.clips`.
- No generar previews.
- No implementar selector visual.
- No implementar playback.
- No implementar render, composer ni export.
- No crear archivos, carpetas, caches, ZIPs ni outputs de producto.
- No hacer IO desde `draw`.
- Los helpers puros no dependen de `bpy.context`.
- Usar `-1` para indices activos cuando no hay elemento.
- Duplicar workspace o clip no debe conservar `cache_key`, `cache_folder`, `preview_path` ni `last_preview_note` como estado valido.
- Cambiar defaults u overrides debe marcar clips afectados como `cache_dirty=True` cuando exista cache state.

## Validaciones Automaticas

- `python3 -m compileall spritesheet_frame_selector`
- `python3 -m unittest discover -s tests`
- Tests unitarios para:
  - nombres incrementales de workspace y clip;
  - clamp de workspace activo con lista vacia;
  - clamp de clip activo con lista vacia;
  - duplicacion de clip limpia cache;
  - duplicacion de workspace genera ids nuevos y limpia cache;
  - reordenamiento mantiene indice activo esperado.
- Busqueda de contrato legacy:
  - no debe aparecer `spritesheet_state.clips`
  - no debe aparecer `spritesheet_state.active_clip_index`
  - no debe aparecer `spritesheet_state.export_settings`

## Validaciones Blender Background

Usar `/Applications/Blender.app/Contents/MacOS/Blender` si existe.

Validar:

- import del addon;
- doble ciclo `register()` / `unregister()`;
- ejecutar operadores de workspace Add/Duplicate/Move/Remove;
- ejecutar operadores de clip Add/Duplicate/Move/Remove dentro del workspace activo;
- configurar default camera/default collection por Python;
- configurar override camera/collection por Python;
- guardar `.blend` temporal fuera del repo;
- reabrir y confirmar persistencia de workspaces, clips, indices, defaults, overrides y export settings;
- confirmar que no se crean previews/cache/export.

## Validaciones Manuales Posteriores

- Panel `SpriteSheet` muestra workspace activo y lista de workspaces.
- Crear/eliminar/duplicar/reordenar workspace desde UI.
- Crear/eliminar/duplicar/reordenar clips dentro de workspace desde UI.
- Cambiar de escena no mezcla workspaces.
- Archivo nuevo sin workspace muestra estado vacio claro.
- Borrar camara o collection referenciada muestra estado manejable sin traceback.

## PCS Y Criterio De Termino

Al ejecutar la fase:

- Marcar este plan como `validado` solo si pasan compile, tests, Blender background y limpieza de residuos.
- Actualizar `.context/agent_context.md`, `.context/index.md`, `.context/handoff.md` y `.context/worklog.jsonl`.
- Dejar como siguiente paso preparar o aprobar `docs/plans/reinicio-v2-fase-5c-workspace-preview-cache.md` o el spike `docs/plans/reinicio-v2-fase-5c-spike-render-preview-nativo.md`.

Criterio final:

- El usuario puede gestionar workspaces y clips desde el panel.
- Workspaces/clips persisten en `.blend`.
- Defaults y overrides existen y persisten.
- No hay preview/cache/render/export implementado.
- El addon sigue registrando/desregistrando limpiamente.
- No quedan residuos de validacion.

## Resultado De Ejecucion

Validado el 2026-07-03.

Cambios implementados:

- Operadores de workspace en `spritesheet_frame_selector/operators/workspaces.py`:
  - add/remove/duplicate/select/move;
  - add/remove de default collections;
  - duplicacion con IDs nuevos y cache derivado invalidado en clips copiados.
- Operadores de clip workspace-root en `spritesheet_frame_selector/operators/clips.py`:
  - add/remove/duplicate/select/move sobre workspace activo;
  - add/remove de included collections por clip;
  - duplicacion con ID nuevo y limpieza de `cache_key`, `cache_folder`, `preview_path` y `last_preview_note`.
- Helpers puros en `spritesheet_frame_selector/core/workspace_state.py` para active state, clamp, nombres incrementales, reordenamiento, duplicacion y limpieza de cache.
- `spritesheet_frame_selector/core/clip_state.py` quedo como capa de compatibilidad ligera sobre helpers workspace-root, sin contrato `Scene.spritesheet_state.clips`.
- UI nativa en `spritesheet_frame_selector/ui/lists.py` y `spritesheet_frame_selector/ui/panels.py` para workspaces, clips, defaults, overrides y resumen de frames.
- Registro centralizado actualizado en `spritesheet_frame_selector/registration.py`.
- Callbacks de propiedades editables en `spritesheet_frame_selector/properties.py` marcan `cache_dirty=True` cuando cambian defaults/overrides o datos que afectan preview futuro.
- Tests unitarios ampliados en `tests/test_clip_state.py`.

Validaciones ejecutadas:

- `python3 -m compileall spritesheet_frame_selector`: OK.
- `python3 -m unittest discover -s tests`: OK, 14 tests.
- Busqueda de contrato legacy `spritesheet_state.clips`, `spritesheet_state.active_clip_index`, `spritesheet_state.export_settings`, `state.clips`, `state.active_clip_index`, `state.export_settings`: OK, sin resultados en codigo/tests.
- Blender background con `/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup`: OK, `SFS_5B_WORKSPACE_CLIPS_OK`.
- Persistencia save/reopen en `.blend` temporal fuera del repo: OK.
- Limpieza de residuos: OK, sin `__pycache__`, `*.pyc`, `.DS_Store` ni temporales 5b dentro del repo.

Nota:

- `spritesheet_frame_selector.zip` sigue apareciendo como ignorado preexistente y no fue tocado por esta fase.

Proximo paso recomendado:

- Preparar o aprobar `docs/plans/reinicio-v2-fase-5c-workspace-preview-cache.md`.
- Si se requiere evidencia tecnica antes de decidir backend, preparar `docs/plans/reinicio-v2-fase-5c-spike-render-preview-nativo.md`.
