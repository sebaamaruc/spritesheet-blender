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
| `docs/plans/reinicio-v2-fase-5-vertical-slices.md` | Cuando se cree; debe aprobarse antes de implementar features de producto | pendiente | no_creado | alta |

## Planes Derivados Validados

| Documento | Cuando leerlo | Estado | Vigencia | Confianza |
|---|---|---|---|---|
| `docs/plans/reinicio-v2-fase-1-preservacion.md` | Para confirmar la referencia Git recuperable del estado generado previo | validado | vigente | alta |
| `docs/plans/reinicio-v2-fase-2-documentacion-base.md` | Para confirmar la normalizacion documental antes de limpiar el arbol activo | validado | vigente | alta |
| `docs/plans/reinicio-v2-fase-3-limpieza-arbol-activo.md` | Para confirmar que el arbol activo quedo minimo antes del scaffold V2 | validado | vigente | alta |
| `docs/plans/reinicio-v2-fase-4-scaffold-addon-v2.md` | Para confirmar estructura y lifecycle base del addon V2 antes de features | validado | vigente | alta |

## Especificaciones

| Documento | Cuando leerlo | Estado | Vigencia | Confianza |
|---|---|---|---|---|
| `docs/specs/PROJECT_VISION.md` | Para entender la filosofia de UX, workflow de multi-clips y playbacks | activo | vigente | alta |
| `docs/specs/product_requirements.md` | Para entender producto, usuario objetivo, objetivos, no objetivos y criterios de exito V2 | activo | vigente | alta |
| `docs/specs/mvp_v2.md` | Para planificar e implementar alcance MVP V2 | activo | vigente | alta |
| `docs/specs/validation_plan.md` | Para definir validaciones automaticas y manuales por fase | activo | vigente | alta |
| `docs/specs/mvp.md` | Para ubicar la referencia historica al MVP original archivado | historico | reemplazado | alta |

## Arquitectura

| Documento | Cuando leerlo | Estado | Vigencia | Confianza |
|---|---|---|---|---|
| `docs/architecture/addon_architecture.md` | Antes de crear scaffold o implementar slices V2 | activo | vigente | alta |

## Diseno

| Documento | Cuando leerlo | Estado | Vigencia | Confianza |
|---|---|---|---|---|
| `docs/design/visual_selector_strategy.md` | Antes de planificar selector visual o playback preview | activo | vigente | alta |

## Codigo

| Documento | Cuando leerlo | Estado | Vigencia | Confianza |
|---|---|---|---|---|
| `spritesheet_frame_selector/` | Scaffold minimo del addon V2; leer antes de planificar slices de implementacion | scaffold | vigente | media |

## Archivo

Los documentos obsoletos o reemplazados viven en `docs/archive/`.

| Documento | Cuando leerlo | Estado | Vigencia | Confianza |
|---|---|---|---|---|
| `docs/archive/implementation_plan.md` | Referencia del plan original de Ordered Clip List (Fase 1) | cerrado | stale | alta |
| `docs/archive/audit_report.md` | Referencia historica de los bugs detectados antes de Workspace V1 | historico | stale | alta |
| `docs/archive/mvp-original.md` | Copia integra del MVP historico previo a la normalizacion V2 | historico | reemplazado | alta |
| `docs/archive/source-goals-v1.md` | Metas V1 archivadas; no usar como estado operativo vigente | historico | reemplazado | alta |
| `docs/archive/source-goals-proposed-v1.md` | Borrador de metas V1 archivado; no usar como estado operativo vigente | historico | reemplazado | alta |
