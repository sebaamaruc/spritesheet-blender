# Auditoria De Decisiones V1 Para Workspace-Root

Estado: vigente como entrada de rediseno
Autoridad: `docs/plans/reinicio-v2-fase-5c1-auditoria-decisiones-workspace-root.md`
Fecha: 2026-07-03

## Proposito

Este documento ejecuta W1 del plan `docs/plans/reinicio-v2-fase-5c1-auditoria-decisiones-workspace-root.md`.

El objetivo es extraer decisiones de V1 que no estaban completamente trasladadas a los documentos V2, clasificarlas y dejar una base concreta para actualizar `docs/specs/mvp_v2.md`, `docs/architecture/addon_architecture.md`, `docs/specs/validation_plan.md` y los planes de Fase 5.

V1 se usa solo como evidencia de producto y riesgos. No es base de codigo para V2.

## Fuentes Revisadas

- `archive/generated-addon-v1:spritesheet_frame_selector/properties.py`
- `archive/generated-addon-v1:spritesheet_frame_selector/utils.py`
- `archive/generated-addon-v1:spritesheet_frame_selector/operators.py`
- `archive/generated-addon-v1:spritesheet_frame_selector/panels.py`
- `archive/generated-addon-v1:spritesheet_frame_selector/exporter.py`
- `archive/generated-addon-v1:spritesheet_frame_selector/preview_generator.py`
- `archive/generated-addon-v1:tests/test_visibility.py`
- `archive/generated-addon-v1:.context/decisions.md`
- `docs/archive/audit_report.md`
- `.context/decisions.md`
- `docs/specs/mvp_v2.md`
- `docs/architecture/addon_architecture.md`

## Resumen Ejecutivo

La V2 actual 5a/5b/5c fue construida con `Scene.spritesheet_state.clips` como raiz operativa. Esa estructura contradice `DEC-0006`: workspace es raiz de dominio.

La auditoria confirma que workspace en V1 no era un detalle de UI. Funcionaba como contenedor de contexto de exportacion, defaults de camara, defaults de colecciones, lista de clips, orden de clips y settings de salida. Por tanto, el rediseno documental debe mover el contrato V2 a:

```text
Scene.spritesheet_state.workspaces -> active_workspace -> clips -> frames
```

Las decisiones mas importantes a incorporar son:

- workspace como raiz persistente;
- export settings por workspace;
- default camera y default collections en workspace, con override por clip;
- visibilidad efectiva por collections para preview/render/export;
- inclusion/exclusion de clips para export;
- orden manual de clips;
- duplicacion de workspace redisenada, sin copiar caches como estado valido;
- JSON multi-clip secuencial basado en orden exportable;
- validaciones estrictas de camera, collections, output, nombres y dimensiones;
- investigacion de render/preview nativo antes de reintroducir WorldSwap o Material Preview simulado.

## Tabla De Decisiones

| ID | Decision V1 / Tema | Evidencia V1 | Estado Para V2 | Razon | Impacto En V2 | Seguimiento |
|---|---|---|---|---|---|---|
| W1-01 | Workspace como raiz de dominio | `SpriteSheetWorkspace` contiene `default_camera`, `default_collections`, `clips`, `active_clip_index`, `export_settings`; UI y operadores gestionan workspace activo. | incorporar | Confirmado por el usuario como decision central. La raiz directa `Scene.clips` no escala para multiples contextos de export. | Redisenar modelo, helpers, UI, operadores, tests y docs. | W2 docs, W3 refactor vs reinicio. |
| W1-02 | Estado raiz unico en Scene | V1 tenia propiedades legacy directas y propiedades workspace separadas. | incorporar con cambio | La V2 debe evitar compatibilidad legacy interna innecesaria. | Usar una sola propiedad `Scene.spritesheet_state` con `workspaces` y `active_workspace_index`. | W2 arquitectura. |
| W1-03 | Export settings como fuente unica, pero bajo workspace | `DEC-0002` y `SpriteSheetWorkspace.export_settings`. | incorporar | Evita duplicacion de output en workspace raiz y settings. | `SpriteSheetExportSettings` debe vivir dentro de cada workspace. | W2 docs y nuevo 5a workspace-root. |
| W1-04 | Selector de workspace con UIList nativa `template_list rows=1` | `DEC-0003`, `SPRITESHEET_UL_workspace_list`, panel workspace. | investigar | Fue una solucion estable en V1, pero debe compararse con opciones nativas actuales antes de fijarla como contrato. | UI puede conservar `template_list` si sigue siendo la opcion mas robusta. | W2/W4: decidir UI de workspace management. |
| W1-05 | Default camera por workspace | `Workspace.default_camera`; `resolve_clip_camera()` prioriza override de clip, luego default de workspace. | incorporar | El usuario confirmo que un workspace puede necesitar camara default para muchos clips. | Modelo necesita camara default workspace y override opcional por clip. | W2 docs, validaciones Blender. |
| W1-06 | Override de camera por clip | `clip.use_camera_override`, `clip.camera`, `resolve_clip_camera()`. | incorporar | Casos reales requieren clips con camara distinta a la default. | UI debe mostrar override explicito y resolver camara efectiva sin fallback ambiguo. | W2 docs, nuevo 5b/5c. |
| W1-07 | Default collections por workspace | `Workspace.default_collections`; UI `Default Collections`; `resolve_clip_collections()`. | incorporar | El usuario marco visibilidad por collections como muy importante. | Workspace define colecciones visibles por defecto para preview/render/export. | W2 arquitectura y validation plan. |
| W1-08 | Override de collections por clip | `clip.use_collection_override`, `clip.included_collections`. | incorporar | Hay clips que necesitan collection distinta del workspace. | Clip debe poder reemplazar defaults de workspace sin mezclar estados. | W2 docs, operadores y paneles. |
| W1-09 | Visibilidad efectiva por collections | `apply_clip_visibility()` excluye layer collections no incluidas, incluye ancestros/descendientes y asegura camara visible; `test_visibility.py`. | incorporar | Es requisito fuerte: preview/render debe mostrar solo el conjunto de collections correcto. | Crear modulo dedicado de visibilidad con save/apply/restore y pruebas Blender. | W2 validation plan, futura fase render/preview workspace-aware. |
| W1-10 | Deteccion de collections borradas | `SpriteSheetIncludedCollection.collection_name` conserva nombre cuando pointer queda vacio. | incorporar | Blender puede dejar referencias nulas; el usuario necesita warnings accionables. | Cada item de collection debe guardar pointer y nombre ultimo conocido. | W2 modelo y tests. |
| W1-11 | Inclusion/exclusion de clips para export | `clip.include_in_export`; UI checkbox; export filtra clips incluidos. | incorporar | El usuario lo marco importante y es esencial para atlas multi-clip. | Clip debe tener `include_in_export`; decidir default. | W2 especificacion. |
| W1-12 | Default de `include_in_export` | V1 usaba `False`; audit report lo marco sorprendente. | investigar | Para UX puede ser mejor `True` en clips nuevos, pero requiere validar flujo de usuario. | Afecta expectativas de export y validaciones. | W2 decision explicita. |
| W1-13 | Orden manual de clips | Operador `move_clip`; export concatena en orden de lista. | incorporar | El usuario lo marco importante; JSON multi-clip depende del orden. | Operadores move up/down y metadata deben respetar orden visible. | W2/W4 subplan gestion workspace/clip. |
| W1-14 | Duplicacion de workspace | `duplicate_workspace` copia settings, collections, clips y frames; usuario indico que no funcionaba bien. | incorporar redisenada | Feature importante, pero V1 copiaba rutas de preview y podia clonar cache como valido. | Duplicar workspace debe copiar configuracion y seleccion, generar ids nuevos y marcar cache dirty. | W2 docs, nuevo subplan. |
| W1-15 | Duplicacion de clips dentro del workspace | `duplicate_clip` copia config y seleccion sin preview paths. | incorporar | Ya existe en V2 5b y sigue siendo util bajo workspace-root. | Adaptar helpers para coleccion de clips del workspace activo. | W3 evaluacion tecnica. |
| W1-16 | Preview segun visibilidad efectiva | `generate_clip_previews()` aplica `apply_clip_visibility()` y resuelve camara efectiva. | incorporar | Preview debe representar lo que luego se renderizara/exportara. | Preview cache debe incluir datos efectivos de workspace y clip en cache key. | W2/W4 plan preview workspace-aware. |
| W1-17 | Cache basado en nombre visible | V1 `get_cache_dir()` usa `clip.name`; audit report advierte colisiones. | descartar | V2 ya corrigio esto con ids/cache keys. Bajo workspace-root debe mantenerse la misma regla. | Usar `workspace.id`, `clip.id` y cache key, nunca solo nombre. | W2 arquitectura. |
| W1-18 | Clear cache borra frames | V1 `clear_clip_previews()` limpia `clip.frames`; V2 5c preserva frames/seleccion. | descartar | La seleccion es estado persistente, cache es derivado. | Clear cache debe limpiar rutas/cache, no seleccion ni frame list salvo resync explicito. | Mantener criterio V2. |
| W1-19 | Material Preview simulado con `WorldSwapContext` | V1 cambia world/engine y usa `BLENDER_EEVEE`; audit report detecta incompatibilidad Blender 5.x y leaks. | investigar antes de decidir | El usuario pidio buscar mejor solucion y probar si render nativo se puede usar. | No reintroducir WorldSwap sin prueba tecnica; preferir render nativo/viewport si satisface el caso. | Futura investigacion preview/render. |
| W1-20 | Render nativo para previews | V1 `preview_generator` usa `bpy.ops.render.render(write_still=True)` con engine segun shading. | investigar | Puede ser mas estable que simular material preview, pero debe medirse frente a OpenGL/viewport. | Necesita spike controlado con Blender 5.x. | Plan tecnico antes de preview/render final. |
| W1-21 | JSON multi-clip secuencial | `write_metadata_json()` genera `clips` con `start`, `end`, `count`, `fps` acumulados. | incorporar | El usuario lo marco importante y docs V2 ya exigen JSON simple para atlas. | Metadata debe usar IDs o estructura que evite sobrescritura por nombres duplicados. | W2 specs/export. |
| W1-22 | JSON por nombre de clip como key | V1 usa dict `metadata["clips"][clip_name]`; audit report detecta sobrescritura con nombres duplicados. | descartar | Riesgo confirmado. | Usar array ordenado o keys estables; validar nombres visibles duplicados si son parte del contrato. | W2 export contract. |
| W1-23 | Validaciones estrictas de export | `validate_export_settings()` revisa clips incluidos, seleccion, output, camera, collections, duplicados. | incorporar | El usuario lo marco importante; evita exports silenciosamente corruptos. | Mover validacion a core sin side effects y con ownership workspace-root. | W2 validation plan. |
| W1-24 | Validacion que crea directorios o hace IO desde draw | Audit report: `validate_export_settings()` antes creaba directorios durante draw. | descartar | UI no debe producir side effects. | Validacion pasiva solo inspecciona; operadores crean directorios al ejecutar export. | Mantener regla de arquitectura. |
| W1-25 | PNG sequence opcional | V1 exporta secuencia si `export_png_sequence`; usuario lo marco importante. | incorporar | Es util y ya esta en docs V2 como opcion apagada por defecto. | Settings siguen bajo workspace. | W2 specs. |
| W1-26 | Warnings de dimensiones 4096/8192 | Panel export V1 muestra warnings; usuario lo marco importante. | incorporar | Evita consumo excesivo de memoria/render. | Validacion debe calcular resolucion estimada por workspace/export. | W2 validation plan. |
| W1-27 | Playback loop por clip | V1 tiene `clip.playback_loop`; docs V2 dicen loop si no complica estabilidad. | diferir | No es requisito para resolver workspace-root y puede esperar a playback. | Mantenerlo fuera del nuevo 5a si no es necesario. | Futura fase playback. |
| W1-28 | Actions/armature awareness | No aparece como modelo formal en archivos V1 revisados; flujo usa frames de escena. | diferir | Puede ser feature futura, pero no debe bloquear workspace-root. | No agregar hasta que haya requerimiento claro. | Roadmap posterior. |
| W1-29 | Compatibilidad legacy `scene.spritesheet_clips` | V1 mantenia fallback legacy en `get_clip_context()`. | descartar | V2 es reinicio limpio; mantener legacy aumenta complejidad sin valor. | Sin fallback legacy interno. Migracion V1 no es objetivo del MVP. | W2 arquitectura. |
| W1-30 | Fallback automatico a `scene.camera` cuando hay workspace | V1 evita fallback a scene camera si hay workspace activo, salvo modo legacy. | incorporar | En workspace-root, usar escena como fallback puede ocultar configuraciones incompletas. | Si hay workspace activo, exigir default camera u override de clip cuando se renderiza/exporta. | W2 validation. |

## Decisiones Aceptadas Para Registrar En V2

Estas decisiones deben convertirse en contrato documental o nuevas entradas en `.context/decisions.md` durante W2:

1. Workspace es raiz persistente del dominio.
2. `Scene` expone una sola propiedad raiz: `spritesheet_state`.
3. `SpriteSheetSceneState` contiene `workspaces` y `active_workspace_index`.
4. `SpriteSheetWorkspace` contiene defaults, clips y settings de export.
5. `SpriteSheetClip` contiene overrides opcionales de camera y collections.
6. La visibilidad efectiva se resuelve por workspace + clip y se aplica a preview/render/export.
7. Los caches son derivados, identificados por ids/cache keys, no por nombres visibles.
8. Export multi-clip respeta inclusion y orden manual.
9. JSON multi-clip no debe sobrescribir clips con nombres duplicados.
10. Validaciones pasivas no crean directorios ni mutan filesystem.

## Decisiones Que Requieren Investigacion

### UI De Workspace Selector

V1 uso `template_list rows=1`, que fue estable. No hay evidencia suficiente para convertirlo en regla final sin comparar:

- `UIList rows=1`;
- panel compacto con lista normal;
- menu/dropdown con operadores;
- tabs/preset-like UI nativa si aplica.

Default de investigacion: mantener `UIList` nativa salvo que una alternativa reduzca complejidad sin perder estabilidad.

### Preview / Render Nativo

V1 intento aproximar Material Preview con `WorldSwapContext`, pero el audit report encontro incompatibilidad con Blender 5.x y riesgo de datablocks temporales. Antes de implementar la fase preview/render workspace-aware se debe probar:

- `bpy.ops.render.opengl` en contexto UI cuando exista;
- `bpy.ops.render.render(write_still=True)` con Workbench/EEVEE Next;
- fallback background controlado;
- comportamiento con camera y collection visibility efectiva;
- calidad visual suficiente para seleccion de frames.

No se debe reintroducir `WorldSwapContext` como solucion por defecto sin validar que Blender 5.x lo soporta limpiamente.

### Default De Inclusion En Export

V1 usaba `include_in_export=False` y el audit report lo marco como UX confusa. Opciones:

- `True` para clips nuevos, mejor para flujo rapido;
- `False`, mas seguro para atlas con muchos clips;
- heredar de preferencia del workspace.

Debe decidirse en W2 porque afecta UI, validacion y tests.

## Decisiones Descartadas De V1

- Doble modelo legacy/workspace en paralelo.
- Cache path basado en `clip.name`.
- JSON con nombres de clip como keys unicas sin validacion.
- Clear cache que borra seleccion persistente.
- Validaciones que crean directorios durante `draw`.
- Prints de produccion como mecanismo principal de error.
- Simular Material Preview modificando world/engine sin cleanup probado en Blender 5.x.

## Implicaciones Sobre La V2 Actual 5a/5b/5c

La implementacion actual ya aporta piezas reutilizables:

- helpers puros de frame math;
- patron de ids estables;
- cache key no basada en nombre;
- clear cache que preserva seleccion;
- register/unregister defensivo;
- tests unitarios y validaciones Blender background.

Pero la arquitectura de dominio queda desplazada porque:

- los clips cuelgan directamente de `Scene.spritesheet_state`;
- export settings cuelgan directamente de state, no de workspace;
- preview cache no considera workspace efectivo, default camera ni default collections;
- UI y operadores asumen una lista global de clips.

W3 debe decidir si conviene refactorizar esos archivos o volver al scaffold limpio de Fase 4 y rehacer 5a/5b/5c. La evidencia preliminar inclina el analisis hacia rehacer las slices de dominio, reaprovechando solo helpers puros y patrones validados, no la forma actual del modelo.

## Criterio De Cierre De W1

W1 queda cumplida cuando:

- existe esta tabla de decisiones V1 aceptadas, descartadas, diferidas e investigables;
- workspace-root queda confirmado como brecha documental y tecnica;
- el siguiente paso PCS apunta a W2: rediseno documental workspace-root.
