# Reinicio V2 Fase 5a: Data Model Y Persistencia

Estado: aprobado
Autoridad: usuario
Modo de ejecucion: ejecutar sin replanificar
Estado De Ejecucion: validado - reemplazado por workspace-root

Estado Operativo Actual: reemplazado por `docs/plans/reinicio-v2-fase-5a-workspace-data-model-persistencia.md`

Nota: este plan se conserva como historial validado del intento 5a previo, pero no es base arquitectonica vigente porque usa clips directos bajo `Scene.spritesheet_state`.

## Referencia Superior

`docs/plans/reinicio-v2-fase-5-vertical-slices.md`

## Objetivo

Reemplazar el estado minimo del scaffold por el modelo persistente real del MVP V2, sin implementar operadores, preview, selector visual, playback, render ni export.

## Alcance

Incluye:

- `SpriteSheetFrameItem`
- `SpriteSheetClip`
- `SpriteSheetExportSettings`
- `SpriteSheetSceneState`
- propiedad raiz `bpy.types.Scene.spritesheet_state`
- helper puro `spritesheet_frame_selector/core/frame_math.py`
- tests unitarios del helper
- validacion Blender background de persistencia `.blend`

No incluye:

- operadores de gestion de clips;
- UI para crear/borrar/duplicar clips;
- preview cache;
- selector visual;
- playback;
- render;
- composer;
- export.

## Reglas

- No copiar codigo V1 desde Git/archive.
- No hacer IO desde `draw`.
- No usar `bpy.context` en helpers puros.
- Indices activos usan `-1` cuando no hay elemento activo.
- `camera` solo acepta objetos tipo `CAMERA`.
- El addon debe seguir importando y registrando sin escena especial.

## Validaciones

- `python3 -m compileall spritesheet_frame_selector`.
- `python3 -m unittest discover -s tests`.
- Blender background:
  - import;
  - doble ciclo `register()`/`unregister()`;
  - crear clip y frames por Python;
  - verificar defaults;
  - verificar `export_settings`;
  - guardar `.blend` temporal fuera del repo;
  - reabrir y confirmar persistencia.
- Confirmar ausencia de `__pycache__/`, `*.pyc`, `.DS_Store`, previews, outputs o ZIPs nuevos.

## Criterio De Termino

- Modelo persistente V2 existe.
- Datos sobreviven save/reopen en Blender.
- `register()`/`unregister()` siguen limpios.
- No existen features fuera de data model/persistencia.
- PCS apunta a preparar `docs/plans/reinicio-v2-fase-5b-gestion-clips.md`.

## Resultado De Ejecucion

La Fase 5a fue ejecutada y validada el 2026-07-03.

Cambios implementados:

- `SpriteSheetFrameItem`
- `SpriteSheetClip`
- `SpriteSheetExportSettings`
- `SpriteSheetSceneState`
- propiedad raiz `bpy.types.Scene.spritesheet_state`
- helper puro `spritesheet_frame_selector/core/frame_math.py`
- tests unitarios `tests/test_frame_math.py`
- panel minimo actualizado para mostrar estado del modelo

Validaciones ejecutadas:

- `python3 -m compileall spritesheet_frame_selector`: paso.
- `python3 -m unittest discover -s tests`: paso.
- Blender background con Blender 5.1.1: paso con `SFS_5A_PERSISTENCE_OK`.
- Limpieza de `__pycache__/`, `*.pyc` y `.blend` temporal: realizada.

No se agregaron operadores, preview, selector visual, playback, render, composer ni export.
