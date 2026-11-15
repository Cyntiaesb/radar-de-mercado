// node scripts/checa_painel.js painel/<slug>.html : renderiza cada aba fora do navegador e acusa undefined/NaN.
// O monta_painel.py roda esta checagem sozinho quando o node está instalado.
const fs = require("fs");
const html = fs.readFileSync(process.argv[2], "utf8");
const js = html.match(/<script>([\s\S]*?)<\/script>/)[1].replace(/abrir\(location\.hash\.slice\(1\)\);\s*$/, "");
global.document = { querySelector: () => ({ innerHTML: "", addEventListener() {}, querySelectorAll: () => [], setAttribute() {} }) };
global.location = { hash: "" }; global.history = { replaceState() {} };
let problemas = 0;
eval(js + `
for (const a of ABAS) {
  const t = a[2]().replace(/data:image[^)'"]+/g, "");
  const m = t.match(/.{60}(undefined|NaN).{20}/);
  if (m) { problemas++; console.log("PROBLEMA", a[0], m[0]); }
}
console.log(problemas ? "com problema" : "ok", ABAS.length, "abas");`);
process.exit(problemas ? 1 : 0);
