# Context Index

Ultima actualizacion: 2026-07-03

## Lectura Minima

Leer siempre:

1. `AGENTS.md`
2. `.context/agent_context.md`
3. `.context/index.md`

## Documentos Operativos

| Documento | Cuando leerlo | Estado | Vigencia | Confianza |
|---|---|---|---|---|
| `AGENTS.md` | Al iniciar cualquier sesion para comprender las reglas operativas de IA | lectura_obligatoria | vigente | alta |
| `.context/agent_context.md` | Al iniciar cualquier sesion para conocer el estado y la tarea activa | activo | vigente | alta |
| `.context/handoff.md` | Al continuar trabajo pendiente o cambiar de agente | activo | vigente | alta |
| `.context/decisions.md` | Antes de cambiar reglas, arquitectura o convenciones | activo | vigente | alta |
| `.context/worklog.jsonl` | Solo para auditoria o reconstruccion historica | append-only | vigente | alta |
| `.context/manifest.json` | Para auditoria de version y estructura PCS | activo | vigente | alta |

## Planes Activos

| Documento | Cuando leerlo | Estado | Vigencia | Confianza |
|---|---|---|---|---|
| `docs/plans/reinicio-v2-master-plan.md` | Siempre antes de planificar o ejecutar cualquier trabajo del reinicio V2 | aprobado | vigente | alta |

## Planes Derivados Pendientes

| Documento | Cuando leerlo | Estado | Vigencia | Confianza |
|---|---|---|---|---|
| `docs/plans/reinicio-v2-fase-1-preservacion.md` | Proximo documento a crear antes de preservar estado por Git | pendiente | requerido | alta |

## Especificaciones

| Documento | Cuando leerlo | Estado | Vigencia | Confianza |
|---|---|---|---|---|
| `docs/specs/PROJECT_VISION.md` | Para entender la filosofia de UX, workflow de multi-clips y playbacks | activo | vigente | alta |
| `docs/specs/mvp.md` | Para comprender el alcance original del MVP y derivar documentacion V2 normalizada | historico | pendiente_de_normalizacion | alta |

## Arquitectura

| Documento | Cuando leerlo | Estado | Vigencia | Confianza |
|---|---|---|---|---|
| Ninguno | - | - | - | - |

## Archivo

Los documentos obsoletos o reemplazados viven en `docs/archive/`.

| Documento | Cuando leerlo | Estado | Vigencia | Confianza |
|---|---|---|---|---|
| `docs/archive/implementation_plan.md` | Referencia del plan original de Ordered Clip List (Fase 1) | cerrado | stale | alta |
| `docs/archive/audit_report.md` | Referencia historica de los bugs detectados antes de Workspace V1 | historico | stale | alta |
