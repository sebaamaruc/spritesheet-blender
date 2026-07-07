# Plan Fase 6a Hito 2 - Integridad Selector Playback

Estado: aprobado
Autoridad: usuario
Modo de ejecucion: ejecutar sin replanificar
Estado De Ejecucion: validado

## Referencia Superior

`docs/plans/reinicio-v2-fase-6-correcciones-auditoria-tecnica.md`

## Fuente Principal

- `docs/technical-audit.md`
- `docs/plans/reinicio-v2-fase-6-correcciones-auditoria-tecnica.md`
- `docs/plans/reinicio-v2-fase-6a-selector-modal-lifecycle.md`
- `docs/plans/reinicio-v2-fase-6a-validacion-hito1-selector-modal-lifecycle.md`

## Objetivo

Cerrar el hito 2 de Fase 6a sobre la superficie selector/playback despues de validar el hito 1. Este subplan corrige problemas de integridad visual y runtime que no son lifecycle critico, pero afectan confianza del selector y coste de playback:

- redraw indiscriminado del playback;
- thumbnails obsoletos por datablocks de imagen reutilizados;
- silenciamiento amplio de excepciones en selector/playback;
- undo inconsistente en clicks del overlay;
- reanudacion de playback con FPS viejo;
- perfilado del coste real de `gpu.texture.from_image`;
- reconciliacion del bug runtime nuevo `P1-playback-selection-snapshot`, ya corregido y validado por el usuario.

## Hallazgos Cubiertos

| ID | Severidad | Titulo | Estado En Este Subplan |
|---|---|---|---|
| M3 | medio | El timer de playback fuerza redraw de todas las areas en cada tick | implementado |
| M9 | medio | Thumbnails obsoletos en selector por `check_existing=True` sin `reload()` | validado por el usuario |
| M10 | medio no verificado | Posible coste de `gpu.texture.from_image` por celda y redraw | instrumentacion debug opt-in agregada; no se implemento cache GPU sin evidencia |
| B6 | bajo | Silenciamiento amplio de excepciones | implementado solo para selector/playback |
| B7 | bajo | Undo inconsistente en overlay | validado por el usuario |
| B10 | bajo | `resume_playback` ignora cambios de FPS | validado por el usuario |
| P1-playback-selection-snapshot | alto runtime | Playback seguia snapshot viejo tras cambios de seleccion | corregido, validado por el usuario y reconciliado |

## Extracto Operativo De Auditoria

### M3 - El timer de playback fuerza el redraw de todas las areas de todas las ventanas

- Problema: `_tag_redraw()` en `spritesheet_frame_selector/playback/controller.py` recorre todas las ventanas y todas las areas a la frecuencia del clip, hasta 60 fps. Esto redibuja Properties, Outliner, editores de nodos y cualquier otra area no relacionada.
- Causa: redraw indiscriminado por simplicidad.
- Impacto: consumo CPU/GPU innecesario durante la reproduccion, visible en layouts complejos.
- Solucion propuesta por auditoria: hacer tag solo de areas `VIEW_3D` o solo del area de la sesion del selector si el controller recibe una referencia debil.
- Archivos/funciones afectados: `spritesheet_frame_selector/playback/controller.py::_tag_redraw`.

Interpretacion del subplan:

- Correccion preferida para MVP: limitar `_tag_redraw()` a areas `VIEW_3D`. Es simple, reduce el blast radius y no acopla el controller a una referencia de area que puede quedar invalida.
- No introducir referencia persistente a `Area` salvo que la validacion GUI muestre que redibujar todos los `VIEW_3D` sigue siendo demasiado costoso.
- Agregar test unitario con ventanas/areas fake para confirmar que solo se llama `tag_redraw()` en areas `VIEW_3D`.

### M9 - Thumbnails obsoletos por `check_existing=True` sin `reload()`

- Problema: `_draw_preview_image` y `_cached_image_or_none` cargan con `bpy.data.images.load(path, check_existing=True)`. Si ya existe un datablock con esa ruta, por una sesion anterior o por regeneracion de cache que reescribio el mismo fichero, Blender puede reutilizar pixeles antiguos sin `image.reload()`.
- Causa: carga de imagen por ruta con reuse de datablock sin invalidacion explicita.
- Impacto: el selector puede mostrar thumbnails que no corresponden al contenido actual del archivo de cache.
- Solucion propuesta por auditoria: al cachear por primera vez en la sesion, llamar `image.reload()` si el datablock ya existia; o invalidar `session.images` cuando cambia `clip.cache_key`.
- Archivos/funciones afectados: `spritesheet_frame_selector/ui/visual_selector.py::_draw_preview_image`, `spritesheet_frame_selector/ui/visual_selector.py::_cached_image_or_none`.

Interpretacion del subplan:

- Crear un helper privado, por ejemplo `_load_preview_image(session, path)`, usado por `_draw_preview_image` y `_cached_image_or_none`.
- En la primera carga por ruta dentro de la sesion, llamar `bpy.data.images.load(..., check_existing=True)`, guardar en `session.images` y ejecutar `image.reload()` de forma controlada para forzar pixeles actuales del archivo. Si `reload()` falla, dibujar fallback y no romper el modal.
- Agregar a la sesion un snapshot de `clip.cache_key` o limpiar `session.images` cuando el clip activo conserva id pero cambia `cache_key`. Esto evita que una generacion de previews dentro de la misma sesion conserve thumbnails viejos.
- Mantener liberacion de imagenes en `close()` sin eliminar datablocks que tengan usuarios externos.

### M10 - Posible coste de `gpu.texture.from_image` por celda y por redraw

- Problema: `_draw_preview_image` llama `gpu.texture.from_image(image)` en cada redraw para cada celda visible. Si Blender no cachea internamente la textura GPU del datablock, esto puede subir texturas cada frame durante playback.
- Causa/Impacto: no verificado sin ejecutar en la version objetivo. Si no hay cache interna, puede ser el mayor coste del overlay.
- Solucion propuesta por auditoria: perfilar en runtime; si hace falta, cachear `GPUTexture` en la sesion junto al datablock.
- Archivos/funciones afectados: `spritesheet_frame_selector/ui/visual_selector.py::_draw_preview_image`.

Interpretacion del subplan:

- No implementar cache GPU especulativa.
- Agregar instrumentacion liviana y desactivada por defecto para contar llamadas a `gpu.texture.from_image` y tiempo aproximado en draw, o preparar una prueba GUI manual con consola/perfilado simple.
- Criterio: solo introducir cache de textura si el perfilado muestra coste relevante durante playback con una grilla poblada. Si no hay evidencia, documentar `M10` como no accionable para MVP y dejarlo para 6f con razon.
- Si se implementa cache GPU, debe quedar dentro de `VisualSelectorSession`, limpiarse en `close()` y no persistir entre archivos.

### B6 - Silenciamiento amplio de excepciones

- Problema: existen `except Exception: pass/return` en `_tag_redraw`, `_session_matches_context`, `_preview_file_has_transparency`, `_draw_preview_image`. Esto dificulta diagnostico.
- Causa: defensividad para no romper UI/render durante draw/timer.
- Impacto: errores reales quedan invisibles.
- Solucion propuesta por auditoria: loggear al menos con `print` o `logging` en modo debug.
- Archivos/funciones cubiertos por este subplan: `spritesheet_frame_selector/playback/controller.py::_tag_redraw`, `spritesheet_frame_selector/playback/controller.py::_session_matches_context`, `spritesheet_frame_selector/ui/visual_selector.py::_draw_preview_image`, `spritesheet_frame_selector/ui/visual_selector.py::_cached_image_or_none` si se mantiene catch amplio.

Interpretacion del subplan:

- B6 completo se divide entre 6a hito 2 y 6e. Este subplan solo toca selector/playback.
- Agregar helper local minimo de debug, por ejemplo `_debug_log(message, exc=None)`, condicionado a una preferencia existente si existe, una constante de modulo, o una variable de entorno simple. Si no hay preferencia de debug en el addon, usar constante privada `DEBUG_SELECTOR_PLAYBACK = False`.
- No imprimir en cada frame bajo condiciones normales. El logging debe ser opt-in para evitar spam durante redraw.
- Mantener catches defensivos en draw/timer donde romper la UI seria peor, pero dejar camino de diagnostico activable.

### B7 - Undo inconsistente en el overlay

- Problema original: el click en una celda en modo `EDIT` mutaba `frame.selected` directamente sin push de undo, mientras que el operador `frame_toggle_selection` declara `UNDO`.
- Causa: camino directo desde UI modal a propiedad persistente.
- Impacto: undo inconsistente; algunas selecciones hechas desde overlay no entraban al stack de undo.
- Solucion propuesta por auditoria: enrutar el click por el operador.
- Archivos/funciones afectados: `spritesheet_frame_selector/ui/visual_selector.py::_handle_click`, `spritesheet_frame_selector/operators/visual_selector.py::SPRITESHEET_OT_frame_toggle_selection`.

Interpretacion del subplan:

- Este hallazgo quedo parcialmente corregido durante `P1-playback-selection-snapshot`: `_handle_click` ya usa `bpy.ops.spritesheet.frame_toggle_selection(index=...)`.
- El subplan debe validar que no quedan otros caminos del overlay mutando seleccion directamente.
- Si faltan rutas, enrutar todas las mutaciones interactivas de seleccion por operadores `UNDO`.
- Validar en Blender GUI que una seleccion de celda en modo Edit puede deshacerse de forma coherente, si Blender registra undo para el operador invocado desde modal.

### B10 - `resume_playback` ignora cambios de FPS

- Problema: al pausar y reanudar, `resume_playback()` usa `_session.fps`, congelado al iniciar playback, aunque el usuario haya cambiado `clip.fps`.
- Causa: la sesion de playback conserva FPS como snapshot y `resume_playback()` no relee el clip activo.
- Impacto: playback reanudado no respeta el FPS actual del clip.
- Solucion propuesta por auditoria: releer `clip.fps` al reanudar.
- Archivos/funciones afectados: `spritesheet_frame_selector/playback/controller.py::resume_playback`, `spritesheet_frame_selector/operators/playback.py::SPRITESHEET_OT_playback_play.execute`.

Interpretacion del subplan:

- Cambiar el contrato de `resume_playback` para aceptar opcionalmente `fps` actual o crear helper `resume_playback(fps=clip.fps)`.
- Validar `fps > 0` antes de reanudar. Si FPS invalido, reportar warning desde operador y no reactivar timer.
- Actualizar `_session.fps` antes de registrar el timer, para que callbacks posteriores usen el FPS nuevo.
- Agregar test unitario de pausa/reanudar cambiando FPS.

### P1-playback-selection-snapshot - Hallazgo runtime nuevo ya corregido

- Problema: despues de cambiar seleccion, playback seguia usando el snapshot anterior de `frame_numbers`/`preview_paths`. El usuario debia presionar `Shift + Left` para que la seleccion se aplicara.
- Causa: `start_playback()` copiaba la secuencia al iniciar, pero los operadores de seleccion no refrescaban la sesion activa.
- Impacto: playback mostraba frames eliminados de la seleccion y rompia confianza en el selector.
- Solucion aplicada: `refresh_playback_session()` reemplaza el snapshot de la sesion activa; operadores de seleccion refrescan despues de mutar seleccion; clicks de celdas usan `frame_toggle_selection`.
- Estado: validado por el usuario.

Interpretacion del subplan:

- No reimplementar este fix. Reconciliar el ledger de Fase 6 y mantener tests de regresion.
- Asegurar que los cambios de B10 no rompen `refresh_playback_session`.

## Alcance De Implementacion

Incluir:

- M3: limitar redraw del playback a areas `VIEW_3D`, con test unitario.
- M9: unificar carga de imagenes del selector y forzar reload/invalidation cuando corresponde, con tests puros o mocks de `bpy.data.images`.
- B6 parcial: agregar logging debug opt-in para excepciones defensivas en selector/playback tocadas por este subplan.
- B7: confirmar/enforzar que clicks de celdas pasan por operador `UNDO`; agregar test o validacion `rg` que no quede mutacion directa `clip.frames[...].selected =` en `ui/visual_selector.py`.
- B10: reanudar playback con FPS actual del clip.
- M10: perfilar/medir antes de cache GPU; documentar resultado en este plan.
- P1: registrar como validado y mantener regresion.

Excluir:

- M6 scroll y sensibilidad trackpad. M6 ya esta validado; sensibilidad es pulido UX separado.
- M5/M7/M8/B3/B4/B6 global. Quedan para 6e.
- A4 regeneracion forzada/depsgraph. Queda para 6b.
- Cache GPU persistente si M10 no demuestra coste real.
- Cambios de contrato modal del selector. El hito 1 acepto UI externa bloqueada como modal intencional.

## Archivos Esperados

- `spritesheet_frame_selector/playback/controller.py`
- `spritesheet_frame_selector/operators/playback.py`
- `spritesheet_frame_selector/ui/visual_selector.py`
- `spritesheet_frame_selector/operators/visual_selector.py` solo si B7 requiere ajuste adicional
- `tests/test_playback_sequence.py`
- Nuevo test unitario si conviene aislar imagen/reload del selector con mocks
- Este plan y el ledger de `docs/plans/reinicio-v2-fase-6-correcciones-auditoria-tecnica.md`

## Validacion Automatica

- `python3 -m compileall spritesheet_frame_selector`
- `python3 -m unittest discover -s tests`
- Busquedas esperadas:
  - confirmar que `playback/controller.py::_tag_redraw` filtra `area.type == "VIEW_3D"`;
  - confirmar que `ui/visual_selector.py` no muta seleccion directa desde `_handle_click`;
  - confirmar que carga de imagen del selector centraliza `reload()` o invalidacion por `cache_key`;
  - confirmar que `resume_playback` recibe o aplica FPS actual.

## Validacion Blender GUI

- M3: iniciar playback con varias areas abiertas (View3D, Properties, Outliner) y confirmar que playback sigue visible sin sensacion de congelamiento; no hace falta demostrar rendimiento exacto si tests confirman filtro `VIEW_3D`.
- M9: generar previews, abrir selector, regenerar previews sobre los mismos paths, volver a abrir o mantener sesion segun flujo disponible y confirmar que thumbnails reflejan los nuevos archivos.
- B7: en modo Edit, click en una celda y usar undo de Blender; confirmar que la seleccion vuelve de forma coherente o registrar limitacion si Blender no integra undo de operador invocado desde modal.
- B10: iniciar playback, pausar, cambiar FPS del clip, reanudar y confirmar que la velocidad responde al FPS nuevo.
- M10: con una grilla poblada, observar/perfilar si `gpu.texture.from_image` produce coste visible. Si no hay evidencia de coste, documentar diferido/no accionable para MVP.
- P1: repetir caso validado por usuario: cambiar seleccion durante playback y confirmar que frames eliminados no siguen reproduciendose.

## Criterios De Aceptacion

- El playback no redibuja areas no `VIEW_3D` desde el timer.
- El selector no muestra thumbnails viejos tras regenerar cache sobre mismos archivos.
- Las excepciones defensivas en selector/playback tienen ruta de diagnostico opt-in sin spam por defecto.
- Clicks de celdas no escriben seleccion directamente desde UI modal.
- Reanudar playback respeta el FPS actual del clip.
- M10 queda medido y decidido: cache GPU implementada solo si hay evidencia; si no, queda diferido con razon.
- `P1-playback-selection-snapshot` queda reconciliado como validado en el ledger.

## Riesgos Y Decisiones

- `image.reload()` en draw puede ser costoso si se ejecuta en cada frame. Debe ejecutarse solo al primer cacheo por ruta en la sesion o cuando cambie `clip.cache_key`.
- Logging dentro de draw/timer puede generar spam si no se controla. Debe quedar desactivado por defecto.
- Cache GPU puede introducir recursos nuevos que requieren cleanup cuidadoso; por eso se condiciona a evidencia de M10.
- Undo desde operador llamado por modal puede depender del comportamiento de Blender. Si no funciona de forma fiable, registrar limitacion y proponer alternativa especifica en vez de ocultarlo.

## Proximo Paso Si Se Aprueba

Implementar este subplan sin ampliar alcance a 6b/6c/6d/6e. Al finalizar, dejar `Estado De Ejecucion: implementado`, ejecutar validaciones automaticas y pedir/registrar validacion Blender GUI antes de marcarlo como `validado`.

## Resumen De Implementacion

- `playback/controller.py`:
  - `resume_playback(fps=...)` acepta el FPS actual del clip y rechaza FPS invalido sin reactivar el timer.
  - `_tag_redraw()` ahora filtra `area.type == "VIEW_3D"` para no redibujar Properties, Outliner u otras areas en cada tick.
  - `_session_matches_context()` y `_tag_redraw()` mantienen catches defensivos, pero agregan logging debug opt-in mediante `SFS_SELECTOR_PLAYBACK_DEBUG` o `DEBUG_SELECTOR_PLAYBACK`.
- `operators/playback.py`:
  - `SPRITESHEET_OT_playback_play.execute()` valida `clip.fps` antes de reanudar y pasa `clip.fps` a `resume_playback`.
- `ui/visual_selector.py`:
  - `VisualSelectorSession` guarda `image_cache_key` y limpia imagenes cuando cambia `clip.cache_key`.
  - `_draw_preview_image()` y `_cached_image_or_none()` usan `_load_preview_image()`.
  - `_load_preview_image()` carga con `check_existing=True` y llama `image.reload()` solo en la primera carga por ruta dentro de la sesion.
  - Se agrego instrumentacion opt-in para contar/medir `gpu.texture.from_image`; no se agrego cache GPU porque M10 requiere evidencia runtime.
  - El click de celda en modo Edit sigue enroutado por `bpy.ops.spritesheet.frame_toggle_selection(index=...)`; no queda mutacion directa de seleccion desde `_handle_click`.
- Tests:
  - `tests/test_playback_sequence.py` cubre reanudar con FPS actual, rechazar FPS invalido, redraw solo en `VIEW_3D` y regresiones de `P1-playback-selection-snapshot`.
  - `tests/test_visual_selector_scroll.py` cubre reload de imagen una vez por ruta/sesion y limpieza de imagenes ante cambio de `cache_key`.

## Validaciones Ejecutadas

- Pasado: `python3 -m compileall spritesheet_frame_selector`.
- Pasado: `python3 -m unittest discover -s tests` con 79 tests.
- Pasado: busqueda de contrato para `VIEW_3D`, `reload()`, `_load_preview_image`, `cache_key`, `resume_playback(fps=...)`, `SFS_SELECTOR_PLAYBACK_DEBUG`, `gpu.texture.from_image`, `frame_toggle_selection` y ausencia de mutacion directa `clip.frames[...].selected =` en `ui/visual_selector.py`.

## Validaciones Blender GUI Pendientes

- M9: regenerar previews sobre los mismos paths y confirmar que el selector muestra thumbnails actualizados.
- B7: click de celda en modo Edit y undo; confirmar que la seleccion vuelve de forma coherente o registrar limitacion de Blender modal/undo.
- B10: pausar playback, cambiar FPS, reanudar y confirmar que cambia la velocidad.
- M10: perfilar/observar grilla poblada; si no hay coste visible, mantener no-cache GPU como decision MVP.

## Resultado De Validacion GUI

Validado por el usuario. El subplan queda listo para continuar con la siguiente subfase de Fase 6. No se implemento cache GPU porque M10 no mostro evidencia suficiente para ampliar alcance durante MVP.
