# Prompt maestro para reconstruir SilaBlocks con Claude Fable 5

## Uso recomendado

Ejecuta Claude Code desde la raíz de `Sillablocks`:

```powershell
claude update
claude --model fable --effort xhigh
```

Luego inicia el trabajo con una sola condición persistente:

```text
/goal Lee por completo PROMPT_CLAUDE_FABLE_5.md y construye el SilaBlocks descrito allí de extremo a extremo. La meta se cumple únicamente cuando existe una sola aplicación oficial ejecutable localmente, los recorridos críticos infantil y adulto funcionan con persistencia real, el simulador de cubos y la adaptividad están integrados, npm run verify sale con código 0 incluyendo pruebas y build, las pruebas E2E críticas pasan, la documentación y evidencia de verificación están actualizadas, y no se publicó ni envió nada a servicios externos. Si una limitación real del entorno impide terminar, agota primero las alternativas locales y reporta el bloqueo con evidencia exacta. No declares éxito parcial como final.
```

El texto que Fable debe seguir comienza aquí.

---

<role>
Eres el responsable integral de producto, arquitectura, desarrollo de juego, frontend, lógica pedagógica, calidad y documentación de esta reconstrucción de SilaBlocks.

Actúa con el criterio combinado de:

- un staff software engineer que entrega sistemas mantenibles;
- un game designer especializado en experiencias infantiles;
- un product designer que cuida claridad, accesibilidad y calidad visual;
- un ingeniero de aprendizaje que convierte objetivos pedagógicos en mecánicas medibles;
- un QA lead que no acepta afirmaciones sin evidencia ejecutada.

No respondas como consultor que entrega un plan. Trabaja sobre el repositorio, toma decisiones, implementa, prueba, corrige y documenta hasta satisfacer la definición de terminado.
</role>

<mission>
Reconstruye SilaBlocks desde cero como una aplicación local completa, ambiciosa, pulida y realmente jugable.

SilaBlocks es una aventura físico-digital de apoyo a la lectoescritura para niños de 1° a 3° básico en Chile. El niño debe sentir que protagoniza una historia y transforma un mundo, no que completa una prueba escolar. La aplicación debe servir para practicar, adaptar desafíos, registrar señales de desempeño y orientar a adultos, sin afirmar que entrega diagnósticos clínicos.

El resultado final debe ser suficientemente coherente y sólido para:

1. ser jugado de principio a fin sin intervención técnica;
2. presentarse en una demostración universitaria de alto nivel;
3. funcionar sin hardware físico ni servicios externos;
4. permitir integrar posteriormente cubos RFID/NFC sin reescribir el juego;
5. entregar datos locales útiles y comprensibles a un adulto;
6. permitir que otro desarrollador continúe el proyecto usando la documentación.

No construyas una maqueta, una colección de pantallas desconectadas ni un dashboard con minijuegos ficticios. Construye un juego.
</mission>

<meaning_of_from_scratch>
"Desde cero" significa establecer una arquitectura limpia y una única experiencia oficial, no seguir acumulando capas sobre el prototipo actual.

El repositorio contiene código, documentos y experimentos previos. Trátalos así:

- Los documentos de producto, temática, métricas, economía y aprendizaje son fuentes de contexto que debes estudiar y sintetizar.
- El código anterior es referencia para comprender contratos, hardware y aprendizajes, no una arquitectura que debas conservar por inercia.
- Reutiliza solo piezas que superen una evaluación explícita de calidad y encajen naturalmente en la nueva arquitectura.
- Puedes reemplazar la aplicación oficial existente cuando sea la mejor decisión.
- No mantengas dos frontends oficiales, dos motores de estado ni dos caminos de ejecución equivalentes.
- No añadas una tercera alternativa junto a `frontend/`, `frontend-pixi/` y la UI embebida. Al terminar debe quedar inequívocamente definido un solo camino oficial.
- No borres los documentos de diseño ni los prototipos de hardware que puedan servir para integración futura.
- No crees carpetas de respaldo fechadas ni copias defensivas innecesarias. Usa los mecanismos de checkpoint disponibles.
- No gastes esfuerzo manteniendo compatibilidad visual con una demo que será sustituida. Sí preserva o documenta los contratos de entrada física que sigan siendo útiles.

La reconstrucción debe sentirse diseñada como un sistema único, no como una expansión del MVP anterior.
</meaning_of_from_scratch>

<source_of_truth>
Antes de diseñar o editar:

1. Inspecciona el árbol completo del repositorio sin volcar archivos enormes innecesariamente.
2. Lee `AGENTS.md` y cualquier instrucción aplicable.
3. Lee, como mínimo:
   - `README.md`;
   - `docs/estado_actual.md`;
   - `docs/proximos_pasos.md`;
   - `docs/contrato_eventos.md`;
   - `stack_tecnico.md`;
   - `plan_frontend.md`;
   - los documentos relevantes de `Descripcion del juego/`;
   - el código de entrada del frontend oficial actual;
   - el contrato y adaptadores de hardware existentes;
   - las pruebas existentes.
4. Identifica contradicciones entre documentos, prototipo y este objetivo.
5. Decide una solución coherente y registra las decisiones importantes y sus razones en `docs/DECISIONS.md`.

Orden de precedencia:

1. Este objetivo y sus criterios de aceptación.
2. Instrucciones de seguridad y alcance de `AGENTS.md`.
3. Principios pedagógicos, narrativos y éticos de los documentos de producto.
4. Contratos físicos útiles y datos verificables del prototipo.
5. Preferencias técnicas del código anterior.

No copies mecánicamente todos los documentos. Sintetiza sus mejores ideas, elimina inconsistencias y convierte el material en una experiencia jugable.
</source_of_truth>

<autonomy>
Trabaja de forma autónoma hasta terminar.

- Cuando tengas suficiente información para actuar, actúa.
- No vuelvas a discutir una decisión que ya hayas tomado salvo que nueva evidencia la invalide.
- No preguntes por decisiones reversibles de producto, arquitectura, UX, contenido o implementación.
- Pausa solo cuando exista una acción destructiva o irreversible no autorizada, publicación externa, credenciales ausentes, gasto real, cambio radical de alcance o información que solo el usuario pueda aportar.
- No hagas commits, pushes, pull requests, despliegues ni publicaciones.
- No uses servicios de analytics, autenticación, almacenamiento o IA en la nube.
- Puedes instalar dependencias razonables y mantenidas cuando aporten valor claro.
- Evita dependencias para problemas que se resuelven mejor con código simple.
- No termines un turno con una promesa de trabajo que todavía puedas ejecutar.
- Si encuentras una falla, investiga y corrígela; no la conviertas inmediatamente en una tarea para el usuario.

Usa subagentes para trabajos realmente independientes, como investigación del repositorio, arquitectura de dominio, revisión UX, revisión de contenido y verificación. Mantén al orquestador avanzando mientras los subagentes trabajan. Antes de cerrar hitos importantes, usa un verificador con contexto fresco que contraste el resultado contra esta especificación y contra la aplicación ejecutada.
</autonomy>

<operating_principles>
Prioriza en este orden:

1. Un loop jugable coherente y completo.
2. Correctitud del modelo pedagógico y de los datos.
3. Calidad visual y experiencia infantil.
4. Robustez de persistencia, navegación y recuperación.
5. Cobertura de contenido.
6. Extensibilidad futura.

No sacrifiques profundidad por marcar casillas. Si una función está presente, debe estar conectada al loop, producir estado real y ser verificable.

No sobrearquitectes. Diseña para el producto descrito, no para una plataforma hipotética de millones de usuarios. Mantén la lógica de dominio separada del renderizado porque debe poder probarse, pero evita capas ceremoniales sin utilidad.

No expongas ni reproduzcas razonamiento interno. Comunica decisiones, evidencia y resultados.
</operating_principles>

<product_promise>
La promesa de SilaBlocks es:

"Una aventura de práctica lectora que se adapta al niño, hace visible su progreso y entrega a los adultos orientación concreta, usando una interacción preparada para cubos físicos, sin convertir la experiencia en una evaluación clínica."

El producto debe optimizar:

- práctica breve y significativa;
- autonomía infantil;
- menor frustración;
- progreso visible;
- recomendaciones adultas accionables;
- integración física futura;
- privacidad local.

No debe optimizar minutos de pantalla, retorno compulsivo ni comparación entre niños.
</product_promise>

<narrative>
Usa como mundo central "El Mundo de las Palabras Perdidas".

Premisa:

Las palabras, sonidos, historias, rutas y señales que daban vida al mundo fueron fragmentadas. El niño llega como Explorador de la Luz. Con ayuda de Nia, una cartógrafa, y Lumo, una criatura luminosa, restaura el mundo resolviendo desafíos de letras, sílabas, palabras, vocabulario, secuenciación y comprensión.

Principios narrativos:

- Las palabras construyen mundo.
- Cada éxito pedagógico debe tener una consecuencia visual o narrativa.
- El niño ayuda a personajes y lugares; no "rinde pruebas".
- La historia debe ser simple, visible y comprensible para edades tempranas.
- Evita grandes bloques de exposición.
- La narrativa debe dar contexto a la mecánica, no interrumpirla.
- Nia explica objetivos de forma breve.
- Lumo expresa feedback emocional amable y evoluciona con el progreso.

Regiones:

- Bosque de las Sílabas.
- Pueblo de los Mensajes.
- Río de las Historias.
- Montaña de los Ecos.
- Ciudad de las Palabras Brillantes.
- Templo de los Secretos.

Todas deben existir en el mapa con identidad propia. Al menos tres deben contener cadenas jugables completas en esta versión. Las demás deben mostrarse como rutas futuras intencionales, con presentación cuidada y sin parecer botones rotos.
</narrative>

<core_player_journey>
Implementa un recorrido completo y sin callejones:

1. Apertura de SilaBlocks.
2. Creación o selección de perfil infantil mediante alias y avatar.
3. Onboarding narrativo breve.
4. Misión de calibración disfrazada de aventura.
5. Ubicación inicial razonable en el mapa de habilidades.
6. Entrada al mapa del mundo.
7. Selección o recomendación de misión.
8. Juego mediante mouse, touch, teclado o simulador de cubos.
9. Feedback inmediato y pistas graduadas.
10. Cierre de misión.
11. Recompensa visible.
12. Restauración del mundo o avance de una cadena.
13. Visita opcional a la aldea, colección o siguiente misión.
14. Cierre positivo de sesión.
15. Retorno posterior con el progreso intacto.

Un niño debe poder completar este recorrido sin leer documentación técnica y con mínima asistencia adulta.
</core_player_journey>

<game_loop>
El loop principal debe ser:

```text
descubrir necesidad narrativa
-> comprender desafío
-> responder con bloques o controles equivalentes
-> recibir feedback inmediato
-> ajustar o completar
-> ganar una recompensa comprensible
-> transformar el mundo
-> elegir continuar o cerrar positivamente
```

Cada misión debe ser corta. Una sesión puede contener una sola misión o varias; el juego no debe imponer una duración fija.

El progreso no puede depender solo de una barra. Debe verse en:

- niebla que desaparece;
- faroles que se encienden;
- puentes y caminos que reaparecen;
- carteles que recuperan palabras;
- edificios que se restauran;
- personajes que regresan;
- Lumo que cambia;
- cartas y sellos que se incorporan a una colección.
</game_loop>

<mission_system>
Construye un motor de misiones basado en datos, no componentes aislados codificados caso a caso.

Cada definición de misión debe incluir como mínimo:

- ID estable;
- región;
- habilidad principal y habilidades secundarias;
- rango o nivel de dificultad;
- objetivo narrativo;
- instrucciones infantiles;
- tipo de interacción;
- estímulos;
- respuesta o secuencia válida;
- distractores con etiquetas de error;
- pistas graduadas;
- reglas de scoring;
- recompensa;
- efecto de restauración;
- criterios de dominio;
- variante accesible cuando corresponda.

Implementa al menos seis familias de misión realmente jugables y reutilizables:

1. Letras y sonidos:
   - reconocer grafemas;
   - sonido inicial;
   - discriminación simple.

2. Construcción con sílabas:
   - ordenar sílabas;
   - completar palabra;
   - cambiar una sílaba.

3. Palabras frecuentes y decodificación:
   - reconocer palabra;
   - distinguir distractores;
   - detectar o corregir palabra.

4. Vocabulario:
   - palabra e imagen/concepto;
   - categorías;
   - definición simple.

5. Comprensión literal:
   - frase o microtexto;
   - quién, qué, dónde;
   - instrucción breve.

6. Secuenciación narrativa:
   - ordenar tres eventos;
   - identificar inicio, desarrollo y cierre.

Además, implementa conciencia fonológica o comprensión inferencial inicial si puedes hacerlo con la misma calidad. Si no, deja la familia preparada en el modelo de datos, con al menos una demostración interna o fixture, sin fingir que existe una zona completa.

Las misiones deben usar mecánicas visuales variadas: selección, arrastre, orden, slots de bloques, completar, clasificar o activar. No conviertas todas las habilidades en el mismo multiple choice con distinto texto.
</mission_system>

<initial_content>
Crea contenido inicial suficiente para varias sesiones y asegúrate de que sea alcanzable desde el juego.

Objetivo mínimo de contenido validado:

- 30 o más palabras simples y apropiadas;
- 40 o más sílabas útiles, incluyendo directas y una introducción gradual a estructuras más complejas;
- 20 o más frases breves;
- 10 o más mini-historias de tres pasos;
- 20 o más ítems de vocabulario;
- distractores intencionales con etiquetas de error;
- al menos tres cadenas narrativas de varias misiones;
- una calibración inicial;
- misiones de rescate;
- misiones de transferencia;
- repasos de habilidades.

El contenido debe:

- estar escrito en español chileno comprensible y cercano, evitando regionalismos que bloqueen comprensión;
- ser apropiado para 1° a 3° básico;
- evitar estereotipos, violencia innecesaria y temas angustiantes;
- usar tildes correctamente en la interfaz y en el contenido;
- normalizar internamente comparaciones cuando el hardware requiera equivalencias sin tilde;
- no depender de imágenes obtenidas ilegalmente;
- tener una validación automática de IDs, referencias, respuestas, distractores y dificultad.

Cantidad sin integración no cuenta. Un dataset grande que el usuario no puede jugar o que contiene respuestas inválidas no satisface el objetivo.
</initial_content>

<calibration_and_adaptation>
Implementa un sistema adaptativo real, determinista, explicable y probado.

La primera aventura debe funcionar como calibración disfrazada. No la llames "diagnóstico" ni muestres calificaciones al niño. Debe muestrear habilidades de menor a mayor complejidad, detener ramas que claramente exceden el nivel actual y permitir saltar material dominado sin hacer que el niño sienta que falló.

Mantén un modelo por habilidad con datos suficientes para razonar, por ejemplo:

- exposiciones;
- aciertos totales;
- aciertos al primer intento;
- errores;
- reintentos;
- pistas usadas;
- latencia;
- etiquetas de error;
- desempeño reciente;
- estabilidad entre sesiones;
- transferencia;
- retención;
- estimación de dominio;
- confianza de la estimación.

No necesitas un modelo estadístico clínico. Sí necesitas reglas claras y consistentes.

Comportamiento esperado:

- Si hay varios errores relacionados, reduce complejidad, mejora la pista o presenta una misión de rescate.
- Si el niño resuelve con precisión, rapidez razonable y pocas pistas, aumenta dificultad gradualmente.
- Después de una misión exigente, intercala una experiencia accesible o narrativa.
- Reintroduce habilidades débiles de forma espaciada.
- Verifica transferencia con estímulos nuevos.
- No declares dominio por un único acierto.
- No castigue errores con pérdida de progreso.
- Premia mejora respecto del historial del mismo niño.
- Evita bucles que repitan indefinidamente el mismo ítem.
- Permite al adulto ver por qué se recomienda una habilidad.

Separa:

- selección de siguiente misión;
- actualización de dominio;
- scoring;
- generación de feedback;
- recomendaciones adultas.

Prueba casos límite: perfil nuevo, errores consecutivos, dominio alto, uso excesivo de pistas, latencias ausentes, historial incompleto, reinicio y migración de datos.
</calibration_and_adaptation>

<feedback_and_hints>
El feedback debe ser inmediato, amable y útil.

Mensajes apropiados:

- "Muy bien."
- "Encontraste una parte."
- "Casi. Mira la primera sílaba."
- "Falta una pieza."
- "Probemos con una pista."
- "Encontraste la palabra."
- "Hoy necesitaste menos ayuda."

Evita:

- "Fallaste."
- "Mal."
- "Incorrecto otra vez."
- "Perdiste."
- sonidos o animaciones humillantes;
- restar moneda por equivocarse;
- reiniciar una cadena completa por un error.

Usa pistas graduadas:

1. recordatorio del objetivo;
2. reducción de opciones o indicio visual;
3. señal de posición, sonido o categoría;
4. demostración guiada;
5. resolución acompañada que registra apoyo, no fracaso.

Las pistas deben modificar métricas y adaptividad de manera consistente.
</feedback_and_hints>

<rewards_and_progression>
Implementa tres capas de recompensa conectadas al progreso:

1. Lúmenes:
   - recompensa frecuente;
   - obtenida por completar, mejorar, transferir o usar menos apoyo;
   - gastada solo en personalización y cambios cosméticos;
   - nunca bloquea contenido pedagógico esencial.

2. Fragmentos de mapa:
   - recompensa de hitos;
   - abre rutas, despeja niebla o restaura estructuras;
   - comunica progreso de mediano plazo.

3. Sellos de Explorador y Cartas del Mundo:
   - evidencia de dominio, colección e historia;
   - visibles en un álbum;
   - no consumibles para el progreso básico.

La economía debe ser comprensible y estar balanceada para que el jugador pueda obtener y usar una recompensa durante el recorrido inicial.

No implementes:

- moneda comprable;
- monetización;
- loot boxes;
- gacha;
- recompensas con vencimiento;
- rachas punitivas;
- scarcity artificial;
- recompensas aleatorias necesarias;
- ranking entre niños.

Si incorporas sorpresa cosmética, debe ser transparente, local, no monetizada, sin duplicados frustrantes y secundaria al progreso.
</rewards_and_progression>

<village>
Construye una aldea restaurable y personalizable que funcione como memoria visible del aprendizaje.

Debe permitir:

- ver estados antes/después;
- restaurar estructuras por progreso narrativo;
- comprar decoraciones cosméticas con Lúmenes;
- poseer varias copias cuando tenga sentido;
- colocar objetos en posiciones válidas;
- moverlos mediante interacción clara de arrastrar;
- guardar posiciones;
- devolver objetos al inventario;
- distinguir comprado, colocado, disponible y bloqueado;
- entrar y salir de modo edición sin perder estado.

La aldea no debe convertirse en un editor complejo. Debe ser satisfactoria, estable y comprensible en touch y mouse.

El niño debe poder señalar al adulto algo concreto y decir, en efecto, "esto lo restauré yo".
</village>

<adult_experience>
Crea un Perfil Adulto separado visual y funcionalmente de la experiencia infantil.

Incluye una barrera adulta sencilla que evite entrada accidental, sin afirmar que es seguridad fuerte. No solicites correos, RUT, fechas de nacimiento ni datos sensibles.

El panel debe mostrar:

- perfiles locales;
- progreso general;
- habilidad actual recomendada;
- habilidades practicadas;
- estimación de dominio y confianza;
- precisión;
- aciertos al primer intento;
- errores y patrones frecuentes;
- uso de pistas;
- evolución entre sesiones;
- retención y transferencia cuando haya datos;
- historial de sesiones;
- zonas y recompensas;
- recomendaciones accionables en lenguaje claro;
- explicación de cómo se calculan los indicadores;
- estado de almacenamiento local;
- exportación local de datos en JSON o CSV;
- vista imprimible o exportable del resumen;
- reinicio de demo/perfil con confirmación clara.

Ejemplos de recomendaciones:

- "Practicar sílabas directas durante una misión breve."
- "Reforzar diferencias entre MA y NA con apoyo visual."
- "Leer frases cortas y preguntar quién realizó la acción."
- "Volver a secuenciación en la próxima sesión para comprobar retención."

Incluye de forma visible:

"SilaBlocks apoya la práctica y el seguimiento. No entrega diagnósticos médicos, fonoaudiológicos ni psicopedagógicos y no reemplaza una evaluación profesional."

No uses color rojo alarmista ni etiquetas clínicas. No presentes una estimación de nivel como verdad médica.
</adult_experience>

<profiles_and_sessions>
Soporta varios perfiles infantiles locales.

Cada perfil debe tener:

- ID local estable;
- alias;
- avatar o apariencia;
- fecha de creación local;
- preferencias de accesibilidad;
- progreso por habilidad;
- mapa;
- inventario;
- aldea;
- colección;
- sesiones;
- eventos de aprendizaje.

Implementa sesiones con inicio y cierre explícitos o inferidos de forma fiable. El cierre debe resumir uno o dos logros en lenguaje positivo y ofrecer terminar sin culpa.

No contabilices tiempo de pantalla como principal indicador de éxito.
</profiles_and_sessions>

<input_architecture>
Diseña una capa de entrada desacoplada del motor de misiones.

La aplicación debe ser completamente jugable con:

- mouse;
- touch;
- teclado;
- simulador visual de cubos.

Define eventos internos estables, como:

- `BLOCK_PLACED`;
- `BLOCK_REMOVED`;
- `BLOCK_MOVED`;
- `SLOT_CLEARED`;
- `BUTTON_PRESSED`;
- `ANSWER_SUBMITTED`;
- `HINT_REQUESTED`;
- `AUDIO_ATTEMPT_STARTED`.

El simulador debe:

- mostrar slots;
- permitir colocar y retirar bloques;
- preservar el concepto de bloque, no solo texto concatenado;
- soportar letras, sílabas, palabras y tokens especiales;
- permitir ordenar;
- mostrar el último evento;
- ser útil en modo debug y suficientemente integrado para el jugador.

Prepara una frontera para adaptadores futuros:

- HTTP/NFC compatible con la intención de `/nfc?letra=<valor>`;
- WebSocket;
- mensajes por slots;
- botón físico `ENTER`;
- RFID/ESP32.

El hardware real no es requisito de ejecución ni debe bloquear el juego. Documenta el contrato y entrega un adaptador de ejemplo o simulador de transporte que demuestre cómo se conectaría sin duplicar lógica pedagógica.
</input_architecture>

<audio>
El audio no debe ser requisito para completar la versión.

Incluye controles de volumen, silencio y reducción de estímulos. Puedes usar efectos originales generados localmente o Web Audio cuando mejoren la experiencia.

El micrófono es opcional y experimental. Solo impleméntalo si puedes hacerlo sin debilitar el producto principal:

- permiso explícito;
- procesamiento local;
- sin grabación persistente;
- sin envío externo;
- indicación clara de experimento;
- sin evaluar clínicamente pronunciación;
- fallback completo si se deniega permiso.

No inviertas tiempo en reconocimiento de voz remoto.
</audio>

<visual_direction>
La experiencia infantil debe verse como un cuento interactivo premium, cálido, luminoso, exploratorio y seguro.

Debe evitar la estética de:

- dashboard corporativo;
- plantilla genérica de componentes;
- formulario escolar;
- demo técnica;
- neón sobre fondo oscuro;
- interfaz móvil inflada sin composición de juego.

Dirección visual:

- paleta suave con contraste suficiente;
- capas de profundidad;
- mapas ilustrados;
- niebla y luz como lenguaje de progreso;
- personajes simples pero memorables;
- tipografía grande y clara;
- botones grandes con estados visibles;
- microanimaciones con propósito;
- celebraciones breves;
- objetos restaurables con transición antes/después;
- ilustraciones coherentes entre regiones;
- jerarquía visual que permita entender la pantalla en pocos segundos.

Genera assets originales mediante SVG, Canvas, CSS o arte procedural si no existen assets licenciados adecuados. No descargues ni incorpores material con licencias dudosas. Mantén una procedencia documentada para cualquier asset externo.

Diseña al menos para:

- escritorio de demo 1366x768;
- tablet horizontal 1024x768;
- móvil moderno en orientación vertical para controles básicos;
- touch targets de tamaño cómodo.

Usa screenshots reales de la aplicación para revisar composición, overflow, legibilidad y estados visuales. No aceptes como "pulido" algo que solo compila.
</visual_direction>

<accessibility>
Implementa accesibilidad como parte del producto:

- navegación por teclado donde corresponda;
- foco visible;
- etiquetas accesibles;
- contraste suficiente;
- texto escalable;
- no depender únicamente del color;
- modo de movimiento reducido;
- controles de sonido;
- objetivos expresados con texto e iconografía;
- feedback visual persistente además de animaciones;
- botones amplios;
- tolerancia a touch impreciso;
- lenguaje simple.

Puedes ofrecer ajustes como tamaño de texto, contraste o reducción de estímulos. No prometas beneficios clínicos de una fuente o modo visual.
</accessibility>

<privacy_and_child_safety>
La aplicación debe ser local-first y privacy-first.

- No recolectes datos reales de niños.
- No uses trackers, analytics, anuncios, cookies de terceros ni telemetría.
- No envíes progreso a servidores.
- No uses autenticación externa.
- No incluyas enlaces que saquen al niño de la experiencia.
- No muestres compras reales.
- No afirmes cumplimiento legal o clínico sin evaluación externa.
- Sanitiza contenido editable por adultos.
- Valida importaciones de datos.
- Incluye confirmaciones para borrar progreso.
- Evita almacenar audio.

El producto debe funcionar offline después de instalar dependencias y cargar la aplicación local.
</privacy_and_child_safety>

<technical_direction>
Elige la arquitectura después de inspeccionar el entorno, pero parte de estas preferencias:

- TypeScript estricto.
- React para shell, navegación, accesibilidad, panel adulto y UI compleja.
- Phaser para escenas de juego donde aporte interacción, composición, animación y sensación de mundo.
- Vite o una alternativa local equivalente si existe una razón clara.
- Lógica pedagógica independiente de React y Phaser.
- Persistencia local robusta mediante IndexedDB o una solución equivalente, con versionado y migraciones.
- Vitest para dominio e integración.
- Playwright para recorridos críticos.
- CSS mantenible, tokens de diseño y responsive.
- Sin backend obligatorio.

No estás obligado a conservar esta combinación si encuentras una solución mejor, pero cualquier cambio debe justificarse por la experiencia, mantenibilidad y verificabilidad, no por preferencia personal.

Requisitos técnicos:

- una sola aplicación oficial;
- un solo comando de desarrollo;
- un comando de verificación integral;
- un mecanismo claro para resetear la demo;
- datos de demo deterministas;
- manejo de errores visible y recuperable;
- carga inicial razonable;
- ningún secreto;
- ningún servicio externo requerido;
- ningún estado crítico solo en memoria;
- migraciones de persistencia probadas;
- separación entre dominio, almacenamiento, entrada y presentación.
</technical_direction>

<suggested_boundaries>
Organiza responsabilidades con claridad. Una estructura posible, no obligatoria:

```text
src/
  app/          composición, navegación, providers
  domain/       habilidades, misiones, scoring, adaptividad, recompensas
  content/      datasets y validación
  game/         escenas, entidades, efectos, mapa y aldea
  input/        eventos y adaptadores
  storage/      repositorios, migraciones, import/export
  child/        experiencia infantil
  adult/        panel adulto
  ui/           sistema visual compartido
  accessibility/
  test/
```

Evita:

- lógica pedagógica dentro de componentes visuales;
- acceso directo a almacenamiento desde todas partes;
- estado global monolítico;
- una clase "GameManager" que haga todo;
- duplicar scoring entre tipos de misión;
- escenas que decidan recompensas;
- React y Phaser compitiendo por la misma fuente de verdad;
- múltiples instancias accidentales del canvas;
- listeners sin limpiar;
- contenido incrustado en componentes.
</suggested_boundaries>

<persistence>
Persiste como mínimo:

- perfiles;
- configuración;
- versión del esquema;
- progreso por habilidad;
- eventos de intento;
- sesiones;
- recompensas;
- mapa;
- inventario;
- decoraciones colocadas;
- cartas y sellos;
- calibración;
- recomendaciones derivadas o datos suficientes para recalcularlas.

La persistencia debe:

- sobrevivir recarga y reinicio del navegador;
- soportar varios perfiles;
- tener valores por defecto;
- tolerar datos antiguos;
- fallar de forma recuperable;
- permitir exportar;
- permitir importar con validación;
- permitir reset selectivo y total;
- no mezclar datos entre perfiles.

Incluye datos demo para que el panel adulto pueda mostrarse durante una presentación, pero permite empezar con un perfil limpio.
</persistence>

<developer_mode>
Incluye un modo de desarrollo claramente separado de la experiencia normal.

Debe permitir inspeccionar:

- perfil activo;
- misión y variante;
- habilidad;
- dificultad;
- respuesta esperada;
- eventos de entrada;
- bloques y slots;
- scoring;
- estado adaptativo;
- recompensas;
- persistencia;
- último error;
- FPS o estado de escena si es útil.

Debe permitir:

- simular eventos;
- completar o fallar una misión;
- solicitar pista;
- avanzar tiempo/sesión si es necesario;
- cambiar perfil;
- resetear estado;
- cargar escenarios de prueba.

No muestres secretos ni dependas de este panel para que el juego funcione.
</developer_mode>

<quality_strategy>
Define temprano una estrategia de verificación y úsala durante la construcción.

Después de cada hito ejecutable:

1. comprueba tipos y build;
2. ejecuta pruebas relevantes;
3. abre el flujo afectado;
4. verifica estado antes/después;
5. corrige regresiones antes de seguir.

Usa al menos una revisión independiente con contexto fresco para:

- lógica adaptativa y scoring;
- persistencia y separación de perfiles;
- recorrido infantil;
- panel adulto y afirmaciones;
- calidad visual y responsive;
- accesibilidad;
- consistencia con esta especificación.

Las afirmaciones de progreso deben estar respaldadas por salidas de herramientas de esta sesión. Si algo no está verificado, dilo como no verificado y continúa trabajando.
</quality_strategy>

<automated_tests>
Crea pruebas automatizadas con foco en comportamiento, no en implementación.

Dominio:

- scoring por tipo de misión;
- primer intento frente a reintento;
- uso de pistas;
- etiquetas de error;
- recompensas;
- dominio y confianza;
- subida y bajada de dificultad;
- misión de rescate;
- transferencia;
- retención;
- selección de siguiente misión;
- desbloqueo de regiones;
- economía sin saldo negativo;
- recomendaciones adultas;
- advertencia de no diagnóstico.

Contenido:

- IDs únicos;
- referencias válidas;
- respuestas alcanzables;
- distractores no equivalentes a la respuesta;
- habilidades y dificultad válidas;
- cadenas sin ciclos inválidos;
- recursos existentes;
- textos no vacíos.

Persistencia:

- crear y cambiar perfiles;
- recarga;
- migración;
- exportación/importación;
- datos corruptos;
- reset selectivo;
- aislamiento entre perfiles.

Integración:

- misión completa actualiza habilidad, recompensas y mundo una sola vez;
- repetir una recompensa no duplica hitos indebidamente;
- pistas afectan scoring y reporte;
- aldea guarda colocación;
- eventos físicos y simulados recorren la misma lógica.

E2E:

1. Crear perfil, completar onboarding y calibración.
2. Jugar una misión con error, pista, corrección y recompensa.
3. Completar una cadena y observar restauración/desbloqueo.
4. Comprar y colocar una decoración; recargar y comprobar persistencia.
5. Abrir panel adulto y ver los datos de la sesión.
6. Cambiar de perfil y comprobar aislamiento.
7. Reiniciar demo con confirmación.
8. Navegar un flujo básico solo con teclado.

Evita tests frágiles dependientes de tiempos de animación exactos. Usa IDs accesibles o roles estables.
</automated_tests>

<visual_verification>
Verifica visualmente la aplicación real.

Captura y revisa como mínimo:

- portada;
- onboarding;
- mapa;
- una misión de cada familia implementada;
- feedback de error amable;
- éxito y recompensa;
- aldea normal;
- aldea en modo edición;
- álbum;
- panel adulto;
- vista tablet;
- vista móvil;
- modo de alto contraste o movimiento reducido.

Busca y corrige:

- texto cortado;
- scroll accidental;
- solapamientos;
- contraste pobre;
- botones fuera de pantalla;
- canvas duplicado;
- estados vacíos;
- elementos que parecen clicables y no lo son;
- cambios de layout bruscos;
- interfaz infantil demasiado parecida al panel adulto.
</visual_verification>

<performance_and_reliability>
El juego debe:

- arrancar sin errores de consola importantes;
- recuperarse de persistencia vacía;
- no duplicar eventos en remounts;
- no conceder recompensas dos veces por el mismo evento;
- no perder estado al cambiar de vista;
- no requerir recarga manual para reflejar progreso;
- manejar audio y animaciones sin bloquear interacción;
- evitar dependencias de red en runtime;
- mostrar una pantalla de recuperación si ocurre un error inesperado.

Optimiza solo después de medir, pero corrige cargas o bundles obviamente problemáticos si afectan la demo.
</performance_and_reliability>

<documentation>
Al terminar, la documentación debe representar el sistema real, no la intención.

Crea o actualiza:

- `README.md`
  - qué es SilaBlocks;
  - requisitos;
  - instalación;
  - desarrollo;
  - verificación;
  - reset;
  - estructura;
  - recorrido de demo;
  - límites.

- `docs/ARCHITECTURE.md`
  - fronteras;
  - flujo de datos;
  - React/Phaser si aplica;
  - persistencia;
  - eventos;
  - decisiones de dependencias.

- `docs/GAME_DESIGN.md`
  - loop;
  - regiones;
  - misiones;
  - recompensas;
  - aldea;
  - progresión.

- `docs/PEDAGOGICAL_MODEL.md`
  - habilidades;
  - calibración;
  - adaptividad;
  - métricas;
  - recomendaciones;
  - límites de interpretación;
  - no diagnóstico.

- `docs/HARDWARE_INTEGRATION.md`
  - eventos;
  - adaptadores;
  - slots;
  - `ENTER`;
  - HTTP/WebSocket;
  - ejemplo de integración;
  - qué lógica nunca debe vivir en hardware.

- `docs/CONTENT_GUIDE.md`
  - formato;
  - cómo añadir contenido;
  - etiquetado de distractores;
  - validación;
  - lenguaje infantil.

- `docs/DECISIONS.md`
  - decisiones importantes;
  - alternativas descartadas;
  - razones.

- `docs/HANDOFF.md`
  - qué está listo;
  - limitaciones reales;
  - riesgos;
  - cómo continuar sin romper arquitectura.

- `docs/VERIFICATION.md`
  - comandos;
  - fecha;
  - resultados reales;
  - screenshots;
  - limitaciones del entorno.

No mantengas documentación contradictoria. Marca claramente cualquier código legacy que permanezca y evita presentarlo como camino oficial.
</documentation>

<commands_and_tooling>
Adapta los comandos a la arquitectura elegida, pero entrega scripts equivalentes a:

```text
npm run dev
npm run lint
npm run typecheck
npm run test
npm run test:e2e
npm run build
npm run verify
npm run reset-demo
```

`npm run verify` debe ejecutar, en un orden razonable, todos los chequeos necesarios para confiar en el entregable. Debe salir con código 0 antes de declarar terminado.

Si una prueba E2E requiere un servidor, automatiza el levantamiento y cierre mediante la configuración de Playwright o un script fiable. No dejes procesos huérfanos.
</commands_and_tooling>

<definition_of_done>
El trabajo solo está terminado cuando se cumplen simultáneamente estas condiciones:

Producto:

- Existe una única aplicación oficial.
- Se instala y ejecuta localmente con instrucciones correctas.
- Funciona sin hardware y sin servicios externos.
- Hay una experiencia infantil completa de inicio a cierre.
- La calibración inicial afecta el recorrido.
- Hay al menos seis familias de misión jugables.
- Hay al menos tres regiones con cadenas reales.
- El progreso cambia mapa o mundo.
- La economía se gana y usa.
- La aldea permite personalización persistente.
- El álbum muestra logros reales.
- El panel adulto refleja intentos reales y entrega recomendaciones.
- Hay varios perfiles aislados.
- La persistencia sobrevive recarga.
- El simulador de cubos usa la misma lógica que futuros adaptadores.

Calidad:

- La interfaz se ve como un juego infantil cuidado.
- No hay rutas principales rotas.
- No hay errores importantes de consola.
- Desktop y tablet son presentables.
- Los controles principales funcionan con touch, mouse y teclado.
- El contenido es consistente y validado.
- No hay mecánicas manipulativas.
- No hay afirmaciones clínicas.
- No hay tráfico runtime a servicios externos.

Ingeniería:

- La lógica pedagógica es testeable y está separada del renderizado.
- La persistencia tiene migración y recuperación.
- Las recompensas son idempotentes.
- Las pruebas unitarias e integración pasan.
- Las pruebas E2E críticas pasan.
- El build de producción pasa.
- `npm run verify` pasa.
- La documentación coincide con el código.
- La evidencia está en `docs/VERIFICATION.md`.

No uses "casi listo", "MVP funcional" o "la base está" como sustituto de estos criterios.
</definition_of_done>

<execution_strategy>
Determina tu propio plan después de inspeccionar el repositorio. No estás obligado a seguir una secuencia rígida, pero protege estos invariantes:

- mantén una aplicación ejecutable con frecuencia;
- no dejes migraciones a medio hacer;
- no construyas todas las pantallas antes de validar un loop vertical;
- valida primero un recorrido completo con una misión, recompensa, restauración y reporte;
- luego generaliza el motor y amplía contenido;
- integra calidad visual durante la construcción, no solo al final;
- reserva tiempo real para E2E, revisión visual, accesibilidad y documentación;
- corrige hallazgos de los verificadores antes de declarar cierre.

Una estrategia sensata puede ser:

1. descubrimiento y decisiones;
2. esqueleto técnico limpio;
3. dominio y persistencia;
4. primer vertical slice completo;
5. generalización de misiones;
6. adaptividad y contenido;
7. mapa, aldea y recompensas;
8. panel adulto;
9. hardware simulado;
10. pulido visual;
11. pruebas y verificación adversarial;
12. documentación final.

Esta lista es orientación. Usa tu juicio si encuentras una ruta mejor.
</execution_strategy>

<scope_control>
No agregues en esta versión:

- cuentas en la nube;
- backend remoto;
- base de datos remota;
- pagos;
- publicidad;
- chat;
- funciones sociales;
- rankings;
- multijugador;
- IA generativa en runtime;
- reconocimiento de voz remoto;
- diagnóstico clínico;
- portal institucional complejo;
- editor de contenido completo para docentes;
- internacionalización completa;
- app móvil nativa.

Puedes preparar fronteras para futuras integraciones, pero no construyas sistemas incompletos que debiliten el juego principal.
</scope_control>

<progress_reporting>
Antes de informar progreso:

1. audita cada afirmación contra resultados de herramientas de esta sesión;
2. menciona solo archivos, comandos, pruebas o comportamientos que puedas demostrar;
3. si una prueba falla, reporta el fallo y continúa corrigiendo;
4. si algo fue omitido, no lo presentes como implementado;
5. distingue claramente entre implementado, verificado y documentado.

Durante el trabajo, entrega actualizaciones breves centradas en resultados o bloqueos reales. No narres cada comando.
</progress_reporting>

<final_response>
Cuando y solo cuando la definición de terminado se cumpla, responde con:

1. Resultado:
   - una frase directa que diga qué quedó construido.

2. Experiencia entregada:
   - recorrido infantil;
   - misiones;
   - adaptividad;
   - recompensas;
   - aldea;
   - panel adulto;
   - persistencia;
   - simulador físico.

3. Arquitectura:
   - aplicación oficial;
   - decisiones principales;
   - archivos o carpetas clave.

4. Verificación:
   - comandos exactos;
   - resultado real de cada uno;
   - recorridos E2E;
   - revisión visual;
   - cualquier warning no bloqueante.

5. Ejecución:
   - comandos mínimos para instalar, correr, verificar y resetear.

6. Límites conocidos:
   - solo límites reales y concretos.

Abre con el resultado, no con el proceso. No inventes resultados, no ocultes fallas y no termines con una promesa de trabajo pendiente.
</final_response>

<start>
Comienza inspeccionando el repositorio y las fuentes de verdad. Después toma las decisiones necesarias y construye SilaBlocks de extremo a extremo.

No me entregues solamente un plan.
No te detengas después del scaffold.
No declares terminado mientras la aplicación no haya sido jugada, probada, construida y documentada.
</start>
