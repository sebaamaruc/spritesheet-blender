# Decisions

Este archivo contiene decisiones vigentes o históricamente relevantes. No reemplaza `.context/worklog.jsonl`.

## Formato

```md
### DEC-0000: Titulo breve

- Estado: vigente | reemplazada | revertida
- Fecha: YYYY-MM-DD
- Decisor: humano | agente | humano + agente
- Contexto:
- Decision:
- Consecuencia:
- Referencias:
```

---

### DEC-0001: PCS persiste contexto operativo en el repositorio

- Estado: vigente
- Fecha: 2026-06-15
- Decisor: pcs bootstrap
- Contexto: El proyecto necesita continuidad entre agentes y sesiones.
- Decision: El contexto operativo vive en archivos PCS dentro del repositorio.
- Consecuencia: Un agente nuevo debe poder continuar leyendo `AGENTS.md`, `.context/agent_context.md` y `.context/index.md`.
- Referencias: `AGENTS.md`, `.context/agent_context.md`

---

### DEC-0002: Unificación de propiedades de salida en SpriteSheetExportSettings

- Estado: vigente
- Fecha: 2026-05-30
- Decisor: humano + agente
- Contexto: Existía una duplicación funcional de las propiedades de destino de salida (`output_name` y `output_folder` en el Workspace frente a `sheet_name` y `output_folder` en Export Settings).
- Decision: Eliminar las propiedades redundantes de la raíz de `SpriteSheetWorkspace`. Alojar la única fuente de verdad en `SpriteSheetExportSettings` (`sheet_name` y `output_folder`).
- Consecuencia: Se simplifican los operadores y el validador, se mantiene la compatibilidad con el modo legacy sin migración de datos compleja, y se limpia la UI del Workspace.
- Referencias: `spritesheet_frame_selector/properties.py`, `spritesheet_frame_selector/panels.py`, `spritesheet_frame_selector/utils.py`

---

### DEC-0003: Workspace Selector con UI nativa template_list

- Estado: vigente
- Fecha: 2026-05-30
- Decisor: humano + agente
- Contexto: Se requería un selector de workspaces que fuera compacto, estable y nativo en la interfaz de Blender.
- Decision: Adoptar `template_list` con `rows=1` para una visualización de fila única, en lugar de un dropdown dinámico con `EnumProperty`.
- Consecuencia: Evita parpadeos y bugs de inicialización en los callbacks dinámicos de Blender, logrando un selector compacto alineado con las directrices visuales nativas de Blender.
- Referencias: `spritesheet_frame_selector/panels.py`

---

### DEC-0004: Documentacion V2 reemplaza el MVP historico como contrato operativo

- Estado: vigente
- Fecha: 2026-07-03
- Decisor: humano + agente
- Contexto: El reinicio V2 requiere documentacion mantenible antes de limpiar el arbol activo o crear scaffold. `docs/specs/mvp.md` mezclaba vision, alcance, arquitectura y decisiones parcialmente contradictorias, especialmente sobre JSON metadata y multi-clip.
- Decision: Preservar el MVP original en `docs/archive/mvp-original.md`, degradar `docs/specs/mvp.md` a puntero historico y usar como contrato vigente `docs/specs/product_requirements.md`, `docs/specs/mvp_v2.md`, `docs/architecture/addon_architecture.md`, `docs/design/visual_selector_strategy.md` y `docs/specs/validation_plan.md`.
- Consecuencia: Las fases posteriores deben planificarse contra los documentos V2. JSON simple es obligatorio para atlas multi-clip, no para export individual simple. Multi-clip debe influir el modelo desde el inicio.
- Referencias: `docs/plans/reinicio-v2-fase-2-documentacion-base.md`, `docs/specs/mvp_v2.md`, `docs/archive/mvp-original.md`

---

### DEC-0005: Arbol activo minimo antes del scaffold V2

- Estado: vigente
- Fecha: 2026-07-03
- Decisor: humano + agente
- Contexto: El usuario indico que es mejor rehacer la mayoria que mantener codigo con malas practicas. La Fase 1 ya preservo el estado V1 por Git y la Fase 2 creo documentacion V2 vigente.
- Decision: Retirar del arbol activo el addon V1, tests legacy, scratch, outputs, caches y residuos locales. Archivar metas V1 de `docs/source/` en `docs/archive/`.
- Consecuencia: La Fase 4 debe crear un scaffold V2 limpio desde documentacion y arquitectura vigentes. El codigo V1 no debe copiarse como base estructural.
- Referencias: `docs/plans/reinicio-v2-fase-3-limpieza-arbol-activo.md`, `archive/generated-addon-v1`, `archive/generated-addon-v1-2026-07-03`

---

### DEC-0006: Workspace es raiz de dominio en V2

- Estado: vigente
- Fecha: 2026-07-03
- Decisor: humano
- Contexto: Durante la reconstruccion V2 se implementaron 5a/5b/5c con `Scene.spritesheet_state.clips` como raiz. Al revisar decisiones no documentadas de V1, el usuario confirmo que workspace no era solo una solucion tecnica sino una entidad central del producto.
- Decision: Redisenar V2 alrededor de workspace como raiz: `Scene.spritesheet_state.workspaces -> active_workspace -> clips -> frames`. Pausar Fase 5d hasta auditar decisiones V1, actualizar documentos y decidir si refactorizar 5a/5b/5c o volver al scaffold limpio de Fase 4.
- Consecuencia: Las fases 5a/5b/5c validadas quedan sujetas a revision arquitectonica. No se debe implementar selector visual, playback, render ni export hasta resolver workspace-root.
- Referencias: `docs/plans/reinicio-v2-fase-5c1-auditoria-decisiones-workspace-root.md`, `docs/plans/reinicio-v2-fase-5a-data-model-persistencia.md`, `docs/plans/reinicio-v2-fase-5b-gestion-clips.md`, `docs/plans/reinicio-v2-fase-5c-preview-cache.md`

---

### DEC-0007: Contrato documental workspace-root para MVP V2

- Estado: vigente
- Fecha: 2026-07-03
- Decisor: humano + agente
- Contexto: W1 de la Fase 5c.1 confirmo que workspace en V1 era una entidad de producto, no solo UI. Los documentos V2 seguian describiendo `Scene.spritesheet_state.clips` como raiz operativa.
- Decision: Actualizar el contrato documental V2 para que `Scene.spritesheet_state` contenga `workspaces`, cada workspace contenga defaults, clips y export settings, y los clips contengan overrides opcionales de camara/collections.
- Consecuencia: Los planes y la implementacion de 5a/5b/5c deben evaluarse en W3 y probablemente reemplazarse o reescribirse como slices workspace-root antes de continuar con 5d.
- Referencias: `docs/specs/workspace_root_decisions.md`, `docs/specs/mvp_v2.md`, `docs/architecture/addon_architecture.md`, `docs/specs/validation_plan.md`

---

### DEC-0008: Visibilidad efectiva por workspace y clip

- Estado: vigente
- Fecha: 2026-07-03
- Decisor: humano + agente
- Contexto: El usuario confirmo que default camera/default collections de workspace y overrides por clip son casos reales. Tambien marco como requisito fuerte que preview/render muestren solo la collection correcta.
- Decision: Preview, render y export deben resolver camara efectiva y collections efectivas desde workspace + clip. En workspace-root no se debe usar `scene.camera` como fallback silencioso cuando falten default camera u override.
- Consecuencia: La arquitectura debe incluir helpers de resolucion y un modulo de visibilidad reversible. Las validaciones deben cubrir camera/collections faltantes, collections borradas, collections anidadas y restauracion del view layer.
- Referencias: `docs/specs/workspace_root_decisions.md`, `docs/architecture/addon_architecture.md`, `docs/specs/validation_plan.md`

---

### DEC-0009: Rehacer Fase 5 desde scaffold para workspace-root

- Estado: vigente
- Fecha: 2026-07-03
- Decisor: humano + agente
- Contexto: W3 comparo refactorizar la V2 actual 5a/5b/5c versus volver al scaffold limpio de Fase 4. La implementacion actual cuelga clips y export settings directamente de `Scene.spritesheet_state`, mientras el contrato V2 vigente exige `Scene.spritesheet_state.workspaces -> active_workspace -> clips`.
- Decision: Rehacer las slices 5a/5b/5c desde el scaffold limpio de Fase 4, reaprovechando solo helpers puros y patrones validados cuando encajen con workspace-root.
- Consecuencia: Los planes 5a/5b/5c existentes quedan como historial validado pero no como base arquitectonica vigente. W4 debe replanificar subplanes workspace-root antes de continuar con 5d.
- Referencias: `docs/specs/workspace_root_refactor_evaluation.md`, `docs/plans/reinicio-v2-fase-5c1-auditoria-decisiones-workspace-root.md`

---

### DEC-0010: Selector modal custom y preview modes persistentes

- Estado: vigente
- Fecha: 2026-07-03
- Decisor: humano + agente
- Contexto: La validacion manual del selector/playback mostro que los thumbnails de 64px no sirven como preview real y que el playback solo avanza estado sin mostrar claramente el resultado. El usuario decidio avanzar hacia superficie modal, guardar `selector_mode` en `.blend`, soportar previews segun solid/textura/rendered y mostrar una vista grande del frame actual.
- Decision: El siguiente trabajo debe insertar una fase correctiva antes de render final: selector modal/custom con visor grande, contornos visuales para seleccionado/playback, modo persistente `EDIT`/`PLAY` por workspace y preview modes persistentes con resolucion efectiva workspace+clip.
- Consecuencia: No avanzar a `5f` render final hasta ejecutar `5e1-selector-playback-ux`. `preview_mode` debe entrar en cache key y la validacion de `SOLID`/`MATERIAL` requiere Blender GUI porque OpenGL/viewport no funciona en background.
- Referencias: `docs/specs/selector_modal_preview_modes_spike.md`, `docs/plans/reinicio-v2-fase-5e1-spike-selector-modal-preview-modes.md`
