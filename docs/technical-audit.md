# Auditoría técnica — SpriteSheet Frame Selector V2

**Alcance:** análisis estático de todo el paquete `spritesheet_frame_selector/` y `tests/`. No se ejecutó el addon dentro de Blender; los hallazgos que dependen de comportamiento en runtime se marcan como **[no verificado en runtime]**. Los 65 tests unitarios (helpers puros) pasan con `unittest`.

**Valoración general:** la arquitectura es notablemente buena para un addon de este tamaño: `core/` contiene helpers puros sin `bpy` (testeados), los operadores son finos, y tanto el generador de previews como el renderer restauran cuidadosamente el estado de escena que tocan. Los problemas principales están en (1) un subsistema de caché de render que quedó a medio implementar, (2) el ciclo de vida del selector modal, y (3) rendimiento/memoria en la composición del spritesheet.

---

## 1. Crítico

### C1. El selector visual bloquea toda la UI de Blender y puede quedar "invisible" pero activo

- **Problema:** el operador modal consume **todos** los eventos: `modal()` devuelve `RUNNING_MODAL` para cualquier evento no gestionado y nunca `PASS_THROUGH`. Mientras el selector está abierto no se puede navegar el viewport, usar menús ni ningún otro panel. Además, si el workspace/clip activo deja de coincidir con la sesión (p. ej. tras un undo que elimina el clip, o al cargar otro archivo), `draw()` retorna temprano y el overlay **desaparece**, pero el modal sigue consumiendo eventos: Blender parece congelado hasta que el usuario adivina pulsar ESC.
- **Causa:** [visual_selector.py:55](spritesheet_frame_selector/operators/visual_selector.py:55) (`modal` devuelve `RUNNING_MODAL` como fallback) y [visual_selector.py:313](spritesheet_frame_selector/ui/visual_selector.py:313) (`handle_visual_selector_event` no distingue clics dentro/fuera del panel ni valida que la sesión siga siendo coherente).
- **Impacto:** percepción de cuelgue total de Blender; el peor tipo de bug de UX en un modal.
- **Solución propuesta:** (a) devolver `PASS_THROUGH` para eventos fuera del rect del panel (al menos navegación: rueda, MIDDLEMOUSE, atajos con modificadores); (b) en cada evento, si `active_workspace_clip_readonly` no coincide con `workspace_id/clip_id` de la sesión, cerrar automáticamente (`cleanup_visual_selector_resources()` + `CANCELLED`).
- **Archivos/funciones:** `operators/visual_selector.py::SPRITESHEET_OT_visual_selector_open.modal`, `ui/visual_selector.py::handle_visual_selector_event`, `_handle_click`.

### C2. Fuga del draw handler y de recursos al terminar el modal sin pasar por cleanup

- **Problema:** si el modal termina sin ejecutar `cleanup_visual_selector_resources()` — el caso típico es cargar otro `.blend` (Blender cancela los modales sin invocar `modal()` de nuevo) — el `draw_handler_add` de [visual_selector.py:86](spritesheet_frame_selector/ui/visual_selector.py:86) queda registrado para siempre, junto con el diccionario `session.images` (datablocks `bpy.data.images` cargados). El addon no registra ningún handler `bpy.app.handlers.load_pre/load_post` que limpie sesión de selector ni sesión de playback; la limpieza solo ocurre en `unregister()`.
- **Causa:** ausencia total de handlers de ciclo de vida de archivo en [registration.py](spritesheet_frame_selector/registration.py); el ciclo de vida de la sesión depende exclusivamente de que el modal muera "limpiamente".
- **Impacto:** fuga de memoria/handler acumulativa por sesión; overlay fantasma dibujándose sobre datos obsoletos; `self.region`/`self.area` de la sesión pasan a ser referencias muertas (los accesos en `draw()` a `self.region.width` lanzarían `ReferenceError` en cada redraw — spam de excepciones en consola). **[no verificado en runtime]** el detalle exacto del `ReferenceError`, pero el leak del handler es estructural.
- **Solución propuesta:** registrar un `@persistent` `load_pre` handler que llame a `cleanup_playback_resources()` y `cleanup_visual_selector_resources()`, y registrarlo/quitarlo en `register()/unregister()`. Adicionalmente, envolver el cuerpo de `draw()` en try/except que auto-cierre la sesión ante `ReferenceError`.
- **Archivos/funciones:** `registration.py::register/unregister`, `ui/visual_selector.py::VisualSelectorSession.draw/close`, `playback/controller.py::cleanup_playback_resources`.

---

## 2. Alto

### A1. Todo el subsistema de caché de render final es código muerto: cada export siempre re-renderiza

- **Problema:** `_ensure_rendered_frames` intenta reutilizar renders previos vía `_existing_render_paths_for_clip` y `not clip.render_dirty`. Pero en todo el addon **nadie escribe jamás** `frame.render_path` con una ruta real ni pone `render_dirty = False` (verificado por grep: solo hay escrituras a `""`/`True`). Resultado: la rama de reutilización nunca se activa y cada export re-renderiza todos los clips. Además, `build_render_key`, `render_warning`, `count_render_references`, `count_existing_renders`, `clear_render_state` y `render_file_name` ([render_state.py](spritesheet_frame_selector/core/render_state.py)) no tienen ningún caller en el addon — solo en `tests/test_render_state.py`. Y los renders van a un `tempfile.TemporaryDirectory` que se destruye al salir del `with`, así que persistir esas rutas sería inútil tal como está.
- **Causa:** feature a medio implementar: el modelo de datos (`render_key/render_folder/render_dirty/last_render_note/render_path` en [properties.py](spritesheet_frame_selector/properties.py)) y los helpers existen, pero el flujo de export nunca cierra el ciclo.
- **Impacto:** exports lentos e innecesariamente repetidos (cada clip se re-renderiza aunque nada cambiara); ~200 líneas de código y 5 propiedades persistidas en el `.blend` sin función; deuda que confunde a cualquier lector (aparenta haber caché donde no la hay).
- **Solución propuesta:** decidir explícitamente: (a) **completar** — renderizar a una carpeta gestionada persistente (análoga a la de previews), escribir `render_path`, `render_key`, `render_dirty=False` tras éxito y validar con `build_render_key`; o (b) **eliminar** todo el subsistema (propiedades, helpers y la rama de `_existing_render_paths_for_clip`) y aceptar el re-render. Cualquiera de las dos es mejor que el estado intermedio.
- **Archivos/funciones:** `operators/export.py::_ensure_rendered_frames/_existing_render_paths_for_clip`, `core/render_state.py` (completo), `properties.py::SpriteSheetClip/SpriteSheetFrameItem`, `core/workspace_state.py::clear_clip_render_state`.

### A2. El render final no fuerza `color_mode = "RGBA"`: el export "transparente" puede salir sin alfa

- **Problema:** `render_clip_frames` fuerza `film_transparent`, formato PNG, resolución… pero **no** toca `image_settings.color_mode` (verificado: cero apariciones de `color_mode` en [renderer.py](spritesheet_frame_selector/render/renderer.py)). Si la escena del usuario tiene `color_mode = "RGB"` o `"BW"`, los PNG se escriben sin canal alfa y el spritesheet "transparente" sale con fondos opacos/negros. El generador de previews sí lo hace correctamente ([generator.py:77](spritesheet_frame_selector/preview/generator.py:77)) — inconsistencia clara entre ambos backends.
- **Causa:** omisión al replicar la lista de estado guardado/forzado del preview generator en el renderer.
- **Impacto:** salida incorrecta silenciosa del artefacto principal del addon, dependiente de configuración previa de la escena (el default de Blender es RGBA, por eso pasa desapercibido).
- **Solución propuesta:** en `render_clip_frames`, guardar/forzar/restaurar `image_settings.color_mode = "RGBA"` cuando `export_settings.transparent` (y valorar fijar `color_depth = "8"` como en previews).
- **Archivos/funciones:** `render/renderer.py::render_clip_frames`.

### A3. Composición del spritesheet en Python puro: O(píxel) en CPU y riesgo de OOM

- **Problema:** `compose_spritesheet_png` construye el canvas como **lista Python de floats** (`[0.0]*W*H*4`) y `_paste_pixels` copia con un bucle anidado **por píxel** con slicing de 4 elementos. Además cada frame se materializa con `list(image.pixels)` (lento). Una lista Python de floats cuesta ~32 bytes/elemento: una hoja de 4096×4096 (p. ej. frames de 256 px, 16 columnas, 256 frames) son ~67M px → ~268M floats → **varios GB de RAM** y decenas de segundos de CPU, con riesgo real de cuelgue/OOM ya que `frame_width/height` no tienen máximo.
- **Causa:** implementación de referencia sin vectorizar en [composer.py:45](spritesheet_frame_selector/export/composer.py:45) y [composer.py:98](spritesheet_frame_selector/export/composer.py:98).
- **Impacto:** exports grandes lentísimos o imposibles; Blender congelado sin feedback (se combina con A5).
- **Solución propuesta:** usar `numpy` (disponible en el Python de Blender): `image.pixels.foreach_get(buffer)` a un `np.float32`, reshape y asignación de bloques 2D por frame; `foreach_set` del canvas final. Reduce memoria ~8× y el tiempo en órdenes de magnitud. Como mínimo, copiar por **filas** (`canvas[a:b] = src[c:d]`) en lugar de por píxel.
- **Archivos/funciones:** `export/composer.py::compose_spritesheet_png/_paste_pixels`.

### A4. Los previews no se invalidan al editar la escena y no existe regeneración forzada en la UI

- **Problema:** la clave de caché ([cache.py:13](spritesheet_frame_selector/core/cache.py:13)) solo depende de ids, rango, tamaño, modo, nombre de cámara y nombres de colecciones. Editar la animación, mallas o materiales **no** marca `cache_dirty` ni cambia la clave, y `SPRITESHEET_OT_preview_generate` siempre llama con `force=False`, que **salta** los archivos ya existentes ([generator.py:86](spritesheet_frame_selector/preview/generator.py:86)). El parámetro `force=True` no es accesible desde ninguna parte de la UI (verificado por grep). El único camino del usuario es Clear Cache + Generate, nada indica que deba hacerlo.
- **Causa:** invalidación basada únicamente en settings del addon, sin señal de cambio de contenido; operador de force nunca expuesto.
- **Impacto:** el usuario selecciona frames mirando thumbnails obsoletos — socava el propósito central del addon.
- **Solución propuesta:** corto plazo: botón "Regenerate (force)" (el pipeline ya lo soporta) y dejar claro en el panel que los previews son instantáneas. Medio plazo: incluir en la clave una señal barata de cambio (p. ej. `depsgraph.updates` via handler que marque `cache_dirty`, o un contador de `bpy.app.handlers.depsgraph_update_post` filtrado por colecciones efectivas).
- **Archivos/funciones:** `core/cache.py::build_preview_cache_key`, `operators/preview.py::SPRITESHEET_OT_preview_generate`, `ui/panels.py::SPRITESHEET_PT_main.draw`.

### A5. Generación de previews y export completamente síncronos: UI congelada sin progreso ni cancelación

- **Problema:** `_generate_preview_cache` y `SPRITESHEET_OT_export_spritesheet.execute` renderizan N frames (potencialmente cientos, y en modo RENDERED con motor de render completo) en un solo `execute()` bloqueante. No hay barra de progreso, ni ESC, ni redraw intermedio.
- **Causa:** diseño de operador simple; no hay uso de operador modal con timer ni de `wm.progress_begin/update/end`.
- **Impacto:** Blender "colgado" durante minutos en escenas reales; el usuario puede matar el proceso creyendo que falló (y con A3, a veces tendrá razón).
- **Solución propuesta:** convertir generación/export a operador modal con `wm.event_timer_add` procesando un frame por tick (el estado guardado/restaurado ya está bien aislado, lo que facilita el refactor), con `wm.progress_*` y cancelación por ESC. Como mejora mínima inmediata: `wm.progress_begin/update/end` alrededor de los bucles.
- **Archivos/funciones:** `operators/preview.py::_generate_preview_cache`, `operators/export.py::execute/_ensure_rendered_frames`, `preview/generator.py::generate_viewport_previews`, `render/renderer.py::render_clip_frames`.

---

## 3. Medio

### M1. Falso positivo en la verificación de transparencia: un frame legítimamente opaco aborta la generación

- **Problema:** `_preview_file_has_transparency` exige `any(alpha < 0.999)`: si el sujeto cubre el 100% del encuadre (sprite a pantalla completa), el preview se borra y toda la generación falla con "did not produce transparent alpha". Además itera todos los píxeles en Python por cada frame (65k lecturas para 256px).
- **Causa:** heurística pensada para detectar viewports que ignoran `film_transparent`, formulada como "debe existir al menos un píxel transparente" ([generator.py:233](spritesheet_frame_selector/preview/generator.py:233)).
- **Impacto:** fallo duro en un caso de uso válido; coste O(px) por frame.
- **Solución propuesta:** degradar a advertencia (`last_preview_note`) en vez de error + borrado; o verificar solo el primer frame; muestrear píxeles (p. ej. bordes) en vez del frame completo.
- **Archivos/funciones:** `preview/generator.py::_preview_file_has_transparency/generate_viewport_previews`.

### M2. Basura de caché acumulada indefinidamente

- **Problema:** cada cambio de settings crea una nueva carpeta `<workspace>/<clip>/<cache_key>`; las carpetas de claves anteriores no se borran nunca (Clear Cache solo borra la actual; `force` solo la actual). También quedan huérfanas las carpetas de clips/workspaces eliminados.
- **Causa:** sin GC en [preview.py:113](spritesheet_frame_selector/operators/preview.py:113).
- **Impacto:** crecimiento de disco sin límite junto al `.blend` del usuario.
- **Solución propuesta:** al generar con éxito, borrar las carpetas hermanas de `<clip_id>/` distintas de la clave actual (ya se tiene `is_managed_cache_folder` como salvaguarda); opcionalmente purgar carpetas de clips inexistentes al abrir.
- **Archivos/funciones:** `operators/preview.py::_generate_preview_cache`, `core/paths.py`.

### M3. El timer de playback fuerza el redraw de **todas** las áreas de todas las ventanas en cada tick

- **Problema:** `_tag_redraw()` ([controller.py:235](spritesheet_frame_selector/playback/controller.py:235)) recorre todas las ventanas/áreas a la frecuencia del clip (hasta 60 fps): redibuja Properties, Outliner, editores de nodos, etc.
- **Causa:** redraw indiscriminado por simplicidad.
- **Impacto:** consumo de CPU/GPU innecesario durante la reproducción, notable en layouts complejos.
- **Solución propuesta:** tag solo de áreas `VIEW_3D` (o solo del área de la sesión del selector, que el controller podría recibir como referencia débil).
- **Archivos/funciones:** `playback/controller.py::_tag_redraw`.

### M4. Frames negativos: desajuste silencioso entre rango del clip y frames almacenados

- **Problema:** `clip.frame_start/frame_end` no tienen `min`, pero `SpriteSheetFrameItem.frame_number` tiene `min=0`. Con `frame_start=-10`, `frame_numbers()` genera negativos, `sync_clip_frames` los escribe y Blender los clampa a 0 → colisiones de números, y `result.frame_paths.get(frame.frame_number)` no encuentra la ruta → previews vacíos sin mensaje de error.
- **Causa:** inconsistencia de rangos entre [properties.py:110](spritesheet_frame_selector/properties.py:110) y [properties.py:200](spritesheet_frame_selector/properties.py:200).
- **Impacto:** edge case (Blender permite frames negativos) con fallo silencioso difícil de diagnosticar.
- **Solución propuesta:** o quitar `min=0` de `frame_number`, o poner `min=0` a `frame_start/frame_end`. Elegir y alinear.
- **Archivos/funciones:** `properties.py::SpriteSheetFrameItem/SpriteSheetClip`, `core/frame_sync.py::sync_clip_frames`.

### M5. Triple implementación de la misma validación + etiquetas duplicadas en el panel

- **Problema:** las comprobaciones cámara/colecciones/override se implementan tres veces: inline en `_generate_preview_cache` ([preview.py:68-92](spritesheet_frame_selector/operators/preview.py:68)), en `preview_context_warnings` ([workspace_state.py:93](spritesheet_frame_selector/core/workspace_state.py:93)) y en `validate_active_clip_render_context` ([validation.py:16](spritesheet_frame_selector/core/validation.py:16)), con órdenes de precedencia ligeramente distintos entre sí (riesgo de divergencia). Además el panel pinta las colecciones faltantes **dos veces**: `preview_context_warnings` ya las incluye y [panels.py:173](spritesheet_frame_selector/ui/panels.py:173) las vuelve a listar.
- **Causa:** evolución incremental sin consolidar.
- **Impacto:** mantenimiento por triplicado; UI con mensajes repetidos.
- **Solución propuesta:** una única función en `core/validation.py` con parámetro de severidad (preview/render) consumida por operador y panel; eliminar el bucle duplicado del panel.
- **Archivos/funciones:** `operators/preview.py::_generate_preview_cache`, `core/workspace_state.py::preview_context_warnings`, `core/validation.py`, `ui/panels.py::SPRITESHEET_PT_main.draw`.

### M6. El selector visual no tiene scroll: los frames que no caben son inseleccionables desde el overlay

- **Problema:** el grid dibuja `max_visible = columns*rows` celdas y muestra "Showing X / Y frames" ([visual_selector.py:220](spritesheet_frame_selector/ui/visual_selector.py:220)); no hay paginación ni rueda de ratón para alcanzar el resto (solo Select All/Invert/Every-2 a ciegas).
- **Causa:** feature no implementada.
- **Impacto:** con clips largos y celdas grandes, parte de la funcionalidad principal (selección visual frame a frame) queda inaccesible.
- **Solución propuesta:** offset de scroll en la sesión manejando `WHEELUPMOUSE/WHEELDOWNMOUSE` (encaja con C1: esos eventos hoy se consumen sin hacer nada).
- **Archivos/funciones:** `ui/visual_selector.py::VisualSelectorSession.draw/handle_visual_selector_event`.

### M7. Duplicación estructural transversal

- **Problema:** (a) `_scene_state`/`_active_workspace` copiados en 4 módulos de operadores; (b) `_clear_collection` duplicado en `workspace_state.py` y `frame_sync.py`; (c) tres sanitizadores de nombres casi idénticos: `safe_path_part` (paths.py), `_safe_file_prefix` (render_state.py), `_safe_sheet_name` (export.py); (d) `effective_preview_mode(workspace, clip)` ignora `workspace` y está duplicado como `effective_preview_label` en visual_selector.py.
- **Causa:** módulos crecidos en paralelo.
- **Impacto:** solo mantenibilidad, pero es la fuente más probable de divergencias futuras (p. ej. los sanitizadores ya producen resultados distintos para el mismo nombre).
- **Solución propuesta:** un `core/context.py` con `scene_state(context)/active_workspace(context)/active_clip(context)`; unificar sanitizador en `core/paths.py`; eliminar `effective_preview_label` y el parámetro muerto.
- **Archivos/funciones:** `operators/{clips,workspaces,preview,playback,export,visual_selector}.py`, `core/{workspace_state,frame_sync,paths,render_state}.py`, `ui/visual_selector.py`.

### M8. Registro defensivo que enmascara errores y puede des-registrar clases ajenas

- **Problema:** en `register()` ([registration.py:118](spritesheet_frame_selector/registration.py:118)), si `register_class` lanza `ValueError` (clase ya registrada, p. ej. por otra copia del addon o un reload a medias), la clase **se añade igualmente** a `_registered_classes`, y `unregister()` la des-registrará aunque este módulo no fuera su dueño. Además el patrón try/except silencioso oculta errores de registro reales (anotaciones mal definidas, etc.).
- **Causa:** defensa contra dobles registros llevada demasiado lejos.
- **Impacto:** en el flujo normal no pasa nada; en escenarios de reload/doble instalación produce estados inconsistentes difíciles de depurar.
- **Solución propuesta:** registro directo con `bpy.utils.register_classes_factory(CLASSES)` (patrón estándar) y dejar que los errores aflofen; mantener como mucho el try/except en `unregister`.
- **Archivos/funciones:** `registration.py::register/unregister`.

### M9. Thumbnails obsoletos en el selector por `check_existing=True` sin `reload()`

- **Problema:** `_draw_preview_image`/`_cached_image_or_none` cargan con `bpy.data.images.load(path, check_existing=True)`: si un datablock con esa ruta ya existe (sesión anterior del selector, o regeneración de caché que reescribió los mismos ficheros), se reutilizan los píxeles antiguos sin `image.reload()`.
- **Causa:** [visual_selector.py:480](spritesheet_frame_selector/ui/visual_selector.py:480) y [visual_selector.py:529](spritesheet_frame_selector/ui/visual_selector.py:529).
- **Impacto:** el selector puede mostrar thumbnails que no corresponden al contenido actual del fichero de caché.
- **Solución propuesta:** al cachear por primera vez en la sesión, llamar `image.reload()` si el datablock ya existía; o invalidar `session.images` cuando cambie `clip.cache_key`.
- **Archivos/funciones:** `ui/visual_selector.py::_draw_preview_image/_cached_image_or_none`.

### M10. Posible coste de `gpu.texture.from_image` por celda y por redraw — **[no verificado]**

- **Problema:** `_draw_preview_image` llama `gpu.texture.from_image(image)` en cada redraw para cada celda visible. Si la versión de Blender objetivo no cachea internamente la textura GPU del datablock, esto implicaría subir texturas cada frame durante el playback.
- **Causa/Impacto:** no puedo verificar el comportamiento interno de `from_image` sin ejecutar en la versión objetivo; si no cachea, es el mayor coste del overlay.
- **Solución propuesta:** perfilar en runtime; si hace falta, cachear `GPUTexture` en la sesión junto al datablock.
- **Archivos/funciones:** `ui/visual_selector.py::_draw_preview_image`.

---

## 4. Bajo

- **B1. Confusión de parámetros en el renderer:** `render_file_path(output_folder, output_index, …)` pasa un índice secuencial por el parámetro `frame_number` ([renderer.py:66](spritesheet_frame_selector/render/renderer.py:66)); el dict resultante mapea números de frame reales a ficheros nombrados por índice. Funciona, pero el nombrado engaña al lector. Renombrar el parámetro o documentarlo.
- **B2. Export de secuencia individual:** el límite de 999 se lanza a mitad de la copia dejando salida parcial ([sequence.py:18](spritesheet_frame_selector/export/sequence.py:18)), y a esas alturas el PNG del sheet ya se escribió, dejando estado mixto; el patrón de limpieza acepta 6 dígitos (rama muerta). Validar `len(frame_paths) <= 999` antes de copiar.
- **B3. Campo muerto `original_index`:** se escribe y copia ([frame_sync.py](spritesheet_frame_selector/core/frame_sync.py), [workspace_state.py:186](spritesheet_frame_selector/core/workspace_state.py:186)) pero ningún código lo lee para lógica. Eliminarlo o documentar su propósito futuro.
- **B4. Código muerto menor en el generator:** `original_compression` se guarda y restaura pero nunca se modifica ([generator.py:64](spritesheet_frame_selector/preview/generator.py:64)); la rama de restauración es ruido.
- **B5. `SPRITESHEET_OT_visual_selector_open.execute()`** devuelve `FINISHED` sin hacer nada cuando no es background ([visual_selector.py:61](spritesheet_frame_selector/operators/visual_selector.py:61)) — invocado desde script parecería funcionar sin abrir nada. Devolver `CANCELLED` con mensaje.
- **B6. Silenciamiento amplio de excepciones:** `except Exception: pass/return` en `_tag_redraw`, `_session_matches_context`, `_preview_file_has_transparency`, `_draw_preview_image`. Dificulta el diagnóstico; loggear al menos con `print`/`logging` en modo debug.
- **B7. Undo inconsistente en el overlay:** el clic en una celda en modo EDIT muta `frame.selected` directamente ([visual_selector.py:377](spritesheet_frame_selector/ui/visual_selector.py:377)) sin push de undo, mientras que el operador equivalente (`frame_toggle_selection`) sí es `UNDO`. Enrutar el clic por el operador.
- **B8. Compatibilidad/manifiesto — [no verificable sin probar en las versiones]:** `blender_version_min = "5.0.0"` excluye 4.x aunque la API usada (`temp_override`, `gpu`, extensiones) es compatible desde 4.2; no hay `bl_info`, así que como addon legacy no aparece. Si es intencional, documentarlo; si no, bajar el mínimo a 4.2.
- **B9. Criterios de identidad distintos entre claves:** la clave de previews usa `name_full` de colecciones y `camera.name`; la de render usa `library.filepath + name_full` (`_id_key`). Renombrar una cámara invalida previews pero conceptualmente es la misma cámara. Unificar en `_id_key` compartido.
- **B10. `resume_playback` ignora cambios de FPS:** al reanudar se usa el fps de la sesión congelada, no el actual del clip ([controller.py:63](spritesheet_frame_selector/playback/controller.py:63)). Releer `clip.fps` al reanudar.
- **B11. Shading del viewport se cambia y restaura por cada frame** en `_write_viewport_thumbnail` en lugar de una vez alrededor del bucle completo — trabajo redundante y posibles parpadeos del viewport durante la generación.
- **B12. `update_workspace_defaults_dirty` no marca `render_dirty`** ([properties.py:72](spritesheet_frame_selector/properties.py:72)) mientras que los operadores análogos de colecciones default sí marcan ambos flags — inconsistencia (irrelevante mientras A1 siga muerto, pero divergirá si se completa).

---

## 5. Mejoras propuestas (sistema, UX, escalabilidad)

1. **Generación asíncrona con progreso** (ver A5) — el beneficio de UX más grande por esfuerzo invertido; el aislamiento actual del estado de escena hace el refactor razonable.
2. **Botón "Regenerate previews" + invalidación por depsgraph** (A4) — cierra la brecha de confianza en los thumbnails.
3. **Scroll/paginación en el selector + eventos PASS_THROUGH** (C1, M6) — convierte el overlay en una herramienta convivial en lugar de un modo bloqueante.
4. **Composer con numpy** (A3) — habilita hojas grandes; hoy el techo práctico es bajo.
5. **GC de caché** (M2) y un pequeño indicador en el panel del tamaño de caché en disco.
6. **Decisión sobre la caché de render** (A1): completarla daría exports incrementales reales (re-render solo de clips con `render_dirty`), que con varios clips por workspace es un ahorro grande; eliminarla quita ~200 líneas y 5 propiedades.
7. **Consolidación** (M5, M7): `core/context.py`, validación única, sanitizador único — reduce el coste de cada cambio futuro.
8. **Extensibilidad del export:** `build_spritesheet_metadata` está bien aislado; si se prevén más motores (TexturePacker, Aseprite JSON), formalizar una interfaz de "metadata writer" ahora que hay un solo formato es barato.

## 6. Lo que no pude verificar

- Comportamiento en runtime dentro de Blender (no se ejecutó el addon): C2 (detalle del `ReferenceError`), M10 (`gpu.texture.from_image`), B8 (compatibilidad real 4.x/5.x), y el rendimiento real del overlay.
- La semántica de `==` entre wrappers de `PropertyGroup` en `_mark_collection_owner_dirty` ([properties.py:87](spritesheet_frame_selector/properties.py:87)): `bpy_struct` compara por puntero interno según la documentación, lo que haría el código correcto, pero no lo he comprobado empíricamente en la versión objetivo.
- Los tests (65) cubren solo `core/`, `export/layout|metadata`, `playback/sequence`: todo el código que toca `bpy` (operadores, generator, renderer, composer, overlay) carece de cobertura — esperable, pero significa que los hallazgos A2/A3/C1/C2 no tienen red de seguridad.

Si quieres, el siguiente paso natural sería atacar C1+C2 (ciclo de vida del selector) y A2 (RGBA), que son fixes pequeños y de alto retorno.