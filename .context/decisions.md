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
