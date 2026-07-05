# Plan Fase 6 - Correcciones Auditoria Tecnica

Estado: propuesto
Autoridad: pendiente
Modo de ejecucion: pendiente
Estado De Ejecucion: pendiente

## Referencia Superior

`docs/plans/reinicio-v2-master-plan.md`

## Planes Relacionados

- `docs/archive/reinicio-v2-fase-5-workspace-root-vertical-slices.md`
- `docs/archive/reinicio-v2-fase-5g-export-spritesheet-json.md`
- `docs/plans/reinicio-v2-fase-7-validacion-distribucion.md`

## Fuente Principal

`docs/technical-audit.md`

## Rol De Este Plan Y De La Auditoria

La auditoria tecnica es la fuente canonica de los hallazgos y de sus soluciones propuestas. Este plan no reemplaza la auditoria ni debe convertirse en una copia divergente. Su funcion es gobernar el proceso:

- ordenar los hallazgos en subfases ejecutables;
- declarar dependencias y prioridades;
- decidir que bloquea la Fase 7;
- fijar el contrato que debe cumplir cada subplan;
- registrar las interpretaciones operativas cuando la auditoria deja alternativas o puntos no verificados.

Regla obligatoria: cada subplan ejecutable debe incorporar explicitamente, para cada hallazgo que cubra, el contenido operativo de la auditoria: problema, causa, impacto, solucion propuesta, archivos/funciones afectados y validaciones. No basta con una referencia generica a `docs/technical-audit.md`.

La copia detallada debe vivir en el subplan que ejecuta el cambio, no en este plan rector. Motivo: la precision tecnica debe estar junto al alcance concreto, los archivos a editar y las validaciones de ese subplan. Este plan mantiene la estrategia y evita duplicar toda la auditoria en un documento que no ejecuta codigo.

## Estado De Entrada

- Fase 5g fue validada manualmente por el usuario.
- `docs/technical-audit.md` audito estaticamente `spritesheet_frame_selector/` y `tests/`.
- La auditoria declara que los 65 tests unitarios pasan con `unittest`.
- La auditoria no ejecuto el addon dentro de Blender; los hallazgos dependientes de runtime se mantienen como pendientes de verificacion runtime cuando corresponda.
- La Fase 7 de validacion/distribucion queda diferida hasta que esta fase corrija o clasifique explicitamente todos los hallazgos de auditoria.

## Interpretacion Operativa

La auditoria no es una lista de pulido posterior. Sus hallazgos afectan estabilidad modal, lifecycle de handlers, exactitud del alpha exportado, confianza de previews, rendimiento/memoria del composer, deuda de render cache y mantenibilidad transversal. Por eso la distribucion no debe ejecutarse antes de resolver esta fase.

Esta Fase 6 es un plan rector de correcciones. No debe implementarse como bloque monolitico. Debe dividirse en subplanes ejecutables por riesgo, area tecnica y validacion posible. Cada subplan debe declarar exactamente que hallazgos cubre, que solucion propone la auditoria, si el subplan adopta o ajusta esa solucion, como la valida y que hallazgos deja fuera.

## Objetivo

Corregir o clasificar formalmente todos los hallazgos de `docs/technical-audit.md` antes de packaging final:

- los hallazgos criticos y altos deben quedar corregidos o convertidos en decision tecnica explicita con justificacion;
- los hallazgos medios deben quedar corregidos, diferidos con criterio de no bloqueo, o absorbidos por una correccion mayor;
- los hallazgos bajos deben quedar corregidos cuando el cambio sea local y seguro, o documentados como deuda aceptada con razon;
- los puntos no verificados en runtime deben tener prueba runtime o una decision de instrumentacion/perfilado;
- la Fase 7 solo puede retomarse cuando esta fase tenga estado `validado` o `listo para cierre`.

## Reglas De Implementacion

- No distribuir ZIP final dentro de esta fase.
- No reducir el alcance de la auditoria por conveniencia; todo ID C/A/M/B debe quedar rastreado.
- No crear subplanes que digan solo "ver auditoria"; deben traer extracto operativo explicito de los hallazgos que ejecutan.
- No reescribir una solucion de auditoria de forma mas vaga que el original. Si se resume, debe conservar todos los requisitos tecnicos, archivos/funciones y validaciones relevantes.
- Si un subplan modifica o rechaza una solucion propuesta por la auditoria, debe explicar por que, que riesgo reduce y que validacion compensa el cambio.
- No cerrar PCS ni archivar planes sin instruccion explicita de cierre.
- No crear un subplan nuevo si el hallazgo pertenece claramente a un subplan aprobado en ejecucion.
- No mezclar refactors amplios con fixes criticos si eso retrasa C1/C2/A2.
- No introducir dependencias externas obligatorias para el addon distribuible.
- Si se usa `numpy`, confirmar que forma parte del Python de Blender objetivo o mantener fallback sin dependencia externa.
- Si Blender background crashea en el entorno, documentar la limitacion y usar Blender GUI para los hallazgos que requieren runtime.
- Mantener rutas PCS repo-relativas en documentos operativos.

## Contrato Obligatorio Para Subplanes

Todo subplan derivado de esta Fase 6 debe ser autosuficiente para ejecutar los hallazgos que cubre. Debe leer `docs/technical-audit.md`, pero no puede delegar su precision a "consultar la auditoria" durante implementacion.

Cada subplan debe incluir estas secciones:

```md
## Hallazgos De Auditoria Cubiertos

| ID | Severidad | Titulo | Estado En Este Subplan |
|---|---|---|---|

## Extracto Operativo De Auditoria

### ID - Titulo

- Problema:
- Causa:
- Impacto:
- Solucion propuesta por la auditoria:
- Archivos/funciones afectados:
- Aspectos no verificados en runtime:

## Interpretacion Del Subplan

- Decision: adoptar solucion de auditoria | ajustar solucion | investigar antes de decidir | diferir con razon.
- Argumento:
- Riesgos:
- Dependencias con otros hallazgos:

## Alcance De Implementacion

- Incluir:
- Excluir:
- Archivos esperados:

## Validacion

- Validaciones automaticas:
- Validaciones Blender GUI/background:
- Criterio de aceptacion por hallazgo:
```

Reglas de contenido para `Extracto Operativo De Auditoria`:

- Debe preservar la solucion propuesta por la auditoria con suficiente detalle para implementarla.
- Debe listar rutas y funciones afectadas tal como las identifica la auditoria, actualizadas solo si el codigo cambio.
- Debe separar claramente la solucion de auditoria de la interpretacion del subplan.
- Si la auditoria ofrece alternativas, el subplan debe elegir una o declarar una investigacion previa corta con criterio de decision.
- Si la auditoria marca algo como no verificado en runtime, el subplan debe incluir una validacion runtime o explicar por que queda para 6f.

Reglas de cobertura:

- Un hallazgo critico o alto no puede quedar cubierto solo por una validacion general.
- Un subplan puede cubrir varios hallazgos solo si comparten superficie tecnica y validacion.
- Un subplan debe declarar explicitamente los hallazgos relacionados que no cubre para evitar cierres accidentales.
- La Fase 6f debe reconciliar la lista completa C1-C2, A1-A5, M1-M10 y B1-B12 contra subplanes implementados.

## Secuencia Rectora

### Fase 6a - Selector Modal Y Lifecycle Runtime

Objetivo: eliminar condiciones donde Blender parece congelado, el overlay queda invisible pero activo o quedan handlers/imagenes vivas tras cambios de archivo.

Hallazgos cubiertos:

- C1.
- C2.
- M3.
- M6.
- M9.
- M10, al menos como perfilado o decision.
- B5.
- B6, solo excepciones del selector/playback tocadas por esta fase.
- B7.
- B10 si el cambio de playback queda dentro del mismo controlador.

Argumento: C1 y C2 son los fallos de peor impacto para el usuario. Si el modal bloquea eventos o queda invisible, el usuario percibe Blender congelado. M3, M6, M9, M10, B5, B7 y B10 se ubican en el mismo limite selector/playback y conviene tratarlos mientras se toca ese lifecycle.

### Fase 6b - Exactitud De Preview, Alpha Y Estado Visual

Objetivo: asegurar que previews y render final representen lo que el usuario espera, especialmente transparencia, regeneracion y rangos de frames.

Hallazgos cubiertos:

- A2.
- A4.
- M1.
- M2, si la regeneracion forzada ya toca carpetas de cache.
- M4.
- B9.
- B11.
- B12 si la decision sobre render dirty no queda diferida por A1.

Argumento: A2 afecta el artefacto principal: un PNG exportado sin alpha cuando el usuario espera transparencia es una salida incorrecta silenciosa. A4, M1 y M9 afectan la confianza en thumbnails; si el selector muestra contenido viejo o falla por un frame opaco valido, el usuario toma decisiones sobre datos falsos. M4 debe decidirse antes de validar rangos de export.

### Fase 6c - Decision Y Correccion Del Render Cache Final

Objetivo: cerrar el estado intermedio de render cache detectado por A1.

Hallazgos cubiertos:

- A1.
- B1.
- B3, si `original_index` no tiene proposito futuro documentado.
- B12, si se decide completar cache.
- M7, solo sanitizadores/naming relacionados con render cache.

Argumento: A1 no es un bug local, es una decision de producto/arquitectura incompleta. El flujo actual renderiza en `tempfile.TemporaryDirectory`, por lo que persistir `frame.render_path` no tendria valor despues del `with`. Completar cache exige carpeta persistente gestionada, invalidacion, GC y estado derivado. Eliminarlo exige quitar propiedades/helpers/ramas muertas para no prometer cache inexistente.

Decision recomendada por defecto: para un primer ZIP MVP, eliminar o diferir explicitamente el render cache persistente y aceptar re-render, salvo que el usuario confirme que export incremental es requisito inmediato. Motivo: completar cache correctamente tiene mas superficie de lifecycle y limpieza que el beneficio actual; el rendimiento grande ya se ataca por A3/A5. Si se elimina, la UI y el modelo no deben sugerir render cache. Si se completa, debe hacerse como subplan especifico y no mezclarse con packaging.

### Fase 6d - Rendimiento, Memoria Y Seguridad De Export

Objetivo: evitar OOM, congelamientos largos sin feedback y salidas parciales inconsistentes en export.

Hallazgos cubiertos:

- A3.
- A5.
- B2.
- Mejoras propuestas 1 y 4.

Argumento: A3 y A5 se refuerzan entre si. El composer usa lista Python de floats y pegado por pixel; cuando una hoja crece, el coste de memoria/CPU puede hacer que Blender parezca colgado. A5 suma que preview/export corren de forma sincrona sin progreso ni cancelacion. B2 debe corregirse antes de escribir archivos para no dejar estado mixto.

Decision recomendada por defecto: aplicar primero una mejora segura de composer por filas y validaciones tempranas de limites; luego evaluar `numpy`/`foreach_get` como optimizacion si se confirma disponibilidad en Blender objetivo. Para progreso, agregar `wm.progress_begin/update/end` como minimo aceptable; convertir preview/export a modal por timer solo si la validacion demuestra que el freeze sigue siendo inaceptable.

### Fase 6e - Consolidacion, Registro Y Higiene Tecnica

Objetivo: reducir divergencias y deuda que hacen fragiles las correcciones futuras.

Hallazgos cubiertos:

- M5.
- M7.
- M8.
- B4.
- B6 restante.
- B8.
- Mejoras propuestas 7 y 8, si no amplian alcance de MVP.

Argumento: M5 y M7 no son solo estilo; la duplicacion de validaciones, context helpers y sanitizadores ya produjo diferencias de precedencia y nombres. M8 afecta reload/doble instalacion, justo antes de packaging. B8 debe decidirse contra el objetivo vigente: el master plan espera Blender 5.x, por lo que bajar a 4.2 no debe hacerse sin matriz runtime; si se mantiene 5.x, debe documentarse.

### Fase 6f - Verificacion Integral De Auditoria

Objetivo: verificar que todos los IDs de la auditoria quedaron corregidos, diferidos con razon o convertidos en limitacion documentada antes de retomar Fase 7.

Hallazgos cubiertos:

- Todos los IDs C/A/M/B.
- Seccion "Lo que no pude verificar" de `docs/technical-audit.md`.

Argumento: la auditoria declaro explicitamente que no verifico runtime Blender para C2, M10, B8, rendimiento real del overlay y semantica de igualdad de `PropertyGroup`. Esta fase debe cerrar esa brecha con Blender GUI/background cuando sea posible, o dejar una decision documentada de riesgo residual.

## Matriz Rectora De Cobertura

Esta matriz no reemplaza `docs/technical-audit.md` ni contiene todo el detalle ejecutable. Define subfase, orientacion y validacion minima para crear subplanes. La solucion completa de cada hallazgo debe incorporarse explicitamente en el subplan derivado usando el contrato anterior.

### C1 - Selector visual bloquea toda la UI y puede quedar invisible activo

- Severidad: critico.
- Subfase: 6a.
- Problema operativo: `SPRITESHEET_OT_visual_selector_open.modal()` llama `handle_visual_selector_event()` y, cuando no hay evento gestionado, retorna `RUNNING_MODAL`. Eso consume eventos que deberian pasar al viewport, menus u otros paneles. `VisualSelectorSession.draw()` retorna temprano si el workspace/clip activo ya no coincide con la sesion, pero el modal sigue activo.
- Correccion requerida: devolver `PASS_THROUGH` para eventos fuera del rect del panel y para navegacion/atajos que no pertenezcan al selector; validar en cada evento que `workspace_id` y `clip_id` de la sesion siguen coincidiendo con `active_workspace_clip_readonly`; si no coinciden, ejecutar cleanup y cancelar.
- Argumento: el usuario no debe necesitar adivinar ESC para recuperar Blender. Un overlay invisible que consume eventos es funcionalmente equivalente a un cuelgue.
- Validacion minima: abrir selector, click fuera del panel, navegar viewport, usar rueda/middle mouse, cambiar workspace/clip o simular undo que elimina el clip; el modal debe dejar pasar eventos o cerrarse.

### C2 - Fuga de draw handler y recursos al terminar modal sin cleanup

- Severidad: critico.
- Subfase: 6a.
- Problema operativo: `draw_handler_add` vive en la sesion y solo se remueve desde `cleanup_visual_selector_resources()`. Cargar otro `.blend` puede cancelar modales sin volver a entrar a `modal()`. No hay `load_pre/load_post` que limpie selector/playback.
- Correccion requerida: registrar un handler persistente `load_pre` que ejecute `cleanup_playback_resources()` y `cleanup_visual_selector_resources()`; quitarlo en `unregister()`. Envolver `VisualSelectorSession.draw()` para que un `ReferenceError` cierre la sesion en vez de spamear consola.
- Argumento: el lifecycle de Blender no garantiza que el modal muera limpiamente. La limpieza debe vivir tambien en handlers de archivo y unregister.
- Validacion minima: abrir selector, cargar archivo nuevo o abrir otro `.blend`, confirmar que no queda overlay fantasma, no quedan timers, no hay traceback repetido y no crece `session.images`.

### A1 - Render cache final a medio implementar

- Severidad: alto.
- Subfase: 6c.
- Problema operativo: `_ensure_rendered_frames()` intenta reutilizar rutas existentes si `_existing_render_paths_for_clip()` retorna paths y `clip.render_dirty` es falso, pero el addon no escribe rutas reales en `frame.render_path` ni pone `render_dirty=False`. Los renders actuales viven bajo `tempfile.TemporaryDirectory`, que se destruye al salir del export. Helpers como `build_render_key`, `render_warning`, `count_render_references`, `count_existing_renders`, `clear_render_state` y `render_file_name` quedan como codigo muerto o solo testeado.
- Correccion requerida: elegir y ejecutar una de dos rutas: completar cache persistente gestionado o eliminar el subsistema de cache final. El estado intermedio no debe sobrevivir.
- Propuesta argumentada: eliminar/diferir cache final para MVP salvo decision contraria del usuario. Completar cache exige diseno de carpeta persistente, invalidacion por camara/colecciones/export settings/frame selection, GC, UI/estado y tolerancia a archivos faltantes. Si no se completa, es mejor aceptar re-render y reducir deuda.
- Validacion minima si se elimina: no quedan ramas de reutilizacion imposibles, props persistidas sin uso ni tests que cubren solo codigo muerto. Validacion minima si se completa: export 1 renderiza, export 2 reutiliza, cambio de settings invalida, borrar archivos fuerza re-render.

### A2 - Render final no fuerza `color_mode = "RGBA"`

- Severidad: alto.
- Subfase: 6b.
- Problema operativo: `render_clip_frames()` fuerza PNG y `film_transparent`, pero no guarda/fuerza/restaura `image_settings.color_mode`. Si la escena esta en RGB o BW, el PNG puede escribirse sin alpha aunque `transparent=True`.
- Correccion requerida: guardar `image_settings.color_mode` y `color_depth`, forzar `RGBA` cuando `export_settings.transparent` sea verdadero y restaurar al final. Valorar `color_depth="8"` para consistencia con previews.
- Argumento: esta es salida incorrecta silenciosa del artefacto principal. El default de Blender puede ocultar el bug, pero el addon no debe depender del estado previo del usuario.
- Validacion minima: escena con `image_settings.color_mode="RGB"` antes del export; export transparente debe generar PNG con canal alpha y restaurar RGB despues.

### A3 - Composer en Python puro con riesgo OOM

- Severidad: alto.
- Subfase: 6d.
- Problema operativo: `compose_spritesheet_png()` crea canvas como lista Python de floats y `_paste_pixels()` copia pixel a pixel con slicing de cuatro floats. `list(image.pixels)` materializa cada frame completo.
- Correccion requerida: reemplazar pegado por pixel por pegado por filas como minimo; evaluar `numpy` + `foreach_get`/`foreach_set` para copia vectorizada si esta disponible en Blender objetivo sin dependencia externa.
- Argumento: una lista Python de floats tiene overhead grande. Hojas 4096x4096 o mayores pueden consumir varios GB y congelar Blender.
- Validacion minima: tests unitarios para `_paste_pixels` o helper equivalente; prueba manual/export con hoja mediana; estimacion de memoria documentada antes/despues si se introduce `numpy`.

### A4 - Previews no se invalidan al editar escena y no hay regeneracion forzada UI

- Severidad: alto.
- Subfase: 6b.
- Problema operativo: la cache key depende de ids/settings/nombres, no de cambios de animacion, mallas o materiales. El operador publico `SPRITESHEET_OT_preview_generate` llama con `force=False`; el parametro `force=True` existe en backend pero no esta expuesto.
- Correccion requerida: agregar ruta UI/operador para regeneracion forzada. Evaluar handler `depsgraph_update_post` filtrado por colecciones efectivas o contador de cambios para marcar `cache_dirty`.
- Argumento: el usuario toma decisiones visuales desde thumbnails. Si los thumbnails son snapshots viejos y no hay regeneracion directa, el selector pierde confiabilidad.
- Validacion minima: generar preview, cambiar material/pose/mesh sin tocar props del addon, usar regeneracion forzada y confirmar thumbnails actualizados. Si se implementa depsgraph, confirmar que cambios relevantes marcan dirty sin degradar performance.

### A5 - Preview/export sincronicos sin progreso ni cancelacion

- Severidad: alto.
- Subfase: 6d.
- Problema operativo: preview y export renderizan N frames en `execute()` bloqueante, sin `wm.progress_*`, sin timer modal, sin ESC ni redraw intermedio.
- Correccion requerida: minimo aceptable: `wm.progress_begin/update/end` alrededor de bucles largos y mensajes de estado claros. Correccion mayor: operadores modales con `wm.event_timer_add`, procesando una unidad por tick y cancelables con ESC.
- Argumento: el aislamiento actual de estado de escena ayuda a refactorizar, pero convertir todo a modal aumenta riesgo. Debe hacerse en dos niveles: progreso minimo primero, modalidad cancelable si la validacion demuestra freeze inaceptable.
- Validacion minima: export/previews de varios frames muestran progreso y restauran estado en exito/error. Si hay modal, validar cancelacion por ESC y cleanup.

### M1 - Falso positivo en verificacion de transparencia de previews

- Severidad: medio.
- Subfase: 6b.
- Problema operativo: `_preview_file_has_transparency()` exige algun alpha menor que 0.999. Un sprite que cubre todo el frame puede ser valido y totalmente opaco, pero la generacion falla y borra el preview.
- Correccion requerida: no abortar por ausencia de pixel transparente. Convertir en warning, muestrear bordes o verificar solo condiciones que prueben ausencia real de canal alpha. No borrar un archivo valido solo porque su contenido es opaco.
- Argumento: la transparencia del canvas no implica que cada frame deba contener pixeles transparentes. Un frame opaco al 100% es caso valido.
- Validacion minima: preview SOLID/MATERIAL de objeto que llena todo el encuadre no debe fallar si el PNG tiene canal alpha.

### M2 - Basura de cache acumulada indefinidamente

- Severidad: medio.
- Subfase: 6b o 6e.
- Problema operativo: cada cache key crea carpeta nueva; las carpetas hermanas anteriores no se purgan. Clear Cache borra solo la actual. Workspaces/clips eliminados pueden dejar carpetas huerfanas.
- Correccion requerida: al generar con exito, purgar carpetas hermanas del mismo clip distintas de la key actual usando `is_managed_cache_folder` como salvaguarda. Opcional: purga de clips/workspaces inexistentes al abrir archivo o desde accion explicita.
- Argumento: la cache vive junto al `.blend`; crecimiento silencioso en disco es mala conducta para un addon distribuible.
- Validacion minima: generar preview con dos configuraciones, confirmar que queda solo la key vigente del clip cuando se aplica GC; no borrar carpetas no gestionadas.

### M3 - Playback redibuja todas las areas en cada tick

- Severidad: medio.
- Subfase: 6a.
- Problema operativo: `_tag_redraw()` recorre todas las ventanas y areas, incluyendo Properties, Outliner y otros editores, a la frecuencia del playback.
- Correccion requerida: taggear solo areas `VIEW_3D`, o preferentemente solo el area asociada a la sesion visual si se mantiene referencia valida.
- Argumento: el playback puede correr a 60 fps. Redibujar toda la UI aumenta CPU/GPU y complica rendimiento del selector.
- Validacion minima: playback sigue actualizando overlay; otras areas no reciben redraw innecesario cuando hay una forma razonable de observarlo/perfilarlo.

### M4 - Frames negativos crean desajuste silencioso

- Severidad: medio.
- Subfase: 6b.
- Problema operativo: `clip.frame_start/frame_end` aceptan negativos, pero `SpriteSheetFrameItem.frame_number` tiene `min=0`. Blender puede clampear frames negativos a 0, generando colisiones y previews/renders vacios.
- Correccion requerida: decidir politica. O permitir negativos quitando `min=0` de `frame_number`, o prohibir negativos agregando `min=0` a `frame_start/frame_end`.
- Propuesta argumentada: permitir negativos si el objetivo es respetar Blender, porque Blender permite timeline negativo. Si se permite, tests y render/preview deben aceptar rutas para frames negativos. Si no se quiere soportar, bloquear temprano con UI/validacion clara.
- Validacion minima: rango negativo produce frames persistentes correctos o mensaje claro antes de generar/exportar; no hay clamp silencioso a 0.

### M5 - Triple implementacion de validacion y etiquetas duplicadas

- Severidad: medio.
- Subfase: 6e.
- Problema operativo: validaciones de camara/colecciones/override existen inline en preview, en `preview_context_warnings()` y en `validate_active_clip_render_context()`. El panel lista colecciones faltantes dos veces.
- Correccion requerida: consolidar validacion en `core/validation.py` con modo/severidad para preview/render/export y consumirla desde operadores y UI. El panel no debe duplicar mensajes.
- Argumento: diferencias de orden y severidad pueden producir mensajes contradictorios y bugs divergentes.
- Validacion minima: mismos casos de error producen mensajes consistentes en panel, preview y export; no se repiten etiquetas.

### M6 - Selector visual sin scroll

- Severidad: medio.
- Subfase: 6a.
- Problema operativo: el grid muestra `columns * rows` frames y solo informa "Showing X / Y frames"; el resto no es seleccionable visualmente.
- Correccion requerida: agregar offset de scroll/paginacion en la sesion y manejar `WHEELUPMOUSE/WHEELDOWNMOUSE` dentro del panel. Fuera del panel, la rueda debe pasar al viewport como parte de C1.
- Argumento: clips largos son parte natural del dominio. El selector visual no debe ocultar frames sin ruta de acceso.
- Validacion minima: clip largo, scroll dentro del panel cambia frames visibles y permite togglear seleccion; scroll fuera del panel navega viewport o pasa evento.

### M7 - Duplicacion estructural transversal

- Severidad: medio.
- Subfase: 6e, con partes en 6c si afectan render cache.
- Problema operativo: `_scene_state`/`_active_workspace` estan copiados en operadores; `_clear_collection` existe en mas de un modulo; sanitizadores de paths/nombres difieren; `effective_preview_mode(workspace, clip)` ignora workspace y `effective_preview_label()` duplica la idea.
- Correccion requerida: crear `core/context.py` para helpers de contexto Blender, unificar sanitizador en `core/paths.py`, eliminar parametros muertos o documentar compatibilidad, y retirar duplicados simples.
- Argumento: los sanitizadores ya pueden producir nombres distintos para el mismo valor. Esta duplicacion aumenta costo y riesgo de cada cambio de export/cache.
- Validacion minima: tests de sanitizador unico; operadores siguen encontrando workspace/clip activo; no queda uso de helpers duplicados salvo razon documentada.

### M8 - Registro defensivo enmascara errores y puede desregistrar clases ajenas

- Severidad: medio.
- Subfase: 6e.
- Problema operativo: `register()` agrega una clase a `_registered_classes` incluso si `bpy.utils.register_class()` lanza `ValueError`. Luego `unregister()` podria desregistrar una clase que este modulo no registro realmente.
- Correccion requerida: migrar a registro directo o a `bpy.utils.register_classes_factory(CLASSES)` si encaja con las necesidades del addon. Mantener tolerancia en `unregister()` pero no ocultar errores reales en `register()`.
- Argumento: antes de packaging, registrar/desregistrar debe fallar fuerte ante errores reales. Ocultar registros rotos complica diagnostico de instalaciones dobles o reloads.
- Validacion minima: register/unregister repetido en entorno Blender; doble llamada controlada; errores de registro no quedan silenciosos.

### M9 - Thumbnails obsoletos por `check_existing=True` sin reload

- Severidad: medio.
- Subfase: 6a o 6b.
- Problema operativo: `_draw_preview_image()` y `_cached_image_or_none()` cargan imagenes con `check_existing=True`. Si existe datablock para la misma ruta, Blender puede devolver pixeles viejos tras regenerar cache.
- Correccion requerida: recargar datablock con `image.reload()` cuando se obtiene por primera vez en sesion, invalidar `session.images` cuando cambia `clip.cache_key`, o cargar sin reutilizar cuando corresponda y liberar explicitamente.
- Argumento: selector visual con thumbnails viejos invalida la seleccion visual.
- Validacion minima: generar preview, abrir selector, regenerar mismos paths, volver a abrir selector; imagen mostrada debe ser la nueva.

### M10 - Posible coste de `gpu.texture.from_image` por celda y redraw

- Severidad: medio, no verificado.
- Subfase: 6a o 6f.
- Problema operativo: `_draw_preview_image()` llama `gpu.texture.from_image(image)` en cada redraw para cada celda visible. Si Blender no cachea internamente, cada frame podria subir texturas.
- Correccion requerida: perfilar en Blender objetivo. Si se confirma coste, cachear `GPUTexture` por imagen/path/cache_key en la sesion y liberarlo al cerrar.
- Argumento: no se debe introducir cache GPU prematuro sin medicion, pero el punto afecta directamente playback/overlay.
- Validacion minima: perfilado runtime con selector visible y playback; decision documentada aunque no se implemente cache.

### B1 - Parametro confuso en renderer

- Severidad: bajo.
- Subfase: 6c o 6e.
- Problema operativo: `render_file_path(output_folder, output_index, ...)` usa un indice de salida como argumento llamado `frame_number`. Funciona, pero el nombre induce a error.
- Correccion requerida: renombrar parametro/helper o documentar que es indice de salida.
- Argumento: el proyecto ya decidio que filenames usan indice continuo; el codigo debe expresar ese contrato.
- Validacion minima: tests de naming siguen pasando.

### B2 - Export de secuencia individual puede dejar salida parcial

- Severidad: bajo.
- Subfase: 6d.
- Problema operativo: el limite de 999 se lanza dentro del loop de copia, despues de haber creado carpeta y copiado parte de los archivos. El patron de limpieza acepta 6 digitos aunque la salida actual usa 3.
- Correccion requerida: validar `len(frame_paths) <= 999` antes de crear/copiar; decidir si el patron de 6 digitos se conserva por compatibilidad de limpieza o se elimina.
- Argumento: una validacion conocida debe ocurrir antes de producir side effects.
- Validacion minima: 1000 frames falla sin crear salida parcial nueva.

### B3 - Campo muerto `original_index`

- Severidad: bajo.
- Subfase: 6c o 6e.
- Problema operativo: `original_index` se escribe y copia, pero no participa en logica.
- Correccion requerida: eliminarlo si no hay proposito futuro aprobado, o documentar el contrato si se usara para orden/restauracion futura.
- Argumento: propiedad persistente muerta agrega ruido al `.blend` y a duplicaciones.
- Validacion minima: si se elimina, save/reopen y tests no dependen del campo; si queda, docs explican uso.

### B4 - `original_compression` se guarda/restaura sin modificarse

- Severidad: bajo.
- Subfase: 6e.
- Problema operativo: preview generator guarda/restaura compresion aunque no la modifica.
- Correccion requerida: retirar guardado/restauracion o empezar a fijar compresion con razon explicita.
- Argumento: ruido pequeño, pero reduce lectura y superficie de estado tocado.
- Validacion minima: preview sigue restaurando los settings que realmente cambia.

### B5 - `execute()` de selector visual retorna `FINISHED` sin abrir nada

- Severidad: bajo.
- Subfase: 6a.
- Problema operativo: llamar `SPRITESHEET_OT_visual_selector_open.execute()` desde script en modo no background parece exitoso aunque no abre selector.
- Correccion requerida: devolver `CANCELLED` con reporte claro o delegar de forma segura a `invoke` solo con contexto/evento valido.
- Argumento: los operadores no deben comunicar exito falso.
- Validacion minima: llamada por script sin invoke devuelve `CANCELLED` y mensaje claro.

### B6 - Silenciamiento amplio de excepciones

- Severidad: bajo.
- Subfase: 6a y 6e.
- Problema operativo: varios `except Exception: pass/return` esconden fallos en redraw, match de sesion, alpha preview y dibujo de imagenes.
- Correccion requerida: reemplazar silencios por capturas especificas o logging/debug print controlado. En paths de draw, evitar spamear consola cada redraw.
- Argumento: antes de distribuir, los errores deben diagnosticarse sin romper UI.
- Validacion minima: errores esperados no spamean; errores inesperados dejan señal util en consola o estado.

### B7 - Undo inconsistente en overlay

- Severidad: bajo.
- Subfase: 6a.
- Problema operativo: click de celda en modo EDIT muta `frame.selected` directamente, mientras `SPRITESHEET_OT_frame_toggle_selection` tiene `UNDO`.
- Correccion requerida: enrutar el click por operador o usar mecanismo de undo equivalente.
- Argumento: seleccion visual es accion de usuario y debe integrarse con undo como los botones/panel.
- Validacion minima: togglear desde overlay y deshacer revierte seleccion.

### B8 - Compatibilidad/manifiesto

- Severidad: bajo, no verificable sin versiones objetivo.
- Subfase: 6e o Fase 7.
- Problema operativo: `blender_version_min = "5.0.0"` excluye Blender 4.x aunque la API podria ser compatible desde 4.2; no hay `bl_info` legacy.
- Correccion requerida: decidir compatibilidad. Como el master plan vigente apunta a Blender 5.x, la correccion minima es documentar intencionalidad de 5.x y validar en 5.x. Bajar a 4.2 requiere matriz runtime y no debe hacerse solo por inferencia estatica.
- Argumento: compatibilidad declarada es contrato de distribucion. Ampliarla sin probar aumenta soporte implicito.
- Validacion minima: manifest revisado; decision documentada; prueba en versiones objetivo si se baja el minimo.

### B9 - Criterios de identidad distintos entre claves

- Severidad: bajo.
- Subfase: 6b o 6e.
- Problema operativo: preview cache usa nombres visibles de camara/colecciones; render key usa `library.filepath + name_full`. Renombrar camara invalida preview aunque conceptualmente sea el mismo objeto.
- Correccion requerida: unificar criterio con helper `_id_key` compartido o aceptar invalidacion por rename y documentarla.
- Argumento: claves de cache deben ser predecibles. Diferencias entre preview/render complican depuracion.
- Validacion minima: tests para key de preview/render con objetos mockeados; decision sobre rename documentada.

### B10 - `resume_playback` ignora cambios de FPS

- Severidad: bajo.
- Subfase: 6a.
- Problema operativo: al reanudar se usa `_session.fps` congelado, no el FPS actual del clip.
- Correccion requerida: al reanudar, resolver clip activo de la sesion y leer `clip.fps`, o decidir que una sesion pausada es snapshot inmutable y documentarlo.
- Propuesta argumentada: releer FPS si workspace/clip sigue coincidiendo. El usuario espera que cambiar FPS afecte playback al reanudar.
- Validacion minima: pausar, cambiar FPS, reanudar; intervalo usa FPS nuevo.

### B11 - Shading viewport cambia/restaura por frame

- Severidad: bajo.
- Subfase: 6b o 6d.
- Problema operativo: `_write_viewport_thumbnail()` cambia shading y overlay por cada frame, aunque el modo es el mismo durante el lote.
- Correccion requerida: mover cambio/restauracion de shading al nivel del loop cuando el contexto viewport se mantiene estable.
- Argumento: reduce trabajo repetido y parpadeos durante generacion.
- Validacion minima: previews SOLID/MATERIAL generan multiples frames y restauran shading tras exito/error.

### B12 - `update_workspace_defaults_dirty` no marca `render_dirty`

- Severidad: bajo, condicionado por A1.
- Subfase: 6b o 6c.
- Problema operativo: cambiar defaults de workspace marca `cache_dirty`, pero no `render_dirty`, mientras operaciones analogas de colecciones si marcan ambos.
- Correccion requerida: si se mantiene render dirty/cache, marcar `render_dirty=True` para clips afectados. Si se elimina cache final, retirar o simplificar estado relacionado.
- Argumento: divergira si A1 se completa. Es irrelevante solo mientras render cache sea codigo muerto.
- Validacion minima: cambiar default camera/collection invalida render o ya no existe estado render cache que invalidar.

## Puntos No Verificados En Runtime

### C2 - Detalle de `ReferenceError`

Debe validarse con Blender GUI cargando otro archivo con selector abierto. Si no se reproduce `ReferenceError`, la limpieza por `load_pre` sigue siendo obligatoria por fuga estructural de handler.

### M10 - Coste real de `gpu.texture.from_image`

Debe perfilarse en Blender objetivo con overlay visible y playback. Si no hay evidencia de coste, no introducir cache GPU compleja; documentar decision. Si hay coste, cachear texturas por sesion y limpiar en `close()`.

### B8 - Compatibilidad real Blender 4.x/5.x

El contrato actual del reinicio V2 es Blender 5.x. Bajar `blender_version_min` a 4.2 solo puede hacerse con prueba runtime y revision de manifest/extension. Si no se prueba, mantener 5.x y documentar.

### Igualdad de `PropertyGroup`

La auditoria no pudo verificar la semantica de `==` entre wrappers de `PropertyGroup` en `_mark_collection_owner_dirty`. Debe validarse en Blender o reemplazarse por busqueda estructural que no dependa de igualdad ambigua.

### Cobertura de codigo con `bpy`

Tests unitarios cubren helpers puros, layout/metadata y playback sequence. Operadores, generator, renderer, composer y overlay necesitan validacion Blender/manual o mocks especificos por subplan.

## Validaciones Automaticas Esperadas Por Subplan

- `python3 -m compileall spritesheet_frame_selector`
- `python3 -m unittest discover -s tests`
- Tests nuevos o actualizados para helpers puros tocados.
- Busquedas `rg` especificas por hallazgo cerrado:
  - render cache muerto o completado;
  - `color_mode` en renderer;
  - `PASS_THROUGH`/cleanup modal;
  - duplicaciones removidas;
  - `except Exception` justificados.

## Validaciones Blender Esperadas

- Abrir selector y confirmar que no bloquea navegacion fuera del panel.
- Cambiar workspace/clip o cargar archivo nuevo con selector abierto y confirmar cleanup.
- Generar previews, regenerarlos forzadamente y confirmar thumbnails frescos.
- Exportar con escena configurada en RGB y confirmar alpha correcto.
- Exportar spritesheet mediano y confirmar que progreso/tiempo/memoria son aceptables.
- Exportar secuencia individual con limite excedido y confirmar que no deja salida parcial.
- Registrar/desregistrar/reactivar addon si se toca `registration.py`.

## Criterio De Termino De Fase 6

La Fase 6 queda validada cuando:

- todos los hallazgos C1-C2, A1-A5, M1-M10 y B1-B12 tienen estado corregido, diferido con razon o no aplicable con evidencia;
- los hallazgos criticos y altos no quedan diferidos salvo decision explicita del usuario;
- el codigo modificado pasa validaciones automaticas aplicables;
- las validaciones Blender requeridas por hallazgos runtime fueron ejecutadas o justificadas por limitacion del entorno;
- `docs/technical-audit.md` sigue como fuente, y el plan o handoff registra el estado final de cobertura;
- la Fase 7 de validacion/distribucion queda habilitada como siguiente paso operativo;
- PCS refleja el estado final sin marcar cerrado salvo instruccion explicita.

## Proximo Paso Recomendado

Revisar y aprobar este plan rector. Si se aprueba, crear el primer subplan ejecutable:

`docs/plans/reinicio-v2-fase-6a-selector-modal-lifecycle.md`

Ese subplan debe cubrir C1, C2, M3, M6, M9, B5, B7, B10 y la parte aplicable de B6/M10.

El subplan 6a debe aplicar el contrato obligatorio de este plan: copiar de `docs/technical-audit.md` el extracto operativo de cada hallazgo cubierto, incluyendo solucion propuesta por auditoria y archivos/funciones afectados, y luego declarar la interpretacion concreta del subplan antes de implementar.
