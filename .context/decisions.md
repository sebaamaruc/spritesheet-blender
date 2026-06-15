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
