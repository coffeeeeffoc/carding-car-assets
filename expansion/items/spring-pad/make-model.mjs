// Rodin flattened the coil twice. Use exact geometry for this simple mechanism.
import { createRequire } from 'node:module';
import { dirname, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { writeFile } from 'node:fs/promises';
import assert from 'node:assert/strict';
const require = createRequire(resolve(process.env.CARDING_PREVIEW_PACKAGE || 'games/local/travel-bund/package.json'));
const THREE = require('three');
const three = resolve(dirname(require.resolve('three')), '..');
const { GLTFExporter } = await import(pathToFileURL(resolve(three, 'examples/jsm/exporters/GLTFExporter.js')));
const { RoundedBoxGeometry } = await import(pathToFileURL(resolve(three, 'examples/jsm/geometries/RoundedBoxGeometry.js')));
globalThis.FileReader = class {
  async readAsArrayBuffer(blob) { this.result = await blob.arrayBuffer(); this.onloadend?.(); }
};
const root = new THREE.Group();
function part(name, geometry, color, y = 0) {
  const base = new THREE.Color(color), normals = geometry.attributes.normal, colors = [];
  for (let i = 0; i < normals.count; i++) {
    const light = 0.72 + 0.28 * Math.max(0, normals.getX(i) * -0.35 + normals.getY(i) * 0.8 + normals.getZ(i) * 0.4);
    colors.push(base.r * light, base.g * light, base.b * light);
  }
  geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
  const mesh = new THREE.Mesh(geometry, new THREE.MeshBasicMaterial({ vertexColors: true }));
  mesh.name = name; mesh.position.y = y; root.add(mesh);
}
part('Base', new RoundedBoxGeometry(1.4, 0.16, 1.4, 2, 0.05), '#fa8c19', 0.08);
const points = Array.from({ length: 121 }, (_, i) => {
  const t = i / 120, angle = t * Math.PI * 6;
  return new THREE.Vector3(Math.cos(angle) * 0.31, 0.17 + t * 0.72, Math.sin(angle) * 0.31);
});
part('Coil', new THREE.TubeGeometry(new THREE.CatmullRomCurve3(points), 120, 0.065, 8, false), '#c3cdd6');
part('Top', new RoundedBoxGeometry(1.12, 0.14, 1.12, 2, 0.05), '#28ceda', 0.97);
const box = new THREE.Box3().setFromObject(root), size = box.getSize(new THREE.Vector3());
assert.equal(root.children.length, 3); assert(size.y > 1 && size.y < 1.1);
const result = await new GLTFExporter().parseAsync(root, { binary: true });
assert(result.byteLength > 1000);
await writeFile(resolve(dirname(fileURLToPath(import.meta.url)), 'model.glb'), Buffer.from(result));
console.log('Spring model: 3 separate named meshes, height', size.y, 'bytes', result.byteLength);
