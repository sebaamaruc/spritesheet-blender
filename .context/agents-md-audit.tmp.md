# Auditoria de AGENTS.md

## Subsistemas Criticos Detectados

1. **Modelado y Persistencia (Workspace-Root)**: Estructura jerarquica de datos en `Scene.spritesheet_state.workspaces`.
2. **Preview Cache**: Generador de thumbnails con OpenGL (SOLID/MATERIAL) forzando Camera View de viewport y fallback en background por render still.
3. **Selector Modal**: UI dibujada en viewport 3D (`SpaceView3D`) mediante draw handler de Blender, usando bucle modal que intercepta eventos selectivos.
4. **Playback Preview**: Reproductor con timer en background que maneja la seleccion activa de frames.
5. **Composer y Export**: Ensamblador de spritesheets 2D, exportador de frames individuales (maximo 999) y metadata JSON.

## Reglas Preservadas (se mantienen en `AGENTS.md`)

- **Idioma**: Español obligatorio.
- **Proposito del Proyecto**: `spritesheet-blender`.
- **Reglas Locales Criticas**:
  - No depender del historial del chat.
  - Reconstruir contexto desde archivos antes de trabajar.
  - Mantener `.context/` breve y operativo.
  - Mantener documentos largos en `docs/`.
  - No duplicar informacion entre archivos; referenciar la fuente de verdad.
  - No editar retroactivamente `.context/worklog.jsonl`.
  - No implementar cambios fuera del alcance solicitado.
- **Reglas de Dominio/Build/Test/Seguridad**:
  - Limite estricto de 999 frames en exportacion individual.
  - Nombres de clips unicos por workspace (agregar sufijo incremental).
  - No frames negativos (`min=0`).
  - No mutar seleccion del selector visual directamente; usar los operadores registrados (`bpy.ops.spritesheet.frame_toggle_selection`).
  - Render final de frames PNG usa indexacion continua de 3 digitos en base 1 (`001`, `002`), no el numero de frame nativo de Blender.
  - Blender background dentro del sandbox crashea en Metal; ejecutar pruebas con Blender GUI o en local fuera de sandbox de ser necesario.

## Reglas Movidas o Reescritas (se delegan a `docs/specs/pcs-agent-usage.md`)

- Proceso PCS general (Lectura obligatoria al iniciar, Fuentes de verdad, Formato de rutas en PCS, Politica Planner/Executor, Proteccion de Contexto, Criterios de Finalizacion, Archivado de Planes, Ciclo de vida y validacion de planes).

## Reglas Eliminadas

- Ninguna regla dura de dominio, build, test ni seguridad ha sido eliminada. Solo se podaron parrafos genericos del proceso PCS ya cubiertos por `docs/specs/pcs-agent-usage.md`.

## Riesgos Identificados

- Modificar `AGENTS.md` sin preservar la especificidad de los tests y el comportamiento modal podria causar que futuros agentes intenten soluciones incompatibles con el entorno (ej. usar render de fondo sandbox o mutar variables nativas de seleccion directamente). Se previene documentando las reglas duras en `AGENTS.md` y mapeando los documentos por tipo de tarea.
