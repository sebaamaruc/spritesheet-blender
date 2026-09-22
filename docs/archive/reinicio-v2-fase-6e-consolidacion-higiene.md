# Plan Fase 6e - Consolidacion, Registro E Higiene Tecnica

Estado: aprobado
Autoridad: usuario
Modo de ejecucion: ejecutar sin replanificar
Estado De Ejecucion: cerrado

## Referencia Superior

`docs/plans/reinicio-v2-fase-6-correcciones-auditoria-tecnica.md`

## Fuente Principal

- `docs/technical-audit.md`
- `docs/plans/reinicio-v2-fase-6-correcciones-auditoria-tecnica.md`
- Codigo actual revisado:
  - `spritesheet_frame_selector/core/validation.py`
  - `spritesheet_frame_selector/core/workspace_state.py`
  - `spritesheet_frame_selector/properties.py`
  - `spritesheet_frame_selector/registration.py`
  - `spritesheet_frame_selector/preview/generator.py`
  - `spritesheet_frame_selector/ui/visual_selector.py`
  - `spritesheet_frame_selector/operators/{clips,workspaces,preview,playback,export,visual_selector}.py`

## Estado De Entrada

- 6d esta implementado pero pendiente de validacion Blender GUI. El usuario aprobo explicitamente avanzar con 6e el 2026-07-06 mediante la instruccion "implementa".
- 6e se ejecuta despues de 6b y 6d porque consolida sobre codigo ya corregido; si 6d requiere correcciones por validacion GUI, esas correcciones tienen prioridad sobre implementar 6e.

## Objetivo

Reducir divergencias, duplicacion y deuda que fragilizan las correcciones futuras:

- consolidar validaciones de contexto preview/render/export;
- unificar helpers transversales de contexto y sanitizacion;
- corregir registro defensivo que enmascara errores;
- eliminar o clasificar campos/codigo muerto;
- completar B6 fuera de selector/playback, sin perder debug util;
- resolver la ambiguedad no verificada de igualdad de `PropertyGroup`.

## Hallazgos De Auditoria Cubiertos

| ID | Severidad | Titulo | Estado En Este Subplan |
|---|---|---|---|
| M5 | medio | Triple implementacion de validacion y etiquetas duplicadas en panel | implementado |
| M7 | medio | Duplicacion estructural transversal | implementado |
| M8 | medio | Registro defensivo enmascara errores y puede desregistrar clases ajenas | implementado |
| B3 | bajo | Campo muerto `original_index` | implementado |
| B4 | bajo | Restauracion de `compression` no modificada en preview generator | implementado |
| B6 | bajo | Silenciamiento amplio de excepciones, resto no cubierto por 6a hito 2 | implementado |
| PG-equality | no verificado | Igualdad de `PropertyGroup` en `_mark_collection_owner_dirty` | implementado |

## Extracto Operativo De Auditoria

### M5 - Triple implementacion de validacion

- Problema: las comprobaciones de camara, colecciones y override existen en tres lugares: inline en `operators/preview.py::_generate_preview_cache`, en `core/workspace_state.py::preview_context_warnings` y en `core/validation.py::validate_active_clip_render_context`. El panel tambien puede pintar colecciones faltantes dos veces porque consume `preview_context_warnings` y luego vuelve a listar `missing_effective_collection_names`.
- Causa: evolucion incremental sin consolidar.
- Impacto: mantenimiento por triplicado, riesgo de divergencia y UI con mensajes repetidos.
- Solucion propuesta por la auditoria: una funcion unica en `core/validation.py` con parametro de severidad/modo preview/render/export, consumida por operadores y panel; eliminar el bucle duplicado del panel.
- Archivos/funciones afectados: `spritesheet_frame_selector/operators/preview.py::_generate_preview_cache`, `spritesheet_frame_selector/core/workspace_state.py::preview_context_warnings`, `spritesheet_frame_selector/core/validation.py`, `spritesheet_frame_selector/ui/panels.py::SPRITESHEET_PT_main.draw`.
- Aspectos no verificados en runtime: que el panel no duplique mensajes y que preview/export reporten mensajes equivalentes tras la consolidacion.

### M7 - Duplicacion estructural transversal

- Problema: `_scene_state` y `_active_workspace` estan copiados en modulos de operadores; `_clear_collection` esta duplicado en `workspace_state.py` y `frame_sync.py`; hay sanitizadores parecidos (`safe_path_part`, `_safe_file_prefix`, `_safe_sheet_name`); `effective_preview_mode(workspace, clip)` ignora `workspace` y existe `effective_preview_label` duplicado en `ui/visual_selector.py`.
- Causa: modulos crecieron en paralelo.
- Impacto: mantenibilidad baja y riesgo de divergencias futuras.
- Solucion propuesta por la auditoria: crear `core/context.py` con `scene_state(context)`, `active_workspace(context)`, `active_clip(context)`; unificar sanitizador en `core/paths.py`; eliminar `effective_preview_label` y el parametro muerto de `effective_preview_mode`; deduplicar `_clear_collection`.
- Archivos/funciones afectados: `spritesheet_frame_selector/operators/{clips,workspaces,preview,playback,export,visual_selector}.py`, `spritesheet_frame_selector/core/{workspace_state,frame_sync,paths,render_state}.py`, `spritesheet_frame_selector/ui/visual_selector.py`.
- Aspectos no verificados en runtime: que los operadores sigan resolviendo workspace/clip activo igual tras mover helpers.

### M8 - Registro defensivo que enmascara errores

- Problema: `registration.py::register()` captura `ValueError` de `bpy.utils.register_class(cls)` y aun asi agrega la clase a `_registered_classes`; luego `unregister()` puede desregistrar una clase que este modulo no registro. El try/except tambien puede ocultar errores de registro reales.
- Causa: defensa contra doble registro llevada demasiado lejos.
- Impacto: en reloads, dobles instalaciones o errores de anotaciones, el addon puede quedar en estado inconsistente y dificil de depurar.
- Solucion propuesta por la auditoria: registro directo con `bpy.utils.register_classes_factory(CLASSES)` o registro directo que deje aflorar errores; mantener tolerancia solo en `unregister`.
- Archivos/funciones afectados: `spritesheet_frame_selector/registration.py::register/unregister`.
- Aspectos no verificados en runtime: reactivar/desactivar addon y reload parcial en Blender.

### B3 - Campo muerto `original_index`

- Problema: `original_index` se escribe y copia en `core/frame_sync.py` y `core/workspace_state.py`, pero no se lee para logica.
- Causa: dato heredado de una idea previa de orden/origen que ya no participa del flujo.
- Impacto: ruido persistido en `.blend` y deuda conceptual.
- Solucion propuesta por la auditoria: eliminarlo o documentar su proposito futuro.
- Archivos/funciones afectados: `spritesheet_frame_selector/properties.py::SpriteSheetFrameItem`, `spritesheet_frame_selector/core/frame_sync.py`, `spritesheet_frame_selector/core/workspace_state.py`, tests que construyen fake frames.
- Aspectos no verificados en runtime: compatibilidad con `.blend` existentes que tengan la propiedad antigua; al eliminar la propiedad, Blender debe ignorar datos no registrados.

### B4 - Restauracion de `compression` no modificada

- Problema: el preview generator guarda y restaura `image_settings.compression`, pero no la modifica.
- Causa: snapshot de estado demasiado amplio.
- Impacto: ruido menor; dificulta leer que estado se toca realmente.
- Solucion propuesta por la auditoria: retirar guardado/restauracion de `compression`.
- Archivos/funciones afectados: `spritesheet_frame_selector/preview/generator.py::generate_viewport_previews`.
- Aspectos no verificados en runtime: que previews sigan restaurando solo el estado realmente modificado.

### B6 - Silenciamiento amplio de excepciones restante

- Problema: `except Exception: pass/return` dificulta diagnostico. 6a hito 2 ya cubrio selector/playback con debug opt-in, pero quedan catches relevantes fuera de esa superficie, especialmente `_preview_file_has_transparency` y algunas rutas de imagen/selector.
- Causa: defensas locales para evitar romper UI en draw/render.
- Impacto: fallos reales quedan ocultos y el usuario solo ve estado incompleto o previews faltantes.
- Solucion propuesta por la auditoria: loggear al menos con `print`/debug opt-in en modo debug.
- Archivos/funciones afectados actuales: `spritesheet_frame_selector/preview/generator.py::_preview_file_has_transparency`, `spritesheet_frame_selector/ui/visual_selector.py` rutas de carga/reset/draw si no quedaron cubiertas por 6a, `spritesheet_frame_selector/export/composer.py` si conviene no capturar todo sin contexto.
- Aspectos no verificados en runtime: que el logging no ensucie consola en uso normal.

### PG-equality - Igualdad de `PropertyGroup` no verificada

- Problema no verificado por la auditoria: `_mark_collection_owner_dirty` usa comparaciones `item == collection_item` para detectar owner. La semantica de igualdad de `PropertyGroup` puede ser ambigua entre versiones/reloads.
- Causa: comparacion directa de wrappers Blender.
- Impacto: dirty flags de cache podrian no marcarse correctamente si igualdad no se comporta como identidad de datablock/wrapper.
- Solucion rectora: sustituir comparacion por identidad explicita usando `as_pointer()` cuando exista, con fallback seguro.
- Archivos/funciones afectados: `spritesheet_frame_selector/properties.py::_mark_collection_owner_dirty`.
- Aspectos no verificados en runtime: semantica exacta de igualdad en Blender objetivo; el cambio a `as_pointer()` evita depender de ella.

## Interpretacion Del Subplan

- M5: adoptar la solucion de auditoria. Crear una validacion unica en `core/validation.py` para preview/render/export o extender la actual con modo. El operador de preview y el panel deben consumir esa fuente unica. Evitar cambios de texto innecesarios salvo para eliminar duplicados.
- M7: adoptar parcialmente y con alcance controlado. Crear `core/context.py` para helpers activos usados por operadores. Unificar sanitizacion de nombres en `core/paths.py` solo si no cambia filenames publicos validados; si cambiara output visible, dejar wrapper compatible y documentar.
- M8: adoptar solucion. Preferir registro directo con `register_classes_factory` si encaja con handler/scene props; si no, registrar en bucle sin capturar errores en `register()`. `unregister()` puede seguir tolerando `RuntimeError/ValueError`.
- B3: eliminar `original_index` si tests y codigo confirman que no hay lectores. Si aparece dependencia real durante implementacion, documentar proposito y marcar B3 diferido con razon.
- B4: eliminar snapshot/restauracion de `compression`.
- B6: completar debug opt-in fuera de selector/playback. No imprimir en modo normal. Reusar el patron existente `SFS_SELECTOR_PLAYBACK_DEBUG` o renombrar a un debug mas general solo si no aumenta alcance.
- PG-equality: implementar comparacion por `as_pointer()` con fallback a identidad de objeto Python.

## Alcance De Implementacion

Incluir:

- `core/validation.py`: funcion comun para validar contexto con modo/severidad (`preview`, `render`, `export`) y mensajes reutilizables.
- `operators/preview.py`: reemplazar validacion inline por helper comun.
- `ui/panels.py`: eliminar duplicacion de missing collections y consumir helper comun.
- `core/context.py`: helpers `scene_state`, `active_workspace`, `active_clip` para operadores.
- Operadores: migrar helpers duplicados `_scene_state`/`_active_workspace` al nuevo `core/context.py` donde sea local y seguro.
- `core/workspace_state.py` / `core/frame_sync.py`: deduplicar `_clear_collection`.
- `core/paths.py`, `core/render_state.py`, `operators/export.py`: revisar sanitizadores y consolidar sin romper nombres publicos validados.
- `ui/visual_selector.py`: eliminar `effective_preview_label` y consumir `effective_preview_mode(clip)` si se retira parametro `workspace`.
- `registration.py`: corregir registro defensivo.
- `properties.py`, `frame_sync.py`, `workspace_state.py`, tests: eliminar o justificar `original_index`.
- `preview/generator.py`: retirar `compression` si no se modifica; completar logging debug opt-in en catches restantes.
- Tests unitarios para validacion comun, registro, deduplicacion de mensajes, `original_index`, sanitizacion y comparacion por pointer cuando sea simulable.

Excluir:

- No cambiar UX visual del panel salvo eliminar duplicados.
- No cambiar formato JSON, filenames publicos ni layout de spritesheet salvo que tests prueben compatibilidad.
- No tocar packaging/Fase 7.
- No resolver A3/A5/B2 pendientes de validacion de 6d; si la validacion de 6d falla, corregir 6d antes de implementar 6e.
- No cerrar ni archivar planes.

## Archivos Esperados

- `spritesheet_frame_selector/core/validation.py`
- `spritesheet_frame_selector/core/context.py`
- `spritesheet_frame_selector/core/workspace_state.py`
- `spritesheet_frame_selector/core/frame_sync.py`
- `spritesheet_frame_selector/core/paths.py`
- `spritesheet_frame_selector/core/render_state.py`
- `spritesheet_frame_selector/operators/{clips,workspaces,preview,playback,export,visual_selector}.py`
- `spritesheet_frame_selector/ui/panels.py`
- `spritesheet_frame_selector/ui/visual_selector.py`
- `spritesheet_frame_selector/registration.py`
- `spritesheet_frame_selector/properties.py`
- `spritesheet_frame_selector/preview/generator.py`
- Tests existentes bajo `tests/` y tests nuevos si conviene separar cobertura.

## Validacion

### Validaciones Automaticas

- `python3 -m compileall spritesheet_frame_selector`
- `python3 -m unittest discover -s tests`
- Busquedas de contrato:
  - `rg -n "def _scene_state|def _active_workspace|def _active_workspace_and_clip" spritesheet_frame_selector/operators`
  - `rg -n "original_index" spritesheet_frame_selector tests`
  - `rg -n "compression" spritesheet_frame_selector/preview/generator.py tests`
  - `rg -n "register_class|register_classes_factory|_registered_classes" spritesheet_frame_selector/registration.py tests`
  - `rg -n "effective_preview_label|effective_preview_mode\\(workspace" spritesheet_frame_selector tests`
  - `rg -n "except Exception" spritesheet_frame_selector/preview spritesheet_frame_selector/ui tests`

Resultado de implementacion:

- `python3 -m compileall spritesheet_frame_selector`: OK.
- `python3 -m unittest discover -s tests`: OK, 81 tests.
- Busquedas de contrato ejecutadas:
  - sin resultados para helpers duplicados `_scene_state`, `_active_workspace`, `_active_workspace_and_clip` en operadores;
  - sin resultados para `original_index`;
  - sin resultados para `compression` en `preview/generator.py` y tests;
  - sin resultados para `effective_preview_label` ni `effective_preview_mode(workspace`;
  - `registration.py` conserva `_registered_classes` solo para clases registradas exitosamente y `unregister`;
  - quedan `except Exception` defensivos en preview/UI con logging debug opt-in o contexto de draw seguro.

### Validaciones Blender GUI/Background

- Activar/desactivar addon y confirmar que registro/desregistro no deja clases/handlers duplicados.
- Generar preview y exportar spritesheet normal para confirmar que validacion comun no cambio comportamiento esperado.
- En panel, provocar camara faltante y coleccion faltante; confirmar que no hay mensajes duplicados.
- Duplicar clip/workspace y confirmar frames/seleccion/cache siguen correctos tras retirar `original_index`.
- Generar preview SOLID/MATERIAL y confirmar que el removal de `compression` no afecta salida.

### Criterio De Aceptacion Por Hallazgo

- M5: preview/export/panel usan una fuente comun de validacion y no duplican mensajes.
- M7: helpers de contexto y limpieza quedan centralizados; sanitizadores quedan unificados o con wrappers compatibles documentados.
- M8: `register()` no silencia errores reales ni agrega clases no registradas a `_registered_classes`; `unregister()` sigue tolerante.
- B3: `original_index` queda eliminado o documentado con razon explicita si se difiere.
- B4: `compression` ya no se guarda/restaura si no se modifica.
- B6: catches restantes relevantes tienen debug opt-in o justificacion local; no hay spam en modo normal.
- PG-equality: `_mark_collection_owner_dirty` no depende de `==` entre `PropertyGroup`.

## Riesgos

- Consolidar validacion puede cambiar mensajes usados por tests o por UX. Mantener textos existentes cuando sea posible.
- Tocar registro puede romper reload de addon si se olvida scene props o handler `load_pre`.
- Eliminar `original_index` cambia schema registrado; `.blend` antiguos deben tolerar datos antiguos no registrados.
- Unificar sanitizadores puede cambiar filenames si se hace de forma agresiva. Mantener compatibilidad de nombres ya validados.

## Proximo Paso

Validar en Blender GUI junto con `docs/plans/reinicio-v2-fase-6d-rendimiento-export.md`. No cerrar ni archivar planes sin instruccion explicita del usuario.
