/* Verschlüsselt den Inhalt des Bereichs "Du" für du.enc.json (AES-256-GCM, Schlüssel per PBKDF2-SHA-256 aus dem Code).
   Aufruf:  DU_CODE='dein-code' node tools/du_encrypt.js eingabe.json du.enc.json
   eingabe.json: {"pflege": "<html>", "haare": "<html>"}. Die Klartext-Datei und den Code NICHT ins Repo legen. */
const fs = require("fs");
const { webcrypto: wc } = require("crypto");
const code = process.env.DU_CODE, [inp, out] = process.argv.slice(2);
if (!code || code.length < 10 || !inp || !out) { console.error("DU_CODE (mindestens 10 Zeichen) und zwei Dateinamen nötig."); process.exit(1); }
const ITER = 600000, b64 = (u) => Buffer.from(u).toString("base64");
(async () => {
  const data = JSON.parse(fs.readFileSync(inp, "utf8"));
  if (typeof data.pflege !== "string" || typeof data.haare !== "string") throw new Error("pflege und haare fehlen");
  const salt = wc.getRandomValues(new Uint8Array(16)), iv = wc.getRandomValues(new Uint8Array(12));
  const base = await wc.subtle.importKey("raw", new TextEncoder().encode(code.normalize("NFKC")), "PBKDF2", false, ["deriveKey"]);
  const key = await wc.subtle.deriveKey({ name: "PBKDF2", salt, iterations: ITER, hash: "SHA-256" }, base, { name: "AES-GCM", length: 256 }, false, ["encrypt"]);
  const ct = await wc.subtle.encrypt({ name: "AES-GCM", iv }, key, new TextEncoder().encode(JSON.stringify(data)));
  fs.writeFileSync(out, JSON.stringify({ v: 1, iter: ITER, salt: b64(salt), iv: b64(iv), ct: b64(new Uint8Array(ct)) }) + "\n");
  console.log("geschrieben:", out, "(" + fs.statSync(out).size + " Byte)");
})().catch((e) => { console.error(e.message); process.exit(1); });
