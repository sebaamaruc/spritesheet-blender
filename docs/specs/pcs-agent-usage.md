# PCS Agent Usage

Estado: activo

Esta guia contiene el detalle operativo de PCS para agentes. `AGENTS.md` conserva solo instrucciones inmediatas de arranque, proteccion y reglas locales criticas; este archivo explica como actualizar, validar, reparar o cerrar PCS sin duplicar todo el contrato minimo. Las reglas locales criticas del proyecto no viven aqui: deben estar brevemente en `AGENTS.md` y el detalle largo en docs locales.

## Regla De Oro Del Presente

Los archivos de `.context/` describen solo el presente. El pasado vive en `.context/worklog.jsonl` y `docs/archive/`. No acumular cronica de fases ni correcciones en `agent_context`, `handoff` ni `index`: al avanzar, mover lo terminado al worklog y podar el presente. Presupuestos: `agent_context.md` <=120 lineas, `handoff.md` <=60, `index.md` <=100. `pcs check` los reporta; `pcs compact` poda lo mecanico y `pcs prompt agy compact` guia la poda semantica.

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
- `pcs close --approved`: cerrar solo con instruccion explicita del usuario; poda el presente al cerrar.
- `pcs compact`: poda mecanica segura (Estado cerrado, exceso de archivos relevantes, tabla de archivo del index).
- `pcs prompt agy compact`: prompt para la poda semantica (handoff, AGENTS.md, contradicciones) con hallazgos medidos.
- `pcs sync --record`: registrar una reparacion mecanica solo cuando se pida dejar evento.

## Planes Y Cierre

Un plan propuesto en `docs/plans/` no es Plan Activo y no requiere `worklog` salvo pedido explicito. Un plan aprobado debe declarar `Estado: aprobado`, `Autoridad: usuario` y `Modo de ejecucion: ejecutar sin replanificar`.

Validar no es cerrar. No ejecutar `pcs close`, archivar planes ni marcar `cerrado` sin instruccion explicita como "cierra PCS" o "ejecuta pcs close".

Si un Plan Activo contradice el codigo o queda bloqueado, detenerse, registrar el bloqueo en `.context/handoff.md` y pedir decision humana.

No eliminar planes en `docs/plans/*.md` con `Delete File`; archivarlos en `docs/archive/` preservando su contenido (`pcs close` lo hace automaticamente). Estados de `Estado De Ejecucion` en un plan: `pendiente` (aprobado, no implementado), `implementado` (cambios hechos, falta validar), `correcciones requeridas` (una revision encontro problemas), `validado` (criterios de aceptacion pasaron), `listo para cierre` (falta actualizar PCS), `cerrado` (PCS ya refleja el cierre). `implementado` no es `validado`; `validado` no es `cerrado`.

## Ritual De Salida

Toda sesion que mueva, renombre o archive documentos, o cierre una implementacion, termina ejecutando `pcs check` y dejandolo en verde antes de entregar el handoff. Las referencias rotas (`references missing path`) son errores que hacen fallar check, no advertencias.

Si check falla, clasificar cada error en una de tres rutas:

1. Mecanico (referencia a un plan movido a `docs/archive/`, tabla malformada, presupuesto de lineas excedido): reparar en la misma sesion, re-ejecutar `pcs check` y terminar solo en verde.
2. Semantico (tarea activa o decision que ya no refleja lo implementado): generar `pcs update draft` para revision del usuario; no reescribir contexto canonico sin aprobacion.
3. No reparable o ambiguo (no se puede determinar la correccion correcta): declararlo explicitamente en `.context/handoff.md` como pendiente o bloqueo.

Un check rojo nunca se oculta ni se resuelve adivinando: o se repara o queda declarado en el handoff.

## Ejecutor Por Fase

Cada fase de un plan puede marcar `Ejecutor: E1`, `E2` o `E3` para indicar la
naturaleza de la tarea. Sin marca, asumir `E3`.

- `E1`: espec cerrada, cambio mecanico, verificacion binaria.
- `E2`: criterio tecnico local; el que hacer esta definido, el como no.
- `E3`: espec abierta, diseno, contratos compartidos o blast radius alto.
- Una fase que califica en mas de un nivel lleva el mas alto, no un nivel mixto.
- Escalar de nivel siempre esta permitido; bajar no. Si el ejecutor falla la
  misma verificacion dos veces, subir un nivel.

## Migracion De AGENTS.md

Para reducir o actualizar un `AGENTS.md`, crear primero `.context/agents-md-audit.tmp.md` con subsistemas criticos detectados, reglas preservadas, reescritas, movidas, eliminadas y riesgos. Ese archivo es temporal, no es estado operativo PCS y no debe agregarse a `.context/index.md`, `agent_context`, `handoff` ni `worklog`.

El nuevo `AGENTS.md` debe conservar solo reglas que todo agente debe obedecer antes de actuar, mas punteros condicionales concretos a docs locales. Los detalles de dominio, runbooks, arquitectura, analisis, tablas y ejemplos deben vivir en docs locales.

Si la auditoria no detecta reglas locales criticas, debe justificarlo. Si detecta subsistemas como dashboard, web/API, datos privados, deploy, scripts, motores, build/test o seguridad, `AGENTS.md` no debe quedar solo con PCS.
