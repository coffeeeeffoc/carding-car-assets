import { createRequire } from 'node:module';
import { createServer } from 'node:http';
import { readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve, relative } from 'node:path';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';
const kit = dirname(fileURLToPath(import.meta.url)), root = resolve(kit, '../..');
const require = createRequire(resolve(process.env.CARDING_PREVIEW_PACKAGE || 'games/local/travel-bund/package.json'));
const three = resolve(dirname(require.resolve('three')), '..');
const { chromium } = require('@playwright/test');
const html = `<!doctype html><style>body{margin:0}</style><script type="importmap">{"imports":{"three":"/three/build/three.module.js","three/addons/":"/three/examples/jsm/"}}</script><script type="module">
import * as THREE from 'three'; import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
const renderer = new THREE.WebGLRenderer({antialias:true}); renderer.setSize(768,768); renderer.outputColorSpace=THREE.SRGBColorSpace; document.body.append(renderer.domElement);
try {const scene=new THREE.Scene();scene.background=new THREE.Color('#dce6ec');const id=new URLSearchParams(location.search).get('id'); const gltf=await new GLTFLoader().loadAsync('/assets/runtime-expansion/props/'+id+'.glb');scene.add(gltf.scene);
const box=new THREE.Box3().setFromObject(gltf.scene), center=box.getCenter(new THREE.Vector3()), size=box.getSize(new THREE.Vector3());
const camera=new THREE.PerspectiveCamera(35,1,.01,5000); camera.position.copy(center).add(new THREE.Vector3(1,.65,1.5).normalize().multiplyScalar(size.length()*1.8)); camera.lookAt(center); renderer.render(scene,camera);
window.result={id,size:size.toArray(),triangles:renderer.info.render.triangles,calls:renderer.info.render.calls};}catch(e){window.result={error:String(e)}}
</script>`;
const server=createServer(async(req,res)=>{try {const url=new URL(req.url,'http://localhost');if(url.pathname==='/'){res.setHeader('Content-Type','text/html');return res.end(html);} const fromThree=url.pathname.startsWith('/three/'),base=fromThree?three:root,prefix=fromThree?'/three/':'/assets/'; const path=resolve(base,decodeURIComponent(url.pathname.slice(prefix.length))); assert(!relative(base,path).startsWith('..'));res.setHeader('Content-Type',path.endsWith('.js')?'application/javascript':'application/octet-stream');res.end(await readFile(path));}catch{res.statusCode=404;res.end();}});
await new Promise(r=>server.listen(0,'127.0.0.1',r));
const browser=await chromium.launch({headless:true,executablePath:process.env.PLAYWRIGHT_EXECUTABLE_PATH||'C:/Program Files/Google/Chrome/Application/chrome.exe'});
try {const page=await browser.newPage({viewport:{width:768,height:768}}),checks=[];for(const id of ['highland-snow-ridge','highland-cliff','highland-lodge']) {await page.goto('http://127.0.0.1:'+server.address().port+'/?id='+id);await page.waitForFunction(()=>window.result);const result=await page.evaluate(()=>window.result);assert(!result.error,result.error);await page.screenshot({path:resolve(kit,id+'.png')});checks.push(result);console.log(result);}await writeFile(resolve(kit,'render-check.json'),JSON.stringify(checks,null,2)+'\n');}finally {await browser.close();server.close();}
