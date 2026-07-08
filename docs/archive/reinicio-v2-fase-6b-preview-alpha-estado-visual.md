# Plan Fase 6b - Exactitud De Preview, Alpha Y Estado Visual

Estado: aprobado
Autoridad: usuario
Modo de ejecucion: ejecutar sin replanificar
Estado De Ejecucion: validado

## Referencia Superior

`docs/plans/reinicio-v2-fase-6-correcciones-auditoria-tecnica.md`

## Fuente Principal

- `docs/technical-audit.md`
- `docs/plans/reinicio-v2-fase-6-correcciones-auditoria-tecnica.md`
- `docs/plans/reinicio-v2-fase-6b0-preview-camera-viewport.md`

## Objetivo

Asegurar que previews y render/export final representen lo que el usuario espera antes de continuar con rendimiento, consolidacion y validacion final:

- export transparente con canal alpha real aunque la escena estuviera configurada en RGB/BW;
- previews regenerables explicitamente cuando el contenido de escena cambio;
- previews opacos validos no deben fallar por una heuristica de transparencia;
- cache de previews sin crecimiento indefinido por carpetas hermanas obsoletas;
- rangos de frame alineados con la decision D2: no permitir frames negativos en MVP;
- criterio de identidad de preview/render revisado tras eliminar render cache final en 6c;
- cambios de shading/overlay del viewport aplicados una sola vez por generacion, no por frame;
- reconciliar que el bug runtime `P1-preview-camera-view` ya fue corregido y validado en 6b0.

## Hallazgos De Auditoria Cubiertos

| ID | Severidad | Titulo | Estado En Este Subplan |
|---|---|---|---|
| A2 | alto | Render final transparente puede salir sin alfa si `image_settings.color_mode` no es RGBA | validado por el usuario |
| A4 | alto | Previews no se invalidan al editar escena y no existe regeneracion forzada en UI | validado por el usuario |
| M1 | medio | Falso positivo de transparencia: preview 100% opaco aborta generacion | validado por el usuario |
| M2 | medio | Basura de cache de previews acumulada indefinidamente | validado por el usuario |
| M4 | medio | Frames negativos desalinean rango de clip y frames almacenados | validado por el usuario |
| B9 | bajo | Criterios de identidad distintos entre preview cache y render key | clasificado tras 6c: no aplica como divergencia preview/render; preview mantiene invalidacion por nombre visible |
| B11 | bajo | Shading del viewport se cambia/restaura por cada frame | validado por el usuario |
| P1-preview-camera-view | alto runtime | Generate Preview SOLID/MATERIAL usaba vista libre del viewport | ya corregido y validado en 6b0; reconciliar, no reimplementar |

## Extracto Operativo De Auditoria

### A2 - Render final no fuerza `color_mode = "RGBA"`

- Problema: `render_clip_frames` fuerza `film_transparent`, formato PNG y resolucion, pero no toca `image_settings.color_mode`. Si la escena del usuario tiene `color_mode = "RGB"` o `"BW"`, los PNG pueden escribirse sin canal alfa y el spritesheet transparente puede salir con fondo opaco/negro. El generador de previews si fuerza RGBA, por lo que hay inconsistencia entre backends.
- Causa: omision al replicar la lista de estado guardado/forzado del preview generator en el renderer final.
- Impacto: salida incorrecta silenciosa del artefacto principal del addon, dependiente de la configuracion previa de la escena.
- Solucion propuesta por la auditoria: en `render_clip_frames`, guardar/forzar/restaurar `image_settings.color_mode = "RGBA"` cuando `export_settings.transparent`; valorar fijar `color_depth = "8"` como en previews.
- Archivos/funciones afectados: `spritesheet_frame_selector/render/renderer.py::render_clip_frames`.
- Aspectos no verificados en runtime: export con escena previamente configurada en RGB/BW y transparencia activa.

### A4 - Previews no se invalidan al editar escena y no existe regeneracion forzada en UI

- Problema: la clave de cache solo depende de ids, rango, tamano, modo, nombre de camara y nombres de colecciones. Editar animacion, mallas o materiales no marca `cache_dirty` ni cambia la clave. `SPRITESHEET_OT_preview_generate` llama con `force=False`, por lo que salta archivos existentes, y `force=True` no esta expuesto desde la UI. El unico camino actual del usuario es Clear Cache + Generate.
- Causa: invalidacion basada solo en settings del addon, sin senal de cambio de contenido; operador de force nunca expuesto al usuario.
- Impacto: el usuario puede seleccionar frames mirando thumbnails obsoletos, lo que rompe la confianza en el selector visual.
- Solucion propuesta por la auditoria: corto plazo, boton `Regenerate`/`Regenerate Preview` que use `force=True`; medio plazo, incluir una senal barata de cambio via `depsgraph_update_post` filtrado por colecciones efectivas o contador similar.
- Archivos/funciones afectados: `spritesheet_frame_selector/core/cache.py::build_preview_cache_key`, `spritesheet_frame_selector/operators/preview.py::SPRITESHEET_OT_preview_generate`, `spritesheet_frame_selector/ui/panels.py::SPRITESHEET_PT_main.draw`.
- Aspectos no verificados en runtime: si una invalidacion por depsgraph puede filtrar cambios relevantes sin marcar dirty por ediciones irrelevantes ni degradar rendimiento.

### M1 - Falso positivo en verificacion de transparencia

- Problema: `_preview_file_has_transparency` exige que exista algun alpha menor que `0.999`. Si el sujeto cubre el 100% del encuadre, el preview puede ser validamente opaco, pero se borra y la generacion falla con mensaje de falta de alpha transparente. Ademas itera todos los pixeles por cada frame.
- Causa: heuristica pensada para detectar viewports que ignoran `film_transparent`, formulada como "debe existir al menos un pixel transparente".
- Impacto: fallo duro en un caso de uso valido y coste O(px) por frame.
- Solucion propuesta por la auditoria: degradar a advertencia en `last_preview_note` en vez de error + borrado; o verificar solo primer frame; o muestrear pixeles, por ejemplo bordes.
- Archivos/funciones afectados: `spritesheet_frame_selector/preview/generator.py::_preview_file_has_transparency`, `spritesheet_frame_selector/preview/generator.py::generate_viewport_previews`.
- Aspectos no verificados en runtime: preview de un objeto que cubre totalmente el encuadre con transparencia activada.

### M2 - Basura de cache acumulada indefinidamente

- Problema: cada cambio de settings crea una nueva carpeta `<workspace>/<clip>/<cache_key>` y las carpetas de claves anteriores no se borran nunca. Clear Cache solo borra la actual; `force` solo opera sobre la actual. Tambien pueden quedar carpetas de clips/workspaces eliminados.
- Causa: no hay GC en `_generate_preview_cache`.
- Impacto: crecimiento de disco sin limite junto al `.blend` del usuario.
- Solucion propuesta por la auditoria: al generar con exito, borrar carpetas hermanas de `<clip_id>/` distintas de la clave actual, usando `is_managed_cache_folder` como salvaguarda; opcionalmente purgar carpetas de clips inexistentes al abrir.
- Archivos/funciones afectados: `spritesheet_frame_selector/operators/preview.py::_generate_preview_cache`, `spritesheet_frame_selector/core/paths.py`.
- Aspectos no verificados en runtime: que el GC solo borre carpetas administradas del cache y no toque carpetas externas/manuales.

### M4 - Frames negativos

- Problema: `clip.frame_start/frame_end` no tienen `min`, pero `SpriteSheetFrameItem.frame_number` tiene `min=0`. Con `frame_start=-10`, `frame_numbers()` genera negativos, `sync_clip_frames` los escribe y Blender los clampa a 0, provocando colisiones de numeros y previews vacios sin mensaje claro.
- Causa: inconsistencia de rangos entre propiedades de clip y frame item.
- Impacto: edge case silencioso y dificil de diagnosticar.
- Solucion propuesta por la auditoria: elegir entre permitir negativos quitando `min=0` de `frame_number`, o prohibir negativos poniendo `min=0` en `frame_start/frame_end`.
- Archivos/funciones afectados: `spritesheet_frame_selector/properties.py::SpriteSheetFrameItem`, `spritesheet_frame_selector/properties.py::SpriteSheetClip`, `spritesheet_frame_selector/core/frame_sync.py::sync_clip_frames`.
- Aspectos no verificados en runtime: comportamiento de UI al ingresar valores negativos tras agregar `min=0`.

### B9 - Criterios de identidad distintos entre claves

- Problema original: la clave de previews usa `name_full` de colecciones y `camera.name`, mientras la clave de render usaba `library.filepath + name_full` por `_id_key`. Renombrar una camara invalida previews aunque conceptualmente sea la misma camara.
- Causa: preview cache y render key crecieron con criterios distintos.
- Impacto: invalidaciones inesperadas o divergencia conceptual entre subsistemas.
- Solucion propuesta por la auditoria: unificar en `_id_key` compartido.
- Archivos/funciones afectados originalmente: `spritesheet_frame_selector/core/cache.py::build_preview_cache_key`, `spritesheet_frame_selector/core/render_state.py::_id_key`.
- Aspectos no verificados en runtime: impacto real de rename de camara/coleccion sobre UX de previews.

### B11 - Shading del viewport se cambia y restaura por cada frame

- Problema: `_write_viewport_thumbnail` cambia/restaura shading y overlay por cada frame.
- Causa: el scope de estado visual esta dentro del helper que se invoca por frame, no alrededor del bucle completo de generacion.
- Impacto: trabajo redundante y posibles parpadeos del viewport durante la generacion.
- Solucion propuesta por la auditoria: mover el cambio/restauracion de shading y overlay fuera del bucle por frame.
- Archivos/funciones afectados: `spritesheet_frame_selector/preview/generator.py::_write_viewport_thumbnail`, `spritesheet_frame_selector/preview/generator.py::generate_viewport_previews`.
- Aspectos no verificados en runtime: confirmar que el viewport queda restaurado tras generacion exitosa y tras excepcion.

### P1-preview-camera-view - Preview desde camara efectiva

- Problema runtime detectado durante validacion: `Generate Preview` en `SOLID`/`MATERIAL`, con solo seleccionar collection y camara sin entrar a Camera View, generaba thumbnails desde la vista libre del viewport. El objeto salia muy pequeno, como si la camara estuviera mucho mas lejos.
- Causa: `bpy.ops.render.opengl(write_still=True, view_context=True)` usa el viewport 3D actual; si el viewport no esta en Camera View, no renderiza desde la camara efectiva.
- Impacto: thumbnails no confiables para seleccionar frames.
- Solucion aplicada en 6b0: mantener `view_context=True`, forzar temporalmente `region_3d.view_perspective = "CAMERA"` antes del render OpenGL y restaurar perspectiva, shading y overlays con `try/finally`.
- Archivos/funciones afectados: `spritesheet_frame_selector/preview/generator.py`, tests de preview cache.
- Aspectos no verificados en runtime: ya validado por el usuario; en este subplan solo se debe evitar regresion al mover scopes de B11.

## Interpretacion Del Subplan

- A2: adoptar solucion de auditoria. Forzar/restaurar `color_mode = "RGBA"` cuando `transparent` es local, seguro y consistente con previews. Tambien se debe guardar/restaurar `color_depth`; fijarlo a `"8"` solo dentro del scope transparente si el codigo de previews ya usa ese contrato.
- A4: adoptar la solucion de corto plazo obligatoria: exponer regeneracion forzada con `force=True`. La invalidacion por depsgraph se investigara en el mismo subplan, pero no se implementara si no hay filtro claro por contenido relevante; un handler ruidoso puede empeorar UX y rendimiento.
- M1: ajustar la solucion de auditoria hacia no fallar duro. En MVP, un preview 100% opaco puede ser valido; la verificacion debe evitar borrar el archivo. Si se conserva inspeccion alpha, debe quedar como warning/nota, no como cancelacion de generacion.
- M2: adoptar GC de carpetas hermanas administradas tras generacion exitosa. No purgar carpetas de clips/workspaces inexistentes en este subplan salvo que ya exista helper seguro y local; ese barrido global puede entrar en 6f/6e si hace falta.
- M4: ejecutar D2 confirmada por el usuario: agregar `min=0` a `frame_start` y `frame_end`, y validar que sync no produce negativos.
- B9: ajustar por cambio de contexto. En 6c se elimino el render key final y tambien `_id_key`; por tanto no se debe reintroducir render key ni cache final para satisfacer literalmente B9. La correccion aceptable aqui es una de estas dos, en orden de preferencia:
  1. si existe o se crea un helper pequeno y reutilizable de identidad para datablocks, usarlo solo en preview cache sin reabrir render cache final;
  2. documentar en el subplan implementado que, tras 6c, B9 queda reducido a comportamiento aceptado de preview MVP: renombrar camara/coleccion invalida cache porque los nombres visibles forman parte del contrato de cache.
- B11: adoptar solucion de auditoria, pero cuidando la correccion 6b0. El scope exterior debe seguir forzando Camera View para cada render OpenGL y restaurar todo con `try/finally`.
- P1-preview-camera-view: no reimplementar; solo mantener tests/contrato para que B11 no rompa la camara efectiva.

## Alcance De Implementacion

Incluir:

- `render/renderer.py::render_clip_frames`: guardar/forzar/restaurar `image_settings.color_mode` y, si aplica, `color_depth`.
- `operators/preview.py`: exponer una regeneracion forzada que llame el backend con `force=True`; mantener Generate normal si el contrato UI lo requiere o convertir Generate en accion forzada si se decide simplificar, pero la UI debe dejar claro que existe regeneracion explicita.
- `ui/panels.py`: agregar control visible de regeneracion forzada sin reintroducir botones innecesarios ni duplicar mensajes.
- `preview/generator.py`: cambiar la verificacion de transparencia para no abortar previews validamente opacos; mover scope de shading/overlay fuera del bucle por frame; preservar Camera View temporal de 6b0.
- `operators/preview.py` y/o `core/paths.py`: purgar carpetas hermanas administradas del cache del clip despues de generacion exitosa.
- `properties.py`: agregar `min=0` a `SpriteSheetClip.frame_start` y `SpriteSheetClip.frame_end`.
- Tests unitarios para A2, A4, M1, M2, M4 y B11 cuando puedan simularse sin Blender real.
- Busquedas de contrato para asegurar que no se reintroduce render cache final eliminado en 6c.

Excluir:

- No implementar cache final de render.
- No reintroducir `render_key`, `render_dirty`, `render_path` ni `_id_key` dentro de `core/render_state.py`.
- No resolver A3/A5/B2; pertenecen a 6d.
- No consolidar validaciones M5 ni helpers transversales M7; pertenecen a 6e.
- No tocar packaging, manifest ni Fase 7.
- No implementar operador modal cancelable para preview/export; A5 queda para 6d.
- No calibrar sensibilidad de trackpad del selector; es pulido UX no bloqueante registrado desde M6.

## Archivos Esperados

- `spritesheet_frame_selector/render/renderer.py`
- `spritesheet_frame_selector/preview/generator.py`
- `spritesheet_frame_selector/operators/preview.py`
- `spritesheet_frame_selector/ui/panels.py`
- `spritesheet_frame_selector/properties.py`
- `spritesheet_frame_selector/core/cache.py` si se ajusta identidad B9
- `spritesheet_frame_selector/core/paths.py` si se agrega helper GC
- `tests/test_preview_cache.py`
- `tests/test_render_state.py` o nuevo test focalizado si el repo ya separa renderer/preview
- `tests/test_workspace_model.py` o test existente de propiedades si hay cobertura de frame range

## Validacion

### Validaciones Automaticas

- `python3 -m compileall spritesheet_frame_selector`
- `python3 -m unittest discover -s tests`
- Busquedas de contrato:
  - `rg -n "color_mode|color_depth" spritesheet_frame_selector/render spritesheet_frame_selector/preview tests`
  - `rg -n "force=True|force = True|force:" spritesheet_frame_selector/operators spritesheet_frame_selector/ui tests`
  - `rg -n "frame_start|frame_end" spritesheet_frame_selector/properties.py tests`
  - `rg -n "render_key|render_dirty|render_path|render_folder|last_render_note|build_render_key|_existing_render_paths_for_clip" spritesheet_frame_selector tests`
  - `rg -n "view_perspective|CAMERA|show_overlays|shading" spritesheet_frame_selector/preview/generator.py tests`

### Validaciones Blender GUI/Background

- A2: configurar escena con `image_settings.color_mode = "RGB"` y export transparente activo; exportar spritesheet y frames individuales; confirmar que PNG resultante conserva alpha y que la configuracion de escena queda restaurada despues.
- A4: generar previews, cambiar material/pose/animacion visible, ejecutar regeneracion forzada y confirmar thumbnails actualizados sin requerir Clear Cache manual.
- M1: generar preview de un sujeto que cubre todo el encuadre; la generacion no debe fallar ni borrar archivos por ausencia de pixeles transparentes.
- M2: generar previews con una configuracion, cambiar tamano/modo/rango para crear otra cache key, regenerar con exito y confirmar que carpetas hermanas administradas antiguas se purgan sin borrar carpetas no administradas.
- M4: intentar ingresar frame negativo en UI o por propiedad; debe clamp/rechazar a 0 y `sync_clip_frames` no debe producir frame numbers negativos.
- B11 + P1: generar previews SOLID/MATERIAL desde viewport inicialmente en perspectiva libre; los thumbnails deben usar la camara efectiva y, al terminar, el viewport debe volver a su perspectiva/shading/overlay previo.

### Criterio De Aceptacion Por Hallazgo

- A2: export transparente produce PNG con canal alpha aunque la escena parta en RGB/BW; estado original restaurado.
- A4: existe ruta UI de regeneracion forzada y usa `force=True`; depsgraph queda implementado solo si la investigacion demuestra filtro seguro, o diferido con razon explicita.
- M1: preview 100% opaco no cancela generacion ni borra archivo valido.
- M2: cache obsoleta del mismo clip se purga solo bajo carpetas administradas.
- M4: frames negativos no pueden entrar al modelo MVP.
- B9: queda corregido con identidad compartida de preview o clasificado con evidencia como no aplicable/aceptado tras 6c, sin reintroducir render cache final.
- B11: shading/overlay se aplica/restaura una vez por generacion y no rompe Camera View temporal de 6b0.
- P1-preview-camera-view: sigue validado por regresion manual o test de contrato.

## Riesgos

- Mover el scope de shading/overlay para B11 puede romper la restauracion fina de 6b0 si no se conserva `try/finally` alrededor de todo estado tocado.
- Una invalidacion por depsgraph demasiado amplia puede marcar cache dirty constantemente. Por eso el entregable obligatorio de A4 es regeneracion forzada UI; depsgraph solo entra si queda claramente filtrado.
- GC de cache debe ser conservador. Solo debe borrar carpetas que pasen `is_managed_cache_folder` o salvaguarda equivalente.
- Cambiar identidad B9 puede invalidar caches existentes. Es aceptable si se documenta, pero no debe traer de vuelta render cache final.

## Proximo Paso Si Se Aprueba

Persistir este plan como aprobado y Plan Activo PCS. Luego implementarlo sin replanificar, dejando el estado como `implementado` hasta completar validacion Blender GUI.

## Resumen De Implementacion

- A2: `render/renderer.py::render_clip_frames` guarda/restaura `image_settings.color_mode` y `color_depth`; cuando `export_settings.transparent` fuerza `color_mode = "RGBA"` y `color_depth = "8"` durante el render PNG.
- A4: se agrego `SPRITESHEET_OT_preview_regenerate` (`spritesheet.preview_regenerate`) y la UI de Preview expone `Regenerate`, que llama `_generate_preview_cache(..., force=True)`.
- M1: la verificacion `_preview_file_has_transparency` ya no aborta ni borra un thumbnail valido si no detecta pixeles transparentes; la generacion termina con warning en el mensaje.
- M2: tras una generacion exitosa se purgan carpetas hermanas del cache del mismo clip, limitadas a nombres de cache key de 16 hex y carpetas administradas por `is_managed_cache_folder`.
- M4: `SpriteSheetClip.frame_start` y `SpriteSheetClip.frame_end` tienen `min=0`, ejecutando D2 para MVP.
- B9: no se reintrodujo `_id_key` ni render cache final. Tras 6c ya no existe divergencia con render key; para previews MVP se acepta que renombrar camara/coleccion invalide cache porque los nombres visibles forman parte de la clave actual.
- B11/P1: `preview/generator.py` mueve perspectiva de camara, shading y overlay a un scope exterior por generacion (`_viewport_render_scope`) y deja el render OpenGL por frame dentro de ese scope, preservando la correccion 6b0.

## Validaciones Ejecutadas

- Pasado: `python3 -m compileall spritesheet_frame_selector`.
- Pasado: `python3 -m unittest discover -s tests` con 77 tests.
- Pasado: busqueda de contrato `color_mode|color_depth` en render/preview/tests; renderer y previews fuerzan/restauran estado.
- Pasado: busqueda de contrato `force=True`; la ruta UI de `Regenerate` llama `force=True`.
- Pasado: busqueda de contrato `frame_start|frame_end`; las propiedades de clip declaran `min=0`.
- Pasado: busqueda de contrato de render cache final eliminado; no reaparecen `render_key`, `render_dirty`, `render_folder`, `last_render_note`, `build_render_key` ni `_existing_render_paths_for_clip`. La unica aparicion relacionada es el helper vivo `render_file_path`.
- Pasado: busqueda de contrato `view_perspective|CAMERA|show_overlays|shading`; el scope exterior conserva Camera View temporal y restauracion.

## Resultado De Validacion Blender GUI

Validado por el usuario el 2026-07-05. La validacion cubre el comportamiento implementado de 6b y habilita avanzar al siguiente subplan.

## Validacion Blender GUI Ejecutada

- A2: configurar escena con `image_settings.color_mode = "RGB"` y export transparente activo; exportar spritesheet y frames individuales; confirmar que PNG resultante conserva alpha y que la configuracion de escena queda restaurada despues.
- A4: generar previews, cambiar material/pose/animacion visible, ejecutar `Regenerate` y confirmar thumbnails actualizados sin requerir Clear Cache manual.
- M1: generar preview de un sujeto que cubre todo el encuadre; la generacion no debe fallar ni borrar archivos por ausencia de pixeles transparentes.
- M2: generar previews con una configuracion, cambiar tamano/modo/rango para crear otra cache key, regenerar con exito y confirmar que carpetas hermanas administradas antiguas se purgan sin borrar carpetas manuales.
- M4: intentar ingresar frame negativo en UI; debe clamp/rechazar a 0 y `sync_clip_frames` no debe producir frame numbers negativos.
- B11 + P1: generar previews SOLID/MATERIAL desde viewport inicialmente en perspectiva libre; thumbnails deben usar la camara efectiva y, al terminar, el viewport debe volver a su perspectiva/shading/overlay previo.
