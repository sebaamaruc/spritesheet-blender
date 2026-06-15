# AGENTS.md

## Idioma

Manten la conversacion y los documentos operativos en espanol.

## Proposito Del Proyecto

Proyecto: spritesheet-blender

Este proyecto usa Project Continuity System (PCS) para persistir contexto operativo dentro del repositorio.

## Lectura Obligatoria Al Iniciar

Todo agente debe leer, en este orden:

1. `AGENTS.md`
2. `.context/agent_context.md`
3. `.context/index.md`

Leer otros archivos solo si la tarea activa lo requiere.

## Fuentes De Verdad

- Estado actual: `.context/agent_context.md`
- Handoff inmediato: `.context/handoff.md`
- Decisiones vigentes: `.context/decisions.md`
- Historial append-only: `.context/worklog.jsonl`
- Indice de lectura: `.context/index.md`
- Planes: `docs/plans/`
- Especificaciones: `docs/specs/`
- Arquitectura: `docs/architecture/`
- Disenos: `docs/design/`
- Archivo: `docs/archive/`

## Formato De Rutas En PCS

- Usar siempre rutas repo-relativas puras: `docs/plans/foo.md`.
- No usar enlaces `file://`.
- No usar enlaces Markdown para rutas internas PCS.
- En tablas y secciones PCS, envolver rutas internas con backticks.
- Todo plan activo debe vivir en `docs/plans/` y referenciarse como ruta repo-relativa.

## Politica Planner/Executor

Crear o guardar un plan en `docs/plans/` no lo convierte en aprobado.

Si el plan fue creado para revision del usuario, debe quedar como plan propuesto:

- `Estado: propuesto`
- `Autoridad: pendiente`
- `Modo de ejecucion: pendiente`

Un plan propuesto no debe aparecer como `Plan Activo` en `.context/agent_context.md`. En ese estado, el proximo paso debe ser revisar/aprobar el plan.

Cuando el usuario aprueba un plan en el chat con una frase como "aprobado", "plan aprobado", "guarda el plan" o equivalente, el agente planner debe persistirlo como Plan Activo PCS aprobado y detenerse.

Ese paso debe:

- guardar el plan en `docs/plans/`
- declarar `Estado: aprobado`
- declarar `Autoridad: usuario`
- declarar `Modo de ejecucion: ejecutar sin replanificar`
- actualizar `Plan Activo` en `.context/agent_context.md`
- actualizar tarea activa y proximo paso para que otro agente ejecute el plan
- agregar el plan en `.context/index.md`
- actualizar `.context/handoff.md`
- agregar evento append-only `plan_approved` en `.context/worklog.jsonl`

No implementar el plan en el mismo turno salvo instruccion explicita del usuario.

Si `.context/agent_context.md` declara un `Plan Activo` con una ruta `docs/plans/*.md`, ese plan es la autoridad operativa.

Un agente ejecutor debe:

- leer el plan activo antes de implementar
- ejecutar la fase o proximo paso indicado
- no crear un plan nuevo
- no reemplazar el plan activo
- no pedir aprobacion para un plan alternativo

Si el plan activo parece incorrecto, contradictorio o bloqueado, detenerse y registrar el bloqueo en `.context/handoff.md`. Cambiar un plan activo requiere instruccion explicita del usuario o de un agente planificador autorizado.

## Reglas De Trabajo Para Agentes

- No depender del historial del chat.
- Reconstruir contexto desde archivos antes de trabajar.
- Mantener `.context/` breve y operativo.
- Mantener documentos largos en `docs/`.
- No duplicar informacion entre archivos; referenciar la fuente de verdad.
- No editar retroactivamente `.context/worklog.jsonl`.
- No implementar cambios fuera del alcance solicitado.

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

## Criterios De Finalizacion

Una tarea no se considera terminada hasta que:

- el entregable solicitado exista
- las validaciones aplicables hayan sido ejecutadas o justificadas
- `.context/agent_context.md` refleje el nuevo estado cuando corresponda
- `.context/handoff.md` indique el proximo paso o que no hay handoff activo
- `.context/worklog.jsonl` tenga un evento relevante

## Archivado Obligatorio De Planes

Los planes completados, cerrados, reemplazados u obsoletos no se eliminan.

Archivar un plan significa mover el archivo desde `docs/plans/` hacia `docs/archive/`, preservando su contenido operativo. No significa borrar el archivo, recrearlo vacio ni reemplazarlo por un resumen.

Reglas obligatorias:

- No usar `Delete File` sobre `docs/plans/*.md` salvo instruccion explicita del usuario que pida borrar ese archivo.
- No eliminar planes para limpiar el repositorio, reducir ruido o evitar duplicados historicos.
- No borrar historial operativo de planes cerrados; el historial se conserva moviendo el documento a `docs/archive/`.
- Al archivar un plan, actualizar las referencias PCS que correspondan: `.context/index.md`, `.context/agent_context.md`, `.context/handoff.md` y `.context/worklog.jsonl`.
- Registrar el archivado con un evento append-only en `.context/worklog.jsonl`, usando un tipo como `plan_archived`, `plan_closed` o equivalente.
- Si existe un conflicto entre borrar y archivar, archivar siempre.
- La unica excepcion es una instruccion explicita del usuario para eliminar un plan concreto; aun asi, registrar el evento en `.context/worklog.jsonl`.

## Ciclo De Vida De Planes Y Validacion

Implementado, validado y cerrado son estados distintos. Un plan no se considera completado solo porque el codigo, documento o cambio solicitado fue escrito.

Estados recomendados para `Estado De Ejecucion` en planes:

- `pendiente`: el plan esta aprobado pero aun no se implemento.
- `implementado`: los cambios fueron realizados, pero falta validacion completa.
- `correcciones requeridas`: una revision o validacion encontro problemas dentro del mismo plan.
- `validado`: los criterios de aceptacion y validaciones esperadas pasaron.
- `listo para cierre`: implementacion y validacion final pasaron, pero aun falta actualizar PCS.
- `cerrado`: PCS fue actualizado con estado final, handoff y worklog.

Reglas obligatorias:

- No marcar `Estado De Ejecucion` como `Completado`, `cerrado` o equivalente antes de validacion final y cierre PCS.
- Si una revision detecta problemas sobre la implementacion de un plan, mantener el mismo plan activo y marcarlo como `correcciones requeridas`; no crear una tarea nueva salvo instruccion explicita del usuario.
- Si el agente solo implemento cambios, debe dejar el estado como `implementado` o `correcciones requeridas`, no como cerrado.
- Si el agente valida cambios pero no actualiza PCS, debe dejar el estado como `validado` o `listo para cierre`, no como cerrado.
- La Fase de Cierre PCS debe actualizar `.context/agent_context.md`, `.context/handoff.md` y `.context/worklog.jsonl` para reflejar el estado final.
- El dashboard puede visualizar estos estados, pero no debe inventarlos; debe derivarlos de PCS.
