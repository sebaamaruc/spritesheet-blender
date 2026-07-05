# Plan Fase 6a - Selector Modal Y Lifecycle Runtime

Estado: aprobado
Autoridad: usuario
Modo de ejecucion: ejecutar sin replanificar
Estado De Ejecucion: implementado

## Referencia Superior

`docs/plans/reinicio-v2-fase-6-correcciones-auditoria-tecnica.md`

## Fuente Principal

`docs/technical-audit.md`

## Alcance Del Subplan

Este subplan ejecuta solo el **Hito 1 bloqueante** de Fase 6a: C1, C2 y B5.

No ejecuta todavia el Hito 2 ni el Hito 3 de Fase 6a. La razon es deliberada: C1 y C2 pueden producir una percepcion de cuelgue total, overlay invisible activo, fugas de handlers y referencias muertas. Deben validarse en Blender antes de sumar mejoras de rendimiento, undo, thumbnails, FPS o scroll.

## Hallazgos De Auditoria Cubiertos

| ID | Severidad | Titulo | Estado En Este Subplan |
|---|---|---|---|
| C1 | critico | El selector visual bloquea toda la UI de Blender y puede quedar "invisible" pero activo | implementado; validacion Blender pendiente |
| C2 | critico | Fuga del draw handler y de recursos al terminar el modal sin pasar por cleanup | implementado; validacion Blender pendiente |
| B5 | bajo | `SPRITESHEET_OT_visual_selector_open.execute()` devuelve `FINISHED` sin hacer nada cuando no es background | implementado; validacion Blender pendiente |

## Hallazgos Relacionados No Cubiertos

| ID | Subfase Rectora | Motivo |
|---|---|---|
| M3 | 6a hito 2 | Comparte superficie de playback/redraw, pero no bloquea la correccion critica del modal. |
| M6 | 6a hito 3 | Scroll/paginacion depende de eventos del selector, pero es feature de accesibilidad del grid; se separa para no retrasar C1/C2. |
| M9 | 6a hito 2 | Thumbnails obsoletos por recarga de imagenes; no forma parte del lifecycle modal minimo. |
| M10 | 6a hito 2 | Requiere perfilado runtime de `gpu.texture.from_image`; no debe implementarse especulativamente. |
| B6 | 6a hito 2 + 6e | Se tocara solo si aparece dentro de los cambios de C1/C2; el barrido general queda fuera. |
| B7 | 6a hito 2 | Undo del overlay requiere enrutar clicks por operador; no es necesario para cerrar fugas/bloqueo modal. |
| B10 | 6a hito 2 | FPS de playback al reanudar; no participa en apertura/cierre del selector. |

## Extracto Operativo De Auditoria

### C1 - El selector visual bloquea toda la UI de Blender y puede quedar "invisible" pero activo

- Problema: el operador modal consume todos los eventos. `modal()` devuelve `RUNNING_MODAL` para cualquier evento no gestionado y nunca `PASS_THROUGH`. Mientras el selector esta abierto no se puede navegar el viewport, usar menus ni ningun otro panel. Si el workspace/clip activo deja de coincidir con la sesion, por ejemplo tras un undo que elimina el clip o al cargar otro archivo, `draw()` retorna temprano y el overlay desaparece, pero el modal sigue consumiendo eventos. Blender parece congelado hasta que el usuario adivina pulsar ESC.
- Causa: `spritesheet_frame_selector/operators/visual_selector.py::SPRITESHEET_OT_visual_selector_open.modal` devuelve `RUNNING_MODAL` como fallback. `spritesheet_frame_selector/ui/visual_selector.py::handle_visual_selector_event` no distingue clicks dentro/fuera del panel ni valida que la sesion siga siendo coherente.
- Impacto: percepcion de cuelgue total de Blender; es el peor tipo de bug de UX en un modal.
- Solucion propuesta por la auditoria: devolver `PASS_THROUGH` para eventos fuera del rect del panel, al menos navegacion con rueda, `MIDDLEMOUSE` y atajos con modificadores. En cada evento, si `active_workspace_clip_readonly` no coincide con `workspace_id/clip_id` de la sesion, cerrar automaticamente con `cleanup_visual_selector_resources()` y devolver `CANCELLED`.
- Archivos/funciones afectados: `spritesheet_frame_selector/operators/visual_selector.py::SPRITESHEET_OT_visual_selector_open.modal`, `spritesheet_frame_selector/ui/visual_selector.py::handle_visual_selector_event`, `spritesheet_frame_selector/ui/visual_selector.py::_handle_click`.
- Aspectos no verificados en runtime: la auditoria no ejecuto el addon dentro de Blender. Debe verificarse manualmente que el selector no bloquea navegacion fuera del panel y que se autocancela si cambia el contexto activo.

### C2 - Fuga del draw handler y de recursos al terminar el modal sin pasar por cleanup

- Problema: si el modal termina sin ejecutar `cleanup_visual_selector_resources()`, caso tipico al cargar otro `.blend` porque Blender cancela modales sin invocar de nuevo `modal()`, el `draw_handler_add` queda registrado para siempre junto con `session.images` y sus datablocks `bpy.data.images`. El addon no registra handlers `bpy.app.handlers.load_pre/load_post` que limpien la sesion del selector ni la sesion de playback; la limpieza solo ocurre en `unregister()`.
- Causa: ausencia de handlers de ciclo de vida de archivo en `spritesheet_frame_selector/registration.py`; el ciclo de vida de la sesion depende exclusivamente de que el modal muera limpiamente.
- Impacto: fuga acumulativa de memoria/handler por sesion, overlay fantasma dibujandose sobre datos obsoletos y referencias muertas en `self.region`/`self.area`. La auditoria indica que accesos como `self.region.width` podrian lanzar `ReferenceError` en cada redraw y generar spam de excepciones en consola.
- Solucion propuesta por la auditoria: registrar un handler `@persistent` `load_pre` que llame a `cleanup_playback_resources()` y `cleanup_visual_selector_resources()`, y registrarlo/quitarlo en `register()/unregister()`. Adicionalmente, envolver el cuerpo de `VisualSelectorSession.draw()` en `try/except` que auto-cierre la sesion ante `ReferenceError`.
- Archivos/funciones afectados: `spritesheet_frame_selector/registration.py::register`, `spritesheet_frame_selector/registration.py::unregister`, `spritesheet_frame_selector/ui/visual_selector.py::VisualSelectorSession.draw`, `spritesheet_frame_selector/ui/visual_selector.py::VisualSelectorSession.close`, `spritesheet_frame_selector/playback/controller.py::cleanup_playback_resources`.
- Aspectos no verificados en runtime: el detalle exacto del `ReferenceError` al cargar otro archivo no fue verificado en Blender. La limpieza por `load_pre` es obligatoria aunque el error no se reproduzca.

### B5 - `SPRITESHEET_OT_visual_selector_open.execute()` devuelve `FINISHED` sin abrir nada cuando no es background

- Problema: `SPRITESHEET_OT_visual_selector_open.execute()` devuelve `FINISHED` sin hacer nada cuando Blender no esta en background. Invocado desde script, pareceria funcionar aunque no abra el selector.
- Causa: `spritesheet_frame_selector/operators/visual_selector.py::SPRITESHEET_OT_visual_selector_open.execute` solo cancela en `bpy.app.background`; fuera de background retorna `FINISHED` sin delegar al flujo modal ni reportar que debe usarse `invoke`.
- Impacto: comportamiento enganoso para llamadas por script o rutas no-UI; dificulta diagnosticar por que el selector no se abrio.
- Solucion propuesta por la auditoria: devolver `CANCELLED` con mensaje.
- Archivos/funciones afectados: `spritesheet_frame_selector/operators/visual_selector.py::SPRITESHEET_OT_visual_selector_open.execute`.
- Aspectos no verificados en runtime: no requiere verificacion Blender compleja; debe validarse por inspeccion y, si se ejecuta en Blender, confirmando que una llamada directa a `execute` no reporta exito falso.

## Interpretacion Del Subplan

- Decision: adoptar la solucion de auditoria para C1, C2 y B5.
- Argumento: los tres cambios reducen estados engañosos donde Blender parece aceptar una accion pero queda bloqueado, invisible o con recursos vivos. C1 y C2 son criticos y deben cerrarse antes de cualquier mejora en selector/playback. B5 es local, barato y evita falsos positivos al invocar el operador por script.
- Riesgos: `PASS_THROUGH` mal aplicado podria impedir interacciones dentro del panel; un `load_pre` duplicado podria registrar varias veces el mismo cleanup; un `try/except ReferenceError` demasiado amplio podria ocultar errores reales si captura mas de lo necesario.
- Dependencias con otros hallazgos: M6 comparte eventos de rueda con C1, pero queda excluido. B6 puede tocarse solo si la implementacion introduce o encuentra silencios de excepcion en las funciones modificadas. B7 queda fuera aunque `_handle_click` este listado en C1; no se debe reescribir toggle/undo dentro de este hito.

## Alcance De Implementacion

- Incluir:
  - Hacer que el modal devuelva `PASS_THROUGH` para eventos fuera del panel cuando no sean acciones propias del selector.
  - Mantener consumo de eventos dentro del panel para clicks/atajos propios del selector.
  - Validar coherencia de sesion contra workspace/clip activo en cada evento; si no coincide, cerrar recursos del selector y devolver `CANCELLED`.
  - Agregar cleanup de selector y playback en un handler persistente `load_pre`.
  - Registrar y desregistrar ese handler sin duplicarlo.
  - Proteger `VisualSelectorSession.draw()` contra `ReferenceError` cerrando la sesion.
  - Cambiar `SPRITESHEET_OT_visual_selector_open.execute()` para que no retorne `FINISHED` sin abrir nada.
- Excluir:
  - Scroll/paginacion de frames del selector (M6).
  - Reroute de clicks por `SPRITESHEET_OT_frame_toggle_selection` para undo (B7).
  - Recarga de thumbnails/imagenes obsoletas (M9).
  - Perfilado o cache de `GPUTexture` (M10).
  - Redraw selectivo del playback (M3).
  - Barrido general de `except Exception` fuera de las funciones tocadas (B6 restante).
- Archivos esperados:
  - `spritesheet_frame_selector/operators/visual_selector.py`
  - `spritesheet_frame_selector/ui/visual_selector.py`
  - `spritesheet_frame_selector/registration.py`
  - `spritesheet_frame_selector/playback/controller.py` solo si hace falta ajustar contrato de cleanup o import.

## Validacion

- Validaciones automaticas:
  - `python3 -m compileall spritesheet_frame_selector` - pasado.
  - `python3 -m unittest discover -s tests` - pasado, 65 tests.
  - Busqueda especifica: confirmar que `SPRITESHEET_OT_visual_selector_open.modal` puede devolver `PASS_THROUGH` - pasado.
  - Busqueda especifica: confirmar que existe handler `load_pre` registrado/desregistrado y que llama a `cleanup_playback_resources()` y `cleanup_visual_selector_resources()` - pasado.
  - Busqueda especifica: confirmar que `SPRITESHEET_OT_visual_selector_open.execute()` no devuelve `FINISHED` sin abrir selector - pasado.
- Validaciones Blender GUI/background:
  - Pendiente: abrir el selector en un View3D con previews existentes.
  - Pendiente: mover/navegar el viewport fuera del panel con rueda y `MIDDLEMOUSE`; Blender no debe parecer congelado.
  - Pendiente: hacer click dentro del panel y confirmar que las acciones del selector siguen funcionando.
  - Pendiente: cambiar workspace o clip activo mientras el selector esta abierto; el selector debe cerrarse sin overlay fantasma ni consumo posterior de eventos.
  - Pendiente: abrir selector y cargar otro `.blend`; el cleanup de `load_pre` debe ejecutarse sin handlers ni imagenes persistentes del selector anterior.
  - Pasado en Blender background fuera del sandbox: cerrar/reabrir o desactivar/reactivar el addon no duplica el handler `load_pre`; `unregister()` lo remueve.
  - Pasado en Blender background fuera del sandbox: llamada directa a `bpy.ops.spritesheet.visual_selector_open()` retorna `CANCELLED` con reporte comprensible.
  - Pasado en Blender background fuera del sandbox: logica de eventos simulada confirma `PASS_THROUGH` fuera del panel/navegacion/modificadores, manejo dentro del panel y cancelacion por sesion incoherente.
  - Pasado en Blender background fuera del sandbox: `draw()` limpia sesion ante `ReferenceError`.
- Criterio de aceptacion por hallazgo:
  - C1: eventos fuera del panel pasan a Blender cuando corresponde; una sesion incoherente se cancela con cleanup y no deja modal invisible activo.
  - C2: cargar archivo o terminar sesion sin camino modal normal limpia selector/playback; `draw()` no spamea `ReferenceError` y cierra la sesion si encuentra referencias muertas.
  - B5: una ejecucion directa no-background sin `invoke` retorna `CANCELLED` con reporte comprensible.

## Actualizacion PCS Esperada Al Aprobar

El usuario pidio implementar este subplan explicitamente. El subplan queda implementado por codigo y validaciones automaticas, pero no validado/cerrado hasta ejecutar las validaciones Blender GUI/background.

## Resumen De Implementacion

- `spritesheet_frame_selector/operators/visual_selector.py`: `modal()` ahora devuelve `{"RUNNING_MODAL", "PASS_THROUGH"}` cuando el selector no maneja el evento, para dejar pasar el evento sin terminar el modal; `execute()` devuelve `CANCELLED` con reporte en vez de `FINISHED` sin abrir nada.
- `spritesheet_frame_selector/ui/visual_selector.py`: cada evento valida que la sesion siga coincidiendo con workspace/clip activo; si no coincide, limpia recursos y cancela. Los clicks fuera del panel y los eventos de navegacion/modificadores devuelven `{"RUNNING_MODAL", "PASS_THROUGH"}`. `VisualSelectorSession.draw()` cierra la sesion ante `ReferenceError`.
- `spritesheet_frame_selector/registration.py`: se registro un handler persistente `load_pre` que limpia playback y selector visual, y se desregistra en `unregister()` sin duplicarlo.
