# Context Index

Ultima actualizacion: 2026-07-05

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
| `docs/plans/reinicio-v2-fase-6-correcciones-auditoria-tecnica.md` | Revisar y aprobar antes de corregir los hallazgos de `docs/technical-audit.md` | propuesto | vigente | alta |
| `docs/plans/reinicio-v2-fase-7-validacion-distribucion.md` | Revisar y aprobar despues de validar Fase 6, antes de packaging e instalacion ZIP | propuesto | diferido | alta |

## Planes Derivados Implementados Pendientes De Validacion

| Documento | Cuando leerlo | Estado | Vigencia | Confianza |
|---|---|---|---|---|

## Planes Derivados Validados

| Documento | Cuando leerlo | Estado | Vigencia | Confianza |
|---|---|---|---|---|

## Especificaciones

| Documento | Cuando leerlo | Estado | Vigencia | Confianza |
|---|---|---|---|---|
| `docs/technical-audit.md` | Antes de planificar o ejecutar Fase 6; fuente de hallazgos tecnicos C/A/M/B | auditoria_tecnica | vigente | alta |
| `docs/specs/PROJECT_VISION.md` | Para entender la filosofia de UX, workflow de multi-clips y playbacks | activo | vigente | alta |
| `docs/specs/product_requirements.md` | Para entender producto, usuario objetivo, objetivos, no objetivos y criterios de exito V2 | activo | vigente | alta |
| `docs/specs/mvp_v2.md` | Para planificar e implementar alcance MVP V2 | activo | vigente | alta |
| `docs/specs/validation_plan.md` | Para definir validaciones automaticas y manuales por fase | activo | vigente | alta |
| `docs/specs/workspace_root_decisions.md` | Antes de actualizar docs V2 o replanificar Fase 5 con workspace como raiz | activo | vigente | alta |
| `docs/specs/workspace_root_refactor_evaluation.md` | Antes de replanificar Fase 5 workspace-root; contiene decision refactor vs reinicio | activo | vigente | alta |
| `docs/specs/selector_modal_preview_modes_spike.md` | Antes de crear o implementar 5e1 selector/playback UX | activo | vigente | alta |
| `docs/specs/mvp.md` | Para ubicar la referencia historica al MVP original archivado | historico | stale | alta |

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
| `docs/archive/mvp-original.md` | Copia integra del MVP historico previo a la normalizacion V2 | historico | archivado | alta |
| `docs/archive/source-goals-v1.md` | Metas V1 archivadas; no usar como estado operativo vigente | historico | archivado | alta |
| `docs/archive/source-goals-proposed-v1.md` | Borrador de metas V1 archivado; no usar como estado operativo vigente | historico | archivado | alta |
| `docs/archive/reinicio-v2-fase-1-preservacion.md` | Preservacion Git del estado V1 validada | validado | archivado | alta |
| `docs/archive/reinicio-v2-fase-2-documentacion-base.md` | Normalizacion documental V2 validada | validado | archivado | alta |
| `docs/archive/reinicio-v2-fase-3-limpieza-arbol-activo.md` | Limpieza del arbol activo validada | validado | archivado | alta |
| `docs/archive/reinicio-v2-fase-4-scaffold-addon-v2.md` | Scaffold V2 validado | validado | archivado | alta |
| `docs/archive/reinicio-v2-fase-5-vertical-slices.md` | Plan rector original de Fase 5 reemplazado parcialmente por workspace-root | reemplazado | archivado | alta |
| `docs/archive/reinicio-v2-fase-5-workspace-root-vertical-slices.md` | Plan rector workspace-root de Fase 5 ejecutado hasta 5g | validado | archivado | alta |
| `docs/archive/reinicio-v2-fase-5a-data-model-persistencia.md` | Historial del intento 5a original basado en clips directos bajo Scene state | reemplazado | archivado | alta |
| `docs/archive/reinicio-v2-fase-5b-gestion-clips.md` | Historial del intento 5b original basado en lista global de clips | reemplazado | archivado | alta |
| `docs/archive/reinicio-v2-fase-5c-preview-cache.md` | Historial del intento 5c original basado en preview cache por clip global | reemplazado | archivado | alta |
| `docs/archive/reinicio-v2-fase-5c1-auditoria-decisiones-workspace-root.md` | Auditoria y rediseno workspace-root validados; contexto historico inmediato | validado | archivado | alta |
| `docs/archive/reinicio-v2-fase-5a-workspace-data-model-persistencia.md` | Modelo persistente workspace-root validado | validado | archivado | alta |
| `docs/archive/reinicio-v2-fase-5b-workspace-clip-management.md` | Gestion workspace-root de workspaces/clips validada | validado | archivado | alta |
| `docs/archive/reinicio-v2-fase-5c-workspace-preview-cache.md` | Preview cache workspace-aware validado | validado | archivado | alta |
| `docs/archive/reinicio-v2-fase-5d-visual-selector-minimo.md` | Selector visual minimo validado | validado | archivado | alta |
| `docs/archive/reinicio-v2-fase-5e-playback-preview.md` | Playback preview validado | validado | archivado | alta |
| `docs/archive/reinicio-v2-fase-5e1-spike-selector-modal-preview-modes.md` | Spike selector modal/preview modes validado | validado | archivado | alta |
| `docs/archive/reinicio-v2-fase-5e1-selector-playback-ux.md` | Correcciones UX selector/playback validadas | validado | archivado | alta |
| `docs/archive/reinicio-v2-fase-5f-render-final-workspace-aware.md` | Render final workspace-aware reemplazado por flujo integrado en 5g | reemplazado | archivado | alta |
| `docs/archive/reinicio-v2-fase-5g-export-spritesheet-json.md` | Export spritesheet, JSON, frames individuales y correcciones UI/naming/atajos validados | validado | archivado | alta |
