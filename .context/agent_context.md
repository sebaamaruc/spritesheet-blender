# Agent Context

PCS-Version: 1
PCS-Template-Version: 1.0.0
Ultima actualizacion: 2026-06-15
Actualizado por: Antigravity

## Resumen Actual

El proyecto `spritesheet-blender` es un addon de Blender 5.x para la seleccion visual de frames y exportacion de spritesheets (PNG + JSON). Se encuentra en estado estable con el sistema Workspace V1 implementado y validado mediante pruebas automatizadas. Todos los bugs criticos identificados en la auditoria previa (caching de camara P1, TypeErrors en poll de UI P2, e indexacion de workspace P3) fueron resueltos en el commit `a98b9b6`.

## Tarea Activa

Ninguna. Esperando instrucciones del usuario para comenzar nuevas features.

## Proximo Paso Recomendado

Validar el comportamiento del selector visual y la exportacion multi-workspace de forma interactiva en la interfaz grafica de Blender con escenas reales de produccion.

## Estado

- PCS bootstrap: completado
- Contexto inicial del proyecto: completado
- Auditoria tecnica post-Workspace V1: cerrada (todos los hallazgos P1-P3 resueltos)

## Archivos Relevantes Ahora

- `AGENTS.md`
- `.context/agent_context.md`
- `.context/index.md`
- `.context/handoff.md`
- `.context/decisions.md`

## Plan Activo

Ninguno.

## Decisiones Vigentes Relevantes

- `DEC-0001`: PCS persiste contexto operativo en el repositorio.
- `DEC-0002`: Unificacion de propiedades de salida en `SpriteSheetExportSettings` (eliminando redundancia de variables en el Workspace).
- `DEC-0003`: Adopcion de `template_list` con `rows=1` para el selector visual de Workspace en la UI de Blender.

## Riesgos Abiertos

- Posibles desincronizaciones visuales temporales si se modifican objetos camara en la escena de Blender externamente sin redibujar el panel de la interfaz.

## Bloqueos

Ninguno detectado.

## Validaciones Pendientes

- [ ] Validacion manual de flujos de workspace y selector visual por parte del usuario en Blender GUI.
