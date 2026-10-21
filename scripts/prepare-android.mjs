// Duelo de Cartas — ajusta el proyecto Android que crea «npx cap add android».
// Se ejecuta en GitHub Actions (ver .github/workflows/android.yml). Si algo no cuadra, se detiene con un mensaje claro.
import fs from 'node:fs';
import path from 'node:path';

const ROOT = process.cwd();
const A = path.join(ROOT, 'android');
const PKG = JSON.parse(fs.readFileSync(path.join(ROOT, 'capacitor.config.json'), 'utf8')).appId;
const cfg = JSON.parse(fs.readFileSync(path.join(ROOT, 'app.config.json'), 'utf8'));
const read = p => fs.readFileSync(p, 'utf8');
const write = (p, s) => fs.writeFileSync(p, s);
const must = (ok, msg) => { if (!ok) { console.error('✖ ' + msg); process.exit(1); } };
const log = msg => console.log('✔ ' + msg);

must(fs.existsSync(A), 'No existe la carpeta android/: falta correr «npx cap add android».');

// 1) MainActivity propia (pantalla completa)
const javaDir = path.join(A, 'app/src/main/java', ...PKG.split('.'));
must(fs.existsSync(javaDir), 'No existe ' + javaDir + ' (¿cambió el appId?).');
for (const f of fs.readdirSync(path.join(ROOT, 'native/java'))) fs.copyFileSync(path.join(ROOT, 'native/java', f), path.join(javaDir, f));
const kt = path.join(javaDir, 'MainActivity.kt'); if (fs.existsSync(kt)) fs.rmSync(kt);
log('Java copiado en ' + path.relative(ROOT, javaDir));

// 2) AndroidManifest: cámara (para escanear el código QR del multijugador)
const manP = path.join(A, 'app/src/main/AndroidManifest.xml');
let man = read(manP);
const add = [];
if (!man.includes('android.permission.CAMERA"')) add.push('    <uses-permission android:name="android.permission.CAMERA" />');
if (!man.includes('android.hardware.camera"')) add.push('    <uses-feature android:name="android.hardware.camera" android:required="false" />');
if (!man.includes('android.permission.INTERNET"')) add.push('    <uses-permission android:name="android.permission.INTERNET" />');
if (!man.includes('android.permission.WRITE_EXTERNAL_STORAGE"')) add.push('    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" android:maxSdkVersion="29" />');
if (!man.includes('android.permission.READ_EXTERNAL_STORAGE"')) add.push('    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" android:maxSdkVersion="32" />');
if (add.length) { const before = man; man = man.replace(/(\n\s*<application\b)/, '\n    <!-- Multijugador (internet y cámara para el QR) y guardar copias de seguridad -->\n' + add.join('\n') + '$1'); must(man !== before, 'No encontré <application> en el AndroidManifest.'); }
write(manP, man);
log('AndroidManifest: internet, cámara y almacenamiento (Android 10 o menos)');

// 3) app/build.gradle: versión
const gP = path.join(A, 'app/build.gradle');
let g = read(gP);
const code = Math.max(1, parseInt(process.env.GITHUB_RUN_NUMBER || '1', 10));
must(/versionCode\s+\d+/.test(g) && /versionName\s+"[^"]*"/.test(g), 'No encontré versionCode/versionName en app/build.gradle.');
g = g.replace(/versionCode\s+\d+/, `versionCode ${code}`).replace(/versionName\s+"[^"]*"/, `versionName "${cfg.versionName}"`);
// Firma fija para los APK de prueba: así cada APK nuevo se instala ENCIMA del anterior (sin desinstalar
// ni perder cartas). Sin esto, GitHub crea una llave distinta en cada compilación y Android rechaza la
// actualización. Esta llave es solo para pruebas (es pública); Google Play usa la llave de subida de los secrets.
fs.copyFileSync(path.join(ROOT, 'native/firma-de-prueba.jks'), path.join(A, 'app/firma-de-prueba.jks'));
if (!g.includes('firma-de-prueba.jks')) {
  const before = g;
  g = g.replace(/\nandroid\s*\{/, `\nandroid {\n    signingConfigs {\n        debug {\n            storeFile file('firma-de-prueba.jks')\n            storePassword 'android'\n            keyAlias 'pruebas'\n            keyPassword 'android'\n        }\n    }`);
  must(g !== before, 'No encontré el bloque android { } en app/build.gradle.');
}
write(gP, g);
log(`app/build.gradle: versión ${cfg.versionName} (código ${code}) y firma fija de prueba`);

// 4) variables.gradle: Android 16 (API 36) para compilar y como objetivo (lo pide Google Play)
const vP = path.join(A, 'variables.gradle');
let v = read(vP);
const setMin = (name, val) => {
  const m = v.match(new RegExp(name + '\\s*=\\s*(\\d+)'));
  must(m, `No encontré ${name} en variables.gradle.`);
  if (+m[1] < val) v = v.replace(m[0], `${name} = ${val}`);
};
setMin('compileSdkVersion', 36); setMin('targetSdkVersion', 36); setMin('minSdkVersion', 24);
write(vP, v);
log('variables.gradle: ' + ['compileSdkVersion', 'targetSdkVersion', 'minSdkVersion'].map(n => n + '=' + v.match(new RegExp(n + '\\s*=\\s*(\\d+)'))[1]).join(', '));

// 5) Recursos: iconos de Sosinas Corp y pantalla de arranque negra
const res = path.join(A, 'app/src/main/res');
const copyDir = (src, dst) => { for (const e of fs.readdirSync(src, { withFileTypes:true })) { const s = path.join(src, e.name), d = path.join(dst, e.name); if (e.isDirectory()) { fs.mkdirSync(d, { recursive:true }); copyDir(s, d); } else fs.copyFileSync(s, d); } };
for (const d of fs.readdirSync(res)) {
  const f = path.join(res, d, 'splash.png'); if (d.startsWith('drawable') && fs.existsSync(f)) fs.rmSync(f);
}
copyDir(path.join(ROOT, 'native/res'), res);
log('Iconos y pantalla de arranque copiados');
console.log('Listo: proyecto Android de Duelo de Cartas preparado.');
