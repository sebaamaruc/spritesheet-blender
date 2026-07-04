# Plan Fase 5e1 Spike - Selector Modal Y Preview Modes

Estado: aprobado
Autoridad: usuario
Modo de ejecucion: ejecutar sin replanificar
Estado De Ejecucion: validado
Referencia superior: `docs/plans/reinicio-v2-master-plan.md`
Plan rector: `docs/plans/reinicio-v2-fase-5-workspace-root-vertical-slices.md`

## Resumen

Ejecutar un spike tecnico antes de crear el plan correctivo de UX del selector/playback.

El objetivo es decidir con evidencia si el selector debe pasar de UI nativa a superficie modal/custom y como deben modelarse los modos de preview necesarios para `SOLID`, textura/material y render con luz.

## Decisiones De Usuario Que Guian El Spike

- Avanzar hacia superficie modal/custom.
- `selector_mode` debe vivir en `.blend`.
- Los thumbnails actuales son demasiado pequenos para servir como preview.
- El playback debe mostrar una vista grande del frame actual.
- El selector debe usar contornos/estado visual en vez de texto y checkbox por celda.
- Revisar solucion para previews en solid, textura/material y luz renderizada.

## Alcance

Incluir:

- Investigar APIs viables para un selector modal/custom en Blender 5.1.
- Confirmar estrategia de cleanup para draw handlers, timers, previews e imagenes cargadas.
- Revisar opciones tecnicas de preview modes:
  - solid/Workbench;
  - textura/material;
  - rendered/EEVEE Next o engine activo equivalente.
- Evaluar si `preview_size` debe ampliarse y ofrecer presets.
- Definir donde vivirian `selector_mode`, `preview_mode` y settings visuales.
- Crear documento de resultados y recomendacion.

Excluir:

- No implementar la nueva UI final.
- No reemplazar el selector actual.
- No modificar el modelo persistente final salvo documentar recomendacion.
- No generar assets dentro del repo.
- No avanzar a render final/export.

## Validaciones

- Inspeccion local de APIs Blender disponibles.
- Pruebas Blender background cuando sean suficientes.
- Si la parte modal requiere GUI real, documentar limitacion y dejar validacion manual obligatoria para 5e1.
- No dejar `__pycache__`, `.DS_Store`, renders, previews ni outputs dentro del repo.

## Entregable

Crear `docs/specs/selector_modal_preview_modes_spike.md` con:

- hallazgos;
- riesgos;
- decision recomendada;
- impacto en modelo;
- impacto en preview cache;
- impacto en plan `5e1-selector-playback-ux`;
- validaciones necesarias.

## Criterio De Termino

El spike queda validado cuando existe una recomendacion clara para:

- tipo de superficie del selector;
- modo persistente del selector;
- modos de preview;
- tamano de preview/cache;
- forma de mostrar playback grande;
- siguiente plan especifico.

## Resultado De Ejecucion

Estado: validado
Fecha: 2026-07-03

Entregable:

- `docs/specs/selector_modal_preview_modes_spike.md`

Validaciones ejecutadas:

- Blender 5.1.1 inspecciono engines, shading types, `render.opengl`, `render.render`, draw handlers y APIs GPU.
- Blender background confirmo que `bpy.ops.render.opengl` falla sin contexto OpenGL.
- Blender background confirmo que `bpy.ops.render.render(write_still=True)` crea PNG temporal fuera del repo.
- Se elimino el PNG temporal generado en `/private/tmp`.

Decision resultante:

- Crear `docs/plans/reinicio-v2-fase-5e1-selector-playback-ux.md` antes de avanzar a render final.
