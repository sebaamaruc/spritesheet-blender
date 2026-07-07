# Plan Fase 6d - Rendimiento, Memoria Y Seguridad De Export

Estado: aprobado
Autoridad: usuario
Modo de ejecucion: ejecutar sin replanificar
Estado De Ejecucion: implementado

## Referencia Superior

`docs/plans/reinicio-v2-fase-6-correcciones-auditoria-tecnica.md`

## Fuente Principal

- `docs/technical-audit.md`
- `docs/plans/reinicio-v2-fase-6-correcciones-auditoria-tecnica.md`
- Codigo actual revisado:
  - `spritesheet_frame_selector/export/composer.py`
  - `spritesheet_frame_selector/export/sequence.py`
  - `spritesheet_frame_selector/operators/export.py`

## Objetivo

Evitar que export quede lento, consuma memoria excesiva o deje salidas parciales inconsistentes:

- reducir el coste de composicion del spritesheet eliminando el pegado por pixel en Python puro;
- agregar feedback minimo de progreso en preview/export segun D4 nivel 1;
- validar limites de secuencia individual antes de renderizar, componer o copiar;
- eliminar la rama muerta de limpieza de secuencia individual con patron de 6 digitos, salvo que durante implementacion aparezca compatibilidad real que la justifique.

## Hallazgos De Auditoria Cubiertos

| ID | Severidad | Titulo | Estado En Este Subplan |
|---|---|---|---|
| A3 | alto | Composicion del spritesheet en Python puro: O(pixel) en CPU y riesgo de OOM | implementado; validacion Blender GUI pendiente |
| A5 | alto | Generacion de previews y export sincronas sin progreso ni cancelacion | implementado nivel D4.1; validacion Blender GUI pendiente |
| B2 | bajo | Export de secuencia individual valida limite de 999 demasiado tarde y deja salida parcial | implementado; validacion Blender GUI pendiente |

## Extracto Operativo De Auditoria

### A3 - Composicion del spritesheet en Python puro

- Problema: `compose_spritesheet_png` construye el canvas como lista Python de floats y `_paste_pixels` copia con un bucle anidado por pixel usando slicing de 4 elementos. Cada frame tambien se materializa con `list(image.pixels)`. En hojas grandes, una lista Python de floats puede ocupar varios GB y tardar decenas de segundos.
- Causa: implementacion de referencia sin vectorizar en `spritesheet_frame_selector/export/composer.py::compose_spritesheet_png/_paste_pixels`.
- Impacto: exports grandes lentos o imposibles; Blender puede parecer congelado o llegar a OOM. Se combina con A5 porque hoy no hay progreso visible.
- Solucion propuesta por la auditoria: usar `numpy` disponible en Python de Blender: `image.pixels.foreach_get(buffer)` hacia `np.float32`, reshape y asignacion de bloques 2D por frame; `foreach_set` para el canvas final. Como minimo, copiar por filas (`canvas[a:b] = src[c:d]`) en vez de por pixel.
- Archivos/funciones afectados: `spritesheet_frame_selector/export/composer.py::compose_spritesheet_png`, `spritesheet_frame_selector/export/composer.py::_paste_pixels`.
- Aspectos no verificados en runtime: disponibilidad real de `numpy` en el Blender objetivo y diferencia de tiempo/memoria con una hoja mediana.

### A5 - Generacion/export sincronas sin progreso ni cancelacion

- Problema: `_generate_preview_cache` y `SPRITESHEET_OT_export_spritesheet.execute` renderizan N frames en un solo `execute()` bloqueante. No hay barra de progreso, cancelacion por ESC ni redraw intermedio.
- Causa: operadores simples y sin uso de `wm.progress_begin/update/end` ni operador modal con timer.
- Impacto: Blender parece colgado durante escenas reales; el usuario puede matar el proceso creyendo que fallo, especialmente si A3 tambien hace pesada la composicion.
- Solucion propuesta por la auditoria: convertir generacion/export a operador modal con `wm.event_timer_add`, `wm.progress_*` y cancelacion por ESC. Como mejora minima inmediata: `wm.progress_begin/update/end` alrededor de los bucles.
- Archivos/funciones afectados: `spritesheet_frame_selector/operators/preview.py::_generate_preview_cache`, `spritesheet_frame_selector/operators/export.py::execute/_ensure_rendered_frames`, `spritesheet_frame_selector/preview/generator.py::generate_viewport_previews`, `spritesheet_frame_selector/render/renderer.py::render_clip_frames`.
- Aspectos no verificados en runtime: si el nivel 1 de D4, barra de progreso sin modal cancelable, basta para que exports medianos de referencia sean aceptables.

### B2 - Export de secuencia individual valida tarde y deja salida parcial

- Problema: `export_individual_frames` lanza el limite de 999 dentro del bucle de copia. A esa altura el spritesheet PNG ya pudo estar escrito, y la copia puede haber dejado frames individuales parciales. Ademas `clear_previous_individual_frames` acepta nombres con 3 o 6 digitos, pero el contrato vigente usa 3 digitos.
- Causa: validacion local tardia en `spritesheet_frame_selector/export/sequence.py::export_individual_frames` y patron de limpieza legado.
- Impacto: salida mixta: PNG/JSON o algunos frames pueden quedar escritos aunque la operacion global falle. El usuario debe limpiar manualmente.
- Solucion propuesta por la auditoria: validar `len(frame_paths) <= 999` antes de copiar y, por nota rectora, antes de renderizar; eliminar la rama muerta del patron de 6 digitos salvo razon de compatibilidad documentada.
- Archivos/funciones afectados: `spritesheet_frame_selector/export/sequence.py`, `spritesheet_frame_selector/operators/export.py::_prepare_export_clips` o validacion previa equivalente.
- Aspectos no verificados en runtime: que el operador falle antes de renderizar cuando `Export Individual Frames` esta activo y hay mas de 999 frames seleccionados.

## Interpretacion Del Subplan

- A3: adoptar solucion en dos niveles, segun el plan rector:
  - Nivel obligatorio: reemplazar `_paste_pixels` por pegado por filas, manteniendo dependencias cero y tests unitarios. Este cambio reduce mucho el overhead de slicing por pixel y es seguro fuera de Blender.
  - Nivel condicional dentro del mismo subplan: verificar disponibilidad de `numpy` en el Blender objetivo. Si esta disponible y el cambio se mantiene acotado, agregar ruta numpy con fallback al pegado por filas. Si no se puede validar o aumenta demasiado el riesgo, documentar que queda diferida a post-MVP o a 6f como decision tecnica.
- A5: ejecutar D4 nivel 1 obligatorio: envolver bucles de preview y export con `wm.progress_begin/update/end`. No convertir a operador modal cancelable en este subplan salvo que la validacion GUI del nivel 1 muestre freeze inaceptable; si ocurre, registrar decision antes de ampliar alcance.
- B2: validar el limite global de 999 frames al preparar el export, antes de renderizar. Mantener tambien una defensa local en `export_individual_frames` para callers directos. Reducir limpieza a patron de 3 digitos, porque 6c/5g ya establecieron naming vigente de 3 digitos.

## Alcance De Implementacion

Incluir:

- `export/composer.py`:
  - crear helper de pegado por filas o reemplazar `_paste_pixels` para copiar segmentos completos de fila;
  - agregar tests puros sobre posicionamiento de pixeles con padding/margin si no existen;
  - investigar `numpy` de forma no obligatoria para el addon si no puede validarse en Blender objetivo.
- `operators/export.py`:
  - calcular el total de frames preparados antes de render;
  - si `export_png_sequence` esta activo y total > 999, cancelar antes de crear salida/renderizar;
  - agregar `wm.progress_*` alrededor del flujo de export: render por clips, composicion, secuencia individual y JSON cuando aplique;
  - asegurar `progress_end` en `finally`.
- `render/renderer.py`:
  - permitir callback/progreso opcional por frame o devolver suficiente informacion para que export actualice progreso sin duplicar render logic.
- `operators/preview.py` y/o `preview/generator.py`:
  - agregar `wm.progress_*` para generacion de previews, incluyendo `Generate` y `Regenerate`;
  - preservar restauracion de estado y cleanup aunque haya errores.
- `export/sequence.py`:
  - validar limite antes de crear/copiar salida;
  - eliminar patron de limpieza de 6 digitos si no se justifica;
  - mantener tests de 3 digitos.
- Tests unitarios para:
  - limite >999 antes de render;
  - `export_individual_frames` no deja salida parcial cuando excede limite;
  - limpieza ya no borra patron de 6 digitos salvo decision contraria;
  - pegado por filas produce el mismo layout esperado.

Excluir:

- No implementar cache final de render ni export incremental.
- No cambiar formato JSON ni layout publico.
- No resolver M5/M7/M8/B3/B4/B6 restante; pertenecen a 6e.
- No tocar packaging ni Fase 7.
- No implementar operador modal cancelable por defecto; queda condicional a medicion D4 nivel 1.
- No introducir dependencia externa distribuible; `numpy` solo puede usarse si esta disponible en Blender objetivo y con fallback seguro.

## Archivos Esperados

- `spritesheet_frame_selector/export/composer.py`
- `spritesheet_frame_selector/export/sequence.py`
- `spritesheet_frame_selector/operators/export.py`
- `spritesheet_frame_selector/render/renderer.py`
- `spritesheet_frame_selector/operators/preview.py`
- `spritesheet_frame_selector/preview/generator.py`
- `tests/test_export_layout_metadata.py`
- `tests/test_preview_cache.py` si se cubre progreso de preview con stubs
- Nuevo test focalizado para composer si conviene separar cobertura

## Validacion

### Validaciones Automaticas

- `python3 -m compileall spritesheet_frame_selector`
- `python3 -m unittest discover -s tests`
- Busquedas de contrato:
  - `rg -n "progress_begin|progress_update|progress_end" spritesheet_frame_selector tests`
  - `rg -n "999|Individual frame export supports up to 999" spritesheet_frame_selector tests`
  - `rg -n "\\\\d\\{6\\}|000001" spritesheet_frame_selector tests`
  - `rg -n "_paste_pixels|foreach_get|foreach_set|numpy|np\\." spritesheet_frame_selector/export tests`

### Validaciones Blender GUI/Background

- A3: exportar una hoja mediana y confirmar que el export completa sin errores y sin regresion visual evidente en el spritesheet.
- A5: durante Generate/Regenerate Preview y Export Spritesheet, confirmar que Blender muestra progreso via barra nativa o feedback equivalente de `wm.progress_*`; confirmar que al finalizar o fallar no queda progreso pegado.
- B2: activar `Export Individual Frames`, preparar mas de 999 frames seleccionados y ejecutar export. Debe fallar antes de renderizar o escribir salidas nuevas, con mensaje claro.
- Repetir export normal con menos de 999 frames individuales y confirmar PNG/JSON/secuencia correctos.

### Criterio De Aceptacion Por Hallazgo

- A3: `_paste_pixels` ya no hace bucle por pixel con slicing de 4 elementos; existe test que valida composicion por filas. Si numpy se implementa, tiene fallback y queda probado. Si se difiere, el subplan debe explicar la razon y dejar el nivel de filas como correccion MVP.
- A5: preview/export usan `wm.progress_begin/update/end` con `finally`; el nivel modal cancelable queda diferido solo con razon explicita.
- B2: el limite de 999 frames se valida antes de renderizar; `export_individual_frames` tambien protege callers directos sin salida parcial; limpieza usa el patron vigente de 3 digitos o documenta compatibilidad.

## Riesgos

- La ruta numpy puede no estar disponible en todos los entornos de prueba. No debe ser dependencia obligatoria sin fallback.
- Progreso mal cerrado deja UI de Blender en estado confuso. Todo uso de `progress_begin` debe tener `progress_end` en `finally`.
- Cambiar composer puede invertir verticalmente filas si no se respeta el contrato top-left de `frame_rect` y el origen bottom-left de pixeles Blender.
- Validar limite >999 tarde seguiria dejando salida parcial; la validacion debe ocurrir antes de `TemporaryDirectory`/render cuando `export_png_sequence` este activo.

## Proximo Paso Si Se Aprueba

Persistir este plan como aprobado y Plan Activo PCS. Luego implementarlo sin replanificar, dejando `Estado De Ejecucion: implementado` hasta completar validacion Blender GUI.

## Resumen De Implementacion

- A3: `export/composer.py::_paste_pixels` ya no copia pixel por pixel; ahora copia segmentos completos por fila. La ruta numpy queda diferida porque el nivel obligatorio de filas reduce el riesgo MVP sin introducir dependencia condicional.
- A5: se agrego `core/progress.py` con `progress_scope()` y `ProgressReporter`, usando `wm.progress_begin/update/end` con cierre en `finally`.
- A5 preview: `_generate_preview_cache` envuelve `generate_viewport_previews` en `progress_scope`; `generate_viewport_previews` acepta `progress_callback` y avanza por cada frame generado o saltado.
- A5 export: `SPRITESHEET_OT_export_spritesheet.execute` envuelve render, composicion, secuencia individual y JSON en `progress_scope`; `render_clip_frames` acepta `progress_callback` y avanza por frame renderizado.
- B2: `export_individual_frames` valida `len(frame_paths) <= 999` antes de crear carpeta, limpiar o copiar. El operador de export valida el total preparado antes de crear salida/renderizar cuando `Export Individual Frames` esta activo.
- B2: `clear_previous_individual_frames` limpia solo el patron vigente de 3 digitos; la rama de 6 digitos queda eliminada.

## Validaciones Ejecutadas

- Pasado: `python3 -m compileall spritesheet_frame_selector`.
- Pasado: `python3 -m unittest discover -s tests` con 81 tests.
- Pasado: busqueda `progress_begin|progress_update|progress_end`; el uso vive centralizado en `core/progress.py`.
- Pasado: busqueda `999|Individual frame export supports up to 999`; el limite esta en `export/sequence.py` y cubierto por tests.
- Pasado: busqueda `\d{6}|000001`; solo queda un test que confirma que el patron legado de 6 digitos no se borra.
- Pasado: busqueda `_paste_pixels|foreach_get|foreach_set|numpy|np\.`; `_paste_pixels` queda cubierto por test de pegado por filas y no se introdujo numpy.

## Validacion Blender GUI Pendiente

- A3: exportar una hoja mediana y confirmar que el export completa sin errores ni regresion visual evidente en el spritesheet.
- A5: durante Generate/Regenerate Preview y Export Spritesheet, confirmar que Blender muestra progreso via barra nativa o feedback equivalente de `wm.progress_*`; confirmar que al finalizar o fallar no queda progreso pegado.
- B2: activar `Export Individual Frames`, preparar mas de 999 frames seleccionados y ejecutar export. Debe fallar antes de renderizar o escribir salidas nuevas, con mensaje claro.
- Repetir export normal con menos de 999 frames individuales y confirmar PNG/JSON/secuencia correctos.
