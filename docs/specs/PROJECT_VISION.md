# SpriteSheet Frame Selector — Visión del Proyecto

## Qué es esta herramienta

SpriteSheet Frame Selector es una herramienta Blender-first enfocada en pipelines reales de producción para videojuegos, web, VFX stylized y animaciones basadas en spritesheets.

El objetivo principal NO es crear un editor general de spritesheets ni competir con software como Aseprite, TexturePacker o herramientas de pixel art.

El objetivo real es resolver un problema específico y poco cubierto:

“Seleccionar visualmente, desde Blender, qué frames de una animación deben convertirse en spritesheet.”

La herramienta debe sentirse:
- rápida;
- técnica;
- enfocada;
- integrada al workflow de Blender;
- cómoda para iterar;
- minimalista;
- orientada a producción.

El producto debe priorizar:
1. reducción de fricción;
2. velocidad de iteración;
3. selección visual clara;
4. preview inmediato;
5. exportación rápida;
6. estabilidad;
7. persistencia del trabajo;
8. UX funcional.

No debe priorizar:
- exceso de features;
- UI extremadamente decorativa;
- workflows complejos;
- convertirse en una suite de animación;
- convertirse en un software externo gigante.

---

# Filosofía de UX

La UX es el producto principal.

La exportación de spritesheets ya existe en muchas herramientas.
Lo realmente diferenciador es la experiencia de seleccionar frames de animación dentro de Blender de forma rápida, visual e iterativa.

La sensación buscada es:
- generar previews;
- revisar movimiento;
- descartar frames inútiles;
- reproducir la animación resultante;
- iterar rápidamente;
- exportar inmediatamente.

La selección de frames debe sentirse:
- ligera;
- visual;
- directa;
- cómoda;
- rápida de aprender.

El usuario debe poder:
- generar previews en segundos;
- entender rápidamente la animación;
- seleccionar frames con pocos clicks;
- reproducir el resultado antes de exportar;
- exportar sin pasos innecesarios.

La herramienta debe reducir el costo mental de:
“¿Qué frames realmente necesito?”

---

# Playback Preview — Parte central del producto

El playback preview es una de las features más importantes del proyecto.

La herramienta debe permitir reproducir la animación resultante usando únicamente los frames seleccionados.

Esto es fundamental porque el usuario necesita validar:
- readability;
- timing;
- sensación del movimiento;
- cantidad de frames;
- recortes de animación;
- fluidez del spritesheet final.

El workflow esperado es:

1. Generar previews.
2. Seleccionar/deseleccionar frames.
3. Presionar Play.
4. Ver exactamente cómo se verá la animación exportada.
5. Ajustar selección.
6. Exportar.

El preview debe:
- ser inmediato;
- usar previews cacheados;
- no volver a renderizar;
- sentirse ligero y responsivo.

La experiencia debe parecerse más a:
“editar ritmo y legibilidad de una animación”
que simplemente “marcar checkboxes”.

---

# Multi-clip workflow — Dirección principal

La herramienta debe diseñarse desde el inicio pensando en múltiples animaciones/clips.

No debe pensarse como:
“un exportador de una sola animación”.

Debe pensarse como:
“un sistema para construir spritesheets completos de varias animaciones.”

El usuario debe poder:
- trabajar clip por clip;
- seleccionar frames distintos para cada animación;
- reproducir clips individualmente;
- exportar clips individuales;
- combinar múltiples clips en un único spritesheet/atlas.

Ejemplos:
- idle
- walk
- run
- attack
- jump

Todo dentro del mismo personaje/proyecto.

Aunque el MVP pueda empezar exportando clips individuales, la arquitectura debe diseñarse desde el inicio para:
- multi-clip atlas;
- metadata por clip;
- export combinado;
- playback independiente;
- persistencia completa.

---

# JSON Metadata — Filosofía

El JSON metadata NO es el producto principal.

La herramienta está centrada en UX y workflow visual.

Sin embargo, cuando múltiples clips se exportan a un mismo atlas/spritesheet, el JSON sí se vuelve importante para pipelines reales.

El JSON debe mantenerse:
- simple;
- técnico;
- legible;
- útil para runtime.

Debe permitir identificar:
- qué frames pertenecen a qué animación;
- índices de inicio y fin;
- cantidad de frames;
- FPS opcional;
- dimensiones básicas.

No debe convertirse en un sistema complejo de metadata.

---

# Identidad técnica del proyecto

La herramienta debe mantenerse:
- modular;
- extensible;
- mantenible;
- desacoplada.

La arquitectura debe permitir:
- reemplazar el sistema de composición;
- reemplazar el visual selector;
- mejorar performance sin rehacer todo;
- agregar nuevos export backends;
- agregar atlas multi-clip;
- agregar metadata más adelante;
- optimizar render/export independientemente.

No se deben acoplar:
- lógica de selección;
- rendering;
- previews;
- playback;
- composición;
- UI;
- persistencia.

---

# Qué NO debe pasar

El proyecto NO debe convertirse en:
- editor de pixel art;
- editor avanzado de sprites;
- sistema de rigging;
- timeline alternativo;
- herramienta de animación completa;
- software externo enorme;
- framework de runtime;
- addon lleno de features irrelevantes.

Cada nueva feature debe responder:
“¿Esto ayuda realmente a seleccionar, revisar y exportar frames de animación más rápido?”

Si la respuesta es no, probablemente no pertenece al core del proyecto.

---

# Dirección visual

La UI debe sentirse:
- técnica;
- clara;
- compacta;
- enfocada en información útil.

No se busca:
- skeuomorphism;
- diseño excesivamente moderno;
- UI experimental pesada.

La UI debe favorecer:
- velocidad;
- legibilidad;
- accesibilidad;
- feedback visual claro;
- estabilidad.

La herramienta debe priorizar:
- fluidez;
- claridad;
- feedback inmediato;
- facilidad de iteración.

No estética compleja.

---

# Prioridades de desarrollo

Orden correcto de prioridades:

1. Flujo funcional completo.
2. Persistencia estable.
3. Playback preview usable.
4. Selector visual usable.
5. Export correcto.
6. Performance.
7. Refinamiento UX.
8. Features secundarias.
9. Pulido visual.

Nunca sacrificar estabilidad por features.

---

# Público objetivo

La herramienta apunta principalmente a:
- technical artists;
- generalistas 3D;
- indie developers;
- artistas stylized;
- pipelines web;
- workflows de spritesheets;
- VFX flipbooks;
- billboard/impostor workflows;
- animaciones realtime optimizadas.

No apunta inicialmente a:
- pixel artists puros;
- ilustradores 2D;
- usuarios casuales;
- edición manual frame-by-frame.

---

# Visión a futuro (no MVP)

Posibles features futuras:

- atlas multi-clip avanzado;
- visualización de frames similares;
- export metadata expandida;
- presets por engine/runtime;
- detección de cambios en preview cache;
- batch exports;
- render profiles;
- preview timeline/scrubbing;
- export normal/depth/emissive;
- integrations con Unreal/Unity;
- compositor backend acelerado;
- GPU accelerated packing;
- reordenamiento manual de frames;
- frame tagging;
- presets por proyecto;
- visualizador de diferencias entre frames;
- frame deduplication assist (manual, nunca automática).

Estas features NO deben afectar negativamente el núcleo simple y rápido de la herramienta.

---

# Filosofía final

La herramienta debe sentirse como:
“Una extensión natural del workflow de Blender para spritesheets.”

No como:
“Una app externa metida dentro de Blender.”

El usuario debería sentir que:
- genera previews rápido;
- selecciona frames intuitivamente;
- reproduce resultados inmediatamente;
- exporta sin fricción;
- mantiene control creativo total;
- evita renderizar frames innecesarios;
- acelera iteración;
- puede construir spritesheets completos de múltiples animaciones cómodamente.

El objetivo no es maximizar cantidad de features.
El objetivo es crear una herramienta pequeña, sólida y sorprendentemente útil.