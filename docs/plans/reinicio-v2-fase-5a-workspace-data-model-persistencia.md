# Plan Fase 5a Workspace-Root - Data Model Y Persistencia

Estado: aprobado
Autoridad: usuario
Modo de ejecucion: ejecutar sin replanificar
Estado De Ejecucion: validado
Referencia superior: `docs/plans/reinicio-v2-master-plan.md`
Plan rector: `docs/plans/reinicio-v2-fase-5-workspace-root-vertical-slices.md`

## Resumen

Rehacer Fase 5a desde la base conceptual del scaffold limpio de Fase 4 para implementar el modelo persistente workspace-root del MVP V2.

Este plan reemplaza operativamente `docs/plans/reinicio-v2-fase-5a-data-model-persistencia.md`, que queda como historial validado del intento anterior basado en clips directos sobre `Scene.spritesheet_state`.

## Decision De Base

Aplicar `DEC-0009`: volver a la arquitectura de Fase 4 y rehacer 5a/5b/5c con workspace como raiz.

La implementacion futura no debe conservar compatibilidad con:

- `Scene.spritesheet_state.clips`
- `Scene.spritesheet_state.active_clip_index`
- `Scene.spritesheet_state.export_settings`

El contrato nuevo es:

```text
Scene
  spritesheet_state: SpriteSheetSceneState

SpriteSheetSceneState
  schema_version
  workspaces
  active_workspace_index

SpriteSheetWorkspace
  id
  name
  default_camera
  default_collections
  clips
  active_clip_index
  export_settings
```

## Alcance

Implementar solo data model, registro y validacion de persistencia.

Incluye:

- `SpriteSheetIncludedCollection`
- `SpriteSheetFrameItem`
- `SpriteSheetExportSettings`
- `SpriteSheetClip`
- `SpriteSheetWorkspace`
- `SpriteSheetSceneState`
- propiedad raiz unica `bpy.types.Scene.spritesheet_state`
- helpers puros minimos para frame math, si se conservan o recrean
- helpers puros minimos para resolver indices activos, si no introducen operadores de producto
- panel minimo de estado si hace falta para confirmar lifecycle, sin UI completa de gestion
- tests unitarios de helpers puros
- validacion Blender background de persistencia `.blend`

No incluye:

- operadores add/remove/duplicate/select de workspace o clips;
- UI completa para gestionar workspaces o clips;
- preview cache;
- selector visual;
- playback;
- render;
- composer;
- export.

## Modelo Detallado

### SpriteSheetIncludedCollection

Campos:

- `collection`: `PointerProperty(type=bpy.types.Collection)`
- `collection_name`: `StringProperty`

Regla:

- `collection_name` conserva el ultimo nombre conocido para poder reportar collections borradas o faltantes.

### SpriteSheetFrameItem

Campos:

- `frame_number`: `IntProperty`
- `selected`: `BoolProperty(default=True)`
- `preview_path`: `StringProperty(subtype="FILE_PATH")`
- `original_index`: `IntProperty(default=-1)`

### SpriteSheetExportSettings

Campos:

- `frame_width`: default `64`
- `frame_height`: default `64`
- `columns`: default `8`
- `padding`: default `0`
- `margin`: default `0`
- `transparent`: default `True`
- `output_folder`: default `""`
- `sheet_name`: default `"spritesheet"`
- `export_png_sequence`: default `False`
- `png_sequence_folder`: default `""`

### SpriteSheetClip

Campos:

- `id`: string estable
- `name`: default `"Clip"`
- `include_in_export`: definir default explicito en este plan como `True` salvo que la implementacion detecte una razon tecnica fuerte para diferirlo; si se cambia, documentarlo en `.context/decisions.md`
- `frame_start`: default `1`
- `frame_end`: default `20`
- `frame_step`: default `1`, min `1`
- `fps`: default `12`
- `use_camera_override`: default `False`
- `camera`: `PointerProperty(type=bpy.types.Object, poll=camera)`
- `use_collection_override`: default `False`
- `included_collections`: `CollectionProperty(type=SpriteSheetIncludedCollection)`
- `preview_size`: default `64`
- `frames`: `CollectionProperty(type=SpriteSheetFrameItem)`
- `active_frame_index`: default `-1`
- `cache_key`: default `""`
- `cache_folder`: default `""`
- `cache_dirty`: default `True`
- `last_preview_note`: default `""`

### SpriteSheetWorkspace

Campos:

- `id`: string estable
- `name`: default `"Workspace"`
- `default_camera`: `PointerProperty(type=bpy.types.Object, poll=camera)`
- `default_collections`: `CollectionProperty(type=SpriteSheetIncludedCollection)`
- `clips`: `CollectionProperty(type=SpriteSheetClip)`
- `active_clip_index`: default `-1`
- `export_settings`: `PointerProperty(type=SpriteSheetExportSettings)`

### SpriteSheetSceneState

Campos:

- `schema_version`: default `2` o version superior documentada
- `workspaces`: `CollectionProperty(type=SpriteSheetWorkspace)`
- `active_workspace_index`: default `-1`

## Reglas De Implementacion

- No copiar codigo V1 desde Git/archive.
- No ejecutar `git reset`, `git checkout` destructivo ni borrar archivos sin instruccion explicita del usuario.
- Si se quiere volver a Fase 4 materialmente, hacerlo mediante ediciones controladas y explicitas.
- Mantener una sola propiedad raiz: `bpy.types.Scene.spritesheet_state`.
- No registrar propiedades legacy directas sobre `Scene`.
- `register()` no debe depender de escena activa.
- `unregister()` debe tolerar registro parcial y doble ciclo.
- Registrar clases en orden dependiente:
  - preferencias;
  - included collection;
  - frame item;
  - export settings;
  - clip;
  - workspace;
  - scene state;
  - UI minima/panel.
- `unregister()` debe limpiar `Scene.spritesheet_state` antes de desregistrar clases.
- No hacer IO desde `draw`.
- No usar `bpy.context` en helpers puros.
- Los indices activos usan `-1` cuando no hay elemento activo.
- `camera` debe aceptar solo objetos tipo `CAMERA`.
- `collection` debe aceptar solo `bpy.types.Collection`.
- El addon debe seguir importando y registrando sin escena especial.

## Piezas Reutilizables Permitidas

Se pueden conservar o adaptar si pasan revision contra workspace-root:

- `spritesheet_frame_selector/core/frame_math.py`
- `spritesheet_frame_selector/core/frame_sync.py`
- patron de registro centralizado defensivo;
- tests unitarios de frame math;
- convencion de ids estables;
- criterio de no usar nombres visibles como identificadores tecnicos.

No conservar tal cual:

- helpers que asumen `state.clips`;
- tests que modelan `Scene.spritesheet_state.clips` como raiz final;
- panel basado en lista global de clips;
- preview/cache actual.

## Validaciones Automaticas

- `python3 -m compileall spritesheet_frame_selector`
- `python3 -m unittest discover -s tests`
- Confirmar por busqueda que no queda contrato activo de:
  - `spritesheet_state.clips`
  - `spritesheet_state.active_clip_index`
  - `spritesheet_state.export_settings`

## Validaciones Blender Background

Usar `/Applications/Blender.app/Contents/MacOS/Blender` si existe.

Validar:

- import del addon;
- doble ciclo `register()` / `unregister()`;
- `bpy.types.Scene.spritesheet_state` existe tras register;
- crear workspace por Python;
- asignar `id`, `name`, `active_workspace_index`;
- crear default camera y asignarla a `workspace.default_camera`;
- crear default collection y asignarla a `workspace.default_collections`;
- crear clip dentro de `workspace.clips`;
- crear frame dentro de `clip.frames`;
- verificar defaults de clip y export settings;
- guardar `.blend` temporal fuera del repo;
- reabrir `.blend`;
- confirmar persistencia de workspace, default camera, default collection, clip, frames y export settings;
- ejecutar unregister sin traceback.

## Validaciones De No Alcance

Confirmar que no se agregaron:

- operadores de gestion de workspace/clip;
- preview cache;
- selector visual;
- playback;
- render;
- composer;
- export.

Confirmar que no quedan dentro del repo:

- `__pycache__/`
- `*.pyc`
- `.DS_Store`
- outputs
- ZIPs nuevos
- `.blend` temporales

## PCS Y Criterio De Termino

Al ejecutar la fase:

- Marcar este plan como `validado` solo si pasan compile, tests, Blender background y limpieza de residuos.
- Actualizar `.context/agent_context.md`, `.context/index.md`, `.context/handoff.md` y `.context/worklog.jsonl`.
- Dejar como siguiente paso preparar o aprobar `docs/plans/reinicio-v2-fase-5b-workspace-clip-management.md`.

Criterio final:

- El modelo persistente workspace-root existe.
- Los datos sobreviven save/reopen en Blender.
- El addon sigue registrando/desregistrando limpiamente.
- No hay features fuera de data model/persistencia.
- No queda modelo activo basado en `Scene.spritesheet_state.clips`.

## Resultado De Ejecucion

La Fase 5a workspace-root fue ejecutada y validada el 2026-07-03.

Cambios implementados:

- `SpriteSheetIncludedCollection`
- `SpriteSheetFrameItem`
- `SpriteSheetExportSettings`
- `SpriteSheetClip`
- `SpriteSheetWorkspace`
- `SpriteSheetSceneState`
- propiedad raiz unica `bpy.types.Scene.spritesheet_state`
- registro centralizado actualizado sin operadores de producto
- panel minimo de estado workspace-root
- helper puro `spritesheet_frame_selector/core/workspace_state.py`
- tests unitarios actualizados para helpers puros workspace-root y frame sync

Validaciones ejecutadas:

- `python3 -m compileall spritesheet_frame_selector`: paso.
- `python3 -m unittest discover -s tests`: paso.
- Busqueda de contrato legacy `spritesheet_state.clips`, `spritesheet_state.active_clip_index`, `spritesheet_state.export_settings`: sin resultados en codigo/tests.
- Validacion Blender background con Blender 5.1.1: paso con `SFS_5A_WORKSPACE_OK`.

Nota de entorno:

- Blender background fallo dentro del sandbox antes de ejecutar Python por inicializacion Metal. Se reintento fuera del sandbox con aprobacion y paso correctamente.

Limpieza:

- `__pycache__/` y `*.pyc` generados por validacion fueron retirados.
- `.DS_Store` en raiz del repo fue retirado.
- No se generaron outputs, ZIPs ni `.blend` temporales dentro del repo.
