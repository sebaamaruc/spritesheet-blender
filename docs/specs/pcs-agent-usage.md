# PCS Agent Usage

Estado: activo

Esta guia contiene el detalle operativo de PCS para agentes. `AGENTS.md` conserva solo instrucciones inmediatas de arranque, proteccion y reglas locales criticas; este archivo explica como actualizar, validar, reparar o cerrar PCS sin duplicar todo el contrato minimo. Las reglas locales criticas del proyecto no viven aqui: deben estar brevemente en `AGENTS.md` y el detalle largo en docs locales.

## Archivos PCS

- `.context/agent_context.md`: estado operativo actual, tarea activa, Plan Activo, proximo paso, riesgos y validaciones vigentes.
- `.context/handoff.md`: transferencia inmediata para otro agente: siguiente accion, bloqueo o validacion pendiente.
- `.context/decisions.md`: decisiones conceptuales vigentes o historicamente relevantes.
- `.context/index.md`: mapa breve de planes, specs y documentos que otros agentes deben encontrar.
- `.context/worklog.jsonl`: historial append-only de eventos relevantes para reconstruccion.
- `docs/plans/`: planes propuestos o aprobados.
- `docs/archive/`: planes cerrados, reemplazados u obsoletos archivados; no borrarlos salvo pedido explicito.

## Cuando Actualizar

Actualizar PCS solo si cambia la continuidad del proyecto: tarea activa, Plan Activo, proximo paso, bloqueo, riesgo, decision vigente, validacion pendiente o cierre.

No registrar borradores, planes propuestos no aprobados, sync sin cambio relevante, normalizaciones triviales ni mantenimiento mecanico salvo pedido explicito.

Para tareas laterales que merezcan registro sin tocar contexto principal, usar `pcs update --scope side`.

## Comandos Preferidos

- `pcs check`: validar y reparar mecanica segura.
- `pcs update --scope main`: actualizar estado operativo principal.
- `pcs update --scope side`: registrar tarea lateral sin reemplazar contexto principal.
- `pcs plan approve`: aprobar un plan persistido y convertirlo en Plan Activo.
- `pcs close --approved`: cerrar solo con instruccion explicita del usuario.
- `pcs sync --record`: registrar una reparacion mecanica solo cuando se pida dejar evento.

## Planes Y Cierre

Un plan propuesto en `docs/plans/` no es Plan Activo y no requiere `worklog` salvo pedido explicito. Un plan aprobado debe declarar `Estado: aprobado`, `Autoridad: usuario` y `Modo de ejecucion: ejecutar sin replanificar`.

Validar no es cerrar. No ejecutar `pcs close`, archivar planes ni marcar `cerrado` sin instruccion explicita como "cierra PCS" o "ejecuta pcs close".

Si un Plan Activo contradice el codigo o queda bloqueado, detenerse, registrar el bloqueo en `.context/handoff.md` y pedir decision humana.

## Migracion De AGENTS.md

Para reducir o actualizar un `AGENTS.md`, crear primero `.context/agents-md-audit.tmp.md` con subsistemas criticos detectados, reglas preservadas, reescritas, movidas, eliminadas y riesgos. Ese archivo es temporal, no es estado operativo PCS y no debe agregarse a `.context/index.md`, `agent_context`, `handoff` ni `worklog`.

El nuevo `AGENTS.md` debe conservar solo reglas que todo agente debe obedecer antes de actuar, mas punteros condicionales concretos a docs locales. Los detalles de dominio, runbooks, arquitectura, analisis, tablas y ejemplos deben vivir en docs locales.

Si la auditoria no detecta reglas locales criticas, debe justificarlo. Si detecta subsistemas como dashboard, web/API, datos privados, deploy, scripts, motores, build/test o seguridad, `AGENTS.md` no debe quedar solo con PCS.
