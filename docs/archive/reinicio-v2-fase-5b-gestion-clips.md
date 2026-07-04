# Plan Fase 5b - Gestion De Clips

Estado: aprobado
Autoridad: usuario
Modo de ejecucion: ejecutar sin replanificar
Estado De Ejecucion: validado - reemplazado por workspace-root
Estado Operativo Actual: reemplazado por `docs/plans/reinicio-v2-fase-5b-workspace-clip-management.md`
Referencia superior: `docs/plans/reinicio-v2-master-plan.md`
Plan rector: `docs/plans/reinicio-v2-fase-5-vertical-slices.md`

Nota: este plan se conserva como historial validado del intento 5b previo, pero no es base arquitectonica vigente porque opera sobre una lista global de clips en vez de workspace-root.

## Resumen

Implementar la gestion basica de clips sobre el modelo persistente validado en Fase 5a.

El objetivo es que el usuario pueda crear, eliminar, duplicar, seleccionar y editar configuracion basica de clips desde el panel `SpriteSheet`, sin implementar preview, selector visual, playback, render, composer ni export.

## Alcance Implementado

- Operadores en `spritesheet_frame_selector/operators/clips.py`:
  - `SPRITESHEET_OT_clip_add`
  - `SPRITESHEET_OT_clip_remove`
  - `SPRITESHEET_OT_clip_duplicate`
  - `SPRITESHEET_OT_clip_select`
- UIList en `spritesheet_frame_selector/ui/lists.py`:
  - `SPRITESHEET_UL_clips`
- Helpers puros en `spritesheet_frame_selector/core/clip_state.py`:
  - `active_clip_or_none(state)`
  - `clamp_active_clip_index(state)`
  - `next_clip_name(existing_names, base="Clip")`
  - `duplicate_clip_data(source, target)`
- Panel `SpriteSheet` actualizado con lista, controles y campos basicos del clip activo.
- Registro centralizado actualizado para UIList y operadores.
- Tests unitarios agregados para helpers de clips.

## Reglas Aplicadas

- No se genero preview.
- No se implemento selector visual.
- No se implemento playback.
- No se implemento render.
- No se implemento composer.
- No se implemento export.
- No se crearon archivos, carpetas, caches, ZIPs ni outputs de producto.
- Los helpers puros no dependen de `bpy.context`.
- Los operadores validan estado ausente, lista vacia e indices fuera de rango sin traceback.

## Validaciones Ejecutadas

- `python3 -m compileall spritesheet_frame_selector`
- `python3 -m unittest discover -s tests`
- Blender background con `/Applications/Blender.app/Contents/MacOS/Blender`:
  - import del addon;
  - doble ciclo `register()` / `unregister()`;
  - ejecucion de `bpy.ops.spritesheet.clip_add`;
  - ejecucion de `bpy.ops.spritesheet.clip_duplicate`;
  - ejecucion de `bpy.ops.spritesheet.clip_remove`;
  - verificacion de `active_clip_index`;
  - edicion de propiedades del clip activo;
  - save/reopen de `.blend` temporal fuera del repo;
  - confirmacion de persistencia;
  - limpieza de archivo temporal.
- Limpieza posterior de `__pycache__` y `*.pyc`.

## Resultado

La Fase 5b queda validada.

El usuario puede gestionar clips basicos desde el panel y los clips persisten en `.blend`. El addon conserva el lifecycle limpio de registro/desregistro y no contiene features de preview/cache/render/export.

## Proximo Paso

Preparar `docs/plans/reinicio-v2-fase-5c-preview-cache.md`.
