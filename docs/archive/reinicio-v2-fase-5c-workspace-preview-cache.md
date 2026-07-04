# Plan Fase 5c Workspace-Root - Preview Cache Workspace-Aware

Estado: aprobado
Autoridad: usuario
Modo de ejecucion: ejecutar sin replanificar
Estado De Ejecucion: validado
Referencia superior: `docs/plans/reinicio-v2-master-plan.md`
Plan rector: `docs/plans/reinicio-v2-fase-5-workspace-root-vertical-slices.md`

## Resumen

Implementar previews cacheados para el clip activo del workspace activo, usando camera efectiva y collections efectivas resueltas desde workspace + clip.

Esta fase reemplaza operativamente el plan historico `docs/plans/reinicio-v2-fase-5c-preview-cache.md`, que funcionaba sobre una lista global de clips. La nueva implementacion debe operar exclusivamente sobre:

```text
Scene.spritesheet_state.workspaces -> active_workspace -> clips -> active_clip -> frames
```

Objetivo funcional:

- `Generate Preview`: sincroniza frames esperados, preserva seleccion por `frame_number`, genera thumbnails faltantes y actualiza estado de cache.
- `Refresh Preview`: fuerza regeneracion del cache del clip activo sin perder seleccion.
- `Clear Preview Cache`: elimina solo cache derivado del clip activo y conserva `clip.frames` y seleccion persistente.

No implementar selector visual, playback, render final, composer ni export.

## Precondiciones

- Fase 5a workspace-root validada.
- Fase 5b workspace-root validada.
- Existe modelo persistente con `Scene.spritesheet_state.workspaces`.
- Workspaces tienen `default_camera`, `default_collections`, `clips`, `active_clip_index` y `export_settings`.
- Clips tienen overrides opcionales de camera y collections, frames persistentes y estado de cache.

## Fuentes Operativas

- `docs/plans/reinicio-v2-fase-5-workspace-root-vertical-slices.md`
- `docs/specs/workspace_root_decisions.md`
- `docs/specs/mvp_v2.md`
- `docs/architecture/addon_architecture.md`
- `docs/specs/validation_plan.md`
- `docs/design/visual_selector_strategy.md`
- `docs/plans/reinicio-v2-fase-5c-preview-cache.md` solo como historial tecnico, no como contrato de dominio.

## Cambios Clave

### Helpers De Contexto Workspace-Root

Agregar o adaptar helpers en `spritesheet_frame_selector/core/workspace_state.py` o nuevo modulo dedicado:

- `active_workspace_or_none(state)`.
- `active_clip_or_none(workspace)`.
- `effective_camera_or_none(workspace, clip)`.
- `effective_collections(workspace, clip)`.
- deteccion de referencias faltantes usando `collection_name`.
- mensajes de validacion pasiva para:
  - sin workspace activo;
  - sin clip activo;
  - sin camera efectiva;
  - sin collections efectivas;
  - camera borrada;
  - collection borrada;
  - rango de frames invalido.

Reglas:

- En workspace-root no usar `scene.camera` como fallback silencioso.
- Camera efectiva: override del clip si `use_camera_override=True`; si no, `workspace.default_camera`.
- Collections efectivas: override del clip si `use_collection_override=True`; si no, `workspace.default_collections`.
- Helpers puros o casi puros no deben depender de `bpy.context` salvo wrappers de operadores.

### Visibilidad Reversible

Crear modulo dedicado, recomendado `spritesheet_frame_selector/core/visibility.py`, con:

- snapshot del estado relevante de `LayerCollection.exclude`;
- aplicacion de whitelist de collections efectivas;
- inclusion de ancestros necesarios para collections anidadas;
- inclusion de collections que contienen la camera efectiva;
- restauracion garantizada con `try/finally`;
- warnings claros para collections faltantes.

Reglas:

- No dejar estado de visibilidad modificado tras preview.
- No mezclar visibilidad de un workspace con otro.
- No depender de nombres visibles como identificador unico.
- No modificar colecciones fuera del tiempo acotado de generacion.

### Cache Workspace-Aware

Adaptar `spritesheet_frame_selector/core/cache.py` y `spritesheet_frame_selector/core/paths.py` para workspace-root:

- cache junto al `.blend` guardado:

```text
//.spritesheet_cache/spritesheet_frame_selector/<workspace_id>/<clip_id>/<cache_key>/
```

- fallback para `.blend` no guardado: carpeta temporal del sistema fuera del repo.
- cache key estable basada en datos que afectan thumbnails:
  - version interna de cache;
  - `workspace.id`;
  - `clip.id`;
  - `clip.frame_start`;
  - `clip.frame_end`;
  - `clip.frame_step`;
  - `clip.preview_size`;
  - camera efectiva;
  - collections efectivas;
  - datos minimos de Blender/escena si son necesarios para evitar cache stale evidente.

Reglas:

- Cache key no depende de `workspace.name` ni `clip.name`.
- Clear cache no borra frames ni seleccion.
- Refresh borra solo la carpeta administrada del clip/cache actual antes de regenerar.
- Cache generado es derivado y descartable; seleccion vive en `.blend`.

### Sincronizacion De Frames

Adaptar `spritesheet_frame_selector/core/frame_sync.py` para recibir el clip activo:

- poblar `clip.frames` segun `frame_math.frame_numbers()`;
- preservar `selected` por `frame_number`;
- limpiar `preview_path` stale si el frame queda fuera del rango;
- conservar `original_index` coherente con el orden esperado.

Reglas:

- Rango invertido debe devolver operacion cancelada con mensaje claro o lista vacia controlada, sin traceback.
- `frame_step` invalido debe rechazarse en helpers y operadores aunque la propiedad tenga `min=1`.

### Backend De Preview

Adaptar `spritesheet_frame_selector/preview/generator.py`:

- generar thumbnails por frame usando camera efectiva y visibility scope;
- restaurar frame actual, camera de escena si se toca, settings de render usados y visibilidad con `try/finally`;
- usar ruta primaria estable para Blender UI y fallback validable para Blender background.

Politica inicial:

- Mantener OpenGL/viewport como ruta preferida cuando haya contexto UI disponible.
- Mantener fallback background por render still solo para validacion automatica y entornos sin contexto OpenGL.
- No reintroducir `WorldSwapContext` ni simulacion de Material Preview desde V1 sin spike tecnico separado.

Si durante implementacion se confirma que la tecnica de preview/render necesita investigacion aislada, detener la fase antes de escribir backend definitivo y crear `docs/plans/reinicio-v2-fase-5c-spike-render-preview-nativo.md`.

### Operadores

Actualizar o reemplazar `spritesheet_frame_selector/operators/preview.py` para workspace-root:

- `SPRITESHEET_OT_preview_generate`
- `SPRITESHEET_OT_preview_refresh`
- `SPRITESHEET_OT_preview_clear_cache`

Reglas comunes:

- Operan sobre workspace activo y clip activo.
- Manejan sin traceback:
  - sin escena;
  - sin `spritesheet_state`;
  - sin workspace activo;
  - sin clip activo;
  - sin camera efectiva;
  - sin collections efectivas;
  - camera borrada;
  - collection borrada;
  - rango invertido;
  - `frame_step` invalido;
  - fallo de escritura en cache;
  - fallo de preview/render.
- Reportan mensajes accionables con `self.report`.
- No crean outputs de export, ZIPs ni carpetas fuera de cache administrado.

Reglas por operador:

- `Generate Preview`:
  - valida workspace/clip/camera/collections;
  - sincroniza `clip.frames`;
  - conserva seleccion existente;
  - genera thumbnails faltantes;
  - actualiza `preview_path`, `cache_key`, `cache_folder`, `cache_dirty=False`, `last_preview_note`.
- `Refresh Preview`:
  - valida igual que generate;
  - limpia la carpeta de cache administrada del clip/cache actual;
  - regenera todos los thumbnails esperados;
  - conserva seleccion.
- `Clear Preview Cache`:
  - elimina solo carpeta administrada del clip activo;
  - limpia `preview_path`, `cache_key`, `cache_folder`, `last_preview_note`;
  - marca `cache_dirty=True`;
  - no borra `clip.frames` ni seleccion.

### UI

Actualizar `spritesheet_frame_selector/ui/panels.py`:

- botones `Generate Preview`, `Refresh Preview`, `Clear Preview Cache` bajo clip activo;
- resumen:
  - frames esperados;
  - frames guardados;
  - previews existentes;
  - frames seleccionados;
  - cache dirty/stale;
  - camera efectiva;
  - numero de collections efectivas;
- warnings claros:
  - no hay workspace activo;
  - no hay clip activo;
  - falta camera efectiva;
  - faltan collections efectivas;
  - hay referencias borradas;
  - cache incompleto o dirty.

Reglas:

- `draw()` no crea carpetas, no renderiza, no borra cache y no muta estado complejo.
- La UI puede leer contadores y mostrar warnings pasivos.
- No agregar selector visual ni thumbnails interactivos en esta fase.

### Registro

Actualizar `spritesheet_frame_selector/registration.py`:

- registrar operadores de preview despues de operadores de workspace/clip;
- mantener unregister en orden inverso;
- preservar doble ciclo `register()` / `unregister()`.

## Reglas De Implementacion

- No copiar codigo V1 como base estructural.
- No reintroducir modelo global `Scene.spritesheet_state.clips`.
- No usar `scene.camera` como fallback silencioso en workspace-root.
- No implementar selector visual.
- No implementar playback.
- No implementar render final.
- No implementar composer.
- No implementar export.
- No crear ZIP distribuible.
- No crear outputs de producto dentro del repo.
- No usar nombres visibles para identificar cache.
- No hacer IO desde UI `draw()`.
- Restaurar siempre frame, camera/settings tocados y visibilidad.
- Si se generan caches temporales en validacion, limpiarlos al final.

## Plan De Ejecucion

1. Verificar `git status --short --ignored`.
2. Leer estado actual de Fase 5a/5b workspace-root y confirmar que no hay modelo legacy activo.
3. Revisar helpers existentes `core/cache.py`, `core/paths.py`, `core/frame_sync.py`, `preview/generator.py` y `operators/preview.py`.
4. Adaptar helpers puros a workspace-root o reemplazarlos si arrastran contrato global de clips.
5. Implementar resolucion efectiva de camera/collections.
6. Implementar visibilidad reversible por collections.
7. Adaptar cache paths/cache keys a `<workspace_id>/<clip_id>/<cache_key>`.
8. Adaptar sincronizacion de frames para clip activo.
9. Adaptar backend de preview con restauracion garantizada.
10. Adaptar operadores Generate/Refresh/Clear.
11. Actualizar panel y registro.
12. Agregar o ajustar tests unitarios.
13. Ejecutar validaciones automaticas.
14. Ejecutar validacion Blender background.
15. Limpiar residuos de validacion.
16. Actualizar plan y PCS solo si validaciones pasan.

## Validaciones Automaticas

- `python3 -m compileall spritesheet_frame_selector`
- `python3 -m unittest discover -s tests`
- Busqueda de contrato legacy:
  - no debe aparecer `spritesheet_state.clips`;
  - no debe aparecer `spritesheet_state.active_clip_index`;
  - no debe aparecer `spritesheet_state.export_settings`;
  - operadores de preview no deben operar sobre lista global de clips.

Tests unitarios recomendados:

- cache key cambia cuando cambia `workspace.id`, `clip.id`, rango, step, preview size, camera efectiva o collections efectivas;
- cache key no cambia por `workspace.name` ni `clip.name`;
- path de cache usa `<workspace_id>/<clip_id>/<cache_key>`;
- fallback temp queda fuera del repo;
- sync de frames conserva seleccion por `frame_number`;
- sync elimina frames fuera de rango;
- clear logico no destruye seleccion;
- resolucion de camera efectiva usa override antes que default;
- resolucion de collections efectivas usa override antes que defaults;
- referencias faltantes producen warning/estado validable sin traceback.

## Validaciones Blender Background

Usar `/Applications/Blender.app/Contents/MacOS/Blender` si existe.

Validar:

- import del addon;
- doble ciclo `register()` / `unregister()`;
- crear workspace con default camera y default collection;
- crear clip sin overrides y rango corto `1-3`;
- ejecutar `bpy.ops.spritesheet.preview_generate`;
- confirmar:
  - `clip.frames` contiene frames esperados;
  - `preview_path` apunta a archivos existentes;
  - `cache_dirty=False`;
  - `cache_key` y `cache_folder` no estan vacios;
  - cache path contiene `workspace.id` y `clip.id`;
- cambiar seleccion manualmente;
- ejecutar `preview_refresh` y confirmar que la seleccion se conserva;
- ejecutar `preview_clear_cache` y confirmar:
  - cache administrado desaparece;
  - `clip.frames` y seleccion permanecen;
  - `preview_path` queda vacio;
  - `cache_dirty=True`;
- crear segundo workspace y confirmar que no lee ni pisa cache del primero;
- crear clip con override camera/collection y confirmar que preview usa overrides efectivos;
- guardar `.blend` temporal fuera del repo, reabrir y confirmar persistencia de frames, seleccion y estado de cache;
- limpiar `.blend` temporal y caches temporales generados.

## Validaciones Manuales Posteriores

- En Blender UI, crear workspace con camera y collections default.
- Crear clip sin overrides y generar preview.
- Confirmar que el panel muestra contadores y warnings correctos.
- Crear clip con camera/collections override y generar preview.
- Confirmar visualmente que la preview respeta collection efectiva.
- Borrar camera default y confirmar warning claro.
- Borrar collection referenciada y confirmar warning claro.
- Cambiar de workspace y confirmar que previews/cache/seleccion no se mezclan.
- Activar/desactivar/reactivar addon sin errores.

## Validaciones De No Alcance

- Confirmar que no se agrego selector visual.
- Confirmar que no se agrego playback.
- Confirmar que no se agrego render final.
- Confirmar que no se agrego composer.
- Confirmar que no se agrego export.
- Confirmar que no se crearon ZIPs, outputs de producto, `__pycache__`, `*.pyc`, `.DS_Store` ni caches dentro del repo.

## Riesgos

- `bpy.ops.render.opengl` puede no funcionar en Blender background sin contexto OpenGL.
- La visibilidad por `LayerCollection` es sensible a collections anidadas y puede dejar estado alterado si no se restaura en `finally`.
- Camera efectiva faltante no debe resolverse con fallback silencioso a `scene.camera`.
- Caches derivados pueden quedar stale si no se incluyen suficientes datos efectivos en cache key.
- Validacion visual exacta de la preview puede requerir prueba manual ademas de Blender background.

## PCS Y Criterio De Termino

Al ejecutar la fase:

- Guardar este plan como aprobado solo si el usuario lo aprueba explicitamente.
- Marcar `Estado De Ejecucion: validado` solo si pasan compile, unit tests, Blender background y limpieza de residuos.
- Actualizar `.context/agent_context.md`, `.context/index.md`, `.context/handoff.md` y `.context/worklog.jsonl`.
- Dejar como siguiente paso preparar o aprobar `docs/plans/reinicio-v2-fase-5d-visual-selector-minimo.md`, salvo que la fase determine que primero debe ejecutarse `docs/plans/reinicio-v2-fase-5c-spike-render-preview-nativo.md`.

Criterio final:

- El clip activo del workspace activo puede generar, refrescar y limpiar previews cacheados.
- La preview respeta camera efectiva y collections efectivas.
- El cache usa `workspace.id`, `clip.id` y cache key estable.
- La seleccion persistente no se pierde al regenerar o limpiar cache.
- El addon sigue registrando/desregistrando limpiamente.
- No hay selector visual/playback/render/export implementado en esta fase.

## Supuestos

- Backend inicial: OpenGL/viewport cuando haya contexto UI, fallback background por render still si es necesario para validacion automatica.
- El spike `docs/plans/reinicio-v2-fase-5c-spike-render-preview-nativo.md` solo se crea si la implementacion detecta una decision tecnica bloqueante sobre backend.
- Los caches son derivados y descartables; la seleccion vive en `.blend`.
- La deteccion automatica exhaustiva de cambios de escena queda fuera de esta fase; el usuario puede usar `Refresh Preview`.

## Resultado De Ejecucion

Validado el 2026-07-03.

Cambios implementados:

- Helpers workspace-aware en `spritesheet_frame_selector/core/workspace_state.py`:
  - camera efectiva;
  - collections efectivas;
  - deteccion de collections faltantes;
  - warnings pasivos para preview.
- Nuevo modulo `spritesheet_frame_selector/core/visibility.py` para aplicar/restaurar visibilidad de collections por `LayerCollection` con `try/finally`.
- Cache workspace-aware en `spritesheet_frame_selector/core/cache.py` y `spritesheet_frame_selector/core/paths.py`:
  - cache key incluye workspace id, clip id, rango, step, preview size, camera efectiva y collections efectivas;
  - path de cache usa `<workspace_id>/<clip_id>/<cache_key>`;
  - nombres visibles no determinan cache key.
- Backend `spritesheet_frame_selector/preview/generator.py` actualizado para recibir camera/collections efectivas y restaurar frame, camera, render settings y visibilidad.
- Operadores `spritesheet_frame_selector/operators/preview.py` actualizados para operar sobre workspace activo y clip activo:
  - `SPRITESHEET_OT_preview_generate`;
  - `SPRITESHEET_OT_preview_refresh`;
  - `SPRITESHEET_OT_preview_clear_cache`.
- UI `spritesheet_frame_selector/ui/panels.py` actualizada con controles de preview, warnings y contadores.
- Registro centralizado `spritesheet_frame_selector/registration.py` actualizado para registrar operadores de preview.
- Tests unitarios ampliados en `tests/test_preview_cache.py`.

Validaciones ejecutadas:

- `python3 -m compileall spritesheet_frame_selector`: OK.
- `python3 -m unittest discover -s tests`: OK, 19 tests.
- Busqueda de contrato legacy `spritesheet_state.clips`, `spritesheet_state.active_clip_index`, `spritesheet_state.export_settings`, `state.clips`, `state.active_clip_index`, `state.export_settings`: OK, sin resultados en codigo/tests.
- Blender background con `/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup`: OK, `SFS_5C_WORKSPACE_PREVIEW_OK`.
- Validacion Blender confirmo:
  - doble ciclo `register()` / `unregister()`;
  - generate/refresh/clear preview;
  - preservacion de seleccion;
  - cache path con workspace id y clip id;
  - workspace separado sin pisar cache;
  - override camera/collection;
  - persistencia save/reopen en `.blend` temporal fuera del repo;
  - limpieza de `.blend` y cache temporal.
- Limpieza de residuos: OK, sin `__pycache__`, `*.pyc`, `.DS_Store` ni cache temporal 5c dentro del repo.

Nota:

- `spritesheet_frame_selector.zip` sigue apareciendo como ignorado preexistente y no fue tocado por esta fase.
- No fue necesario crear el spike `docs/plans/reinicio-v2-fase-5c-spike-render-preview-nativo.md`; el fallback background por render still permitio validar sin reintroducir `WorldSwapContext`.

Proximo paso recomendado:

- Preparar `docs/plans/reinicio-v2-fase-5d-visual-selector-minimo.md`.
