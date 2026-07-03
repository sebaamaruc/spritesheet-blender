# Reinicio V2 Fase 3: Limpieza Del Arbol Activo

Estado: aprobado
Autoridad: usuario
Modo de ejecucion: ejecutar sin replanificar
Estado De Ejecucion: validado

## Referencia Superior

`docs/plans/reinicio-v2-master-plan.md`

## Objetivo

Dejar el repositorio en estado minimo antes del scaffold V2.

La limpieza de esta fase es agresiva por decision del usuario: es mejor rehacer la mayoria que mantener codigo o pruebas legacy que puedan arrastrar malas practicas al addon V2.

## Estado Inicial Validado

- Fase 1 validada en `docs/plans/reinicio-v2-fase-1-preservacion.md`.
- Estado V1 preservado por Git en rama `archive/generated-addon-v1`.
- Estado V1 preservado por Git en tag `archive/generated-addon-v1-2026-07-03`.
- Fase 2 validada en `docs/plans/reinicio-v2-fase-2-documentacion-base.md`.
- Documentacion V2 vigente creada.
- `docs/specs/mvp.md` degradado a puntero historico.
- Residuos ignorados detectados: `.DS_Store`, `Imagenes_test/`, `MagicMock/`, `spritesheet_frame_selector.zip`, `__pycache__/`.

## Conservar

- `AGENTS.md`
- `.gitignore`
- `.context/`
- `docs/plans/reinicio-v2-master-plan.md`
- `docs/plans/reinicio-v2-fase-1-preservacion.md`
- `docs/plans/reinicio-v2-fase-2-documentacion-base.md`
- `docs/plans/reinicio-v2-fase-3-limpieza-arbol-activo.md`
- `docs/specs/PROJECT_VISION.md`
- `docs/specs/product_requirements.md`
- `docs/specs/mvp_v2.md`
- `docs/specs/validation_plan.md`
- `docs/specs/mvp.md`
- `docs/architecture/addon_architecture.md`
- `docs/design/visual_selector_strategy.md`
- `docs/archive/`

## Retirar Del Arbol Activo

- `spritesheet_frame_selector/`
- `tests/`
- `scratch/`
- `spritesheet_frame_selector.zip`
- `Imagenes_test/`
- `MagicMock/`
- `__pycache__/`
- `*.pyc`
- `.DS_Store`
- `.gitkeep` redundantes donde el directorio ya contiene archivos reales.

## Archivar Documentacion Fuente Obsoleta

- Archivar `docs/source/goals.md` como `docs/archive/source-goals-v1.md`.
- Archivar `docs/source/goals.proposed.md` como `docs/archive/source-goals-proposed-v1.md`.
- Mantener `docs/source/index.md` como inventario historico minimo.
- Marcar las fuentes V1 archivadas como historicas/reemplazadas.

## Pasos

1. Verificar `git status --short --ignored`.
2. Confirmar rama/tag de preservacion.
3. Detenerse si aparecen cambios trackeados inesperados fuera de `.context/`, `docs/` o `.gitignore`.
4. Archivar `docs/source/goals.md` y `docs/source/goals.proposed.md`.
5. Retirar addon V1, tests legacy y scratch.
6. Retirar residuos ignorados.
7. Limpiar `.gitkeep` redundantes.
8. Actualizar `.gitignore` solo si faltan reglas de residuos.
9. Actualizar PCS.
10. Validar que el arbol activo quedo minimo.

## Reglas

- No crear scaffold V2.
- No implementar codigo nuevo.
- No modificar documentacion V2 salvo referencias de indice/estado.
- No borrar planes.
- No borrar `docs/archive/`.
- No retirar `AGENTS.md`, `.context/`, `.gitignore` ni docs V2.

## Validaciones Obligatorias

- `git status --short --ignored` antes y despues.
- `git branch --list archive/generated-addon-v1`.
- `git tag --list archive/generated-addon-v1-2026-07-03`.
- `test ! -d spritesheet_frame_selector`.
- `test ! -d tests`.
- `test ! -d scratch`.
- `test ! -d Imagenes_test`.
- `test ! -d MagicMock`.
- `test ! -f spritesheet_frame_selector.zip`.
- `find . -name __pycache__ -o -name '*.pyc' -o -name .DS_Store` sin residuos dentro del repo.
- `.context/index.md` sin fuentes V1 como operativas.
- PCS apunta a preparar `docs/plans/reinicio-v2-fase-4-scaffold-addon-v2.md`.

## Criterio De Termino

La fase queda validada cuando:

- el arbol activo conserva solo PCS, documentacion vigente, archivo historico y archivos base;
- no queda codigo generado V1 como base activa;
- no quedan tests legacy ni scratch;
- no quedan residuos locales conocidos;
- el estado V1 sigue recuperable por rama/tag Git;
- PCS apunta a planificar Fase 4.

## Resultado De Ejecucion

La Fase 3 fue ejecutada y validada el 2026-07-03.

Se retiro del arbol activo:

- `spritesheet_frame_selector/`
- `tests/`
- `scratch/`
- `Imagenes_test/`
- `MagicMock/`
- `spritesheet_frame_selector.zip`
- residuos `.DS_Store`, `__pycache__/` y `*.pyc`
- `.gitkeep` redundantes en directorios de documentacion con archivos reales

Se archivo documentacion fuente V1:

- `docs/source/goals.md` -> `docs/archive/source-goals-v1.md`
- `docs/source/goals.proposed.md` -> `docs/archive/source-goals-proposed-v1.md`

Se actualizo `.gitignore` para cubrir `.DS_Store`.

PCS actualizado para que el siguiente paso sea preparar `docs/plans/reinicio-v2-fase-4-scaffold-addon-v2.md`.
