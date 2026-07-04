# Reinicio V2 Fase 4: Scaffold Limpio Del Addon V2

Estado: aprobado
Autoridad: usuario
Modo de ejecucion: ejecutar sin replanificar
Estado De Ejecucion: validado

## Referencia Superior

`docs/plans/reinicio-v2-master-plan.md`

## Objetivo

Crear el primer scaffold V2 instalable y validable del addon, sin implementar features de producto.

El scaffold debe demostrar lifecycle basico de Blender: import, `register()`, `unregister()`, manifest valido, propiedad minima de escena y panel minimo en `3D Viewport > Sidebar > SpriteSheet`.

## Alcance

Incluye:

- paquete nuevo `spritesheet_frame_selector/`;
- `blender_manifest.toml`;
- `registration.py` con registro centralizado;
- `preferences.py` con `AddonPreferences` minimo;
- `properties.py` con `PropertyGroup` minimo;
- `ui/panels.py` con panel minimo;
- paquetes placeholder para `core/`, `operators/`, `preview/`, `playback/`, `render/` y `export/`;
- validaciones de sintaxis, import y registro/desregistro.

No incluye:

- clips;
- modelo MVP completo;
- preview;
- selector visual;
- playback;
- render;
- composer;
- export;
- tests legacy;
- ZIP distribuible.

## Reglas

- No copiar codigo V1 desde Git/archive.
- No agregar dependencias externas.
- No hacer IO desde UI.
- `register()` no depende de escena activa.
- `unregister()` tolera registro parcial, recarga y ejecucion repetida.
- La estructura debe quedar preparada para los slices de Fase 5.

## Validaciones

- `python3 -m compileall spritesheet_frame_selector`.
- Import controlado del paquete con un mock minimo de `bpy`.
- Blender background si el entorno lo permite.
- Confirmar que no quedan `__pycache__/`, `.DS_Store` ni outputs despues de limpiar caches de validacion.

## Criterio De Termino

- El scaffold existe.
- El paquete puede importarse.
- `register()` y `unregister()` pueden ejecutarse repetidamente.
- Existe panel minimo `SpriteSheet`.
- No hay features de producto fuera del scaffold.
- PCS apunta a preparar Fase 5.

## Resultado De Ejecucion

La Fase 4 fue ejecutada y validada el 2026-07-03.

Se creo scaffold V2 minimo en `spritesheet_frame_selector/`:

- `__init__.py`
- `blender_manifest.toml`
- `registration.py`
- `preferences.py`
- `properties.py`
- `ui/panels.py`
- paquetes placeholder para `core/`, `operators/`, `preview/`, `playback/`, `render/` y `export/`

Validaciones ejecutadas:

- `python3 -m compileall spritesheet_frame_selector`: paso.
- Import y doble ciclo `register()`/`unregister()` con mock minimo de `bpy`: paso.
- Blender background con `/Applications/Blender.app/Contents/MacOS/Blender`: paso en reintento posterior. Blender 5.1.1 ejecuto import y doble ciclo `register()`/`unregister()` sin traceback y emitio `SFS_SCAFFOLD_OK`.
- Limpieza posterior de `__pycache__/` y `*.pyc`: realizada.

Limitacion:

- Falta validacion manual en Blender GUI para confirmar visualmente el panel en `3D Viewport > Sidebar > SpriteSheet`.

PCS actualizado para que el siguiente paso sea preparar `docs/plans/reinicio-v2-fase-5-vertical-slices.md`.
