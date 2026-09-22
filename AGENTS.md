# AGENTS.md

## Idioma

Manten la conversacion y los documentos operativos en espanol.

## Proposito Del Proyecto

Proyecto: spritesheet-blender

Este proyecto usa Project Continuity System (PCS) para persistir contexto operativo dentro del repositorio.

## PCS (Project Continuity System)

Para el arranque, proteccion del contexto activo y cierre de PCS, se referencia la guia detallada: `docs/specs/pcs-agent-usage.md`.
Antes de comenzar, lee en orden:

1. `AGENTS.md`
2. `.context/agent_context.md`
3. `.context/index.md`

Validar no es cerrar. No ejecutes `pcs close`, no archives planes ni marques planes como `cerrado` sin instruccion explicita del usuario.

## Reglas Locales Criticas

### Flujo de Trabajo y PCS
- No dependas del historial del chat. Reconstruye contexto desde archivos de PCS.
- Manten `.context/` breve y operativo. Documentos largos van en `docs/`.
- No dupliques informacion; referencia las fuentes de verdad.
- No edites retroactivamente `.context/worklog.jsonl`.
- No implementes cambios fuera del alcance solicitado.

### Reglas de Dominio (spritesheet-blender)
- **Workspace como Raiz**: Toda propiedad persistida y de configuracion (export settings, default camera/collections) debe vivir bajo el workspace en `Scene.spritesheet_state.workspaces`.
- **Nombres de Clips Unicos**: No se permiten nombres duplicados de clips en un mismo workspace. Al crear o renombrar, agregar automaticamente sufijo numerico incremental.
- **Rango de Frames**: Se prohiben frames negativos (`min=0` en propiedades `frame_start` y `frame_end`).
- **Nombres de Salida**: Los frames individuales renderizados se nombran secuencialmente por su orden de exportacion (`001`, `002`), no con el frame nativo de Blender.
- **Transparencia**: Forzar y restaurar `RGBA` y profundidad de `8` bits durante render final con export transparente.

### Reglas de Build, Test y Sandbox
- **Compilacion**: Ejecutar compilacion con `python3 -m compileall spritesheet_frame_selector` para validar sintaxis.
- **Tests**: Ejecutar tests con `python3 -m unittest discover -s tests`.
- **Limites Fisicos**: Limitar la exportacion de frames individuales a un maximo de 999 por ejecucion.
- **Blender Sandbox**: Blender en background crashea en Metal al inicializarse en este sandbox. Las pruebas que dependan de renderizado o GUI real se deben validar manualmente o correr en entornos no sandboxed si es posible.

### Reglas de Seguridad y Buenas Practicas
- **Modificacion de UI/Seleccion**: No mutar propiedades de seleccion directamente en archivos de UI (`ui/visual_selector.py`). Siempre delegar al operador registrado `bpy.ops.spritesheet.frame_toggle_selection` para mantener la sincronizacion del playback preview.
- **Draw Handlers**: Todo handler de dibujo en view_3d debe cerrarse o limpiarse limpiamente ante eventos `ReferenceError` o al cambiar de escena / archivo.

## Mapa de Lectura y Docs de Dominio

### Router por Tipo de Tarea
Segun la tarea asignada, lee prioritariamente los siguientes documentos:

- **Modificaciones de Modelado, Workspaces y Clips**:
  - `docs/architecture/addon_architecture.md` (Estructura del modelo)
  - `docs/specs/workspace_root_decisions.md` (Reglas del workspace como raiz)
- **UI del Selector Modal, Teclado, Playback**:
  - `docs/design/visual_selector_strategy.md` (Estrategia modal y dibujo)
  - `docs/specs/selector_modal_preview_modes_spike.md` (Visor y UI)
- **Generacion de Previews o Viewport OpenGL**:
  - `docs/plans/reinicio-v2-fase-6b0-preview-camera-viewport.md` (Fuerzo de Camera View)
- **Render Final, Composer de Spritesheets, JSON**:
  - `docs/specs/mvp_v2.md` (Requisitos del atlas)
  - `docs/plans/reinicio-v2-fase-6c-render-cache-final.md` (Detalles de renderizado)
- **Resolver Fallos de Auditoria Tecnica**:
  - `docs/technical-audit.md` (Lista completa de hallazgos C/A/M/B)
  - `docs/plans/reinicio-v2-fase-6-correcciones-auditoria-tecnica.md` (Rector de correcciones)
- **Ejecucion de Validaciones**:
  - `docs/specs/validation_plan.md` (Plan de no regresion y pruebas manuales)

### Inventario Breve de Docs de Dominio
- `docs/specs/PROJECT_VISION.md`: Filosofia de diseno de multi-clips y preview.
- `docs/specs/product_requirements.md`: Objetivos generales del addon V2.
- `docs/specs/mvp_v2.md`: Definicion de alcance minimo para V2.
- `docs/architecture/addon_architecture.md`: Estructura de carpetas, modulos y registro del addon.
- `docs/technical-audit.md`: Analisis detallado de fallas del Workspace V1.

## Documentacion Fuente

La documentacion fuente representa guias previas del proyecto, como MVPs, GDDs, roadmaps, research, notas o `current_state` improvisados.

- Guardar documentos fuente en `docs/source/`.
- Guardar documentos previos sin normalizar en `docs/source/raw/`, preservando su contenido original.
- Usar `docs/source/index.md` como inventario de lectura.
- Usar `docs/source/goals.md` para metas o hitos trazables.
- Usar `docs/source/goals.proposed.md` solo como borrador revisable creado por agentes.
- No tratar archivos en `docs/source/raw/` como contexto operativo vigente hasta derivarlos a `.context/`, `docs/plans/` o `.context/decisions.md`.
- Los planes basados en documentacion fuente deben declarar `Documentación Fuente Usada` e `Interpretación Operativa`.
- Las decisiones deben registrar desviaciones importantes frente a documentos fuente.

## Proteccion Del Contexto Activo

El contexto PCS representa la tarea principal compartida del proyecto, no cualquier accion lateral ejecutada dentro del repositorio.

Actualizar `.context/agent_context.md`, `.context/handoff.md` o `docs/plans/` solo cuando:

- la tarea actual corresponde al `Plan Activo` o al proximo paso registrado en PCS
- el usuario pidio explicitamente actualizar/cerrar contexto PCS
- se esta usando `pcs update`, `pcs update apply` o un flujo PCS equivalente

No actualizar contexto operativo cuando:

- la tarea es lateral, puntual o no relacionada con el `Plan Activo`
- el agente no reconstruyo contexto desde PCS
- el usuario solo pidio editar un archivo, dato, DB o carpeta especifica
- existe un `Plan Activo` y la tarea solicitada no pertenece a ese plan

Si una tarea lateral debe quedar registrada, agregar como maximo un evento append-only a `.context/worklog.jsonl` o pedir confirmacion antes de tocar contexto operativo.
Para registrar una tarea lateral con PCS, usar `pcs update --scope side` o un draft con `Scope: side`.

Registrar solo cambios utiles para continuidad: `.context/agent_context.md` es estado actual, `.context/handoff.md` es transferencia inmediata, `.context/worklog.jsonl` es historial relevante y `.context/decisions.md` guarda decisiones conceptuales vigentes. No registrar borradores, propuestas no aprobadas, sync sin cambio relevante ni normalizaciones triviales.
Usar `policy_updated` solo para cambios conceptuales de reglas PCS; usar `context_synced` solo para sync mecanico registrado explicitamente.

## Cierre PCS

Validar no es cerrar. Un agente no debe ejecutar `pcs close`, archivar planes ni marcar `cerrado` salvo instruccion explicita de cierre del usuario, como "cierra PCS", "cierra y archiva el plan" o "ejecuta pcs close".

Si el usuario solo dice "aprobado", "validado", "se ve bien", "procede" o similar, dejar el plan como `validado` o `listo para cierre` y esperar cierre explicito.

Si la tarea implica actualizar, validar, reparar o cerrar PCS, leer `docs/specs/pcs-agent-usage.md` antes de actuar.

Ritual de salida: toda sesion que mueva, renombre o archive documentos, o cierre una implementacion, debe terminar ejecutando `pcs check` y dejarlo en verde antes de entregar el handoff. Si check falla: reparar lo mecanico en la misma sesion, proponer lo semantico con `pcs update draft`, y declarar lo no reparable en `.context/handoff.md`. Un check rojo nunca se oculta ni se resuelve adivinando.
