# MVP de curaduría visual

Estado: `implemented_v2_pending_user_validation`

Fecha: 2026-08-02

## Resultado buscado

La pantalla construye primero una biblioteca editorial de toda la evidencia real de Granja Luna.
La portada, presentación y primeras publicaciones de Facebook son una campaña medible dentro de la
biblioteca, no el único motivo para revisar o conservar un medio. La misma base servirá después para
Instagram, publicaciones comerciales y campañas.

La cobertura visual inicial es:

1. portada horizontal;
2. bienvenida a Granja Luna;
3. pollitos caseros;
4. Brahma;
5. Rhode Island Red y Plymouth Rock Barred para Black Star;
6. vida natural, cuidado o enriquecimiento;
7. imagen expresiva para abrir conversación.

La foto de perfil provisional o el logo es una pieza de identidad aparte. No se marca como cubierta
por una ráfaga de fotografías sólo para completar el contador.

## Flujo implementado

```text
media/inbox (original privado)
    -> inventario SQLite y ráfagas temporales
    -> miniatura local + copia de análisis sin EXIF
    -> brillo, contraste, nitidez heurística y hash perceptual
    -> Néstor aporta contexto real, temas y posibles pilares
    -> vista ampliada local para no decidir sólo por miniaturas
    -> favorita principal + secundaria opcional, reserva, privado o ninguna sirve
    -> motivos rápidos opcionales y usos por cada favorita
    -> botón explícito "Analizar con Gemini"
    -> sugerencia visual y de etiquetas, siempre subordinada al contexto humano
```

Las decisiones humanas y sugerencias de Gemini viven en
`runtime/state/media-library/library.sqlite3`. Los derivados viven en
`runtime/state/media-library/derivatives/`. El directorio completo está ignorado por Git; los
originales nunca se modifican.

## Límites conscientes

- La nitidez es una señal matemática de bordes, no una puntuación estética absoluta.
- El hash perceptual identifica similitud fuerte dentro de la pantalla, pero la formación de grupos
  por distancia visual todavía no.
- La pantalla actual revisa ráfagas de fotos; la curaduría completa de video es la siguiente etapa.
- La carga múltiple desde teléfono todavía no está conectada a esta API.
- Gemini recibe copias reducidas sólo después de confirmación, puede sugerir calidad, encuadre,
  etiquetas y usos, y no publica contenido.
- Ningún análisis confirma raza, salud, bienestar, disponibilidad ni fecha comercial.

## Calibración por tandas

Néstor revisó 31 de 68 grupos. Diez comparaciones humano–Gemini válidas se completaron hasta el
2026-08-03: hubo cuatro coincidencias exactas de principal, seis casos donde la principal de Gemini
estaba entre las favoritas humanas y ocho grupos con al menos una favorita compartida. El resultado
habilita asistencia y revisión dirigida, no selección autónoma. El detalle y los nuevos guardianes
se documentan en `docs/media-gemini-calibration-2026-08-03.md`.
