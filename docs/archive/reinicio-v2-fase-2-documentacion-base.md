# Reinicio V2 Fase 2: Documentacion Base V2

Estado: aprobado
Autoridad: usuario
Modo de ejecucion: ejecutar sin replanificar
Estado De Ejecucion: validado

## Referencia Superior

`docs/plans/reinicio-v2-master-plan.md`

## Objetivo

Normalizar la documentacion base del reinicio V2 antes de limpiar el arbol activo, crear scaffold o implementar codigo.

Esta fase debe convertir la vision y el MVP historico en documentos operativos claros, no contradictorios y suficientes para que las fases posteriores puedan ejecutarse sin consultar el codigo generado actual como base de implementacion.

## Alcance

Incluye:

- derivar requisitos de producto desde `docs/specs/PROJECT_VISION.md` y `docs/specs/mvp.md`;
- separar vision, MVP, arquitectura, estrategia del selector visual y validacion;
- declarar decisiones V2 explicitas cuando el MVP historico contenga contradicciones;
- actualizar referencias PCS para que la documentacion V2 sea la fuente operativa posterior;
- archivar o degradar `docs/specs/mvp.md` solo despues de crear sus reemplazos V2.

No incluye:

- limpiar codigo generado;
- borrar residuos;
- crear scaffold del addon;
- implementar features;
- ejecutar pruebas Blender;
- cambiar el master plan.

## Documentacion Fuente Usada

- `docs/specs/PROJECT_VISION.md`: fuente vigente de vision, filosofia UX, direccion multi-clip y limites de producto.
- `docs/specs/mvp.md`: fuente historica con requisitos iniciales, decisiones sugeridas, contradicciones y alcance a normalizar.
- `docs/archive/audit_report.md`: referencia historica de riesgos tecnicos del addon generado, solo para informar restricciones de arquitectura y validacion.
- `docs/plans/reinicio-v2-master-plan.md`: plan gobernante de orden, restricciones y faseado.
- `docs/plans/reinicio-v2-fase-1-preservacion.md`: confirmacion de preservacion Git antes de reestructurar documentacion.

## Interpretacion Operativa

- `PROJECT_VISION.md` se mantiene como documento de vision vigente.
- `mvp.md` no debe seguir siendo contrato operativo directo despues de esta fase.
- El contenido util de `mvp.md` debe derivarse a documentos V2 con responsabilidades separadas.
- Las contradicciones internas deben resolverse a favor de:
  - estabilidad primero;
  - UX visual como diferenciador;
  - playback preview como feature core;
  - multi-clip como direccion inicial de arquitectura;
  - cero dependencias externas obligatorias;
  - addon instalable por ZIP;
  - no construir editor de pixel art, suite de animacion ni app externa.

## Entregables

Crear o actualizar:

1. `docs/specs/product_requirements.md`
   - Define producto, usuario objetivo, objetivos, no objetivos, prioridades y criterios de exito.
   - No debe incluir detalles de implementacion de Blender salvo restricciones de producto.

2. `docs/specs/mvp_v2.md`
   - Define alcance MVP V2 por capacidades.
   - Debe distinguir obligatorio, diferido y fuera de alcance.
   - Debe resolver la contradiccion del MVP historico sobre JSON: para V2, metadata JSON simple es obligatoria para atlas multi-clip, no para export individual simple.

3. `docs/architecture/addon_architecture.md`
   - Define limites de modulos y dependencias permitidas.
   - Debe separar data model, registro, UI, operadores, selector visual, preview, render, composer, export, cache/pathing y validacion.
   - Debe declarar que utilidades de dominio no deben depender de `bpy.context` global si pueden recibir `context`, `scene` o datos explicitos.

4. `docs/design/visual_selector_strategy.md`
   - Define estrategia UX y tecnica del selector visual.
   - Debe priorizar selector visual robusto minimo antes que interacciones avanzadas.
   - Debe incluir playback preview como parte central del flujo, usando previews cacheados.

5. `docs/specs/validation_plan.md`
   - Define validaciones automaticas y manuales por fase.
   - Debe incluir activar/desactivar/reactivar addon, archivo nuevo, cambio de escena, camara faltante, coleccion faltante, persistencia `.blend`, preview, export PNG y atlas multi-clip con JSON.

6. `docs/archive/mvp-original.md`
   - Debe preservar el contenido historico de `docs/specs/mvp.md` si se decide moverlo.
   - Alternativa permitida: mantener `docs/specs/mvp.md` en su lugar, pero actualizar `docs/source/index.md` o `.context/index.md` para marcarlo como historico/no operativo.

## Decisiones De Contenido

### Producto

- El producto es una herramienta Blender-first para seleccionar visualmente frames de animacion y exportarlos como spritesheet.
- El diferenciador principal es la UX de seleccion visual y playback de frames seleccionados.
- El addon debe evitar convertirse en herramienta general de spritesheets, editor de pixel art, sistema de rigging o suite de animacion.

### MVP V2

Obligatorio:

- clips multiples en el modelo desde el inicio;
- preview cacheado;
- selector visual minimo;
- playback preview con frames seleccionados;
- export PNG individual;
- arquitectura preparada para atlas multi-clip;
- metadata JSON simple cuando se exporte atlas multi-clip;
- persistencia de estado en `.blend`;
- instalacion por ZIP sin dependencias externas obligatorias.

Diferido:

- box select avanzado;
- deteccion de frames duplicados;
- integraciones runtime;
- packing irregular;
- marketplace/licensing;
- UI altamente pulida.

Fuera de alcance:

- editor de pixel art;
- app externa;
- timeline alternativo;
- editor de pivots;
- trimming automatico;
- auto remove de frames similares.

### Arquitectura

- Los planes posteriores no deben usar el addon generado como base estructural.
- El codigo viejo puede consultarse solo como referencia puntual para riesgos, no para copiar arquitectura.
- La arquitectura V2 debe permitir reemplazar composer y selector visual sin reescribir persistencia/export.
- Registro y unregister deben ser idempotentes y defensivos desde el scaffold.

## Pasos De Ejecucion

1. Verificar que la Fase 1 este validada leyendo `docs/plans/reinicio-v2-fase-1-preservacion.md`.
2. Leer por completo:
   - `docs/specs/PROJECT_VISION.md`;
   - `docs/specs/mvp.md`;
   - `docs/archive/audit_report.md`;
   - `docs/plans/reinicio-v2-master-plan.md`.
3. Crear `docs/specs/product_requirements.md`.
4. Crear `docs/specs/mvp_v2.md`.
5. Crear `docs/architecture/addon_architecture.md`.
6. Crear `docs/design/visual_selector_strategy.md`.
7. Crear `docs/specs/validation_plan.md`.
8. Resolver contradicciones detectadas en una seccion `Decisiones V2` dentro del documento que corresponda.
9. Archivar `docs/specs/mvp.md` como `docs/archive/mvp-original.md` o degradarlo explicitamente a historico no operativo.
10. Actualizar `.context/index.md` para marcar los nuevos documentos V2 como vigentes y `docs/specs/mvp.md` como historico/archivado.
11. Actualizar `.context/agent_context.md` y `.context/handoff.md` para dejar como proximo paso preparar `docs/plans/reinicio-v2-fase-3-limpieza-arbol-activo.md`.
12. Agregar evento append-only en `.context/worklog.jsonl`.

## Reglas De Ejecucion

- No modificar codigo del addon en esta fase.
- No limpiar ni borrar residuos.
- No crear scaffold.
- No cambiar el master plan.
- No marcar `docs/specs/mvp.md` como fuente vigente despues de crear `mvp_v2.md`.
- Si al archivar `mvp.md` surge duda entre borrar y archivar, archivar siempre.
- Si se detecta una decision de producto no resuelta por las fuentes, detenerse y pedir decision al usuario antes de escribir documentos definitivos.

## Riesgos

- Riesgo: duplicar informacion entre docs.
  - Mitigacion: cada documento debe tener una responsabilidad clara y referenciar, no repetir, cuando corresponda.
- Riesgo: convertir `mvp_v2.md` en arquitectura.
  - Mitigacion: mantener requisitos en specs y decisiones tecnicas en `docs/architecture/addon_architecture.md`.
- Riesgo: dejar contradicciones del MVP historico vivas.
  - Mitigacion: registrar decisiones V2 explicitas.
- Riesgo: avanzar a limpieza sin docs aprobados.
  - Mitigacion: PCS debe dejar Fase 3 como proximo plan, no como ejecucion directa.

## Validaciones

Validaciones documentales:

- Cada documento nuevo existe y tiene proposito claro.
- `product_requirements.md` no contiene diseño tecnico detallado.
- `mvp_v2.md` distingue obligatorio, diferido y fuera de alcance.
- `addon_architecture.md` define limites de modulo suficientes para planificar scaffold.
- `visual_selector_strategy.md` define selector minimo y playback preview.
- `validation_plan.md` cubre pruebas automaticas y manuales esperadas.
- `.context/index.md` referencia los documentos V2 nuevos.
- `docs/specs/mvp.md` no queda como documento operativo vigente.

Validaciones de no alcance:

- `git status --short` no muestra cambios en codigo del addon salvo que se hayan tocado accidentalmente; si ocurre, revertir solo cambios propios antes de cerrar.
- No existen cambios en `spritesheet_frame_selector/`, `tests/` o `scratch/` producidos por esta fase.

## Criterio De Termino

- Documentacion V2 base creada o actualizada.
- `docs/specs/mvp.md` archivado o degradado a historico no operativo.
- PCS actualizado para que el siguiente paso sea planificar Fase 3.
- Fase 2 queda como `validado` o `listo para cierre`, no como `cerrado`, salvo instruccion explicita de cierre del usuario.

## Proximo Paso Tras Esta Fase

Preparar `docs/plans/reinicio-v2-fase-3-limpieza-arbol-activo.md`, con la preservacion Git y la documentacion V2 ya validadas como precondiciones.

## Resultado De Ejecucion

La Fase 2 fue ejecutada y validada el 2026-07-03.

Documentos V2 creados:

- `docs/specs/product_requirements.md`
- `docs/specs/mvp_v2.md`
- `docs/architecture/addon_architecture.md`
- `docs/design/visual_selector_strategy.md`
- `docs/specs/validation_plan.md`

Documento historico preservado:

- `docs/archive/mvp-original.md`

Documento historico degradado:

- `docs/specs/mvp.md`

PCS actualizado para que el siguiente paso sea preparar `docs/plans/reinicio-v2-fase-3-limpieza-arbol-activo.md`.
