# Plan Fase 6f - Verificacion Integral De Auditoria

Estado: aprobado
Autoridad: usuario
Modo de ejecucion: ejecutar sin replanificar
Estado De Ejecucion: cerrado

## Referencia Superior

`docs/plans/reinicio-v2-fase-6-correcciones-auditoria-tecnica.md`

## Documentacion Fuente Usada

- `docs/technical-audit.md`
- `docs/plans/reinicio-v2-fase-6-correcciones-auditoria-tecnica.md`
- `docs/plans/reinicio-v2-master-plan.md`
- Subplanes de Fase 6 ya creados:
  - `docs/plans/reinicio-v2-fase-6a-selector-modal-lifecycle.md`
  - `docs/plans/reinicio-v2-fase-6a-validacion-hito1-selector-modal-lifecycle.md`
  - `docs/plans/reinicio-v2-fase-6a-hito2-selector-playback-integridad.md`
  - `docs/plans/reinicio-v2-fase-6a-hito3-selector-scroll.md`
  - `docs/plans/reinicio-v2-fase-6b0-preview-camera-viewport.md`
  - `docs/plans/reinicio-v2-fase-6b-preview-alpha-estado-visual.md`
  - `docs/plans/reinicio-v2-fase-6c-render-cache-final.md`
  - `docs/plans/reinicio-v2-fase-6d-rendimiento-export.md`
  - `docs/plans/reinicio-v2-fase-6e-consolidacion-higiene.md`

## Interpretacion Operativa

6f no es una fase para corregir codigo nuevo de forma amplia. Es una fase de verificacion, reconciliacion y cierre tecnico de la auditoria antes de habilitar Fase 7.

La auditoria tecnica sigue siendo la fuente canonica de problema, causa, impacto y solucion propuesta. Este plan trae una copia operativa de los hallazgos para que la ejecucion de 6f no dependa de releer la auditoria durante cada chequeo. Si durante 6f aparece una divergencia entre codigo, subplan y auditoria, se debe tratar asi:

- si es un bug local y acotado de una correccion ya implementada, corregirlo dentro de 6f y documentar la evidencia;
- si exige reabrir una decision rectora, detenerse y pedir decision del usuario;
- si pertenece a Fase 7 por decision vigente, verificar que el diferimiento esta documentado y no bloquear Fase 6;
- si es un hallazgo runtime nuevo, registrarlo como hallazgo nuevo y proponer subplan o correccion acotada segun severidad.

## Estado De Entrada

- 6a hito 1, validacion hito 1, hito 2 e hito 3 estan validados por el usuario.
- 6b0, 6b y 6c estan validados por el usuario.
- 6d esta implementado y con validacion Blender GUI pendiente.
- 6e esta implementado y con validacion Blender GUI pendiente.
- Fase 7 existe como plan propuesto, diferido hasta validar Fase 6.
- `docs/technical-audit.md` no debe editarse para actualizar hallazgos; el estado vivo se registra en planes/PCS.

## Objetivo

Verificar integralmente que todos los hallazgos de `docs/technical-audit.md` quedaron en uno de estos estados antes de retomar Fase 7:

- corregido con evidencia automatica y/o GUI;
- diferido con decision explicita y razon no bloqueante;
- no aplica con evidencia en codigo/plan;
- pendiente de correccion nueva, en cuyo caso Fase 7 sigue bloqueada.

## Hallazgos De Auditoria Cubiertos

| ID | Severidad | Titulo | Estado En Este Subplan |
|---|---|---|---|
| C1 | critico | Selector visual bloquea UI y puede quedar invisible pero activo | verificar correccion validada en 6a |
| C2 | critico | Fuga de draw handler/recursos al terminar modal sin cleanup | verificar correccion validada en 6a y punto runtime |
| A1 | alto | Render cache final muerto: cada export re-renderiza | verificar eliminacion validada en 6c |
| A2 | alto | Render final transparente puede salir sin alfa por no forzar RGBA | verificar correccion validada en 6b |
| A3 | alto | Composer Python puro lento y con riesgo OOM | verificar implementacion 6d y validacion GUI pendiente |
| A4 | alto | Previews no se invalidan al editar escena y no hay regeneracion forzada | verificar correccion validada en 6b |
| A5 | alto | Preview/export sin progreso ni cancelacion | verificar implementacion 6d y decidir si D4 nivel 1 basta |
| M1 | medio | Falso positivo de transparencia aborta previews opacos validos | verificar correccion validada en 6b |
| M2 | medio | Basura de cache acumulada indefinidamente | verificar correccion validada en 6b |
| M3 | medio | Playback redibuja todas las areas en cada tick | verificar correccion validada en 6a hito 2 |
| M4 | medio | Frames negativos desalinean rango y frames almacenados | verificar D2 validado en 6b |
| M5 | medio | Validacion duplicada y etiquetas duplicadas en panel | verificar implementacion 6e y validacion GUI pendiente |
| M6 | medio | Selector visual sin scroll | verificar correccion validada en 6a hito 3 |
| M7 | medio | Duplicacion estructural transversal | verificar implementacion 6e |
| M8 | medio | Registro defensivo enmascara errores | verificar implementacion 6e y validacion GUI pendiente |
| M9 | medio | Thumbnails obsoletos por `check_existing=True` sin `reload()` | verificar correccion validada en 6a hito 2 |
| M10 | medio/no verificado | Posible coste de `gpu.texture.from_image` por redraw | verificar clasificacion/perfilado de 6a hito 2 |
| B1 | bajo | Parametro engañoso en renderer | verificar correccion validada en 6c |
| B2 | bajo | Export individual valida limite 999 tarde y deja salida parcial | verificar implementacion 6d y validacion GUI pendiente |
| B3 | bajo | Campo muerto `original_index` | verificar implementacion 6e |
| B4 | bajo | `compression` guardado/restaurado sin modificarse | verificar implementacion 6e |
| B5 | bajo | Operador visual selector devuelve `FINISHED` sin abrir nada | verificar correccion validada en 6a |
| B6 | bajo | `except Exception` amplios silencian errores | verificar 6a/6e |
| B7 | bajo | Overlay muta seleccion directo sin operador/undo | verificar correccion validada en 6a hito 2 |
| B8 | bajo/no verificable | Compatibilidad/manifiesto 5.x vs 4.x | verificar diferimiento D3 a Fase 7 |
| B9 | bajo | Criterios de identidad distintos entre preview/render keys | verificar clasificacion de 6b/6c |
| B10 | bajo | `resume_playback` ignora cambios de FPS | verificar correccion validada en 6a hito 2 |
| B11 | bajo | Shading viewport cambia/restaura por frame | verificar correccion validada en 6b |
| B12 | bajo | `update_workspace_defaults_dirty` no marca `render_dirty` | verificar no aplica tras D1/6c |
| P1-preview-camera-view | alto runtime | Preview SOLID/MATERIAL usaba viewport libre en vez de camara efectiva | verificar correccion validada en 6b0 |
| P1-playback-selection-snapshot | alto runtime | Playback seguia usando snapshot anterior tras cambiar seleccion | verificar correccion validada en 6a hito 2 |
| PG-equality | no verificado | Igualdad de `PropertyGroup` en dirty owner | verificar implementacion 6e por `as_pointer()` |

## Extracto Operativo De Auditoria

### C1 - Selector visual bloquea UI y puede quedar invisible pero activo

- Problema: el operador modal consumia todos los eventos y podia quedar activo aunque el overlay desapareciera.
- Causa: `operators/visual_selector.py::SPRITESHEET_OT_visual_selector_open.modal` devolvia `RUNNING_MODAL` como fallback y `ui/visual_selector.py::handle_visual_selector_event` no distinguia eventos dentro/fuera ni invalidaba sesion incoherente.
- Impacto: Blender parecia congelado hasta que el usuario pulsaba ESC.
- Solucion propuesta por la auditoria: devolver `PASS_THROUGH` para eventos fuera del rect o navegacion; cerrar automaticamente si workspace/clip activo no coincide con la sesion.
- Archivos/funciones afectados: `operators/visual_selector.py`, `ui/visual_selector.py`.
- Aspectos no verificados en runtime: comportamiento exacto ante cambios de contexto y eventos fuera del panel.

### C2 - Fuga de draw handler y recursos al terminar modal sin cleanup

- Problema: al cargar otro `.blend` o cancelar el modal fuera del flujo normal, el draw handler y `session.images` podian quedar vivos.
- Causa: no habia handlers `load_pre/load_post`; la limpieza dependia de que `modal()` terminara limpiamente.
- Impacto: fuga de memoria/handler, overlay fantasma, referencias muertas y posible spam de `ReferenceError`.
- Solucion propuesta por la auditoria: registrar handler persistente `load_pre` que llame a `cleanup_playback_resources()` y `cleanup_visual_selector_resources()`; envolver `draw()` para auto-cerrar ante `ReferenceError`.
- Archivos/funciones afectados: `registration.py::register/unregister`, `ui/visual_selector.py::VisualSelectorSession.draw/close`, `playback/controller.py::cleanup_playback_resources`.
- Aspectos no verificados en runtime: detalle exacto del `ReferenceError` al cargar otro archivo.

### A1 - Render cache final muerto

- Problema: la rama de reutilizacion de renders finales nunca se activaba porque nadie escribia rutas reales ni marcaba `render_dirty=False`; varios helpers eran codigo muerto.
- Causa: feature de cache final a medio implementar con rutas temporales destruidas al salir del export.
- Impacto: exports siempre re-renderizados, propiedades persistidas sin funcion y deuda tecnica confusa.
- Solucion propuesta por la auditoria: decidir completar cache persistente o eliminar el subsistema.
- Archivos/funciones afectados: `operators/export.py::_ensure_rendered_frames/_existing_render_paths_for_clip`, `core/render_state.py`, `properties.py`, `core/workspace_state.py::clear_clip_render_state`.
- Aspectos no verificados en runtime: beneficio real de cache incremental; Fase 6 decidio D1 eliminar para MVP.

### A2 - Render final no fuerza RGBA

- Problema: export transparente podia generar PNG sin alpha si la escena estaba en `RGB` o `BW`.
- Causa: `render/renderer.py::render_clip_frames` no guardaba/forzaba/restauraba `image_settings.color_mode`.
- Impacto: spritesheet transparente con fondo opaco o negro segun configuracion previa del usuario.
- Solucion propuesta por la auditoria: forzar/restaurar `image_settings.color_mode = "RGBA"` cuando export es transparente y valorar `color_depth = "8"`.
- Archivos/funciones afectados: `render/renderer.py::render_clip_frames`.
- Aspectos no verificados en runtime: export con escena previamente configurada en RGB.

### A3 - Composer Python puro lento y con riesgo OOM

- Problema: `compose_spritesheet_png` usaba lista Python de floats y `_paste_pixels` copiaba por pixel; frames se materializaban con `list(image.pixels)`.
- Causa: implementacion no vectorizada en `export/composer.py`.
- Impacto: hojas grandes lentas, consumo de varios GB y posible cuelgue/OOM.
- Solucion propuesta por la auditoria: usar `numpy` con `foreach_get/foreach_set`; como minimo copiar por filas.
- Archivos/funciones afectados: `export/composer.py::compose_spritesheet_png/_paste_pixels`.
- Aspectos no verificados en runtime: disponibilidad real de numpy y medicion con hoja mediana.

### A4 - Previews no se invalidan al editar escena y no hay regeneracion forzada

- Problema: la key de cache no cambiaba con ediciones de malla/material/animacion y `Generate` no exponia `force=True`.
- Causa: invalidacion basada en settings del addon, no en contenido, y operador sin accion de regenerate.
- Impacto: thumbnails obsoletos para seleccionar frames.
- Solucion propuesta por la auditoria: boton de regeneracion forzada como corto plazo; investigar invalidacion por depsgraph como medio plazo.
- Archivos/funciones afectados: `core/cache.py`, `operators/preview.py`, `ui/panels.py`.
- Aspectos no verificados en runtime: confiabilidad y coste de invalidacion depsgraph.

### A5 - Preview/export sincronicos sin progreso ni cancelacion

- Problema: generacion de previews y export procesaban N frames en un `execute()` bloqueante.
- Causa: operadores simples sin `wm.progress_*`, modal timer ni cancelacion.
- Impacto: Blender parecia colgado en escenas reales.
- Solucion propuesta por la auditoria: idealmente operador modal cancelable; minimo inmediato con `wm.progress_begin/update/end`.
- Archivos/funciones afectados: `operators/preview.py`, `operators/export.py`, `preview/generator.py`, `render/renderer.py`.
- Aspectos no verificados en runtime: si D4 nivel 1 es suficiente para exports medianos.

### M1 - Falso positivo de transparencia

- Problema: `_preview_file_has_transparency` exigia algun pixel con alpha menor a 0.999 y abortaba previews 100% opacos validos.
- Causa: heuristica formulada como fallo duro.
- Impacto: generacion fallaba aunque el sujeto cubriera todo el encuadre.
- Solucion propuesta por la auditoria: degradar a advertencia o verificar canal alpha sin exigir transparencia visual.
- Archivos/funciones afectados: `preview/generator.py::_preview_file_has_transparency/generate_viewport_previews`.
- Aspectos no verificados en runtime: frame opaco legitimo en preview transparente.

### M2 - Basura de cache acumulada

- Problema: cada cambio de settings creaba carpetas de cache antiguas que no se borraban.
- Causa: sin GC en `_generate_preview_cache`; Clear Cache solo borraba la cache actual.
- Impacto: crecimiento de disco junto al `.blend`.
- Solucion propuesta por la auditoria: tras generacion exitosa, borrar carpetas hermanas de la key actual con `is_managed_cache_folder` como salvaguarda.
- Archivos/funciones afectados: `operators/preview.py::_generate_preview_cache`, `core/paths.py`.
- Aspectos no verificados en runtime: limpieza de carpetas administradas sin tocar archivos del usuario.

### M3 - Playback redibuja todas las areas

- Problema: `_tag_redraw()` recorria todas las ventanas/areas a cada tick.
- Causa: redraw indiscriminado por simplicidad.
- Impacto: gasto CPU/GPU innecesario.
- Solucion propuesta por la auditoria: redibujar solo `VIEW_3D` o area de sesion.
- Archivos/funciones afectados: `playback/controller.py::_tag_redraw`.
- Aspectos no verificados en runtime: mejora real en layouts complejos.

### M4 - Frames negativos

- Problema: `clip.frame_start/frame_end` permitian negativos pero `SpriteSheetFrameItem.frame_number` tenia `min=0`, provocando clamps/colisiones.
- Causa: inconsistencia de rangos.
- Impacto: previews vacios o rutas no encontradas.
- Solucion propuesta por la auditoria: alinear rangos; Fase 6 decidio D2 prohibir negativos con `min=0`.
- Archivos/funciones afectados: `properties.py`, `core/frame_sync.py`.
- Aspectos no verificados en runtime: comportamiento con archivos que ya tenian negativos.

### M5 - Validacion duplicada y etiquetas duplicadas

- Problema: validaciones camara/colecciones/override existian en tres lugares y el panel podia mostrar colecciones faltantes dos veces.
- Causa: evolucion incremental.
- Impacto: divergencia futura y UI repetida.
- Solucion propuesta por la auditoria: funcion unica en `core/validation.py` con modo/severidad, consumida por operadores y panel.
- Archivos/funciones afectados: `operators/preview.py`, `core/workspace_state.py`, `core/validation.py`, `ui/panels.py`.
- Aspectos no verificados en runtime: que panel y operadores muestren mensajes equivalentes sin duplicados.

### M6 - Selector visual sin scroll

- Problema: el grid solo dibujaba `max_visible` celdas sin paginacion ni rueda.
- Causa: feature no implementada.
- Impacto: frames fuera de la ventana eran inseleccionables desde overlay.
- Solucion propuesta por la auditoria: offset de scroll manejado con `WHEELUPMOUSE/WHEELDOWNMOUSE`.
- Archivos/funciones afectados: `ui/visual_selector.py::VisualSelectorSession.draw/handle_visual_selector_event`.
- Aspectos no verificados en runtime: sensibilidad de trackpad; el usuario valido funcionalidad y noto ajuste UX opcional.

### M7 - Duplicacion estructural transversal

- Problema: helpers de contexto, limpieza de colecciones, sanitizadores y labels/modos de preview estaban duplicados.
- Causa: modulos crecidos en paralelo.
- Impacto: divergencia futura.
- Solucion propuesta por la auditoria: `core/context.py`, sanitizador unico, eliminar parametro muerto y deduplicar `_clear_collection`.
- Archivos/funciones afectados: operadores, `core/workspace_state.py`, `core/frame_sync.py`, `core/paths.py`, `core/render_state.py`, `ui/visual_selector.py`.
- Aspectos no verificados en runtime: que los operadores resuelvan workspace/clip igual tras la consolidacion.

### M8 - Registro defensivo enmascara errores

- Problema: `register()` capturaba `ValueError`, agregaba clases a `_registered_classes` y podia desregistrar clases ajenas.
- Causa: defensa contra dobles registros demasiado amplia.
- Impacto: estados inconsistentes en reload/doble instalacion.
- Solucion propuesta por la auditoria: registro directo o `register_classes_factory`; tolerancia solo en `unregister`.
- Archivos/funciones afectados: `registration.py::register/unregister`.
- Aspectos no verificados en runtime: activar/desactivar/reactivar addon.

### M9 - Thumbnails obsoletos en selector

- Problema: `bpy.data.images.load(path, check_existing=True)` podia reutilizar pixeles antiguos sin `image.reload()`.
- Causa: cache de datablocks por ruta sin invalidacion.
- Impacto: selector podia mostrar thumbnails que no correspondian al archivo actual.
- Solucion propuesta por la auditoria: llamar `image.reload()` al reutilizar datablock o invalidar imagenes de sesion al cambiar `clip.cache_key`.
- Archivos/funciones afectados: `ui/visual_selector.py::_draw_preview_image/_cached_image_or_none`.
- Aspectos no verificados en runtime: regeneracion de cache con mismos paths y selector abierto/cerrado.

### M10 - Posible coste de `gpu.texture.from_image`

- Problema: `_draw_preview_image` llamaba `gpu.texture.from_image(image)` por celda y redraw.
- Causa: no estaba verificado si Blender cachea internamente la textura GPU.
- Impacto: si no cachea, seria el mayor coste del overlay.
- Solucion propuesta por la auditoria: perfilar en runtime y cachear `GPUTexture` solo si hace falta.
- Archivos/funciones afectados: `ui/visual_selector.py::_draw_preview_image`.
- Aspectos no verificados en runtime: comportamiento interno de `from_image` en Blender objetivo.

### B1 - Parametro engañoso en renderer

- Problema: `render_file_path(output_folder, output_index, ...)` usaba un indice secuencial pero el parametro sugeria frame nativo.
- Causa: nombre/contrato confuso.
- Impacto: lectura engañosa aunque funcionara.
- Solucion propuesta por la auditoria: renombrar parametro o documentar contrato.
- Archivos/funciones afectados: `render/renderer.py::render_file_path`.
- Aspectos no verificados en runtime: no aplica; es claridad de codigo.

### B2 - Export individual valida limite 999 tarde

- Problema: el limite de 999 se lanzaba durante la copia, dejando salida parcial.
- Causa: validacion local tardia en `export/sequence.py`.
- Impacto: PNG/JSON o algunos frames podian quedar escritos aunque fallara la operacion.
- Solucion propuesta por la auditoria: validar `len(frame_paths) <= 999` antes de copiar; Fase 6 exige antes de renderizar.
- Archivos/funciones afectados: `export/sequence.py`, `operators/export.py`.
- Aspectos no verificados en runtime: fallo temprano sin render ni salida nueva con mas de 999 frames.

### B3 - Campo muerto `original_index`

- Problema: se escribia/copiaba pero no se leia para logica.
- Causa: dato heredado sin uso vigente.
- Impacto: ruido persistido y deuda conceptual.
- Solucion propuesta por la auditoria: eliminarlo o documentar proposito futuro.
- Archivos/funciones afectados: `properties.py`, `core/frame_sync.py`, `core/workspace_state.py`.
- Aspectos no verificados en runtime: tolerancia de `.blend` existentes con propiedad antigua.

### B4 - `compression` guardado/restaurado sin modificarse

- Problema: preview generator guardaba/restauraba `image_settings.compression` aunque no la cambiaba.
- Causa: snapshot de estado demasiado amplio.
- Impacto: ruido menor.
- Solucion propuesta por la auditoria: retirar guardado/restauracion.
- Archivos/funciones afectados: `preview/generator.py::generate_viewport_previews`.
- Aspectos no verificados en runtime: previews siguen restaurando solo estado tocado.

### B5 - Visual selector devuelve `FINISHED` sin abrir nada

- Problema: `SPRITESHEET_OT_visual_selector_open.execute()` devolvia `FINISHED` sin hacer nada cuando no era background.
- Causa: contrato de operador incompleto para invocacion desde script.
- Impacto: aparenta exito sin abrir selector.
- Solucion propuesta por la auditoria: devolver `CANCELLED` con mensaje.
- Archivos/funciones afectados: `operators/visual_selector.py::SPRITESHEET_OT_visual_selector_open.execute`.
- Aspectos no verificados en runtime: invocacion directa por script.

### B6 - Silenciamiento amplio de excepciones

- Problema: `except Exception: pass/return` ocultaba fallos.
- Causa: defensas locales para no romper draw/UI.
- Impacto: diagnostico dificil.
- Solucion propuesta por la auditoria: loggear al menos con debug opt-in.
- Archivos/funciones afectados: `_tag_redraw`, `_session_matches_context`, `_preview_file_has_transparency`, `_draw_preview_image` y catches restantes.
- Aspectos no verificados en runtime: que el logging no genere ruido en modo normal.

### B7 - Undo inconsistente en overlay

- Problema: click de celda mutaba `frame.selected` directamente.
- Causa: UI bypass del operador con `UNDO`.
- Impacto: seleccion no integrada con undo/sincronizacion.
- Solucion propuesta por la auditoria: enrutar por `bpy.ops.spritesheet.frame_toggle_selection`.
- Archivos/funciones afectados: `ui/visual_selector.py::_handle_click`.
- Aspectos no verificados en runtime: comportamiento de undo y playback tras toggles.

### B8 - Compatibilidad/manifiesto

- Problema: `blender_version_min = "5.0.0"` excluye 4.x aunque parte de la API podria ser compatible; sin `bl_info` legacy.
- Causa: decision de compatibilidad no documentada inicialmente.
- Impacto: usuarios 4.x excluidos si no era intencional.
- Solucion propuesta por la auditoria: documentar intencion o bajar minimo a 4.2 tras pruebas.
- Archivos/funciones afectados: manifest/addon metadata.
- Aspectos no verificados en runtime: compatibilidad real 4.x/5.x. Fase 6 decidio D3 mantener 5.x y diferir revision de manifest a Fase 7.

### B9 - Criterios de identidad distintos

- Problema: preview key usaba nombres; render key usaba `library.filepath + name_full`.
- Causa: dos criterios de identidad paralelos.
- Impacto: invalidaciones distintas al renombrar camara/coleccion.
- Solucion propuesta por la auditoria: unificar en `_id_key` compartido o documentar invalidacion por rename.
- Archivos/funciones afectados: `core/cache.py`, `core/render_state.py`.
- Aspectos no verificados en runtime: impacto real tras eliminar render cache final.

### B10 - `resume_playback` ignora cambios de FPS

- Problema: al reanudar, playback usaba FPS congelado en la sesion anterior.
- Causa: no releia `clip.fps`.
- Impacto: velocidad incorrecta tras editar FPS.
- Solucion propuesta por la auditoria: releer `clip.fps` al reanudar.
- Archivos/funciones afectados: `playback/controller.py::resume_playback`.
- Aspectos no verificados en runtime: cambio de FPS entre pausa y resume.

### B11 - Shading viewport cambia/restaura por frame

- Problema: `_write_viewport_thumbnail` cambiaba/restauraba shading y overlay en cada frame.
- Causa: scope demasiado interno.
- Impacto: trabajo redundante y posible parpadeo.
- Solucion propuesta por la auditoria: mover cambio/restauracion alrededor del bucle completo.
- Archivos/funciones afectados: `preview/generator.py`.
- Aspectos no verificados en runtime: estabilidad visual durante generacion.

### B12 - `update_workspace_defaults_dirty` no marca `render_dirty`

- Problema: defaults de workspace marcaban preview dirty pero no render dirty.
- Causa: inconsistencia con operadores analogos.
- Impacto: si se completaba render cache final, podria divergir.
- Solucion propuesta por la auditoria: marcar ambos o eliminar render cache. Fase 6 decidio D1 eliminar render cache final.
- Archivos/funciones afectados: `properties.py::update_workspace_defaults_dirty`.
- Aspectos no verificados en runtime: no aplica tras eliminar render cache.

### P1-preview-camera-view - Preview usaba viewport libre

- Problema: `Generate Preview` en `SOLID`/`MATERIAL` podia renderizar desde la vista libre si el usuario no estaba en Camera View.
- Causa: `bpy.ops.render.opengl(write_still=True, view_context=True)` usa el viewport 3D actual.
- Impacto: thumbnails con objeto diminuto o encuadre incorrecto.
- Solucion implementada: forzar temporalmente `RegionView3D.view_perspective = "CAMERA"` durante el render OpenGL y restaurar estado.
- Archivos/funciones afectados: `preview/generator.py`.
- Aspectos no verificados en runtime: repeticion estable ya validada por usuario en 6b0.

### P1-playback-selection-snapshot - Playback usa snapshot anterior

- Problema: cambios de seleccion no siempre se reflejaban inmediatamente en playback.
- Causa: la sesion activa conservaba `frame_numbers`/`preview_paths` previos y algunos clicks modificaban seleccion sin pasar por operador.
- Impacto: frames eliminados seguian reproduciendose hasta forzar actualizacion manual.
- Solucion implementada: refrescar sesion activa al cambiar seleccion y enrutar toggles por operador.
- Archivos/funciones afectados: `playback/controller.py`, `operators/playback.py`, `ui/visual_selector.py`, `core/selection.py`.
- Aspectos no verificados en runtime: validado por usuario tras 6a hito 2.

### PG-equality - Igualdad de PropertyGroup

- Problema: `_mark_collection_owner_dirty` dependia de `item == collection_item`.
- Causa: semantica de igualdad de wrappers Blender no verificada.
- Impacto: dirty flags podrian no marcarse en alguna version/reload.
- Solucion rectora: comparar identidad por `as_pointer()` con fallback seguro.
- Archivos/funciones afectados: `properties.py::_mark_collection_owner_dirty`.
- Aspectos no verificados en runtime: semantica exacta de `==`; 6e debe evitar depender de ella.

## Interpretacion Del Subplan

- Decision: verificar y reconciliar, no reimplementar masivamente.
- Argumento: Fase 6 ya ejecuto subplanes especificos para cada superficie. 6f debe proteger contra cierres accidentales, regresiones entre subplanes y validaciones GUI pendientes, especialmente 6d/6e.
- Riesgos: un chequeo superficial podria habilitar Fase 7 con hallazgos altos no validados; un chequeo demasiado amplio podria reabrir decisiones ya tomadas sin evidencia nueva.
- Dependencias con otros hallazgos:
  - A3/A5/B2 dependen de validar 6d en Blender GUI.
  - M5/M7/M8/B3/B4/B6/PG-equality dependen de validar 6e en Blender GUI.
  - B8 queda fuera de Fase 6 por D3, pero 6f debe confirmar que Fase 7 lo recoge.
  - M10 queda clasificado solo si la validacion de overlay/playback no muestra degradacion que justifique cache GPU.

## Alcance De Implementacion

### Incluir

- Reconciliar el ledger del plan rector contra:
  - codigo actual;
  - subplanes implementados/validados;
  - validaciones automaticas;
  - validaciones Blender GUI reportadas por el usuario.
- Ejecutar validaciones automaticas:
  - `python3 -m compileall spritesheet_frame_selector`
  - `python3 -m unittest discover -s tests`
  - busquedas `rg` por contratos cerrados.
- Preparar una matriz de validacion GUI final de Fase 6 para el usuario.
- Incorporar como primer hito las validaciones GUI pendientes de 6d y 6e.
- Revisar que `docs/technical-audit.md` no fue editado para falsear estado.
- Revisar que `docs/plans/reinicio-v2-fase-7-validacion-distribucion.md` cubre B8/D3 y las limitaciones que deben pasar a packaging.
- Actualizar el estado del plan 6f a `implementado` solo si se ejecutan los chequeos documentales/automaticos; dejar `validado` solo cuando el usuario confirme las validaciones GUI requeridas.

### Excluir

- No crear ZIP final ni ejecutar packaging de Fase 7.
- No archivar planes ni cerrar PCS.
- No modificar `docs/technical-audit.md`.
- No cambiar decisiones D1, D2, D3, D4, D5 sin aprobacion del usuario.
- No implementar cache final de render.
- No bajar compatibilidad a Blender 4.x.
- No convertir preview/export a operadores modales cancelables salvo que la validacion de A5 demuestre que D4 nivel 1 es insuficiente y el usuario apruebe ampliar alcance.

### Archivos Esperados

- `docs/plans/reinicio-v2-fase-6f-verificacion-integral-auditoria.md`
- Posibles actualizaciones, solo durante ejecucion aprobada:
  - `docs/plans/reinicio-v2-fase-6-correcciones-auditoria-tecnica.md` para estado final del ledger.
  - `.context/agent_context.md`, `.context/index.md` y `.context/handoff.md` si PCS debe reflejar cambio de Plan Activo o proximo paso.
  - Codigo/test acotado solo si 6f descubre regresion local de una correccion ya implementada.

## Hitos De Ejecucion

### Hito 0 - Precondicion 6d/6e

Validar o registrar como pendiente bloqueante:

- 6d A3: export mediano completa sin regresion visual evidente.
- 6d A5: preview/export muestran progreso y no dejan progreso pegado al finalizar/fallar.
- 6d B2: export individual con mas de 999 frames falla antes de renderizar/escribir salidas nuevas.
- 6e M5/M8: activar/desactivar/reactivar addon sin clases/handlers duplicados; panel sin mensajes duplicados para camara/coleccion faltante.
- 6e M7/B3/B4/B6/PG-equality: preview/export normales siguen funcionando tras consolidacion; dirty flags se marcan al cambiar defaults/overrides.

Si Hito 0 falla, 6f se detiene y se crea correccion acotada para el subplan correspondiente.

### Hito 1 - Verificacion Estatica Y Busquedas De Contrato

Ejecutar busquedas que demuestren que los contratos cerrados siguen vigentes:

- Render cache final eliminado/no usado: `rg -n "render_key|render_folder|render_dirty|last_render_note|render_path|build_render_key|clear_render_state|count_existing_renders|count_render_references" spritesheet_frame_selector tests`
- RGBA render final: `rg -n "color_mode|color_depth|film_transparent" spritesheet_frame_selector/render spritesheet_frame_selector/preview tests`
- Frames negativos prohibidos: `rg -n "frame_start|frame_end|frame_number" spritesheet_frame_selector/properties.py tests`
- Limite 999 temprano: `rg -n "999|Individual frame export supports up to 999" spritesheet_frame_selector tests`
- Registro: `rg -n "register_class|register_classes_factory|_registered_classes|load_pre" spritesheet_frame_selector/registration.py tests`
- Selector/playback: `rg -n "PASS_THROUGH|cleanup_visual_selector_resources|cleanup_playback_resources|frame_toggle_selection|resume_playback|tag_redraw" spritesheet_frame_selector tests`
- Preview/cache: `rg -n "force|Regenerate|is_managed_cache_folder|reload\\(|view_perspective|CAMERA|overlay|shading" spritesheet_frame_selector tests`
- Consolidacion: `rg -n "def _scene_state|def _active_workspace|original_index|effective_preview_label|effective_preview_mode\\(workspace|compression|except Exception" spritesheet_frame_selector tests`

### Hito 2 - Validaciones Automaticas

- Ejecutar `python3 -m compileall spritesheet_frame_selector`.
- Ejecutar `python3 -m unittest discover -s tests`.
- Si fallan, corregir solo lo necesario para restaurar el contrato ya aprobado.

### Hito 3 - Matriz GUI Final De Fase 6

Validar en Blender GUI:

- Abrir selector, interactuar fuera del panel segun contrato modal vigente y cerrar con ESC sin overlay fantasma.
- Generar preview desde viewport no puesto en Camera View; confirmar encuadre de camara efectiva.
- Generar y regenerar previews `SOLID` y `MATERIAL`; confirmar thumbnails frescos, scroll y seleccion/playback sincronizados.
- Exportar PNG transparente con escena configurada previamente en `RGB`; confirmar alpha y restauracion de settings.
- Exportar spritesheet y secuencia individual validada por el usuario; confirmar JSON si aplica.
- Repetir export con mas de 999 frames individuales; confirmar fallo temprano.
- Activar/desactivar/reactivar addon; confirmar handlers y clases sin duplicados.
- Provocar camara/coleccion faltante; confirmar mensajes no duplicados.
- Cambiar defaults/overrides de workspace/clip; confirmar dirty/cache/invalidation esperada.

### Hito 4 - Reconciliacion Del Ledger

Actualizar el ledger de Fase 6 con evidencia:

- `corregido`: ruta de subplan, validacion automatica y/o GUI.
- `diferido`: decision vigente y destino exacto.
- `no aplica`: evidencia concreta.
- `pendiente`: solo si bloquea Fase 7 y requiere nuevo subplan/correccion.

### Hito 5 - Habilitacion De Fase 7

Fase 7 queda habilitada solo si:

- no quedan IDs criticos/altos pendientes;
- A3/A5/B2 y M5/M8 fueron validados en GUI o tienen limitacion aceptada por el usuario;
- B8 esta explicitamente diferido por D3 y cubierto por el plan de Fase 7;
- las validaciones automaticas pasan;
- PCS refleja el proximo paso sin cerrar ni archivar planes.

## Validacion

### Validaciones Automaticas

- `python3 -m compileall spritesheet_frame_selector`
- `python3 -m unittest discover -s tests`
- Busquedas `rg` listadas en Hito 1.
- Revision de `git diff -- docs/technical-audit.md` para confirmar que la auditoria canonica no fue modificada.

### Validaciones Blender GUI/Background

Blender background no es suficiente para validar `SOLID/MATERIAL`, modal, draw handlers ni UI real. En este entorno, Blender background puede crashear por Metal; por lo tanto la validacion relevante de 6f es Blender GUI manual.

La validacion GUI debe cubrir:

- selector modal/lifecycle;
- preview desde camara efectiva;
- preview alpha/regeneracion/scroll;
- playback y seleccion;
- export transparente;
- export mediano con progreso;
- limite >999 antes de render;
- registro/desregistro/reactivacion;
- panel sin warnings duplicados.

### Criterio De Aceptacion Por Hallazgo

- C1/C2/B5: selector se cierra/limpia sin bloquear Blender fuera del contrato modal aceptado; no quedan overlays/handlers fantasmas.
- A1/B1/B12: render cache final muerto no queda como subsistema activo; helpers vivos tienen nombres/contratos claros.
- A2: render final transparente fuerza/restaura RGBA/8 bits segun contrato.
- A3: composer no copia por pixel; export mediano completa sin regresion visual.
- A4/M1/M2/B9/B11/P1-preview-camera-view: previews son confiables, regenerables, con cache GC y camara efectiva.
- A5: hay progreso visible suficiente; si no basta, se debe crear subplan de operador modal cancelable antes de Fase 7.
- M3/M9/M10/B7/B10/P1-playback-selection-snapshot: selector/playback reflejan seleccion y FPS actuales, no fuerzan redraw global innecesario y no muestran thumbnails obsoletos.
- M4: frames negativos quedan prohibidos por propiedades.
- M5/M7/M8/B3/B4/B6/PG-equality: consolidacion no rompio registro, panel, operadores ni dirty flags.
- M6: scroll permite acceder a todos los frames; sensibilidad trackpad queda como ajuste UX opcional si no bloquea uso.
- B2: limite 999 falla antes de render/escritura parcial.
- B8: queda diferido a Fase 7 por D3, con `blender_version_min = "5.0.0"` intencional.

## Riesgos

- Ejecutar 6f antes de validar 6d/6e puede dar falso cierre de Fase 6. Por eso Hito 0 es bloqueante.
- Algunas evidencias runtime dependen de validacion manual del usuario; si no se ejecutan, el estado correcto es `implementado pendiente de validacion`, no `validado`.
- Busquedas `rg` pueden encontrar referencias historicas en tests o docs; la interpretacion debe distinguir codigo activo, tests y documentacion.
- Corregir bugs nuevos dentro de 6f debe mantenerse acotado; si aparece un fallo transversal, crear subplan nuevo.

## Resumen De Implementacion

6f fue aprobado por instruccion explicita del usuario e implementado como verificacion documental/automatica. No se marco como validado porque Hito 0 e Hito 3 requieren Blender GUI.

Resultados:

- Hito 0: pendiente de Blender GUI. Bloquea validar Fase 6 y habilitar Fase 7.
- Hito 1: ejecutado con busquedas de contrato. No se detecto una regresion bloqueante en codigo activo.
- Hito 2: ejecutado. Compilacion y tests pasan.
- Hito 3: matriz GUI preparada; pendiente de ejecucion manual.
- Hito 4: reconciliacion preliminar completada; A3/A5/B2 y M5/M8/B3/B4/B6/PG-equality siguen dependiendo de validacion GUI de 6d/6e.
- Hito 5: Fase 7 aun no queda habilitada porque falta validacion GUI acumulada.

Interpretacion de busquedas relevantes:

- Render cache final: no quedan propiedades/helpers muertos `render_key`, `render_folder`, `render_dirty`, `last_render_note`, `render_path`, `build_render_key`, `clear_render_state`, `count_existing_renders` ni `count_render_references` en codigo activo. Solo queda `core/render_state.py::render_file_path(render_folder, output_index, sheet_name)`, helper vivo del flujo de render/export.
- RGBA/render final: `render/renderer.py` guarda, fuerza y restaura `color_mode`, `color_depth` y `film_transparent`; tests cubren restauracion desde RGB/16.
- M1 alpha preview: `_preview_file_has_transparency` conserva la deteccion `any(alpha < 0.999)` solo como warning agregado al mensaje; ya no aborta ni borra previews validos.
- M4 frames negativos: `frame_start`, `frame_end` y `frame_number` tienen `min=0`.
- B2 limite 999: `export/sequence.py` conserva validacion defensiva y `operators/export.py` valida antes del render; tests cubren el fallo temprano.
- Registro/lifecycle: `registration.py` registra `load_pre`, limpia playback/selector y solo agrega clases a `_registered_classes` tras registro exitoso.
- Selector/playback: existen `PASS_THROUGH`, cleanup runtime, uso de `frame_toggle_selection`, `resume_playback(fps=clip.fps)` y redraw limitado a `VIEW_3D`.
- Preview/cache: existen `Regenerate`, `force=True`, `is_managed_cache_folder`, `image.reload()`, Camera View temporal y restauracion de shading/overlay.
- Consolidacion: no quedan helpers duplicados `_scene_state`/`_active_workspace` en operadores, `original_index`, `effective_preview_label`, `effective_preview_mode(workspace` ni `compression` en generator. Los `except Exception` restantes tienen debug opt-in o devuelven fallo contextual.
- PG-equality: `_mark_collection_owner_dirty` usa comparacion por `as_pointer()` con fallback a identidad Python.
- B8/D3: `spritesheet_frame_selector/blender_manifest.toml` mantiene `blender_version_min = "5.0.0"` y Fase 7 incluye revision de manifest/compatibilidad.
- Auditoria canonica: `git diff -- docs/technical-audit.md` no produjo cambios; la auditoria sigue intacta.

## Validaciones Ejecutadas

- Pasado: `python3 -m compileall spritesheet_frame_selector`.
- Pasado: `python3 -m unittest discover -s tests` con 81 tests.
- Pasado: busquedas `rg` de Hito 1, con las interpretaciones registradas arriba.
- Pasado: revision de `docs/technical-audit.md` sin diff.

## Validacion Blender GUI Pendiente

Estas validaciones siguen siendo obligatorias antes de marcar 6f como validado o habilitar Fase 7:

- 6d A3: export mediano completa sin regresion visual evidente.
- 6d A5: Generate/Regenerate Preview y Export muestran progreso y no dejan progreso pegado al finalizar/fallar.
- 6d B2: export individual con mas de 999 frames falla antes de renderizar o escribir salidas nuevas.
- 6e M5/M8: activar/desactivar/reactivar addon sin clases/handlers duplicados; panel sin mensajes duplicados para camara/coleccion faltante.
- 6e M7/B3/B4/B6/PG-equality: preview/export normales siguen funcionando tras consolidacion; defaults/overrides marcan cache dirty como corresponde.
- Matriz acumulada 6f: selector modal/lifecycle, preview desde camara efectiva, regenerate, scroll, playback/seleccion, export transparente y B8 diferido a Fase 7.

## Proximo Paso

Ejecutar la validacion Blender GUI pendiente de 6d/6e/6f. Si pasa, actualizar 6f y el plan rector de Fase 6 a `validado` o `listo para cierre` segun corresponda, sin cerrar PCS ni archivar planes salvo instruccion explicita.
