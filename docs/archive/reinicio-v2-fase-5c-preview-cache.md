# Plan Fase 5c - Preview Cache

Estado: aprobado
Autoridad: usuario
Modo de ejecucion: ejecutar sin replanificar
Estado De Ejecucion: validado - reemplazado por workspace-root
Estado Operativo Actual: reemplazado por `docs/plans/reinicio-v2-fase-5c-workspace-preview-cache.md`
Referencia superior: `docs/plans/reinicio-v2-master-plan.md`
Plan rector: `docs/plans/reinicio-v2-fase-5-vertical-slices.md`

Nota: este plan se conserva como historial validado del intento 5c previo, pero no es base arquitectonica vigente porque genera preview cache por clip global y no resuelve workspace, camera efectiva ni collections efectivas.

## Resumen

Implementar previews cacheados por clip usando thumbnails de Viewport/OpenGL y cache derivado junto al `.blend` cuando el archivo esta guardado. Si el `.blend` no esta guardado, usar carpeta temporal controlada fuera del repo.

Nota de implementacion validada: Blender 5.1.1 no permite `bpy.ops.render.opengl` en `--background` por falta de contexto OpenGL. El backend mantiene OpenGL como ruta primaria y usa un fallback de thumbnail por render still solo cuando `bpy.app.background` esta activo, para permitir validacion automatica sin introducir export/composer.

El objetivo es agregar `Generate Preview`, `Refresh Preview` y `Clear Preview Cache`, poblar `clip.frames` con el rango esperado, conservar seleccion existente por `frame_number`, escribir thumbnails pequenos en cache y mostrar estado claro en el panel. No implementar selector visual, playback, render final, composer ni export.

## Alcance Implementado

- Helpers:
  - `spritesheet_frame_selector/core/cache.py`
  - `spritesheet_frame_selector/core/paths.py`
  - `spritesheet_frame_selector/core/frame_sync.py`
- Backend:
  - `spritesheet_frame_selector/preview/generator.py`
- Operadores:
  - `SPRITESHEET_OT_preview_generate`
  - `SPRITESHEET_OT_preview_refresh`
  - `SPRITESHEET_OT_preview_clear_cache`
- UI:
  - botones `Generate Preview`, `Refresh Preview`, `Clear Preview Cache`
  - contadores de frames esperados, frames guardados, paths de preview y frames seleccionados
  - warning simple de cache stale o incompleto
- Tests unitarios para cache key, paths y sincronizacion de frames.

## Reglas Aplicadas

- Cache junto al `.blend`: `//.spritesheet_cache/spritesheet_frame_selector/<clip_id>/<cache_key>/`.
- Cache fallback para `.blend` no guardado: carpeta temporal del sistema fuera del repo.
- Cache key basada en `clip.id`, rango, step, `preview_size`, camara y version interna.
- Cache key no depende de `clip.name`.
- `Generate Preview` sincroniza frames, conserva seleccion y genera thumbnails faltantes.
- `Refresh Preview` fuerza regeneracion sin cambiar seleccion.
- `Clear Preview Cache` elimina solo carpetas administradas por el addon y no borra `clip.frames`.
- La UI no crea carpetas, no renderiza y no limpia cache desde `draw()`.
- No se implemento selector visual, playback, render final, composer ni export.
- El fallback de render still existe solo para generar thumbnails en Blender background cuando OpenGL no esta disponible.

## Validaciones Ejecutadas

- `python3 -m compileall spritesheet_frame_selector`
- `python3 -m unittest discover -s tests`
- Blender background con `/Applications/Blender.app/Contents/MacOS/Blender`:
  - import del addon;
  - doble ciclo `register()` / `unregister()`;
  - creacion de clip corto;
  - generacion de previews;
  - refresh conservando seleccion;
  - clear cache conservando frames y seleccion;
  - save/reopen de `.blend` temporal fuera del repo;
  - limpieza de `.blend` y cache temporal.
- Limpieza posterior de `__pycache__`, `*.pyc` y temporales.

## Resultado

La Fase 5c queda validada.

El clip activo puede generar, refrescar y limpiar previews cacheados. La seleccion persistente no se pierde al regenerar previews, el cache usa identificador estable y no se agregaron features fuera del alcance.

## Proximo Paso

Preparar `docs/plans/reinicio-v2-fase-5d-visual-selector-minimo.md`.
