# Plan de Implementación: Ordered Clip List (Fase 1)

Este plan de implementación define el diseño técnico y los cambios necesarios para introducir la funcionalidad de **Ordered Clip List** (Lista de Clips Ordenada). Esta feature servirá como pilar fundamental para la posterior transición hacia el sistema de **Spritesheet Workspaces**, permitiendo la generación de múltiples spritesheets independientes desde un mismo archivo `.blend`.

---

## 1. Contexto y Objetivos

Actualmente, los clips se exportan en el orden en que fueron creados (según su índice interno en la colección de la escena). Con la introducción de **Ordered Clip List**, el usuario tendrá control explícito sobre el orden de exportación, afectando directamente a:
1. El orden físico de composición de los frames dentro del spritesheet final.
2. El orden de los registros en el archivo de metadatos JSON.
3. El orden de guardado en la secuencia de archivos individuales.

### Restricción Arquitectónica de Futuro (Workspaces)
Para evitar tener que rediseñar la Clip List en el futuro:
* **Desacoplamiento**: Todos los operadores de edición de clips, lógica de rendering, exportación y UI no deben acceder directamente a la colección de la escena (`scene.spritesheet_clips`).
* **Abstracción**: Se crea una capa de acceso indirecto (`utils.py`). En la Fase 1, esta capa resolverá la colección global de la escena. En la Fase 2, resolverá dinámicamente la colección del Workspace activo.

---

## 2. Cambios Propuestos

### Componente 1: Capa de Abstracción de Datos (`utils.py`)

#### [NEW] Función de resolución en [utils.py](../../spritesheet_frame_selector/utils.py)
Añadir una función helper para centralizar el acceso a la colección de clips y su índice activo:

```python
def get_clip_context(context):
    """
    Devuelve una tupla (collection, index_property_name, owner_data_block)
    para aislar a los operadores y UI de la estructura exacta de datos.
    Fase 1: Apoya en la colección global de la Scene.
    Fase 2: Apoyará en la colección del Workspace activo del Scene.
    """
    scene = context.scene
    return scene.spritesheet_clips, "active_clip_index", scene
```

### Componente 2: Operadores Core (`operators.py`)

#### [MODIFY] Operadores en [operators.py](../../spritesheet_frame_selector/operators.py)
* Refactorizar todos los operadores de clips existentes (`add_clip`, `remove_clip`, `duplicate_clip`) para que obtengan la colección y el índice de forma dinámica usando `get_clip_context(context)`.
* **[NEW]** Crear el operador `SPRITESHEET_OT_move_clip`:
  * **Identificador**: `spritesheet.move_clip`
  * **Propiedad**: `direction` (Enum: `'UP'`, `'DOWN'`)
  * **Lógica**: 
    1. Obtiene la colección e índice mediante `get_clip_context(context)`.
    2. Determina el índice de destino en base a `direction`.
    3. Llama al método nativo `.move(from_index, to_index)` de la colección de Blender.
    4. Actualiza la propiedad del índice activo con el nuevo índice.
    5. Retorna `{'FINISHED'}` y emite opcionalmente un reporte.

### Componente 3: Interfaz de Usuario (`panels.py`)

#### [MODIFY] Panel de Clips en [panels.py](../../spritesheet_frame_selector/panels.py)
* Actualizar el panel `SPRITESHEET_PT_clips` para incluir los botones de ordenamiento en la columna lateral de la grilla de clips.
* Utilizar iconos estándar de Blender (`TRIA_UP` y `TRIA_DOWN`) mapeados al nuevo operador de movimiento:

```python
# panels.py
col = row.column(align=True)
col.operator("spritesheet.add_clip", text="", icon='ADD')
col.operator("spritesheet.remove_clip", text="", icon='REMOVE')
col.operator("spritesheet.duplicate_clip", text="", icon='DUPLICATE')
col.separator()
col.operator("spritesheet.move_clip", text="", icon='TRIA_UP').direction = 'UP'
col.operator("spritesheet.move_clip", text="", icon='TRIA_DOWN').direction = 'DOWN'
```

### Componente 4: Pipeline de Exportación (`exporter.py`)

#### [MODIFY] Ordenamiento en [exporter.py](../../spritesheet_frame_selector/exporter.py)
* Asegurar que `export_multiple_clips` procese y renderice los clips en el orden exacto en que están posicionados en la lista ordenada de clips.
* Al escribir el archivo de metadatos JSON (`write_metadata_json`), poblar el diccionario de `clips` iterando secuencialmente sobre la lista ordenada de clips, garantizando que el JSON final refleje el orden de exportación deseado de forma idéntica a la UI.

---

## 3. Plan de Verificación

### Pruebas Automatizadas (Nuevos Tests)
1. **Test de Reordenación**:
   * Crear tres clips: `ClipA`, `ClipB`, `ClipC`.
   * Mover `ClipC` a la primera posición usando `spritesheet.move_clip(direction='UP')`.
   * Verificar que la colección de clips de la escena tenga el orden `['ClipC', 'ClipA', 'ClipB']`.
2. **Test de Consistencia en Exportación**:
   * Ejecutar el pipeline de exportación con la lista reordenada.
   * Cargar el JSON resultante y comprobar que las llaves dentro del objeto `"clips"` sigan el orden `['ClipC', 'ClipA', 'ClipB']`.
   * Comprobar que los índices iniciales y finales de los frames se calculen secuencialmente de acuerdo con este nuevo orden.

### Verificación Manual (Paso a Paso en Blender)
1. Crear dos o tres clips animados en la sidebar.
2. Utilizar los botones de flecha de la lista para alterar su orden.
3. Validar que la selección activa siga de forma correcta al clip reordenado.
4. Generar previews y exportar el spritesheet.
5. Comprobar que en la imagen de la hoja de sprites resultante, la secuencia del clip que fue movido al principio aparezca en la parte superior/izquierda (primeros cuadros).
6. Abrir el archivo `.json` de metadatos generado y constatar el orden de inserción de las animaciones.
