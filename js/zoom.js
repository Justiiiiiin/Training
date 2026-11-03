/* Fitness Coach: Zoom sperren wie in einer App, sofort beim Laden (nicht erst nach dem Sync-Abgleich).
   - Android/Chrome: touch-action: pan-x pan-y in styles.css (kein Pinch, kein Doppeltipp-Zoom).
   - iOS Safari und Home-Bildschirm-App: Safari ignoriert user-scalable=no seit iOS 10, deshalb hier die
     iOS-eigenen Gesten-Ereignisse und Touch-Bewegungen mit Skalierung abfangen.
   - Hineinzoomen beim Antippen von Feldern verhindert die Mindestgröße von 16 px für Eingaben (styles.css).
   Größere Schrift gibt es stattdessen unter Einstellungen > Textgröße (bis 200 %), die Zoom-Funktionen
   des Systems (Bedienungshilfen) bleiben nutzbar. */
(function () {
  var stop = function (e) { if (e.cancelable) e.preventDefault(); };
  ["gesturestart", "gesturechange", "gestureend"].forEach(function (n) { document.addEventListener(n, stop, { passive: false }); });
  document.addEventListener("touchmove", function (e) { if (typeof e.scale === "number" && e.scale !== 1) stop(e); }, { passive: false });
})();
