# Plan Fase 6a - Validacion Hito 1 Selector Modal Y Lifecycle

Estado: aprobado
Autoridad: usuario
Modo de ejecucion: ejecutar sin replanificar
Estado De Ejecucion: implementado

## Referencia Superior

`docs/plans/reinicio-v2-fase-6a-selector-modal-lifecycle.md`

## Fuente Principal

- `docs/plans/reinicio-v2-fase-6-correcciones-auditoria-tecnica.md`
- `docs/plans/reinicio-v2-fase-6a-selector-modal-lifecycle.md`
- `docs/technical-audit.md`

## Objetivo

Validar en Blender el hito 1 implementado de Fase 6a antes de crear o ejecutar cualquier plan de hito 2/3.

Este plan no implementa funcionalidades nuevas. Su funcion es confirmar que las correcciones ya aplicadas para C1, C2 y B5 cumplen el contrato runtime, o detectar problemas y devolver el mismo hito 1 a `correcciones requeridas`.

## Hallazgos De Auditoria Cubiertos

| ID | Severidad | Titulo | Estado En Este Plan |
|---|---|---|---|
| C1 | critico | El selector visual bloquea toda la UI de Blender y puede quedar "invisible" pero activo | correccion ajustada tras prueba GUI; validacion background de logica pasada; validacion GUI real pendiente |
| C2 | critico | Fuga del draw handler y de recursos al terminar el modal sin pasar por cleanup | validacion background de `load_pre`/`ReferenceError` pasada; validacion GUI real pendiente |
| B5 | bajo | `SPRITESHEET_OT_visual_selector_open.execute()` devuelve `FINISHED` sin hacer nada cuando no es background | validado en Blender background |

## Extracto Operativo De Auditoria

### C1 - El selector visual bloquea toda la UI de Blender y puede quedar "invisible" pero activo

- Problema: el operador modal consumia todos los eventos y podia dejar Blender con apariencia de cuelgue si el overlay desaparecia pero el modal seguia activo.
- Causa: `SPRITESHEET_OT_visual_selector_open.modal` devolvia `RUNNING_MODAL` como fallback y `handle_visual_selector_event` no distinguia eventos dentro/fuera del panel ni validaba coherencia de sesion.
- Impacto: percepcion de cuelgue total de Blender.
- Solucion propuesta por la auditoria: devolver `PASS_THROUGH` para eventos fuera del rect del panel, al menos navegacion con rueda, `MIDDLEMOUSE` y atajos con modificadores; validar en cada evento que workspace/clip activo coincida con la sesion y cerrar con cleanup + `CANCELLED` si no coincide.
- Archivos/funciones afectados: `spritesheet_frame_selector/operators/visual_selector.py::SPRITESHEET_OT_visual_selector_open.modal`, `spritesheet_frame_selector/ui/visual_selector.py::handle_visual_selector_event`, `spritesheet_frame_selector/ui/visual_selector.py::_handle_click`.
- Aspectos no verificados en runtime: navegacion real de viewport fuera del panel y autocancelacion por cambio de workspace/clip.

### C2 - Fuga del draw handler y de recursos al terminar el modal sin pasar por cleanup

- Problema: si Blender termina el modal sin pasar por `cleanup_visual_selector_resources()`, el draw handler y las imagenes de sesion pueden quedar vivos.
- Causa: ausencia de handlers de ciclo de vida de archivo en `registration.py`; la limpieza dependia de muerte limpia del modal o de `unregister()`.
- Impacto: fuga acumulativa de handlers/imagenes, overlay fantasma y posibles `ReferenceError` por referencias muertas de area/region.
- Solucion propuesta por la auditoria: registrar handler persistente `load_pre` que llame a `cleanup_playback_resources()` y `cleanup_visual_selector_resources()`, registrarlo/quitarlo en `register()/unregister()`, y envolver `VisualSelectorSession.draw()` para autocerrar ante `ReferenceError`.
- Archivos/funciones afectados: `spritesheet_frame_selector/registration.py::register/unregister`, `spritesheet_frame_selector/ui/visual_selector.py::VisualSelectorSession.draw/close`, `spritesheet_frame_selector/playback/controller.py::cleanup_playback_resources`.
- Aspectos no verificados en runtime: detalle exacto del `ReferenceError` al cargar otro archivo; aun si no se reproduce, debe confirmarse que `load_pre` limpia recursos.

### B5 - `SPRITESHEET_OT_visual_selector_open.execute()` devuelve `FINISHED` sin abrir nada cuando no es background

- Problema: una llamada directa a `execute()` podia reportar exito aunque no abriera el selector.
- Causa: el operador solo cancelaba en background y fuera de background retornaba `FINISHED` sin usar `invoke`.
- Impacto: comportamiento enganoso para scripts y rutas no-UI.
- Solucion propuesta por la auditoria: devolver `CANCELLED` con mensaje.
- Archivos/funciones afectados: `spritesheet_frame_selector/operators/visual_selector.py::SPRITESHEET_OT_visual_selector_open.execute`.
- Aspectos no verificados en runtime: confirmar desde Blender que la llamada directa no reporta exito falso.

## Interpretacion Del Plan

- Decision: validar exactamente la implementacion existente, sin ampliar alcance a M3, M6, M9, M10, B6, B7 ni B10.
- Argumento: el plan rector exige que C1/C2 queden validados antes de tocar los hitos 2/3. Saltar directo al siguiente fix mezclaria defectos de lifecycle con mejoras de selector/playback.
- Riesgos: la validacion GUI puede revelar problemas de input que no aparecen en tests unitarios; si ocurre, el hito 1 vuelve a `correcciones requeridas` y no se crea plan de hito 2/3.
- Dependencias con otros hallazgos: M6 depende de eventos de rueda, pero no se valida scroll aqui; solo que rueda fuera del panel pasa a Blender. B7 depende de clicks en celdas, pero no se valida undo aqui; solo que las acciones actuales siguen funcionando.

## Alcance De Validacion

- Incluir:
  - Repetir validaciones automaticas basicas sobre el worktree actual.
  - Validar apertura del selector desde UI en un `VIEW_3D`.
  - Validar navegacion fuera del panel con rueda, `MIDDLEMOUSE` y atajos con modificadores.
  - Validar que clicks dentro del panel siguen ejecutando acciones del selector.
  - Validar que cambiar workspace/clip activo con selector abierto cancela y limpia la sesion.
  - Validar que cargar otro `.blend` con selector abierto dispara cleanup por `load_pre`.
  - Validar que registrar/desregistrar/reactivar addon no duplica el handler `load_pre`.
  - Validar que llamada directa a `execute()` retorna `CANCELLED` con reporte comprensible.
- Excluir:
  - Implementar scroll/paginacion del selector (M6).
  - Corregir undo de clicks de celdas (B7).
  - Corregir thumbnails obsoletos (M9).
  - Perfilar `gpu.texture.from_image` (M10).
  - Optimizar `_tag_redraw` del playback (M3).
  - Barrido general de `except Exception` (B6 restante).
- Archivos esperados:
  - No se esperan cambios de codigo si la validacion pasa.
  - Si falla, los archivos probables son `spritesheet_frame_selector/operators/visual_selector.py`, `spritesheet_frame_selector/ui/visual_selector.py` y `spritesheet_frame_selector/registration.py`.

## Procedimiento De Validacion

### V1 - Validaciones Automaticas

Ejecutar:

```bash
python3 -m compileall spritesheet_frame_selector
python3 -m unittest discover -s tests
rg -n "PASS_THROUGH|load_pre|_cleanup_runtime_sessions_on_load|Visual selector must be opened|cleanup_playback_resources\\(\\)|cleanup_visual_selector_resources\\(\\)" spritesheet_frame_selector/operators/visual_selector.py spritesheet_frame_selector/ui/visual_selector.py spritesheet_frame_selector/registration.py
```

Criterio de aceptacion:

- `compileall` pasa.
- `unittest` pasa.
- `rg` confirma `PASS_THROUGH`, handler `load_pre`, cleanup de playback/selector y `execute()` sin exito falso.

Resultado:

- Pasado: `python3 -m compileall spritesheet_frame_selector`.
- Pasado: `python3 -m unittest discover -s tests` con 65 tests.
- Pasado: `rg` confirmo `{"RUNNING_MODAL", "PASS_THROUGH"}`, `load_pre`, `_cleanup_runtime_sessions_on_load`, cleanup de playback/selector y mensaje de `execute()`.
- Nota de entorno: Blender background dentro del sandbox crashea antes de ejecutar Python con exit code 139; las validaciones Blender se ejecutaron fuera del sandbox con aprobacion.

### V2 - Preparacion Blender GUI

Preparar una escena con:

- un workspace activo;
- un clip activo con previews existentes;
- selector visual abrible desde un `VIEW_3D`;
- al menos dos workspaces o dos clips para poder cambiar contexto mientras el selector esta abierto.

Criterio de aceptacion:

- el selector abre desde UI;
- no aparecen errores inmediatos en consola;
- el panel del selector queda visible dentro del `VIEW_3D`.

Resultado:

- Parcial: Blender GUI abrio con el selector visible sobre `VIEW_3D` usando escena temporal de validacion.
- Pasado por validacion del usuario: el selector abre y funciona en `VIEW_3D`.

### V3 - C1: Eventos Fuera Y Dentro Del Panel

Pasos:

1. Abrir el selector.
2. Usar rueda y `MIDDLEMOUSE` fuera del panel.
3. Usar un atajo con modificador fuera del panel.
4. Hacer clicks dentro del panel sobre botones y celdas.
5. Confirmar que `ESC` cierra el selector.

Criterio de aceptacion:

- fuera del panel, Blender recibe navegacion y no parece congelado;
- dentro del panel, las acciones del selector siguen funcionando;
- los atajos del selector sin modificador siguen funcionando cuando corresponde;
- `ESC` cierra y no queda overlay fantasma.

Resultado:

- Fallo detectado en primer intento GUI: devolver solo `PASS_THROUGH` hacia que el overlay desapareciera tras un evento fuera del panel. Se corrigio la implementacion para devolver `{"RUNNING_MODAL", "PASS_THROUGH"}`.
- Pasado despues de la correccion en Blender background: con sesion simulada, `MIDDLEMOUSE`, rueda, atajos con modificador y click fuera del panel devuelven `{"RUNNING_MODAL", "PASS_THROUGH"}`; click dentro del panel devuelve `RUNNING_MODAL`.
- Pasado/aceptado por validacion del usuario: el selector funciona y las acciones dentro del selector responden; acciones/clicks fuera del selector no operan mientras el selector esta abierto y el usuario lo considera comportamiento correcto.

### V4 - C1: Sesion Incoherente

Pasos:

1. Abrir el selector sobre workspace/clip A.
2. Cambiar el workspace o clip activo desde la UI/panel sin cerrar manualmente el selector.
3. Generar un evento de mouse/teclado.

Criterio de aceptacion:

- el selector se cancela y limpia automaticamente;
- no queda modal invisible consumiendo eventos;
- Blender vuelve a recibir eventos normalmente.

Resultado:

- Parcial pasado en Blender background: con sesion simulada, un workspace/clip activo incoherente devuelve `CANCELLED`, ejecuta `close()` y limpia la sesion global.
- Aceptado por validacion del usuario: desde la GUI no se puede cambiar workspace o clip con el selector abierto, y el usuario considera correcto ese comportamiento. La cobertura de sesion incoherente queda en la validacion background ya pasada.

### V5 - C2: `load_pre` Y Recursos

Pasos:

1. Abrir selector y, si es posible, iniciar playback.
2. Cargar otro `.blend` o disparar el flujo de carga que ejecute handlers `load_pre`.
3. Revisar que no queden overlay, playback, timers ni errores repetidos en consola.

Criterio de aceptacion:

- `cleanup_visual_selector_resources()` y `cleanup_playback_resources()` quedan cubiertos por `load_pre`;
- no hay overlay fantasma;
- no hay spam de `ReferenceError`;
- el addon sigue usable tras cargar el archivo.

Resultado:

- Parcial pasado en Blender background: `register()` instala un handler persistente `load_pre` que cubre cleanup de selector/playback; `VisualSelectorSession.draw()` limpia la sesion ante `ReferenceError`.
- Pendiente: cargar otro `.blend` con selector abierto en Blender GUI y confirmar ausencia de overlay fantasma, timers vivos y spam de consola. Procedimiento recomendado: crear o abrir un `.blend` temporal de prueba, abrir el selector, usar `File > Open...` o `File > New` sin cerrar manualmente el selector y confirmar que el nuevo archivo no conserva overlay/timer/errores del selector anterior.

### V6 - C2: Registro/Desregistro

Pasos:

1. Desactivar/reactivar el addon o ejecutar `unregister()`/`register()` en Blender.
2. Inspeccionar `bpy.app.handlers.load_pre`.
3. Repetir el ciclo.

Criterio de aceptacion:

- `_cleanup_runtime_sessions_on_load` aparece como maximo una vez en `bpy.app.handlers.load_pre`;
- `unregister()` lo remueve;
- `register()` lo vuelve a agregar;
- no se rompen clases ni propiedades del addon.

Resultado:

- Pasado en Blender background fuera del sandbox: `register()` agrega `_cleanup_runtime_sessions_on_load` una vez; una segunda llamada a `register()` no duplica el handler; `unregister()` lo remueve.

### V7 - B5: Llamada Directa A `execute()`

Pasos:

1. Desde Blender Python, instanciar o invocar el operador por ruta directa que use `execute()` sin contexto de `invoke`.
2. Observar resultado y reporte.

Criterio de aceptacion:

- retorna `CANCELLED`;
- reporta que el selector debe abrirse desde contexto `VIEW_3D`/`invoke`;
- no se crea sesion de selector invisible.

Resultado:

- Pasado en Blender background fuera del sandbox: `bpy.ops.spritesheet.visual_selector_open()` retorno `CANCELLED` y reporto `Visual selector must be opened from a 3D Viewport invoke context`.

## Validaciones Ejecutadas En Esta Corrida

- `python3 -m compileall spritesheet_frame_selector` - pasado.
- `python3 -m unittest discover -s tests` - pasado, 65 tests.
- `rg` de contrato `RUNNING_MODAL.*PASS_THROUGH|PASS_THROUGH|load_pre|_cleanup_runtime_sessions_on_load|Visual selector must be opened` - pasado.
- Blender background sandbox - fallido por entorno antes de Python, exit code 139.
- Blender background fuera del sandbox - pasado para V6/V7 con marcador `SFS_6A_HITO1_BACKGROUND_OK`.
- Blender background fuera del sandbox - pasado para logica C1 con marcador `SFS_6A_HITO1_EVENT_LOGIC_OK`.
- Blender background fuera del sandbox - pasado para C2 `ReferenceError` con marcador `SFS_6A_HITO1_DRAW_REFERENCEERROR_OK`.
- Blender GUI - parcial: V2 pasado por usuario; V3 pasado/aceptado por usuario con acciones dentro del selector funcionando y clicks fuera bloqueados mientras el selector esta abierto; V4 aceptado por usuario porque la GUI no permite cambiar workspace/clip con el selector abierto y la cobertura de sesion incoherente ya paso en background; V5 sigue pendiente.
- Bug runtime nuevo encontrado durante la validacion: cuando los thumbnails superan la capacidad de la ventana quedan ocultos. Este bug corresponde a M6 de `docs/technical-audit.md` y se planifica en `docs/plans/reinicio-v2-fase-6a-hito3-selector-scroll.md`.

## Validaciones Pendientes

- V5: cargar otro `.blend` con selector abierto y confirmar ausencia de overlay fantasma, timers vivos o spam de consola.

## Resultado Esperado

Si todas las validaciones pasan:

- actualizar `docs/plans/reinicio-v2-fase-6a-selector-modal-lifecycle.md` a `Estado De Ejecucion: validado`;
- actualizar el ledger de `docs/plans/reinicio-v2-fase-6-correcciones-auditoria-tecnica.md` para C1, C2 y B5 como `corregido`;
- actualizar PCS para habilitar el siguiente plan de Fase 6a hito 2;
- no cerrar ni archivar planes sin instruccion explicita.

Si alguna validacion falla:

- mantener `docs/plans/reinicio-v2-fase-6a-selector-modal-lifecycle.md` como activo;
- marcar `Estado De Ejecucion: correcciones requeridas`;
- registrar la falla concreta y el proximo fix minimo;
- no crear ni ejecutar hito 2/3.

## Proximo Paso Recomendado

Ejecutar las validaciones GUI pendientes V2-V5. No marcar el hito 1 como `validado` ni crear hito 2/3 hasta completar esas pruebas o registrar correcciones requeridas.
