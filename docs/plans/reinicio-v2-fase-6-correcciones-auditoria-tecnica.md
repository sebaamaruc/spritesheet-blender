# Plan Fase 6 - Correcciones Auditoria Tecnica

Estado: aprobado (revision 2, revisada por arquitectura)
Autoridad: usuario
Modo de ejecucion: ejecutar sin replanificar
Estado De Ejecucion: implementado; validacion Blender GUI pendiente

## Referencia Superior

`docs/plans/reinicio-v2-master-plan.md`

## Planes Relacionados

- `docs/archive/reinicio-v2-fase-5-workspace-root-vertical-slices.md`
- `docs/archive/reinicio-v2-fase-5g-export-spritesheet-json.md`
- `docs/plans/reinicio-v2-fase-6b0-preview-camera-viewport.md`
- `docs/plans/reinicio-v2-fase-6b-preview-alpha-estado-visual.md`
- `docs/plans/reinicio-v2-fase-6d-rendimiento-export.md`
- `docs/plans/reinicio-v2-fase-6e-consolidacion-higiene.md`
- `docs/plans/reinicio-v2-fase-6f-verificacion-integral-auditoria.md`
- `docs/plans/reinicio-v2-fase-7-validacion-distribucion.md`

## Fuente Principal

`docs/technical-audit.md`

## Rol De Este Plan Y De La Auditoria

La auditoria tecnica es la fuente canonica de los hallazgos: problema, causa, impacto, solucion propuesta y archivos/funciones. Este plan rector no duplica ese contenido. El detalle tecnico vive exactamente en dos lugares:

1. `docs/technical-audit.md` (canonico, no se edita para "actualizar" hallazgos);
2. el subplan que ejecuta cada hallazgo (copia operativa, segun el contrato de este plan).

Este plan rector aporta unicamente lo que la auditoria no contiene:

- asignacion de cada hallazgo a una subfase unica;
- decisiones rectoras donde la auditoria dejo alternativas;
- orden de ejecucion y dependencias;
- ledger de estado por hallazgo;
- criterio de bloqueo de la Fase 7.

Regla obligatoria: cada subplan ejecutable debe incorporar el extracto operativo de la auditoria para los hallazgos que cubre (ver contrato). Este plan rector no debe crecer con detalle por hallazgo mas alla de las notas rectoras; si un hallazgo necesita mas precision, esa precision pertenece al subplan.

## Estado De Entrada

- Fase 5g fue validada manualmente por el usuario.
- `docs/technical-audit.md` audito estaticamente `spritesheet_frame_selector/` y `tests/`.
- La auditoria declara que los 65 tests unitarios pasan con `unittest`.
- La auditoria no ejecuto el addon dentro de Blender; los hallazgos dependientes de runtime se mantienen como pendientes de verificacion runtime.
- La Fase 7 de validacion/distribucion queda diferida hasta que esta fase corrija o clasifique explicitamente todos los hallazgos de auditoria.

## Decisiones Rectoras

Estas decisiones resuelven las alternativas que la auditoria dejo abiertas. Deben confirmarse o corregirse al aprobar este plan; los subplanes las ejecutan, no las reabren.

- **D1 (A1, render cache final): eliminar el subsistema para MVP.** Confirmado por el usuario al aprobar este plan. Completar la cache exige carpeta persistente gestionada, invalidacion, GC, estado derivado y tolerancia a archivos faltantes; el beneficio (export incremental) no justifica esa superficie antes del primer ZIP. El rendimiento de export se ataca por A3/A5. Precaucion de ejecucion: `core/render_state.py` mezcla helpers muertos (`build_render_key`, `render_warning`, `count_render_references`, `count_existing_renders`, `clear_render_state`, `render_file_name`) con helpers vivos usados por el flujo real de render/export (`selected_frame_numbers`, `render_file_path`, `render_output_file_name`, `_safe_file_prefix`); el subplan 6c debe separarlos explicitamente antes de borrar.
- **D2 (M4, frames negativos): prohibir negativos en MVP** agregando `min=0` a `frame_start`/`frame_end`. Confirmado por el usuario al aprobar este plan. Soportar negativos obliga a revisar naming de archivos (`{:03d}` con signo), regex de limpieza y orden lexicografico, para un caso raro en el dominio spritesheet. Si un usuario real lo pide, se reabre como feature post-MVP.
- **D3 (B8, compatibilidad): mantener `blender_version_min = "5.0.0"`** conforme al master plan, documentar la intencionalidad y validar solo en 5.x. B8 queda diferido a Fase 7 (revision de manifest en packaging); no consume trabajo en Fase 6. Bajar a 4.2 requeriria matriz runtime que no esta en alcance.
- **D4 (A5, sincronia): correccion en dos niveles.** Nivel 1 obligatorio: `wm.progress_begin/update/end` en bucles de preview y export. Nivel 2 condicional: operador modal cancelable por ESC, solo si la validacion Blender del nivel 1 muestra freeze inaceptable en un export mediano de referencia.
- **D5 (A3, numpy):** numpy viene incluido en los builds oficiales de Blender desde hace anos; aun asi el subplan 6d debe verificarlo con un `import numpy` en el Blender objetivo antes de depender de el. Si faltara, el fallback es el pegado por filas (que se implementa primero de todos modos).

## Objetivo

Corregir o clasificar formalmente todos los hallazgos de `docs/technical-audit.md` antes de packaging final:

- los hallazgos criticos y altos deben quedar corregidos o convertidos en decision tecnica explicita con justificacion;
- los hallazgos medios deben quedar corregidos, diferidos con criterio de no bloqueo, o absorbidos por una correccion mayor;
- los hallazgos bajos deben quedar corregidos cuando el cambio sea local y seguro, o documentados como deuda aceptada con razon;
- los puntos no verificados en runtime deben tener prueba runtime o una decision de instrumentacion/perfilado;
- la Fase 7 solo puede retomarse cuando esta fase tenga estado `validado` o `listo para cierre`.

## Reglas De Implementacion

- No distribuir ZIP final dentro de esta fase.
- No reducir el alcance de la auditoria por conveniencia; todo ID C/A/M/B debe quedar rastreado en el ledger.
- No crear subplanes que digan solo "ver auditoria"; deben traer extracto operativo explicito de los hallazgos que ejecutan.
- Si un subplan modifica o rechaza una solucion propuesta por la auditoria, debe explicar por que, que riesgo reduce y que validacion compensa el cambio.
- No cerrar PCS ni archivar planes sin instruccion explicita de cierre.
- No crear un subplan nuevo si el hallazgo pertenece claramente a un subplan aprobado en ejecucion.
- No mezclar refactors amplios con fixes criticos: dentro de 6a, los hitos son secuenciales y el hito 1 (C1/C2) se valida antes de empezar el resto.
- No introducir dependencias externas obligatorias para el addon distribuible (numpy bundled no cuenta como externa; ver D5).
- Si Blender background crashea en el entorno, documentar la limitacion y usar Blender GUI para los hallazgos que requieren runtime.
- Mantener rutas PCS repo-relativas en documentos operativos.

## Contrato Obligatorio Para Subplanes

Todo subplan derivado de esta Fase 6 debe ser autosuficiente para ejecutar los hallazgos que cubre, sin releer la auditoria durante implementacion.

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

Reglas de contenido:

- El extracto debe preservar la solucion de auditoria con detalle suficiente para implementarla, con rutas y funciones actualizadas solo si el codigo cambio desde la auditoria.
- Debe separar la solucion de auditoria de la interpretacion del subplan.
- Si la auditoria marca algo como no verificado en runtime, el subplan incluye validacion runtime o justifica por que queda para 6f.
- Un hallazgo critico o alto no puede quedar cubierto solo por una validacion general.
- Un subplan debe declarar los hallazgos relacionados que no cubre para evitar cierres accidentales.

## Orden De Ejecucion

```text
6a (criticos de lifecycle/UX) -> 6c (decision render cache) -> 6b (exactitud preview/alpha) -> 6d (rendimiento export) -> 6e (consolidacion) -> 6f (verificacion integral)
```

6c se adelanta respecto a la version anterior de este plan por dos razones:

1. Con D1 (eliminar), 6c es mayormente borrado de bajo riesgo que reduce la superficie que 6b, 6d y 6e deben razonar (B12 desaparece, `core/render_state.py` queda solo con helpers vivos, M7 consolida sanitizadores sobre el codigo final).
2. Elimina la dependencia invertida de la version anterior, donde B12 (asignado a 6b) dependia de una decision tomada en 6c despues de 6b.

## Subfases

### Fase 6a - Selector Modal Y Lifecycle Runtime

Objetivo: eliminar condiciones donde Blender parece congelado, el overlay queda invisible pero activo o quedan handlers/imagenes vivas tras cambios de archivo.

Hitos secuenciales (el hito 1 se valida antes de continuar):

- **Hito 1 (bloqueante):** C1, C2, B5. Es el nucleo critico; nada mas entra hasta que su validacion Blender pase.
- **Hito 2:** M3, M9, B6 (solo modulos selector/playback), B7, B10, M10 (perfilado y decision, no implementacion especulativa) y el hallazgo runtime nuevo `P1-playback-selection-snapshot`.
- **Hito 3:** M6 (scroll). Es una feature, no un fix; si su implementacion crece, se separa en subplan propio sin bloquear el cierre de los hitos 1-2.

Argumento: C1 y C2 son los fallos de peor impacto para el usuario. El resto comparte superficie tecnica (sesion del selector y controlador de playback) y conviene tratarlo mientras se toca ese lifecycle, pero nunca a costa de retrasar el hito 1.

Hallazgo runtime nuevo:

- `P1-playback-selection-snapshot`: no estaba contemplado explicitamente por `docs/technical-audit.md`. Despues de cambiar seleccion, el playback podia seguir reproduciendo el snapshot anterior de `frame_numbers`/`preview_paths`. Se corrigio refrescando la sesion activa cuando cambian operadores de seleccion y enroutando clicks de celdas por `spritesheet.frame_toggle_selection`, alineado con B7.

### Fase 6c - Decision Y Ejecucion Del Render Cache Final

Objetivo: cerrar el estado intermedio del render cache (A1) ejecutando D1.

Hallazgos cubiertos: A1, B1, B12.

Argumento: A1 no es un bug local sino una feature a medio implementar. Con D1 (eliminar), el subplan borra propiedades persistidas (`render_key`, `render_folder`, `render_dirty`, `last_render_note`, `frame.render_path`), helpers muertos, la rama de reutilizacion en export y los tests que solo cubren codigo muerto, separando primero los helpers vivos listados en D1. B1 se resuelve en el mismo paso (renombrar el parametro `frame_number` a `output_index` en `render_file_path` o documentar el contrato). B12 desaparece con la eliminacion; si D1 cambiara a "completar", B12 y este subplan se replantean juntos.

### Fase 6b - Exactitud De Preview, Alpha Y Estado Visual

Objetivo: asegurar que previews y render final representen lo que el usuario espera: transparencia, regeneracion y rangos de frames.

Hallazgos cubiertos: A2, A4, M1, M2, M4, B9, B11, y el hallazgo runtime nuevo P1-preview-camera-view.

Notas rectoras:

- P1-preview-camera-view: correccion bloqueante validada por el usuario en `docs/plans/reinicio-v2-fase-6b0-preview-camera-viewport.md`. `SOLID`/`MATERIAL` renderizan desde la camara efectiva aunque el viewport este en perspectiva libre.
- A2: forzar/restaurar `image_settings.color_mode = "RGBA"` (y valorar `color_depth = "8"`) en `render_clip_frames` cuando `transparent`; validar con escena previamente en RGB y confirmar restauracion posterior.
- A4: el boton de regeneracion forzada es obligatorio (el backend `force=True` ya existe). La invalidacion por `depsgraph_update_post` es una investigacion opcional con criterio de aceptacion explicito: no degradar rendimiento ni marcar dirty en cascada por ediciones irrelevantes; si no cumple, se difiere documentada.
- M1: no abortar ni borrar un preview valido por ser 100% opaco; degradar a warning o verificar solo ausencia real de canal alpha.
- M2: purgar carpetas hermanas del clip tras generacion exitosa, usando `is_managed_cache_folder` como salvaguarda.
- M4: ejecutar D2 (min=0 en `frame_start`/`frame_end`).
- B9: unificar criterio de identidad (`_id_key`) entre preview cache key y render key, o documentar la invalidacion por rename como comportamiento aceptado.
- B11: mover el cambio/restauracion de shading y overlay fuera del bucle por frame.

### Fase 6d - Rendimiento, Memoria Y Seguridad De Export

Objetivo: evitar OOM, congelamientos largos sin feedback y salidas parciales inconsistentes en export.

Hallazgos cubiertos: A3, A5, B2.

Notas rectoras:

- A3: primero pegado por filas (seguro, sin dependencias) con tests unitarios del helper; despues vectorizacion numpy segun D5, con estimacion antes/despues documentada.
- A5: ejecutar D4 (nivel 1 obligatorio, nivel 2 condicional a medicion).
- B2: el limite de 999 frames debe validarse **antes de renderizar** (al preparar los clips en `_prepare_export_clips` o en la validacion de export), no solo antes de copiar: fallar tras minutos de render es tan malo como la salida parcial. Eliminar la rama muerta del patron de 6 digitos en la limpieza, salvo razon de compatibilidad documentada.

### Fase 6e - Consolidacion, Registro Y Higiene Tecnica

Objetivo: reducir divergencias y deuda que hacen fragiles las correcciones futuras.

Hallazgos cubiertos: M5, M7, M8, B3, B4, B6 (resto).

Notas rectoras:

- M5: validacion unica en `core/validation.py` con modo/severidad (preview/render/export) consumida por operadores y panel; eliminar las etiquetas duplicadas del panel.
- M7: crear `core/context.py` para helpers de contexto; unificar sanitizador en `core/paths.py`; eliminar `effective_preview_label` y el parametro muerto de `effective_preview_mode`; deduplicar `_clear_collection`.
- M8: migrar a registro directo o `bpy.utils.register_classes_factory`; los errores de `register` deben aflorar; mantener tolerancia solo en `unregister`.
- B3: eliminar `original_index` salvo proposito futuro documentado y aprobado.
- B4: retirar guardado/restauracion de `compression` no modificada.
- Igualdad de `PropertyGroup` (punto no verificado de la auditoria): sustituir la comparacion `==` en `_mark_collection_owner_dirty` por comparacion explicita de `as_pointer()`, que elimina la ambiguedad sin coste; si se prefiere no tocar, validar la semantica en 6f.

Se ejecuta despues de 6b/6d para consolidar sobre el codigo final y no refactorizar codigo que 6c elimina o que 6b/6d reescriben.

### Fase 6f - Verificacion Integral De Auditoria

Objetivo: verificar que todos los IDs quedaron corregidos, diferidos con razon o convertidos en limitacion documentada antes de retomar Fase 7.

Cubre: reconciliacion del ledger completo (C1-C2, A1-A5, M1-M10, B1-B12), los puntos no verificados en runtime que sigan pendientes, y la seccion "Lo que no pude verificar" de la auditoria.

Plan ejecutable: `docs/plans/reinicio-v2-fase-6f-verificacion-integral-auditoria.md`.

Estado: implementado en verificacion documental/automatica; validacion Blender GUI pendiente. Fase 7 no queda habilitada hasta validar 6d/6e/6f en GUI o registrar limitacion aceptada por el usuario.

## Ledger De Cobertura

Unico registro de estado por hallazgo. Cada handoff de subplan actualiza su columna Estado (`pendiente | en subplan <id> | corregido | diferido: <razon> | no aplica: <evidencia>`). La Fase 6f reconcilia esta tabla contra el codigo.

| ID | Severidad | Subfase | Estado |
|---|---|---|---|
| P1-preview-camera-view | alto runtime | 6b0 | corregido y validado por el usuario en `docs/plans/reinicio-v2-fase-6b0-preview-camera-viewport.md` |
| C1 | critico | 6a hito 1 | corregido y validado por el usuario en `docs/plans/reinicio-v2-fase-6a-selector-modal-lifecycle.md` y `docs/plans/reinicio-v2-fase-6a-validacion-hito1-selector-modal-lifecycle.md` |
| C2 | critico | 6a hito 1 | corregido y validado por el usuario; V5 GUI por menu no aplica bajo contrato modal visible/intencional y C2 queda cubierto por `load_pre`/`ReferenceError` |
| A1 | alto | 6c | corregido y validado por el usuario en `docs/plans/reinicio-v2-fase-6c-render-cache-final.md` |
| A2 | alto | 6b | corregido y validado por el usuario en `docs/plans/reinicio-v2-fase-6b-preview-alpha-estado-visual.md` |
| A3 | alto | 6d | implementado en `docs/plans/reinicio-v2-fase-6d-rendimiento-export.md`; validacion Blender GUI pendiente |
| A4 | alto | 6b | corregido y validado por el usuario en `docs/plans/reinicio-v2-fase-6b-preview-alpha-estado-visual.md` |
| A5 | alto | 6d | implementado en `docs/plans/reinicio-v2-fase-6d-rendimiento-export.md` (D4 nivel 1); validacion Blender GUI pendiente |
| M1 | medio | 6b | corregido y validado por el usuario en `docs/plans/reinicio-v2-fase-6b-preview-alpha-estado-visual.md` |
| M2 | medio | 6b | corregido y validado por el usuario en `docs/plans/reinicio-v2-fase-6b-preview-alpha-estado-visual.md` |
| M3 | medio | 6a hito 2 | corregido y validado por el usuario en `docs/plans/reinicio-v2-fase-6a-hito2-selector-playback-integridad.md` |
| M4 | medio | 6b | corregido y validado por el usuario en `docs/plans/reinicio-v2-fase-6b-preview-alpha-estado-visual.md` (D2) |
| M5 | medio | 6e | implementado en `docs/plans/reinicio-v2-fase-6e-consolidacion-higiene.md`; validacion Blender GUI pendiente |
| M6 | medio | 6a hito 3 | validado por el usuario en `docs/plans/reinicio-v2-fase-6a-hito3-selector-scroll.md`; queda ajuste UX opcional de sensibilidad trackpad |
| M7 | medio | 6e | implementado en `docs/plans/reinicio-v2-fase-6e-consolidacion-higiene.md`; validacion Blender GUI pendiente |
| M8 | medio | 6e | implementado en `docs/plans/reinicio-v2-fase-6e-consolidacion-higiene.md`; validacion Blender GUI pendiente |
| M9 | medio | 6a hito 2 | corregido y validado por el usuario en `docs/plans/reinicio-v2-fase-6a-hito2-selector-playback-integridad.md` |
| M10 | medio (no verificado) | 6a hito 2 | medido/validado por el usuario sin evidencia para cache GPU; instrumentacion debug opt-in queda disponible en `docs/plans/reinicio-v2-fase-6a-hito2-selector-playback-integridad.md` |
| B1 | bajo | 6c | corregido y validado por el usuario en `docs/plans/reinicio-v2-fase-6c-render-cache-final.md` |
| B2 | bajo | 6d | implementado en `docs/plans/reinicio-v2-fase-6d-rendimiento-export.md`; validacion Blender GUI pendiente |
| B3 | bajo | 6e | implementado en `docs/plans/reinicio-v2-fase-6e-consolidacion-higiene.md`; validacion Blender GUI pendiente |
| B4 | bajo | 6e | implementado en `docs/plans/reinicio-v2-fase-6e-consolidacion-higiene.md`; validacion Blender GUI pendiente |
| B5 | bajo | 6a hito 1 | corregido y validado por el usuario en `docs/plans/reinicio-v2-fase-6a-selector-modal-lifecycle.md` y `docs/plans/reinicio-v2-fase-6a-validacion-hito1-selector-modal-lifecycle.md` |
| B6 | bajo | 6a hito 2 + 6e | corregido y validado por el usuario para selector/playback en `docs/plans/reinicio-v2-fase-6a-hito2-selector-playback-integridad.md`; resto implementado en `docs/plans/reinicio-v2-fase-6e-consolidacion-higiene.md`, validacion Blender GUI pendiente |
| B7 | bajo | 6a hito 2 | corregido y validado por el usuario en `docs/plans/reinicio-v2-fase-6a-hito2-selector-playback-integridad.md` |
| B8 | bajo | Fase 7 | diferido por D3 |
| B9 | bajo | 6b | clasificado en `docs/plans/reinicio-v2-fase-6b-preview-alpha-estado-visual.md`: no aplica como divergencia preview/render tras 6c; preview mantiene invalidacion por nombre visible |
| B10 | bajo | 6a hito 2 | corregido y validado por el usuario en `docs/plans/reinicio-v2-fase-6a-hito2-selector-playback-integridad.md` |
| P1-playback-selection-snapshot | alto runtime | 6a hito 2 | corregido y validado por el usuario; reconciliado en `docs/plans/reinicio-v2-fase-6a-hito2-selector-playback-integridad.md` |
| B11 | bajo | 6b | corregido y validado por el usuario en `docs/plans/reinicio-v2-fase-6b-preview-alpha-estado-visual.md` |
| B12 | bajo | 6c | no aplica: desaparece con D1 implementado y validado en `docs/plans/reinicio-v2-fase-6c-render-cache-final.md` |

## Mapeo De Las Mejoras Propuestas De La Auditoria

Para que 6f no las persiga por separado:

- Mejora 1 (generacion asincrona con progreso) = A5.
- Mejora 2 (regenerate + depsgraph) = A4.
- Mejora 3 (scroll + PASS_THROUGH) = C1 + M6.
- Mejora 4 (composer numpy) = A3.
- Mejora 5 (GC de cache) = M2; el indicador de tamano en panel es opcional no bloqueante.
- Mejora 6 (decision render cache) = A1/D1.
- Mejora 7 (consolidacion) = M5 + M7.
- Mejora 8 (interfaz de metadata writers): **diferida post-MVP**; amplia alcance y no corrige ningun hallazgo.

## Puntos No Verificados En Runtime

| Punto | Donde se resuelve |
|---|---|
| C2: detalle del `ReferenceError` al cargar otro archivo | 6a hito 1 (la limpieza por `load_pre` es obligatoria aunque no se reproduzca) |
| M10: coste real de `gpu.texture.from_image` | 6a hito 2 (perfilado con overlay + playback; cache GPU solo con evidencia) |
| B8: compatibilidad real 4.x/5.x | Fase 7 (D3: se mantiene 5.x) |
| Igualdad de `PropertyGroup` | 6e (sustitucion por `as_pointer()`) o 6f (validacion runtime) |
| Cobertura de codigo con `bpy` | cada subplan aporta validacion Blender manual; 6f verifica que se ejecutaron |

## Validaciones Automaticas Esperadas Por Subplan

- `python3 -m compileall spritesheet_frame_selector`
- `python3 -m unittest discover -s tests`
- Tests nuevos o actualizados para helpers puros tocados.
- Busquedas `rg` especificas por hallazgo cerrado (render cache eliminado, `color_mode` en renderer, `PASS_THROUGH`/cleanup modal, duplicaciones removidas, `except Exception` justificados).

## Validaciones Blender Esperadas

- Abrir selector y confirmar que no bloquea navegacion fuera del panel.
- Cambiar workspace/clip o cargar archivo nuevo con selector abierto y confirmar cleanup (sin overlay fantasma, sin timers, sin crecimiento de imagenes).
- Generar previews, regenerarlos forzadamente y confirmar thumbnails frescos.
- Exportar con escena configurada en `color_mode="RGB"`: el PNG debe tener alpha y el ajuste debe quedar restaurado tras el export.
- Exportar spritesheet mediano y confirmar que progreso/tiempo/memoria son aceptables (referencia para el nivel 2 de D4).
- Intentar export de secuencia con mas de 999 frames: debe fallar antes de renderizar, sin salida parcial.
- Registrar/desregistrar/reactivar el addon si se toca `registration.py`.

## Criterio De Termino De Fase 6

La Fase 6 queda validada cuando:

- el ledger no contiene ningun `pendiente`: todo ID esta `corregido`, `diferido: <razon>` o `no aplica: <evidencia>`;
- los hallazgos criticos y altos no quedan diferidos salvo decision explicita del usuario;
- el codigo modificado pasa las validaciones automaticas aplicables;
- las validaciones Blender requeridas fueron ejecutadas o justificadas por limitacion del entorno;
- `docs/technical-audit.md` sigue intacto como fuente y este plan registra el estado final de cobertura;
- la Fase 7 queda habilitada como siguiente paso operativo;
- PCS refleja el estado final sin marcar cerrado salvo instruccion explicita.

## Proximo Paso Recomendado

1. Ejecutar validacion Blender GUI acumulada de `docs/plans/reinicio-v2-fase-6d-rendimiento-export.md`, `docs/plans/reinicio-v2-fase-6e-consolidacion-higiene.md` y `docs/plans/reinicio-v2-fase-6f-verificacion-integral-auditoria.md`.
2. Confirmar A3/A5/B2: export mediano sin regresion visual, progreso visible, progreso cerrado al finalizar/fallar y fallo temprano con mas de 999 frames individuales.
3. Confirmar M5/M8/M7/B3/B4/B6/PG-equality: activar/desactivar/reactivar addon, panel sin mensajes duplicados, preview/export normales tras consolidacion y dirty flags correctos al cambiar defaults/overrides.
4. Si la validacion pasa, actualizar 6f y este plan rector a `validado` o `listo para cierre` segun corresponda, sin cerrar PCS ni archivar planes salvo instruccion explicita.
5. Solo despues de esa validacion, retomar `docs/plans/reinicio-v2-fase-7-validacion-distribucion.md`.
