# Informe: Sistema de métricas lectoras para diagnóstico inicial y seguimiento de progreso en SilaBlocks

## 1. Introducción

SilaBlocks es una solución físico-digital orientada a apoyar la práctica lectora inicial en niños de 1° a 3° básico mediante cubos físicos con tecnología NFC y una experiencia digital gamificada. Su propósito no es reemplazar la evaluación profesional de docentes, fonoaudiólogos o psicopedagogos, sino entregar una herramienta de apoyo que permita registrar desempeño lector, orientar la práctica en el hogar y entregar información más clara a adultos responsables.

El problema identificado por el equipo se relaciona con la baja frecuencia de evaluación, la falta de métricas objetivas de progreso, la retroalimentación poco accionable y la dificultad de las familias para saber si el niño está avanzando o no. En entrevistas previas se levantó que muchas familias evalúan el avance “al ojo”, sin criterios comparables en el tiempo, lo que dificulta distinguir entre una mejora real, un rezago leve o una dificultad que requiere apoyo especializado.

En este contexto, se propone un sistema de métricas lectoras para SilaBlocks basado en dos objetivos: primero, estimar una línea base del nivel lector del niño; segundo, monitorear su evolución a través de sesiones sucesivas. Estas métricas deben entenderse como indicadores de tamizaje, seguimiento y práctica guiada, no como diagnóstico clínico definitivo de dislexia, trastorno del lenguaje u otra condición. La International Dyslexia Association plantea que una evaluación de dificultades lectoras debe considerar múltiples componentes, como historia del niño, habilidades fonológicas, lectura, escritura, vocabulario y comprensión, por lo que no puede reducirse a una única medición automatizada. ([International Dyslexia Association](https://dyslexiaida.org/testing-and-evaluation/?utm_source=chatgpt.com "Testing and Evaluation"))

---

## 2. Marco conceptual

La lectura inicial depende de una serie de habilidades progresivas: conciencia fonológica, reconocimiento de letras, correspondencia grafema-fonema, decodificación de sílabas y palabras, fluidez, vocabulario y comprensión. Diversos instrumentos de evaluación temprana, como DIBELS 8 y mCLASS Lectura, miden precisamente estos componentes mediante tareas breves, repetibles y orientadas a detectar riesgo lector o monitorear progreso. DIBELS 8 incluye guías de administración, puntuación y uso de datos para tomar decisiones pedagógicas, mientras que mCLASS Lectura evalúa habilidades fundacionales en español como nombramiento de letras, conciencia fonológica, principio alfabético, fluidez y comprensión. ([DIBELS](https://dibels.uoregon.edu/materials/dibels?utm_source=chatgpt.com "DIBELS 8th Edition Materials - University of Oregon"))

Además, la fluidez lectora no debe entenderse solamente como velocidad. La Agencia de Calidad de la Educación en Chile define la fluidez como una lectura precisa, expresiva y realizada a una velocidad adecuada, respetando puntuación, ritmo y entonación. Por lo tanto, un sistema de evaluación lectora debe considerar tanto la cantidad de palabras o respuestas correctas como la calidad del desempeño. ([Archivos Agencia Educación](https://archivos.agenciaeducacion.cl/ACE_Rubrica_Habilidad_Decodificacion_y_fluidez.pdf?utm_source=chatgpt.com "HABILIDAD DECODIFICACIÓN Y FLUIDEZ1"))

Para SilaBlocks, esto implica que el sistema debe medir más que aciertos y errores. Debe identificar **qué habilidad está fallando**, **qué tipo de error se repite**, **cuánto apoyo necesita el niño**, **si mejora con la práctica** y **si transfiere lo aprendido a nuevos ejercicios**.

---

## 3. Objetivo del sistema de métricas

El sistema de métricas lectoras de SilaBlocks tiene como objetivo registrar, interpretar y comunicar el desempeño lector del niño de manera simple, frecuente y accionable.

### Objetivo general

Diseñar un sistema de métricas que permita estimar el nivel lector inicial del niño, identificar habilidades descendidas y monitorear su progreso a lo largo del uso de SilaBlocks.

### Objetivos específicos

1. Medir precisión, velocidad, errores y autonomía en tareas lectoras iniciales.
    
2. Identificar patrones de error asociados a conciencia fonológica, correspondencia grafema-fonema, decodificación y comprensión.
    
3. Generar indicadores de progreso comparables entre sesiones.
    
4. Entregar información clara para apoderados, docentes y especialistas.
    
5. Evitar presentar el sistema como diagnóstico clínico, manteniéndolo como herramienta de apoyo, práctica y seguimiento.
    

---

## 4. Principio metodológico: evaluación por capas

La evaluación propuesta se organiza en cinco capas:

1. **Habilidades precursoras:** conciencia fonológica, reconocimiento de letras y asociación grafema-fonema.
    
2. **Decodificación:** lectura y construcción de sílabas, pseudopalabras y palabras reales.
    
3. **Fluidez inicial:** precisión, velocidad, ritmo, pausas y autonomía.
    
4. **Comprensión:** comprensión literal, inferencial básica y secuenciación.
    
5. **Progreso longitudinal:** mejora entre sesiones, retención y transferencia.
    

Esta estructura es coherente con la lógica de SilaBlocks, ya que el juego propone un mapa de habilidades lectoras visible, con zonas asociadas a letras, sonidos, sílabas, palabras frecuentes, vocabulario, comprensión literal y secuenciación.

---

# 5. Métricas diagnósticas iniciales

## 5.1. Precisión lectora

La precisión mide qué tan correctamente el niño responde o lee un estímulo. En SilaBlocks, puede medirse a partir de la selección correcta de cubos, formación de sílabas, construcción de palabras y respuestas a misiones.

|Métrica|Definición|Forma de cálculo|Aplicación en SilaBlocks|
|---|---|---|---|
|Porcentaje de precisión|Proporción de respuestas correctas|respuestas correctas / respuestas totales × 100|Mide aciertos en letras, sílabas, palabras o frases|
|Errores totales|Cantidad total de respuestas incorrectas|suma de errores|Registra fallos por misión|
|Errores por tipo|Clasificación cualitativa del error|conteo por categoría|Omisión, sustitución, inversión, adición, orden incorrecto|
|Errores por 10 ítems|Densidad de error|errores / ítems totales × 10|Permite comparar misiones de distinta extensión|
|Autocorrecciones|Veces que el niño corrige un error|conteo|Mide monitoreo del propio error|
|Precisión por habilidad|Aciertos en una habilidad específica|aciertos por habilidad / ítems de esa habilidad × 100|Identifica si falla en letras, sílabas, vocabulario o comprensión|

### Utilidad diagnóstica

Esta métrica permite estimar si el niño domina una habilidad o si presenta errores persistentes. Por ejemplo, si logra 90% de precisión en sílabas directas, pero solo 45% en sílabas trabadas, el sistema puede sugerir práctica focalizada en esa segunda habilidad.

---

## 5.2. Velocidad de respuesta y automatización

La velocidad permite inferir el nivel de automatización. Un niño puede responder correctamente, pero demorarse demasiado, lo que sugiere que todavía no ha consolidado la habilidad.

|Métrica|Definición|Forma de cálculo|Aplicación|
|---|---|---|---|
|Tiempo por ítem|Tiempo desde instrucción hasta respuesta|segundos por ítem|Mide rapidez al formar sílabas o palabras|
|Tiempo por misión|Duración total de una misión|tiempo final - tiempo inicial|Evalúa eficiencia global|
|Latencia inicial|Tiempo antes de realizar la primera acción|segundos antes del primer escaneo|Mide comprensión inicial o bloqueo|
|Tiempo hasta corrección|Tiempo que tarda en reparar un error|segundos desde error hasta respuesta correcta|Mide recuperación|
|Palabras correctas por minuto|Cantidad de palabras correctas leídas por minuto|palabras correctas / minutos|Requiere lectura oral o tarea equivalente|
|Sílabas correctas por minuto|Cantidad de sílabas correctas por minuto|sílabas correctas / minutos|Aplicable al uso de cubos silábicos|

### Utilidad diagnóstica

La velocidad debe interpretarse junto con la precisión. Un aumento de velocidad sin precisión no implica mejora lectora. Por ello, la métrica central debe ser **velocidad con precisión**, no velocidad aislada.

---

## 5.3. Conciencia fonológica

La conciencia fonológica mide la capacidad del niño para identificar, segmentar y manipular sonidos del lenguaje oral. Es una habilidad clave en la lectura inicial y en la detección temprana de dificultades lectoras. Instrumentos como mCLASS Lectura y DIBELS consideran medidas vinculadas a conciencia fonológica, principio alfabético y fluidez. ([Amplify](https://amplify.com/programs/mclass-lectura/?utm_source=chatgpt.com "mCLASS Lectura"))

|Métrica|Qué evalúa|Ejemplo de tarea|
|---|---|---|
|Identificación de sonido inicial|Reconocer con qué sonido comienza una palabra|“mesa empieza con /m/”|
|Identificación de sonido final|Reconocer el sonido final|“sol termina con /l/”|
|Segmentación silábica|Separar una palabra en sílabas|“casa” → “ca-sa”|
|Segmentación fonémica|Separar una palabra en sonidos|“sol” → /s/ /o/ /l/|
|Síntesis silábica|Unir sílabas para formar palabra|“ma-no” → “mano”|
|Síntesis fonémica|Unir sonidos para formar sílaba o palabra|/m/ + /a/ → “ma”|
|Reconocimiento de rimas|Identificar palabras con sonido similar|“casa” y “taza”|
|Discriminación auditiva|Diferenciar sonidos similares|/p/ vs /b/|
|Omisión de sílaba|Quitar una sílaba|“pelota sin pe” → “lota”|
|Omisión de fonema|Quitar un sonido|“sol sin /s/” → “ol”|

### Aplicación en SilaBlocks

SilaBlocks puede transformar estas tareas en misiones de juego. Por ejemplo, si el personaje pide “busca la sílaba que empieza como mamá”, el niño debe seleccionar el cubo **MA**. Si el niño confunde **MA** con **NA**, el sistema registra una confusión fonológica específica.

---

## 5.4. Reconocimiento de letras

El reconocimiento de letras mide si el niño identifica grafemas y los diferencia visualmente.

|Métrica|Qué evalúa|Aplicación|
|---|---|---|
|Letras nombradas correctamente|Reconocimiento visual de grafemas|Mostrar letra y pedir identificación|
|Tiempo para reconocer letra|Automatización visual|Medir segundos hasta escaneo correcto|
|Confusiones visuales|Dificultad con letras parecidas|b/d, p/q, m/n|
|Reconocimiento de mayúsculas|Dominio de letras en mayúscula|A, B, C|
|Reconocimiento de minúsculas|Dominio de letras en minúscula|a, b, c|
|Asociación mayúscula-minúscula|Relación entre formas de una letra|A ↔ a|
|Letras dominadas|Letras con alta precisión sostenida|≥80% o ≥90% según criterio|
|Letras críticas|Letras con errores repetidos|letras que deben reforzarse|

### Aplicación en SilaBlocks

El sistema puede generar un mapa de letras dominadas, en desarrollo y críticas. Esto permite que el apoderado no reciba solo un mensaje general como “va bajo”, sino una indicación concreta: “confunde b/d” o “requiere reforzar m/n”.

---

## 5.5. Correspondencia grafema-fonema

Esta dimensión mide si el niño asocia correctamente letras o combinaciones de letras con sonidos.

|Métrica|Qué evalúa|Ejemplo|
|---|---|---|
|Sonido correcto por grafema|Asociación letra-sonido|M → /m/|
|Precisión por grafema|% de acierto en cada letra|80% en M, 50% en N|
|Confusión fonológica|Error por sonido parecido|/p/ vs /b/|
|Confusión visual|Error por forma parecida|b/d|
|Dominio de dígrafos|Reconocimiento de ch, ll, rr, qu, gu|“que”, “gui”|
|Aplicación en sílabas|Transferencia letra-sonido a sílabas|M + A = MA|
|Aplicación en palabras nuevas|Generalización|formar “malo” aunque no la haya memorizado|
|Tiempo por asociación|Automatización|segundos hasta elegir cubo correcto|

### Utilidad diagnóstica

Esta métrica es especialmente relevante para el MVP de SilaBlocks, porque permite enfocar el prototipo en un tipo concreto de rezago: dificultades fonológicas y de correspondencia grafema-fonema.

---

# 6. Métricas de decodificación

## 6.1. Decodificación de sílabas

|Métrica|Qué evalúa|Ejemplo|
|---|---|---|
|Precisión en sílabas directas|Lectura o formación CV|ma, pa, la|
|Precisión en sílabas inversas|Lectura o formación VC|al, es, un|
|Precisión en sílabas trabadas|Lectura o formación CCV|pla, bra, tri|
|Precisión en sílabas complejas|Uso de combinaciones ortográficas|que, gui, gue|
|Tiempo por sílaba|Automatización|segundos por sílaba correcta|
|Error de orden silábico|Secuenciación incorrecta|pa-ma en vez de ma-pa|
|Error de sustitución silábica|Cambio de sílaba|ma por na|
|Error de omisión silábica|Falta una sílaba|“mesa” → “me”|
|Generalización silábica|Uso de sílabas nuevas|formar palabra no practicada|
|Nivel silábico alcanzado|Complejidad máxima dominada|directa, inversa, trabada, compleja|

### Aplicación en SilaBlocks

Esta dimensión debería ser el núcleo del prototipo inicial. La interacción con cubos permite registrar con precisión qué sílaba eligió el niño, en qué orden, cuántas veces se equivocó y cuánto tardó.

---

## 6.2. Lectura o construcción de pseudopalabras

Las pseudopalabras son combinaciones inventadas que respetan reglas del idioma. Sirven para evaluar decodificación real, porque el niño no puede depender de memoria visual.

|Métrica|Qué evalúa|Ejemplo|
|---|---|---|
|Pseudopalabras correctas|Decodificación fonológica|“mepo”, “lusa”, “tami”|
|Tiempo por pseudopalabra|Automatización|segundos por respuesta|
|Errores fonológicos|Cambio de sonido|“mepo” → “nepo”|
|Errores de orden|Inversión de sílabas|“tami” → “mita”|
|Errores por estructura|Dificultad según patrón|CV, CVC, CCV|
|Autocorrecciones|Detección de error|corrige luego de equivocarse|
|Comparación palabra/pseudopalabra|Diferencia entre memoria y decodificación|lee “casa”, falla en “lasa”|

### Utilidad diagnóstica

Si el niño lee bien palabras familiares, pero falla en pseudopalabras, puede estar usando memoria visual o adivinación por contexto en vez de decodificación fonológica sólida.

---

## 6.3. Lectura o formación de palabras reales

|Métrica|Qué evalúa|Ejemplo|
|---|---|---|
|Palabras correctas|Reconocimiento o construcción adecuada|“mano”, “mesa”|
|Palabras frecuentes correctas|Automatización de vocabulario común|mamá, casa, sol|
|Palabras infrecuentes correctas|Decodificación más exigente|palabras menos familiares|
|Tiempo por palabra|Automatización|segundos por palabra|
|Error por longitud|Dificultad según extensión|palabras de 2, 3 o más sílabas|
|Error por frecuencia|Dificultad según familiaridad|frecuente vs infrecuente|
|Error ortográfico específico|Dificultad con combinaciones|que, gui, rr|
|Lectura silabeada|Falta de automatización|ca-sa|
|Lectura global incorrecta|Adivinación visual|“camisa” por “casa”|
|Nivel de palabra alcanzado|Complejidad máxima dominada|monosílaba, bisílaba, trisílaba|

---

# 7. Métricas de fluidez lectora

La fluidez integra precisión, velocidad y expresividad. En SilaBlocks, algunas métricas pueden capturarse directamente mediante la interacción físico-digital, mientras que otras requieren audio o evaluación profesional. La Agencia de Calidad de la Educación destaca que la fluidez implica leer de forma precisa, expresiva y a velocidad adecuada, por lo que no debe reducirse a palabras por minuto. ([Diagnóstico Integral](https://diagnosticointegral.agenciaeducacion.cl/documentos/Mineduc/Reactivacion/10-fluidez%20lectora.pdf?utm_source=chatgpt.com "¿Qué es la fluidez lectora?"))

|Métrica|Qué evalúa|Captura en MVP|
|---|---|---|
|Precisión|Respuestas correctas|Sí|
|Velocidad|Tiempo por respuesta|Sí|
|Palabras correctas por minuto|Lectura oral fluida|Solo con audio|
|Ritmo lector|Regularidad de lectura|Solo con audio|
|Pausas adecuadas|Respeto de puntuación|Solo con audio/texto leído|
|Pausas indebidas|Detenciones dentro de palabra o frase|Solo con audio|
|Prosodia|Entonación y expresividad|Solo con audio|
|Lectura palabra a palabra|Falta de agrupación significativa|Observación/audio|
|Lectura por grupos de sentido|Fluidez sintáctica|Observación/audio|
|Expresividad|Uso de tono adecuado|Observación/audio|

### Recomendación

Para la Entrega 2, SilaBlocks debería comprometerse principalmente con **precisión, velocidad de respuesta y errores por tipo**. La medición de entonación y prosodia puede plantearse como desarrollo futuro con captura de audio.

---

# 8. Métricas de comprensión

## 8.1. Comprensión literal

La comprensión literal mide si el niño identifica información explícita.

|Métrica|Qué evalúa|Ejemplo|
|---|---|---|
|Preguntas literales correctas|Recuperar información explícita|¿Quién aparece?|
|Identificación de personaje|Reconocer sujeto de la historia|“el perro”|
|Identificación de acción|Comprender qué ocurrió|“corrió”|
|Identificación de lugar|Reconocer dónde ocurrió|“en la plaza”|
|Identificación de objeto|Reconocer elemento clave|“la pelota”|
|Orden de eventos simples|Secuencia explícita|primero/después|
|Respuesta con apoyo visual|Comprensión apoyada en imagen|elegir imagen correcta|
|Respuesta sin apoyo visual|Comprensión autónoma|responder sin pista|
|Necesidad de relectura|Dependencia de repetir|conteo|
|Precisión en instrucción|Comprensión de consigna|ejecuta lo pedido|

## 8.2. Comprensión inferencial inicial

|Métrica|Qué evalúa|Ejemplo|
|---|---|---|
|Inferencia causal|Por qué ocurrió algo|“¿Por qué se escondió?”|
|Predicción|Qué podría pasar después|“¿Qué crees que hará?”|
|Emoción del personaje|Deducir estado emocional|feliz, triste, asustado|
|Intención del personaje|Comprender motivo|“quería ayudar”|
|Relación causa-consecuencia|Conectar hechos|si llueve, se moja|
|Uso de pistas del texto|Justificación|responde usando información dada|
|Inferencia con imagen|Apoyo visual|deducir desde escena|
|Inferencia sin imagen|Mayor exigencia|deducir desde texto solo|

## 8.3. Comprensión global y secuenciación

|Métrica|Qué evalúa|Ejemplo|
|---|---|---|
|Idea principal|De qué trata el texto|“un niño perdió su perro”|
|Resumen oral|Relatar lo leído|inicio, desarrollo, cierre|
|Orden narrativo|Secuenciar eventos|1-2-3|
|Problema-solución|Identificar conflicto y resolución|perdió/encontró|
|Detalles relevantes|Distinguir información importante|personaje, lugar, acción|
|Coherencia del relato|Orden lógico|sin saltos|
|Retención inmediata|Recuerda tras leer|responde después de una pausa breve|
|Comprensión de instrucción escrita|Ejecuta consigna|formar palabra indicada|

### Aplicación en SilaBlocks

La comprensión puede implementarse mediante misiones donde el niño deba formar una palabra respuesta, ordenar cubos para completar una frase o elegir con cubos una alternativa vinculada a una historia breve.

---

# 9. Métricas de vocabulario y lenguaje oral

El vocabulario es relevante porque la comprensión lectora depende tanto de decodificar palabras como de entender su significado. En entrevistas del equipo también apareció la baja exposición a vocabulario en el hogar como un factor que puede afectar la comprensión y el aprendizaje lector.

|Métrica|Qué evalúa|Ejemplo|
|---|---|---|
|Vocabulario receptivo|Comprende palabra escuchada o leída|elegir imagen de “árbol”|
|Vocabulario expresivo|Produce palabra adecuada|nombrar objeto|
|Asociación palabra-imagen|Relación significado-representación|unir “sol” con imagen|
|Definición simple|Explica significado|“¿qué es una casa?”|
|Categorías semánticas|Agrupa por significado|animales, comida, objetos|
|Sinónimos|Reconoce significado similar|feliz/contento|
|Antónimos|Reconoce opuestos|grande/chico|
|Vocabulario en contexto|Deduce palabra en oración|“el perro ladra”|
|Palabras nuevas aprendidas|Adquisición durante sesiones|nuevas palabras dominadas|
|Retención de vocabulario|Recuerda después de días|evaluación posterior|

---

# 10. Métricas socioemocionales asociadas a la lectura

Aunque no son métricas lectoras puras, son relevantes porque la lectura inicial suele estar asociada a frustración, rechazo, cansancio o inseguridad. El diseño de SilaBlocks ya plantea que el juego debe promover progreso visible, retorno positivo y cierre emocionalmente saludable, evitando dinámicas de presión o compulsión.

|Métrica|Qué evalúa|Método|
|---|---|---|
|Frustración observable|Señales de bloqueo o rechazo|observación|
|Persistencia ante error|Sigue intentando después de fallar|conteo de reintentos|
|Tolerancia a la corrección|Acepta feedback sin abandonar|observación|
|Deseo de repetir|Quiere jugar otra misión|pregunta directa|
|Confianza percibida|Se siente capaz|escala simple|
|Cierre positivo|Termina tranquilo o motivado|observación|
|Evitación|Rechaza iniciar lectura|observación|
|Autonomía emocional|Requiere menos apoyo adulto|registro de ayuda|
|Orgullo por logro|Reconoce su avance|pregunta: “¿qué lograste?”|

---

# 11. Métricas de progreso

## 11.1. Progreso dentro de una sesión

|Métrica|Qué mide|Ejemplo|
|---|---|---|
|Mejora intra-sesión de precisión|Aciertos al inicio vs final|50% → 80%|
|Reducción de errores|Menos fallos en la misma habilidad|6 errores → 2 errores|
|Reducción de pistas|Menos ayuda requerida|4 pistas → 1 pista|
|Menor tiempo de respuesta|Mayor automatización|12 s → 7 s|
|Corrección después de feedback|Aprende tras error|reintento correcto|
|Persistencia|Continúa pese a error|no abandona|
|Generalización breve|Aplica regla a ítem similar|ma-pa → ma-no|

## 11.2. Progreso entre sesiones

|Métrica|Qué mide|Ejemplo|
|---|---|---|
|Cambio en precisión|Sesión inicial vs sesión actual|55% → 82%|
|Cambio en velocidad|Menor tiempo por respuesta|10 s → 6 s|
|Cambio en errores por tipo|Menos inversiones u omisiones|5 inversiones → 1|
|Cambio en uso de pistas|Mayor autonomía|3 pistas → 0|
|Habilidades dominadas|Nodos completados|sílabas directas dominadas|
|Habilidades en riesgo|Errores persistentes|trabadas siguen bajas|
|Retención a 7 días|Mantiene habilidad después de pausa|repite acierto una semana después|
|Transferencia|Resuelve ítems nuevos|palabra no entrenada|
|Tasa de mejora semanal|Ritmo de avance|+8 puntos porcentuales/semana|
|Consistencia|Desempeño estable|3 sesiones seguidas sobre 80%|

---

# 12. Índice SilaBlocks de Progreso Lector

Se propone construir un indicador propio llamado **Índice SilaBlocks de Progreso Lector**, entendido como una síntesis de desempeño para orientar la práctica, no como diagnóstico clínico.

## 12.1. Componentes del índice

|Componente|Peso sugerido|Justificación|
|---|--:|---|
|Precisión|30%|Mide dominio de la habilidad|
|Velocidad ajustada|20%|Mide automatización sin sacrificar precisión|
|Tipo y reducción de errores|20%|Identifica dificultad específica|
|Uso de pistas|15%|Mide autonomía|
|Retención y transferencia|15%|Mide aprendizaje más estable|

## 12.2. Interpretación sugerida

|Puntaje|Interpretación|
|--:|---|
|0-39|Requiere apoyo intensivo en la habilidad evaluada|
|40-59|Habilidad en desarrollo inicial|
|60-79|Avance adecuado, requiere práctica adicional|
|80-100|Habilidad consolidada para el nivel trabajado|

## 12.3. Ejemplo de reporte para apoderados

> “Durante esta semana, el niño mejoró en sílabas directas. Su precisión subió de 58% a 82%, necesitó menos pistas y redujo errores de inversión. Se recomienda continuar con misiones de sílabas directas y comenzar introducción gradual a sílabas inversas.”

Este tipo de reporte responde directamente al dolor identificado en entrevistas: la necesidad de que las familias reciban información clara, objetiva y accionable, en vez de indicaciones generales como “está bajo” o “debe practicar más”.

---

# 13. Métricas medibles mediante el juego y los cubos físicos

Una ventaja central de SilaBlocks es que la interacción físico-digital permite registrar datos de desempeño sin transformar la experiencia en una evaluación escolar explícita. Cada vez que el niño escanea un cubo, el sistema puede guardar qué elemento eligió, en qué orden lo hizo, cuánto tiempo demoró, si necesitó pistas, si corrigió errores y si logró completar la misión. Esto permite convertir la práctica lectora en información objetiva, comparable y accionable.

Esta lógica es coherente con la propuesta de SilaBlocks de utilizar progreso visible, recompensas comprensibles y avance por habilidades, evitando que el juego mida únicamente tiempo de uso o permanencia en pantalla. Además, la narrativa del “Mundo de las Palabras Perdidas” permite que cada actividad correcta tenga una consecuencia visible dentro del juego, como restaurar caminos, señales, mapas o zonas del mundo.

## 13.1. Datos base que debe registrar el sistema

Para calcular las métricas lectoras, SilaBlocks debe registrar automáticamente un conjunto mínimo de eventos por misión.

|Dato registrado|Descripción|Ejemplo|
|---|---|---|
|ID de misión|Identificador de la misión realizada|Misión 03: sílabas directas|
|Habilidad evaluada|Dimensión lectora trabajada|sílabas directas, grafema-fonema, vocabulario|
|Estímulo objetivo|Respuesta esperada por el sistema|MA + PA|
|Secuencia escaneada|Cubos realmente usados por el niño|MA + BA|
|Orden de escaneo|Secuencia temporal de cubos|primero MA, luego BA|
|Tiempo de inicio|Momento en que comienza la tarea|10:04:21|
|Tiempo de respuesta|Tiempo hasta completar la respuesta|18 segundos|
|Número de intentos|Veces que intenta resolver|2 intentos|
|Número de errores|Respuestas incorrectas antes del acierto|1 error|
|Tipo de error|Clasificación del error cometido|sustitución silábica|
|Uso de pistas|Si pidió o recibió ayuda|1 pista visual|
|Corrección|Si logró reparar el error|sí|
|Resultado final|Éxito, éxito con ayuda o no logrado|éxito con ayuda|
|Nivel de dificultad|Complejidad de la misión|básico, intermedio, avanzado|

A partir de estos datos se pueden calcular métricas de precisión, velocidad, autonomía, tipo de error, progreso, retención y transferencia.

---

# 13.2. Precisión por habilidad lectora

## Qué mide

La precisión indica qué porcentaje de respuestas fueron correctas. Es la métrica más básica para estimar si el niño domina o no una habilidad.

## Cómo se mide en SilaBlocks

El sistema compara la secuencia esperada con la secuencia escaneada por el niño.

Ejemplo:

- Misión: formar **MA-PA**.
    
- Respuesta esperada: `[MA, PA]`.
    
- Respuesta del niño: `[MA, PA]`.
    
- Resultado: correcta.
    

Otro ejemplo:

- Respuesta esperada: `[MA, PA]`.
    
- Respuesta del niño: `[MA, BA]`.
    
- Resultado: incorrecta por sustitución silábica.
    

## Fórmula

> Precisión = respuestas correctas / respuestas totales × 100

## Aplicación

|Habilidad|Cómo se mediría|
|---|---|
|Reconocimiento de letras|El niño debe escanear la letra solicitada|
|Sílabas directas|El niño debe formar sílabas como MA, PA, SA|
|Sílabas complejas|El niño debe formar o reconocer sílabas como PLA, BRA, QUE|
|Palabras simples|El niño debe ordenar cubos para formar una palabra|
|Vocabulario|El niño debe elegir el cubo que corresponde a una imagen o concepto|
|Comprensión literal|El niño debe responder una pregunta usando cubos|

## Utilidad

Permite decir, por ejemplo:

> “El niño presenta 85% de precisión en sílabas directas, pero solo 45% en sílabas trabadas.”

Esto transforma la retroalimentación en información específica y accionable.

---

# 13.3. Tipo de error lector

## Qué mide

No basta con saber que el niño se equivocó. Es necesario saber **cómo se equivocó**, porque distintos errores apuntan a dificultades distintas.

## Cómo se mide en SilaBlocks

El sistema compara la respuesta esperada con la secuencia escaneada y clasifica el error.

|Tipo de error|Definición|Ejemplo|
|---|---|---|
|Omisión|Falta un cubo o sonido esperado|Esperado: MA-PA / Respuesta: MA|
|Sustitución|Cambia una letra o sílaba por otra|Esperado: MA / Respuesta: NA|
|Inversión|Cambia el orden de los elementos|Esperado: MA-PA / Respuesta: PA-MA|
|Adición|Agrega un elemento no solicitado|Esperado: SOL / Respuesta: SO-LA|
|Confusión visual|Confunde grafemas parecidos|b/d, p/q|
|Confusión fonológica|Confunde sonidos similares|p/b, m/n, t/d|
|Error de secuenciación|Ordena mal una palabra o frase|LA-CASA → CASA-LA|
|Error persistente|Repite el mismo error varias veces|confunde siempre MA con NA|
|Error recuperado|Se equivoca, pero luego corrige|MA-BA → borra → MA-PA|
|Error no recuperado|No logra corregir|abandona o requiere ayuda|

## Aplicación

Cada misión debe tener una respuesta esperada y distractores diseñados intencionalmente. Por ejemplo, si se quiere medir discriminación entre **MA** y **NA**, se incluyen ambos cubos como opciones. Si el niño elige **NA**, el sistema no solo registra “incorrecto”, sino “confusión fonológica m/n”.

## Utilidad

Permite entregar reportes como:

> “El error más frecuente fue la sustitución de sílabas con sonidos parecidos. Se recomienda reforzar discriminación fonológica entre MA, NA y PA.”

Esto responde mejor al problema detectado en entrevistas: la retroalimentación escolar suele ser general y poco accionable, sin indicar exactamente qué habilidad debe reforzarse.

---

# 13.4. Tiempo de respuesta

## Qué mide

El tiempo de respuesta permite estimar el nivel de automatización. Un niño puede responder correctamente, pero demorarse mucho, lo que indica que la habilidad aún no está consolidada.

## Cómo se mide en SilaBlocks

El sistema registra el tiempo desde que aparece la instrucción hasta que el niño completa la respuesta.

Ejemplo:

- Instrucción aparece: 10:00:00.
    
- Niño escanea último cubo: 10:00:18.
    
- Tiempo de respuesta: 18 segundos.
    

## Métricas derivadas

|Métrica|Cómo se calcula|Qué indica|
|---|---|---|
|Tiempo por ítem|segundos por respuesta|velocidad básica|
|Tiempo por misión|duración total de misión|carga general|
|Tiempo hasta primer cubo|segundos hasta iniciar|comprensión inicial o bloqueo|
|Tiempo entre cubos|segundos entre escaneos|fluidez de construcción|
|Tiempo hasta corrección|segundos desde error hasta corrección|recuperación|
|Tiempo por respuesta correcta|segundos solo en respuestas correctas|automatización real|

## Utilidad

Permite distinguir tres casos:

|Caso|Interpretación|
|---|---|
|Alta precisión + bajo tiempo|habilidad consolidada|
|Alta precisión + alto tiempo|habilidad correcta, pero poco automatizada|
|Baja precisión + alto tiempo|habilidad descendida o confusa|

Ejemplo de reporte:

> “Aunque logró formar las palabras correctamente, demoró más que en sesiones anteriores. Esto sugiere que la habilidad aún requiere práctica para automatizarse.”

---

# 13.5. Uso de pistas y nivel de ayuda

## Qué mide

El uso de pistas mide cuánta ayuda necesita el niño para completar una misión. Es una métrica clave de autonomía.

## Cómo se mide en SilaBlocks

El sistema registra cada vez que el niño solicita una pista o cuando el adulto/interfaz entrega ayuda.

Las pistas pueden clasificarse por nivel:

|Nivel de pista|Tipo de ayuda|Ejemplo|
|---|---|---|
|Pista 0|Sin ayuda|completa solo|
|Pista 1|Ayuda visual leve|se ilumina el primer cubo|
|Pista 2|Ayuda sonora|se reproduce el sonido objetivo|
|Pista 3|Ayuda parcial|se muestra parte de la secuencia|
|Pista 4|Ayuda directa|se indica el cubo correcto|

## Fórmula

> Índice de autonomía = 1 - pistas usadas / pistas máximas disponibles

## Utilidad

Permite medir si el niño está avanzando aunque todavía cometa errores.

Ejemplo:

- Sesión 1: 5 pistas.
    
- Sesión 2: 3 pistas.
    
- Sesión 3: 1 pista.
    

Aunque la precisión no haya llegado al 100%, hay una mejora clara en autonomía.

Ejemplo de reporte:

> “El niño aún requiere apoyo en sílabas inversas, pero redujo el uso de pistas de 5 a 2, lo que indica mayor independencia.”

---

# 13.6. Número de intentos por misión

## Qué mide

El número de intentos muestra cuántas veces el niño necesita probar antes de llegar a la respuesta correcta.

## Cómo se mide en SilaBlocks

Cada secuencia enviada o validada por el niño cuenta como un intento.

Ejemplo:

- Intento 1: MA-BA.
    
- Intento 2: MA-PA.
    
- Resultado: correcto en segundo intento.
    

## Indicadores

|Métrica|Interpretación|
|---|---|
|1 intento correcto|dominio alto|
|2 intentos|error recuperable|
|3 o más intentos|dificultad significativa|
|muchos intentos sin éxito|posible frustración o habilidad no consolidada|

## Utilidad

Permite diferenciar entre error leve y dificultad persistente. No es lo mismo equivocarse una vez y corregir que repetir el mismo error cinco veces.

---

# 13.7. Corrección de errores

## Qué mide

Evalúa si el niño puede detectar y reparar un error después de recibir feedback.

## Cómo se mide en SilaBlocks

El sistema registra si, después de una respuesta incorrecta, el niño logra corregirla usando una nueva secuencia.

Ejemplo:

- Respuesta esperada: MA-PA.
    
- Primer intento: MA-BA.
    
- Feedback: “Revisa el segundo cubo.”
    
- Segundo intento: MA-PA.
    
- Resultado: error corregido.
    

## Métricas derivadas

|Métrica|Cálculo|Interpretación|
|---|---|---|
|Tasa de corrección|errores corregidos / errores totales × 100|capacidad de reparar|
|Tiempo de corrección|segundos desde error hasta acierto|recuperación|
|Corrección con ayuda|corrige después de pista|aprendizaje guiado|
|Corrección sin ayuda|corrige solo|monitoreo autónomo|
|Error persistente|repite error pese a feedback|dificultad específica|

## Utilidad

Esta métrica es muy valiosa porque muestra aprendizaje durante la sesión, no solo resultado final.

Ejemplo:

> “El niño cometió errores inicialmente, pero corrigió el 80% después del feedback. Esto indica que la retroalimentación del juego fue comprendida.”

---

# 13.8. Retención entre sesiones

## Qué mide

La retención indica si el niño mantiene una habilidad aprendida después de un intervalo de tiempo.

## Cómo se mide en SilaBlocks

El sistema repite, en una sesión posterior, algunos ítems equivalentes o similares a los ya trabajados.

Ejemplo:

- Día 1: trabaja sílabas MA, PA, LA.
    
- Día 4: se le presenta una nueva misión con MA, PA, LA en otro orden.
    
- Si mantiene precisión alta, hay retención.
    

## Fórmula

> Retención = desempeño posterior / desempeño inicial consolidado × 100

## Aplicación

|Tipo de retención|Ejemplo|
|---|---|
|Retención inmediata|repetir al final de la misma sesión|
|Retención a corto plazo|repetir al día siguiente|
|Retención semanal|repetir después de 5 a 7 días|

## Utilidad

Permite diferenciar aprendizaje real de desempeño momentáneo.

Ejemplo de reporte:

> “La habilidad de sílabas directas se mantuvo estable después de 5 días, por lo que puede pasar a una dificultad mayor.”

---

# 13.9. Transferencia a palabras o combinaciones nuevas

## Qué mide

La transferencia mide si el niño puede aplicar una habilidad en un contexto nuevo, no solo repetir algo memorizado.

## Cómo se mide en SilaBlocks

Después de practicar una estructura, el sistema presenta una palabra o combinación nueva que usa la misma regla.

Ejemplo:

- Práctica: MA-PA, MA-NO, PA-TO.
    
- Transferencia: formar MA-LE o PA-LA.
    
- Si lo logra, aplica la regla a un estímulo nuevo.
    

## Indicadores

|Métrica|Qué indica|
|---|---|
|Transferencia correcta|aplica habilidad a nuevo ítem|
|Transferencia con pista|necesita ayuda parcial|
|Transferencia fallida|no generaliza|
|Tiempo en transferencia|automatización de la regla|
|Error en transferencia|tipo de dificultad persistente|

## Utilidad

Es una de las métricas más sólidas para demostrar aprendizaje.

Ejemplo:

> “El niño no solo repitió sílabas trabajadas, sino que logró formar una palabra nueva usando la misma estructura. Esto sugiere transferencia de la habilidad.”

---

# 13.10. Nivel de dificultad alcanzado

## Qué mide

Indica hasta qué complejidad puede avanzar el niño dentro del mapa lector.

## Cómo se mide en SilaBlocks

Cada misión se clasifica por nivel de dificultad.

|Nivel|Tipo de tarea|Ejemplo|
|---|---|---|
|Nivel 1|Reconocimiento de letras|M, P, A|
|Nivel 2|Sílabas directas|MA, PA, SA|
|Nivel 3|Palabras bisílabas simples|MAMA, PATO|
|Nivel 4|Sílabas inversas|AL, ES, IN|
|Nivel 5|Sílabas trabadas|PLA, BRA, TRA|
|Nivel 6|Palabras con dificultad ortográfica|QUE, GUI, RR|
|Nivel 7|Frases breves|LA MESA|
|Nivel 8|Comprensión literal simple|responder desde una historia|

El sistema registra el nivel máximo en el que el niño alcanza un criterio mínimo de desempeño.

## Criterio sugerido

Una habilidad puede considerarse “dominada” si el niño logra:

- al menos 80% de precisión,
    
- en dos sesiones distintas,
    
- con baja cantidad de pistas,
    
- y con tiempo de respuesta estable.
    

## Utilidad

Permite mostrar progreso como avance por etapas:

> “Actualmente domina letras y sílabas directas. Está en desarrollo en palabras bisílabas y aún requiere apoyo en sílabas inversas.”

---

# 13.11. Consistencia del desempeño

## Qué mide

La consistencia evalúa si el rendimiento del niño es estable o variable.

## Cómo se mide en SilaBlocks

El sistema compara el desempeño de una misma habilidad en distintas sesiones.

Ejemplo:

|Sesión|Precisión en sílabas directas|
|---|--:|
|Sesión 1|75%|
|Sesión 2|82%|
|Sesión 3|80%|

En este caso hay desempeño estable. En cambio:

|Sesión|Precisión en sílabas directas|
|---|--:|
|Sesión 1|90%|
|Sesión 2|45%|
|Sesión 3|70%|

Aquí hay alta variabilidad, por lo que no conviene considerar la habilidad consolidada.

## Utilidad

Evita declarar mejora por un solo buen resultado aislado.

Ejemplo de reporte:

> “La precisión ha mejorado, pero todavía es variable entre sesiones. Se recomienda seguir practicando antes de avanzar de nivel.”

---

# 13.12. Comprensión literal mediante misiones

## Qué mide

Mide si el niño comprende información explícita presentada en una instrucción, imagen, frase o microhistoria.

## Cómo se mide en SilaBlocks

El juego presenta una situación breve y el niño responde usando cubos.

Ejemplo:

- La pantalla muestra: “Lumo encontró un sol.”
    
- Pregunta: “¿Qué encontró Lumo?”
    
- Opciones de cubos: SOL, PAN, MAR.
    
- Respuesta correcta: SOL.
    

## Métricas

|Métrica|Cómo se mide|
|---|---|
|Preguntas literales correctas|aciertos / preguntas totales|
|Tiempo de respuesta|segundos hasta elegir cubo|
|Relectura requerida|si necesita escuchar/ver de nuevo|
|Respuesta con apoyo visual|si responde gracias a imagen|
|Respuesta sin apoyo visual|si responde solo desde texto|
|Error semántico|elige palabra relacionada pero incorrecta|

## Utilidad

Permite avanzar desde decodificación hacia comprensión sin depender todavía de textos largos.

---

# 13.13. Vocabulario y asociación semántica

## Qué mide

Evalúa si el niño entiende el significado de palabras y puede asociarlas con imágenes, categorías o contextos.

## Cómo se mide en SilaBlocks

El sistema muestra una imagen, categoría o escena, y el niño debe seleccionar el cubo correcto.

Ejemplo:

- Imagen: sol.
    
- Cubos disponibles: SOL, SAL, PAN.
    
- Respuesta esperada: SOL.
    

También puede medir categorías:

- Instrucción: “Busca un animal.”
    
- Cubos disponibles: GATO, MESA, SOL.
    
- Respuesta esperada: GATO.
    

## Métricas

|Métrica|Cómo se mide|
|---|---|
|Asociación palabra-imagen|% de respuestas correctas|
|Reconocimiento de categoría|elige palabra de una categoría|
|Confusión semántica|elige palabra relacionada pero incorrecta|
|Vocabulario nuevo aprendido|palabras nuevas acertadas después de práctica|
|Retención de vocabulario|mantiene acierto en otra sesión|

## Utilidad

Sirve para abordar no solo lectura mecánica, sino también comprensión de significado.

---

# 13.14. Secuenciación de palabras o eventos

## Qué mide

Evalúa si el niño puede ordenar elementos en una secuencia lógica o lingüística.

## Cómo se mide en SilaBlocks

El niño debe escanear cubos en el orden correcto.

Ejemplo de secuencia lingüística:

- Objetivo: “LA CASA”.
    
- Cubos: CASA, LA.
    
- Respuesta correcta: LA + CASA.
    

Ejemplo de secuencia narrativa:

- Historia: “Primero Lumo encuentra una llave. Después abre la puerta.”
    
- Cubos: LLAVE, PUERTA.
    
- Respuesta esperada: LLAVE + PUERTA.
    

## Métricas

|Métrica|Cómo se mide|
|---|---|
|Orden correcto|secuencia correcta / total|
|Error de inversión|invierte elementos|
|Tiempo de ordenamiento|segundos para completar|
|Intentos hasta ordenar|cantidad de intentos|
|Secuencia con apoyo|requiere pista visual o sonora|

## Utilidad

Esta métrica conecta lectura con comprensión de estructura, orden y sentido.

---

# 13.15. Persistencia ante dificultad

## Qué mide

Evalúa si el niño continúa intentando después de equivocarse. Aunque no es una métrica lectora pura, es importante para medir la sostenibilidad de la práctica.

## Cómo se mide en SilaBlocks

El sistema registra si, después de un error, el niño:

- vuelve a intentar,
    
- usa una pista,
    
- corrige,
    
- abandona,
    
- requiere intervención adulta.
    

## Métricas

|Métrica|Cómo se mide|
|---|---|
|Reintentos después de error|cantidad de nuevos intentos|
|Abandono de misión|misión no completada|
|Uso de pista en vez de abandono|señal de continuidad|
|Corrección posterior|error seguido de acierto|
|Tiempo de permanencia útil|tiempo hasta completar o abandonar|

## Utilidad

Permite evaluar si la experiencia reduce frustración y sostiene la práctica lectora. Esto es relevante porque en el proceso de descubrimiento se observó que la lectura puede asociarse a frustración, resistencia y agotamiento en el hogar.

---

# 13.16. Métricas de avance para el panel de apoderados

Las métricas anteriores deben traducirse en información simple para el adulto. El apoderado no necesita ver todos los datos técnicos, sino una síntesis clara.

## Indicadores recomendados para el panel

|Indicador para apoderado|Datos usados|Ejemplo de visualización|
|---|---|---|
|Habilidad más fuerte|precisión alta y estable|“Domina sílabas directas”|
|Habilidad a reforzar|baja precisión o muchos errores|“Reforzar sílabas inversas”|
|Error más frecuente|clasificación de errores|“Confunde MA con NA”|
|Progreso semanal|precisión actual vs anterior|“Subió de 60% a 78%”|
|Autonomía|pistas usadas|“Necesitó menos ayuda”|
|Velocidad|tiempo por respuesta|“Responde más rápido”|
|Retención|desempeño en sesión posterior|“Mantuvo lo aprendido”|
|Recomendación|regla automática|“Practicar 10 min sílabas MA/NA”|

## Ejemplo de reporte

> “Esta semana, el niño trabajó sílabas directas. Su precisión aumentó de 62% a 84%, redujo el uso de pistas de 4 a 1 y corrigió la mayoría de sus errores después del feedback. El error más frecuente fue confundir MA con NA. Se recomienda reforzar discriminación de sonidos m/n antes de avanzar a sílabas más complejas.”

Este tipo de reporte es más útil que una calificación general porque muestra progreso, dificultad específica y acción sugerida.

---

# 13.17. Protocolo de medición dentro del juego

Para llevar a cabo estas mediciones, cada sesión de SilaBlocks debería seguir una estructura fija.

## Paso 1: Selección de habilidad

El sistema o el adulto define qué habilidad se evaluará.

Ejemplo:

- letras,
    
- sílabas directas,
    
- sílabas inversas,
    
- palabras simples,
    
- vocabulario,
    
- comprensión literal.
    

## Paso 2: Misión de línea base

El niño realiza una misión breve sin ayuda inicial. Esta misión permite estimar su nivel de entrada.

Datos registrados:

- precisión,
    
- errores,
    
- tiempo,
    
- pistas,
    
- intentos.
    

## Paso 3: Práctica guiada

El juego entrega feedback, pistas graduadas y nuevas misiones similares.

Datos registrados:

- errores corregidos,
    
- reducción de pistas,
    
- mejora en tiempo,
    
- persistencia.
    

## Paso 4: Misión de transferencia

El sistema presenta un estímulo nuevo con la misma regla.

Ejemplo:

- Si practicó MA-PA, se le pide formar MA-NO.
    
- Si practicó SOL, se le pide reconocer SAL/SOL.
    

Datos registrados:

- capacidad de generalizar,
    
- errores en estímulos nuevos,
    
- tiempo de respuesta.
    

## Paso 5: Reporte al apoderado

El sistema genera un resumen simple:

- habilidad trabajada,
    
- precisión,
    
- error principal,
    
- nivel de autonomía,
    
- progreso respecto a la sesión anterior,
    
- recomendación de práctica.
    

## Paso 6: Repetición en sesión posterior

En una sesión futura, se repiten algunos ítems equivalentes para medir retención.

---

# 13.18. Priorización para el MVP

Para la primera versión del prototipo, no conviene intentar medir todas las dimensiones. Se recomienda priorizar las métricas más directamente capturables con cubos NFC.

|Prioridad|Métrica|Razón|
|---|---|---|
|Alta|Precisión por habilidad|Fácil de medir y muy informativa|
|Alta|Tipo de error|Diferencia a SilaBlocks de una app simple|
|Alta|Tiempo de respuesta|Mide automatización|
|Alta|Uso de pistas|Mide autonomía|
|Alta|Intentos por misión|Mide dificultad real|
|Alta|Corrección de errores|Mide aprendizaje durante la sesión|
|Alta|Retención|Mide si el avance se mantiene|
|Alta|Transferencia|Mide si el niño generaliza|
|Media|Comprensión literal|Requiere diseño de microhistorias|
|Media|Vocabulario|Requiere banco de imágenes/palabras|
|Media|Secuenciación narrativa|Requiere contenido adicional|
|Baja por ahora|Prosodia|Requiere audio|
|Baja por ahora|Entonación|Requiere audio|
|Baja por ahora|Palabras por minuto oral|Requiere lectura grabada|
|Baja por ahora|Diagnóstico clínico|Requiere especialista|

---

# 13.19. Limitaciones de medición con cubos

Aunque los cubos NFC permiten capturar muchas métricas relevantes, existen dimensiones que no pueden medirse de forma completa solo con interacción física.

|Dimensión|¿Se puede medir con cubos?|Limitación|
|---|---|---|
|Precisión en selección|Sí|mide respuesta, no pronunciación|
|Orden de sílabas|Sí|depende de diseño de misión|
|Tiempo de respuesta|Sí|no equivale siempre a velocidad lectora oral|
|Tipo de error|Sí|requiere clasificación previa de distractores|
|Uso de pistas|Sí|mide autonomía dentro del juego|
|Retención|Sí|requiere sesiones repetidas|
|Transferencia|Sí|requiere ítems nuevos|
|Prosodia|No|requiere audio|
|Entonación|No|requiere audio o evaluador|
|Coordinación respiratoria|No|requiere análisis fonoaudiológico|
|Articulación fonética|No|requiere audio y criterio profesional|
|Diagnóstico de dislexia|No|requiere evaluación clínica multidimensional|

Por lo tanto, la formulación correcta para SilaBlocks es que el sistema permite medir **indicadores de desempeño lector y progreso**, no emitir diagnósticos clínicos definitivos.

---

# 13.20. Síntesis

Las métricas más viables de medir con el juego y los cubos físicos son precisión por habilidad, tipo de error, tiempo de respuesta, uso de pistas, número de intentos, corrección de errores, retención y transferencia. Estas métricas pueden capturarse automáticamente mediante el registro de cada escaneo NFC y la comparación entre la respuesta esperada y la respuesta real del niño.

El valor de este sistema está en que transforma una práctica lúdica en datos útiles para el seguimiento. El niño vive la actividad como una misión dentro del juego, mientras el sistema registra información objetiva sobre su desempeño. Para el apoderado, estos datos se traducen en reportes simples que indican qué habilidad está mejorando, qué error se repite y qué conviene practicar después. Esto permite que SilaBlocks actúe como una herramienta de apoyo y seguimiento lector en el hogar, manteniendo una separación clara respecto del diagnóstico clínico profesional.

---

# 14. Métricas que requieren evaluación profesional

Existen dimensiones que SilaBlocks no debería prometer medir autónomamente en su versión inicial.

|Métrica o dimensión|Por qué requiere especialista|
|---|---|
|Diagnóstico de dislexia|Requiere evaluación multidimensional|
|Diagnóstico de TEL/TDL|Requiere evaluación lingüística profesional|
|Articulación fonética fina|Requiere criterio fonoaudiológico|
|Coordinación fono-respiratoria|Requiere análisis de voz y respiración|
|Comprensión auditiva clínica|Requiere instrumentos específicos|
|Memoria fonológica|Requiere pruebas estandarizadas|
|Perfil cognitivo-lingüístico completo|Excede una app de práctica|
|Diagnóstico diferencial|Requiere integrar historia, conducta, contexto y pruebas|

Por ello, la formulación correcta es:

> SilaBlocks no diagnostica clínicamente; entrega indicadores frecuentes de desempeño lector para orientar práctica, seguimiento y eventual derivación.

---

# 15. Integración con la experiencia de juego

La narrativa de “El Mundo de las Palabras Perdidas” permite integrar las métricas lectoras sin que el niño sienta que está siendo evaluado. Cada zona del juego puede asociarse a una habilidad específica: letras y sonidos, sílabas, palabras frecuentes, vocabulario, secuenciación y comprensión. Esto permite que el progreso lector se traduzca en progreso visible dentro del mundo: caminos que reaparecen, señales que vuelven a leerse o zonas que se desbloquean.

|Zona o misión|Habilidad medida|Métrica principal|
|---|---|---|
|Bosque de las Sílabas|sílabas directas|precisión, tiempo, errores|
|Montaña de los Ecos|conciencia fonológica|discriminación de sonidos|
|Pueblo de los Mensajes|palabras frecuentes|reconocimiento y vocabulario|
|Río de las Historias|secuenciación|orden narrativo|
|Ciudad de las Palabras|vocabulario|asociación semántica|
|Templo de los Secretos|comprensión|inferencias simples|

Esta estructura permite que la evaluación no sea percibida como una prueba escolar, sino como una serie de misiones con sentido narrativo.

---

# 16. Propuesta de implementación para Entrega 2

Para la Entrega 2, se recomienda presentar un protocolo de validación con métricas acotadas, medibles y defendibles.

## 16.1. Métricas mínimas recomendadas

|Dimensión|Métrica|Objetivo|
|---|---|---|
|Precisión|% de respuestas correctas|Medir dominio inicial|
|Error dominante|tipo de error más frecuente|Identificar dificultad|
|Velocidad|tiempo por ítem|Medir automatización|
|Autonomía|cantidad de pistas|Medir independencia|
|Progreso|diferencia entre sesión 1 y sesión 2|Medir mejora|
|Retención|repetición correcta posterior|Medir aprendizaje estable|
|Transferencia|resolución de ítem nuevo|Medir generalización|
|Comprensión adulta|apoderado entiende el reporte|Validar utilidad del panel|

## 16.2. Protocolo breve de prueba

1. Aplicar una misión inicial de línea base.
    
2. Registrar precisión, errores, tiempo y pistas.
    
3. Entregar feedback y práctica guiada.
    
4. Aplicar una segunda misión equivalente.
    
5. Comparar desempeño inicial y final.
    
6. Mostrar reporte al apoderado.
    
7. Preguntar si entiende qué habilidad debe reforzar.
    

## 16.3. Indicadores de éxito del prototipo

|Indicador|Criterio esperado|
|---|---|
|El sistema identifica habilidad descendida|Sí / No|
|El sistema registra tipo de error|Sí / No|
|El niño completa misión sin frustración alta|Sí / No|
|El reporte muestra progreso comprensible|≥70% de adultos lo entiende|
|El apoderado identifica qué practicar|≥70% responde correctamente|
|El niño mejora en una habilidad dentro de la sesión|aumento de precisión o reducción de pistas|
|El sistema entrega recomendación accionable|Sí / No|

---

# 17. Discusión

El sistema de métricas propuesto permite que SilaBlocks se diferencie de una aplicación educativa convencional, ya que no se limita a entregar ejercicios, sino que registra desempeño, identifica patrones de error y comunica progreso. Esto responde a tres dolores centrales del proceso de descubrimiento: evaluación lenta, falta de seguimiento continuo y retroalimentación poco accionable.

Además, el sistema es coherente con una lógica de innovación basada en evidencia. No se afirma que el prototipo diagnostique trastornos lectores, sino que permite levantar señales tempranas, monitorear desempeño y orientar la práctica. Esta distinción es importante para evitar promesas excesivas y mantener credibilidad frente a docentes, fonoaudiólogos y psicopedagogos.

La principal fortaleza del sistema es que transforma la práctica lectora en datos simples y accionables. En vez de informar que el niño “lee mal” o “está atrasado”, SilaBlocks podría indicar que presenta baja precisión en sílabas trabadas, alta cantidad de inversiones, uso frecuente de pistas o baja retención entre sesiones. Esa información permite orientar mejor el trabajo en casa y facilitar la comunicación con especialistas.

---

# 18. Conclusión

SilaBlocks debe medir la lectura infantil mediante un sistema de métricas por capas, considerando habilidades precursoras, decodificación, fluidez inicial, comprensión, vocabulario y progreso longitudinal. Las métricas más relevantes para el MVP son precisión, tipo de error, tiempo de respuesta, uso de pistas, retención y transferencia. Estas dimensiones pueden capturarse mediante la interacción físico-digital con cubos NFC y permiten entregar reportes claros a los adultos.

El sistema no debe presentarse como diagnóstico clínico, sino como una herramienta de tamizaje, seguimiento y práctica guiada. Su valor principal está en transformar la lectura en una experiencia medible, comprensible y accionable, reduciendo la incertidumbre de las familias y facilitando intervenciones más tempranas.

En síntesis, las métricas lectoras de SilaBlocks permiten pasar de una evaluación subjetiva y esporádica a un seguimiento frecuente, específico y orientado a la mejora. Esto fortalece tanto la propuesta pedagógica como la propuesta de valor del proyecto.

---

# Referencias utilizadas

- DIBELS 8th Edition, University of Oregon: evaluación de habilidades lectoras iniciales, administración, puntuación y uso de datos para decisiones pedagógicas. ([DIBELS](https://dibels.uoregon.edu/materials/dibels?utm_source=chatgpt.com "DIBELS 8th Edition Materials - University of Oregon"))
    
- mCLASS Lectura, Amplify: evaluación en español para habilidades fundacionales como nombramiento de letras, conciencia fonológica, principio alfabético, fluidez y comprensión. ([Amplify](https://amplify.com/programs/mclass-lectura/?utm_source=chatgpt.com "mCLASS Lectura"))
    
- Agencia de Calidad de la Educación, Chile: rúbrica de decodificación y fluidez lectora, con énfasis en precisión, expresividad y velocidad adecuada. ([Archivos Agencia Educación](https://archivos.agenciaeducacion.cl/ACE_Rubrica_Habilidad_Decodificacion_y_fluidez.pdf?utm_source=chatgpt.com "HABILIDAD DECODIFICACIÓN Y FLUIDEZ1"))
    
- International Dyslexia Association: criterios generales de evaluación de dificultades lectoras y dislexia. ([International Dyslexia Association](https://dyslexiaida.org/testing-and-evaluation/?utm_source=chatgpt.com "Testing and Evaluation"))
    
- Informe de Entrega 1 Grupo 14: hallazgos de entrevistas sobre falta de métricas objetivas, evaluación lenta, baja trazabilidad y retroalimentación poco accionable.