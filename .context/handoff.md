# Handoff

Ultima actualizacion: 2026-07-05

Hay handoff activo para continuar la planificacion del reinicio V2.

## Situacion

El usuario aprobo guardar un master plan para reiniciar `spritesheet-blender` como addon V2 mantenible, distribuible y extensible. El master plan aprobado vive en `docs/plans/reinicio-v2-master-plan.md`.

Este master plan no debe ejecutarse como plan monolitico. Cada fase o subfase que se beneficie de precision debe tener un plan especifico antes de ejecutarse. No implementar codigo ni limpiar archivos desde el master plan directamente.

La Fase 1 fue ejecutada, validada y archivada en `docs/archive/reinicio-v2-fase-1-preservacion.md`. El estado trackeado previo quedo preservado por Git en la rama `archive/generated-addon-v1` y el tag anotado `archive/generated-addon-v1-2026-07-03`.

La Fase 2 fue ejecutada, validada y archivada en `docs/archive/reinicio-v2-fase-2-documentacion-base.md`. La documentacion operativa V2 vigente quedo separada en:

- `docs/specs/product_requirements.md`
- `docs/specs/mvp_v2.md`
- `docs/architecture/addon_architecture.md`
- `docs/design/visual_selector_strategy.md`
- `docs/specs/validation_plan.md`

El MVP historico original fue preservado en `docs/archive/mvp-original.md`. `docs/specs/mvp.md` quedo como puntero historico/no operativo.

La Fase 3 fue ejecutada, validada y archivada en `docs/archive/reinicio-v2-fase-3-limpieza-arbol-activo.md`. El addon V1, tests legacy, scratch y residuos locales fueron retirados del arbol activo. Las metas V1 de docs/source/goals.md y docs/source/goals.proposed.md fueron archivadas en `docs/archive/source-goals-v1.md` y `docs/archive/source-goals-proposed-v1.md`.

La Fase 4 fue ejecutada, validada y archivada en `docs/archive/reinicio-v2-fase-4-scaffold-addon-v2.md`. Existe scaffold V2 minimo en `spritesheet_frame_selector/` con manifest, registro centralizado, preferencias, propiedad minima de escena y panel minimo. Validaron `compileall`, import/register/unregister con mock minimo de `bpy`, y Blender background real con Blender 5.1.1. Queda pendiente solo validacion manual GUI del panel.

El plan rector de Fase 5 fue aprobado y archivado en `docs/archive/reinicio-v2-fase-5-vertical-slices.md`. La Fase 5a fue ejecutada, validada y archivada en `docs/archive/reinicio-v2-fase-5a-data-model-persistencia.md`: existe modelo persistente V2 con clips, frames, export settings y estado de escena; Blender background valido persistencia save/reopen con `SFS_5A_PERSISTENCE_OK`.

La Fase 5b fue ejecutada, validada y archivada en `docs/archive/reinicio-v2-fase-5b-gestion-clips.md`: existen operadores Add/Remove/Duplicate/Select, UIList nativa, panel de edicion del clip activo, helpers puros de estado y tests unitarios. Blender background valido gestion de clips y persistencia save/reopen con `SFS_5B_CLIPS_OK`. Durante cierre de Blender aparecio un traceback de un addon externo local `Procedural-Stadiums-main`; no pertenece a este repo y no impidio la validacion.

La Fase 5c fue ejecutada, validada y archivada en `docs/archive/reinicio-v2-fase-5c-preview-cache.md`: existen operadores Generate/Refresh/Clear Preview, helpers de cache/paths/frame sync, backend de thumbnails y UI de estado. Blender background valido generacion, refresh conservando seleccion, clear cache conservando frames/seleccion y persistencia con `SFS_5C_PREVIEW_CACHE_OK`. OpenGL es la ruta primaria, pero Blender background usa fallback de thumbnail por render still porque `bpy.ops.render.opengl` no funciona sin contexto OpenGL. Durante cierre de Blender se repitio el traceback del addon externo local `Procedural-Stadiums-main`; no pertenece a este repo.

El usuario confirmo que workspace es raiz de dominio en V2. Se registro `DEC-0006` y se creo el plan aprobado, luego validado y archivado, `docs/archive/reinicio-v2-fase-5c1-auditoria-decisiones-workspace-root.md`. Las fases 5a/5b/5c quedan sujetas a revision arquitectonica antes de continuar. La Fase 5d queda detenida hasta decidir si se refactoriza lo actual o se vuelve al scaffold limpio de Fase 4.

W1 de la Fase 5c.1 fue ejecutada y validada. El entregable vive en `docs/specs/workspace_root_decisions.md` y clasifica decisiones V1 como incorporar, descartar, diferir o investigar. Las conclusiones principales son: workspace debe ser raiz persistente, export settings deben vivir bajo workspace, camera/default collections deben resolverse por workspace con override por clip, la visibilidad efectiva por collections es requisito fuerte, y el preview/render nativo debe investigarse antes de reintroducir soluciones tipo WorldSwap.

W2 de la Fase 5c.1 fue ejecutada y validada. Los documentos V2 ahora declaran workspace-root como contrato operativo en `docs/specs/mvp_v2.md`, `docs/architecture/addon_architecture.md`, `docs/specs/validation_plan.md` y `docs/design/visual_selector_strategy.md`. Se registraron `DEC-0007` y `DEC-0008`.

W3 de la Fase 5c.1 fue ejecutada y validada. La evaluacion vive en `docs/specs/workspace_root_refactor_evaluation.md`. Decision registrada como `DEC-0009`: rehacer las slices 5a/5b/5c desde el scaffold limpio de Fase 4, reaprovechando solo helpers puros y patrones validados cuando encajen con workspace-root.

W4 de la Fase 5c.1 fue ejecutada y validada. Se creo el nuevo rector, luego archivado, `docs/archive/reinicio-v2-fase-5-workspace-root-vertical-slices.md` y el primer plan ejecutable, luego validado y archivado, `docs/archive/reinicio-v2-fase-5a-workspace-data-model-persistencia.md`. Los planes originales 5a/5b/5c fueron marcados como reemplazados por workspace-root y se conservan como historial validado en `docs/archive/`.

La Fase 5a workspace-root fue ejecutada y validada. El addon registra un modelo persistente con `Scene.spritesheet_state.workspaces`, `SpriteSheetWorkspace`, defaults de camera/collections, clips, frames y export settings por workspace. Las validaciones automáticas pasaron y Blender background valido save/reopen con `SFS_5A_WORKSPACE_OK` fuera del sandbox porque el sandbox crasheaba antes de Python en inicializacion Metal.

La Fase 5b workspace-root fue ejecutada, validada y archivada en `docs/archive/reinicio-v2-fase-5b-workspace-clip-management.md`: existen operadores y UI nativa para crear, eliminar, duplicar, seleccionar y reordenar workspaces/clips. Defaults de workspace y overrides de clip existen y persisten. Las validaciones automaticas pasaron y Blender background valido save/reopen con `SFS_5B_WORKSPACE_CLIPS_OK`.

La Fase 5c workspace-root fue ejecutada, validada y archivada en `docs/archive/reinicio-v2-fase-5c-workspace-preview-cache.md`: previews cacheados operan sobre workspace activo y clip activo, resuelven camera/collections efectivas, usan cache por workspace id + clip id + cache key y preservan seleccion durante refresh/clear. Blender background valido generate/refresh/clear, overrides, separacion entre workspaces y persistencia save/reopen con `SFS_5C_WORKSPACE_PREVIEW_OK`.

La Fase 5d workspace-root fue ejecutada, validada y archivada en `docs/archive/reinicio-v2-fase-5d-visual-selector-minimo.md`: existe selector visual minimo como dialogo nativo con grilla/contact sheet de thumbnails existentes, toggle por frame y acciones globales de seleccion. Blender background valido operadores, persistencia de seleccion y lifecycle con `SFS_5D_VISUAL_SELECTOR_OK`. Queda pendiente validacion manual GUI de clicks reales sobre el dialogo visual.

La Fase 5e workspace-root fue ejecutada, validada y archivada en `docs/archive/reinicio-v2-fase-5e-playback-preview.md`: existe playback preview runtime sobre previews cacheados existentes y frames seleccionados, con operadores Play/Pause/Stop, controlador con timer unico, estado visible en selector/panel y cleanup en `unregister()`. Validaron `compileall`, unit tests, busqueda de contrato legacy y Blender background con `SFS_5E_PLAYBACK_OK`.

El usuario reviso manualmente selector/playback y detecto que los thumbnails son demasiado pequenos y que el playback no muestra claramente el resultado animado. Se ejecuto el spike archivado en `docs/archive/reinicio-v2-fase-5e1-spike-selector-modal-preview-modes.md` y el resultado vive en `docs/specs/selector_modal_preview_modes_spike.md`. Decision registrada como `DEC-0010`: antes de render final se debe crear una fase correctiva para selector/playback UX con superficie modal/custom, visor grande, `selector_mode` persistente y preview modes persistentes.

## Proxima Accion Recomendada

`docs/archive/reinicio-v2-fase-5e1-selector-playback-ux.md` fue aprobado por instruccion explicita del usuario, implementado, validado y archivado. El plan incorpora la decision del usuario: `preview_size` minimo 32, default 64, preset 128 y maximo 256.

Estado actual de 5e1: validado por revision manual del usuario. Quedan ajustes menores de UI, pero no son bloqueantes para avanzar. Compile y unit tests pasaron. Blender background dentro del sandbox crashea antes de ejecutar Python y la ejecucion fuera del sandbox fue rechazada por politica del entorno actual.

Correccion aplicada tras validacion manual fallida: el selector modal dejo de pintar pantalla completa, ahora usa un panel flotante con margenes seguros dentro del View3D, limita la grilla a las celdas visibles, compacta controles y preserva aspect ratio del visor grande.

Segunda correccion UX aplicada: el selector modal usa todo el espacio util disponible del View3D, `preview_size` paso a la seccion `Selector`, playback se retiro del panel principal y queda en el selector modal, `Edit`/`Play` se movio desde `Workspace` hacia `Selector`, y el preview mode de workspace/clip quedo en `Preview Cache`.

Tercera correccion UX aplicada: el selector modal ahora detecta el panel lateral `N` visible y reserva ese ancho para que botones/controles no queden tapados. En Blender, el draw handler `SpaceView3D` no es una ventana global sobre toda la aplicacion y no puede garantizar dibujo por encima de regiones UI laterales.

Cuarta correccion UX aplicada: el modo de preview ya no tiene default por workspace ni override por clip. `clip.preview_mode` es la unica fuente de verdad porque preview generation es bajo demanda por clip. `Preview Cache` queda para elegir modo y ejecutar Generate/Refresh/Clear; `Preview Status` muestra estado compacto separado.

Pendiente operativo: `compileall` genero `__pycache__`; la limpieza automatica fue rechazada por politica del entorno y no se intento una via alternativa.

Plan 5f fue aprobado por instruccion explicita del usuario, implementado y archivado en `docs/archive/reinicio-v2-fase-5f-render-final-workspace-aware.md`.

Estado actual de 5f: funcionalidad base validada por usuario. El flujo publico separado de render/export por frame fue reemplazado por una opcion integrada en 5g.

Cambios principales de 5f: render final por clip activo con camera/collections efectivas, `render_path` por frame, estado derivado de render por clip y backend `bpy.ops.render.render(write_still=True)`.

Nota vigente: ya no existe un boton/operador publico separado para render/export por frame. La validacion vigente ocurre desde 5g con `Export Individual Frames`.

Correcciones posteriores aplicadas a 5f el 2026-07-04: `Final Render` fue movido bajo `Export Settings`; `Export Settings` usa solo el selector nativo de carpeta destino; lista de clips muestra cantidad de frames seleccionados en vez del rango; clips nuevos sincronizan frames iniciales seleccionados por defecto; `Default Collections` se presenta como un unico `Default Collection`; preview/render reportan error si hay mas de un default collection legado sin override de clip; render final escribe PNGs directamente en `output_folder` y ya no expone clear cache. Compile y unit tests pasaron con 47 tests.

Decision de contrato export/JSON aplicada el 2026-07-04: no se permiten nombres duplicados de clips dentro de un mismo workspace. Si el usuario renombra un clip a un nombre ya existente, el addon agrega sufijo numerico incremental. Esto permite usar nombres visibles como keys del JSON multi-clip compartido por el usuario. Compile y unit tests pasaron con 48 tests.

Correccion de naming render final aplicada el 2026-07-04: los PNG de `Render Final Frames` usan indice de salida continuo, no el numero de frame original de Blender. Ejemplo: frames originales 3, 5 y 6 generan `*_frame_000001.png`, `*_frame_000002.png`, `*_frame_000003.png`. Compile y unit tests pasaron con 48 tests.

Plan 5g fue aprobado por instruccion explicita del usuario, implementado, validado y archivado en `docs/archive/reinicio-v2-fase-5g-export-spritesheet-json.md`.

Estado actual de 5g: export validado por el usuario en Blender, incluidas las correcciones UI/naming/atajos posteriores. Compile, unit tests y busqueda legacy pasaron. Blender background crashea antes de ejecutar Python con exit code 139 en este entorno.

Cambios principales de 5g: `Export Spritesheet` genera PNG final y JSON con el formato compartido por el usuario; composer aislado en `spritesheet_frame_selector/export/composer.py`; layout puro en `export/layout.py`; metadata JSON en `export/metadata.py`; operador `spritesheet.export_spritesheet`; UI en `Export Settings`; estado `last_export_note/png/json` en workspace.

Correccion aplicada tras validacion manual: se quito el boton/operador publico separado de render/export por frame. `Export Individual Frames` ahora vive como opcion en `Export Settings` y se ejecuta dentro de `Export Spritesheet`, guardando PNGs individuales en `<output_folder>/<sheet_name>_frames/` con numeracion global del orden exportado.

Correccion UI/naming/atajos posterior aplicada: filenames de preview/render/export individual usan 3 digitos (`001`), `Preview Cache` se renombro a `Preview`, `Preview Size` paso a menu desplegable en Preview, Preview queda con solo `Generate Preview` y `Clear Cache`, Selector del panel ya no muestra Edit/Play, Export Settings quedo en orden Sheet/Folder/W-H-Columns/Sheet Size/Export Individual Frames/Export Spritesheet, las filas de workspaces/clips usan nombres editables nativos, y el selector visual soporta `Space`, `Tab` y `Shift + Left`.

Plan propuesto anterior de validacion/distribucion movido a Fase 7: `docs/plans/reinicio-v2-fase-7-validacion-distribucion.md`.

Plan rector aprobado para correcciones de auditoria tecnica: `docs/plans/reinicio-v2-fase-6-correcciones-auditoria-tecnica.md`.

La Fase 6 usa `docs/technical-audit.md` como fuente principal y no debe resumir ni acotar los hallazgos C/A/M/B. La Fase 7 queda diferida hasta que Fase 6 corrija o clasifique todos los hallazgos y valide los puntos runtime aplicables.

Correccion al plan rector Fase 6: el plan no debe copiar toda la auditoria. Debe gobernar orden, dependencias y criterios. Cada subplan ejecutable debe ser explicito y autosuficiente: para cada hallazgo que cubra, debe incorporar problema, causa, impacto, solucion propuesta por auditoria, archivos/funciones afectados, interpretacion del subplan y validacion. No basta con decir "ver auditoria".

El usuario confirmo D1 y D2 al aprobar el plan: para MVP se elimina el subsistema de render cache final y se prohiben frames negativos agregando `min=0` a `frame_start`/`frame_end`.

Subplan `docs/plans/reinicio-v2-fase-6a-selector-modal-lifecycle.md` implementado por instruccion explicita del usuario. Cubre solo el hito 1 bloqueante de Fase 6a: C1, C2 y B5. No implementa M3, M6, M9, M10, B6 restante, B7 ni B10.

Cambios implementados: modal del selector devuelve `PASS_THROUGH` para eventos no manejados; clicks fuera del panel y navegacion/modificadores pasan a Blender; cada evento cancela y limpia si workspace/clip activo ya no coincide; `draw()` limpia ante `ReferenceError`; `registration.py` registra/desregistra un handler persistente `load_pre` que limpia playback y selector; `execute()` del operador visual devuelve `CANCELLED` con reporte en vez de exito falso.

Validaciones automaticas ejecutadas: `python3 -m compileall spritesheet_frame_selector`, `python3 -m unittest discover -s tests` (65 tests), y busquedas `rg` de `PASS_THROUGH`, `load_pre`, cleanup y `execute()`.

Proximo paso: validar en Blender `docs/plans/reinicio-v2-fase-6a-selector-modal-lifecycle.md`. Debe verificarse navegacion fuera del panel, acciones dentro del panel, cambio de workspace/clip con selector abierto, carga de otro `.blend` y reactivacion del addon sin duplicar `load_pre`. No avanzar a hitos 2/3 de Fase 6a hasta validar este hito 1 o registrar correcciones requeridas.

Plan de validacion `docs/plans/reinicio-v2-fase-6a-validacion-hito1-selector-modal-lifecycle.md` aprobado/ejecutado por instruccion explicita del usuario. No reemplaza el hito 1 implementado ni habilita hitos 2/3.

Resultados: V1 paso (`compileall`, 65 tests, `rg` de contrato). Blender background dentro del sandbox crashea antes de Python con exit code 139; fuera del sandbox pasaron V6/V7 (`SFS_6A_HITO1_BACKGROUND_OK`), logica C1 con sesion simulada (`SFS_6A_HITO1_EVENT_LOGIC_OK`) y cleanup C2 ante `ReferenceError` (`SFS_6A_HITO1_DRAW_REFERENCEERROR_OK`). La prueba GUI inicial detecto un bug real: devolver solo `PASS_THROUGH` cerraba/desactivaba el overlay tras evento fuera del panel. Se corrigio a `{"RUNNING_MODAL", "PASS_THROUGH"}` y se repitieron validaciones automaticas/background con exito.

Pendiente: V2-V5 requieren Blender GUI real estable: abrir selector en `VIEW_3D`, navegar fuera del panel, accionar dentro del panel, cambiar workspace/clip con selector abierto y cargar otro `.blend` con selector abierto. En el segundo intento GUI el selector abrio con la correccion, pero la ventana quedo blanca/inestable al manipular el splash; no marcar hito 1 como `validado` ni crear hito 2/3 hasta completar esas pruebas o registrar correcciones requeridas.

Plan 6b0 `docs/plans/reinicio-v2-fase-6b0-preview-camera-viewport.md` fue creado, implementado y validado por el usuario para corregir un bug runtime no contemplado explicitamente por `docs/technical-audit.md`: `Generate Preview` en `SOLID`/`MATERIAL` generaba thumbnails desde la vista libre del viewport si el usuario no habia entrado manualmente a Camera View, haciendo que el objeto saliera muy pequeno.

Diagnostico confirmado: `bpy.ops.render.opengl(write_still=True, view_context=True)` usa el viewport 3D actual. La correccion mantiene `view_context=True` para preservar shading `SOLID`/`MATERIAL`, pero fuerza temporalmente `region_3d.view_perspective = "CAMERA"` durante el render OpenGL y restaura perspectiva, shading y overlays con `try/finally`.

Validaciones de 6b0: `python3 -m compileall spritesheet_frame_selector` paso; `python3 -m unittest discover -s tests` paso con 66 tests; validacion Blender GUI confirmada por el usuario.

Pendiente operativo inmediato: retomar V2-V5 del plan `docs/plans/reinicio-v2-fase-6a-validacion-hito1-selector-modal-lifecycle.md`. No crear hito 2/3 hasta completar esas pruebas o registrar correcciones requeridas.

Actualizacion de validacion GUI reportada por el usuario: V2 funciona; en V3 el selector funciona y el usuario considera correcto que acciones/clicks fuera del selector no operen mientras el selector esta abierto; en V4 no se puede cambiar workspace o clip con selector abierto y el usuario lo considera correcto. V5 sigue pendiente. Para V5, abrir el selector y luego usar `File > Open...` o `File > New` para cargar otro archivo/escena sin cerrar manualmente el selector; confirmar que no quedan overlay fantasma, timers/playback vivos ni spam de consola.

Bug nuevo durante validacion: si los thumbnails superan la capacidad visible, quedan ocultos e inaccesibles. Esto coincide con M6 de `docs/technical-audit.md`. El usuario pidio implementar `docs/plans/reinicio-v2-fase-6a-hito3-selector-scroll.md`; el plan fue aprobado por instruccion del usuario e implementado.

Implementacion M6: `VisualSelectorSession` guarda `grid_offset`, `grid_columns` y `grid_max_visible`; el grid dibuja una ventana desplazable; `FrameCell.index` apunta al indice real en `clip.frames`; rueda y trackpad dentro del panel desplazan una fila; rueda/trackpad fuera del panel conservan `RUNNING_MODAL + PASS_THROUGH`; el status muestra `Showing A-B / N frames`. Validaciones automaticas pasaron: `python3 -m compileall spritesheet_frame_selector` y `python3 -m unittest discover -s tests` con 70 tests.

Correccion posterior: el primer intento no funcionaba con trackpad porque solo manejaba `WHEELUPMOUSE/WHEELDOWNMOUSE` con `value == "PRESS"` y dejaba `TRACKPADPAN` como passthrough. Se corrigio `TRACKPADPAN` usando `mouse_y - mouse_prev_y`.

Pendiente operativo inmediato: validar M6 en Blender GUI con un clip mas largo que la grilla visible. Confirmar trackpad dentro del panel, click/toggle sobre frames inicialmente ocultos y trackpad/rueda fuera del panel pasando al viewport. Luego resolver V5 del plan `docs/plans/reinicio-v2-fase-6a-validacion-hito1-selector-modal-lifecycle.md`.
