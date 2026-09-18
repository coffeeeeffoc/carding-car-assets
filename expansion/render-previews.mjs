// Render the actual GLBs for review; no image-generation substitutes.
// CARDING_PREVIEW_PACKAGE can point to an installed workspace package.json.
import { createRequire } from 'node:module';
import { createServer } from 'node:http';
import { readFile, writeFile, readdir, access } from 'node:fs/promises';
import { dirname, resolve, relative, extname } from 'node:path';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';

const root = dirname(fileURLToPath(import.meta.url));
const require = createRequire(resolve(process.env.CARDING_PREVIEW_PACKAGE || 'games/local/travel-bund/package.json'));
const three = resolve(dirname(require.resolve('three')), '..');
const { chromium } = require('@playwright/test');
const pageHtml = `<!doctype html><html><head><meta charset="utf-8"><style>body{margin:0}</style>
<script type="importmap">{"imports":{"three":"/three/build/three.module.js","three/addons/":"/three/examples/jsm/"}}</script></head><body><script type="module">
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
const renderer = new THREE.WebGLRenderer({antialias:true, preserveDrawingBuffer:true});
renderer.setSize(768,768);renderer.setPixelRatio(1);renderer.outputColorSpace=THREE.SRGBColorSpace;
document.body.append(renderer.domElement);
const scene=new THREE.Scene();scene.background=new THREE.Color('#edf3f6');
const camera=new THREE.PerspectiveCamera(34,1,0.001,1000);
try{
 const gltf=await new GLTFLoader().loadAsync('/assets/'+new URLSearchParams(location.search).get('asset'));
 scene.add(gltf.scene);
 gltf.scene.traverse(o=>{if(o.isMesh){
  const basic=m=>new THREE.MeshBasicMaterial({map:m.map||m.emissiveMap,color:m.map||m.emissiveMap?0xffffff:m.color,vertexColors:!!o.geometry.attributes.color,side:THREE.DoubleSide});
  o.material=Array.isArray(o.material)?o.material.map(basic):basic(o.material);
 }});
 const box=new THREE.Box3().setFromObject(gltf.scene),center=box.getCenter(new THREE.Vector3()),size=box.getSize(new THREE.Vector3());
 const radius=size.length()/2,distance=radius/Math.sin(THREE.MathUtils.degToRad(17))*1.08;
 camera.position.copy(center).add(new THREE.Vector3(1,0.7,1.3).normalize().multiplyScalar(distance));
 camera.near=Math.max(distance/1000,0.0001);camera.far=distance*20;camera.updateProjectionMatrix();camera.lookAt(center);
 renderer.render(scene,camera);window.assetStats={meshes:renderer.info.render.calls,triangles:renderer.info.render.triangles,size:size.toArray()};window.ready=true;
}catch(error){window.renderError=String(error);}
</script></body></html>`;
const server=createServer(async(req,res)=>{
 try {
  const pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
  if(pathname==='/'){res.setHeader('Content-Type','text/html');res.end(pageHtml);return;}
  const base=pathname.startsWith('/three/')?three:root;
  const prefix=pathname.startsWith('/three/')?'/three/':'/assets/';
  assert(pathname.startsWith(prefix));
  const file=resolve(base,pathname.slice(prefix.length));
  assert(!relative(base,file).startsWith('..'));
  res.setHeader('Content-Type',extname(file)==='.js'?'application/javascript':'application/octet-stream');
  res.end(await readFile(file));
 } catch {res.statusCode=404;res.end();}
});
await new Promise(r=>server.listen(0,'127.0.0.1',r));
const browser=await chromium.launch({headless:true,executablePath:process.env.PLAYWRIGHT_EXECUTABLE_PATH || undefined});
try {
 const page=await browser.newPage({viewport:{width:768,height:768}});
 const files=await readdir(root,{recursive:true});
 for(const file of files.filter(f=>f.endsWith('model.glb'))){
  const preview=resolve(root,dirname(file),'preview.png');
  try{await access(preview);continue;}catch{}
  await page.goto('http://127.0.0.1:'+server.address().port+'/?asset='+encodeURIComponent(file.replaceAll('\\','/')));
  await page.waitForFunction(()=>window.ready || window.renderError,{},{timeout:60000});
  const result=await page.evaluate(()=>({error:window.renderError,stats:window.assetStats}));
  assert(!result.error,result.error);assert(result.stats.triangles>0);
  await page.screenshot({path:preview});
  await writeFile(resolve(root,dirname(file),'render-check.json'),JSON.stringify(result.stats,null,2)+'\n');
  console.log(file,JSON.stringify(result.stats));
 }
}finally{await browser.close();server.close();}
