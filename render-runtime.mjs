// Review actual derived geometry using the same workspace Three.js/Playwright dependencies.
import { createRequire } from 'node:module';
import { createServer } from 'node:http';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname, resolve, relative, extname } from 'node:path';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';
const root = dirname(fileURLToPath(import.meta.url));
const require = createRequire(resolve(process.env.CARDING_PREVIEW_PACKAGE || 'games/local/travel-bund/package.json'));
const three = resolve(dirname(require.resolve('three')), '..');
const { chromium } = require('@playwright/test');
const html = `<!doctype html><html><head><style>body{margin:0}</style>
<script type="importmap">{"imports":{"three":"/three/build/three.module.js","three/addons/":"/three/examples/jsm/"}}</script></head><body><script type="module">
import * as THREE from 'three'; import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
const renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setSize(512,512);renderer.outputColorSpace=THREE.SRGBColorSpace;document.body.append(renderer.domElement);
const scene=new THREE.Scene();scene.background=new THREE.Color('#e7eef3');const camera=new THREE.PerspectiveCamera(34,1,.001,1000);
try{const q=new URLSearchParams(location.search);const asset=await new GLTFLoader().loadAsync('/assets/runtime-expansion/'+q.get('asset'));scene.add(asset.scene);
if(q.get('driver')){const driver=await new GLTFLoader().loadAsync('/assets/runtime-expansion/drivers/'+q.get('driver')+'.glb');const m=JSON.parse(q.get('mount'));driver.scene.position.set(m.x,m.y,m.z);driver.scene.scale.setScalar(m.scale);scene.add(driver.scene);}
const box=new THREE.Box3().setFromObject(scene),center=box.getCenter(new THREE.Vector3()),size=box.getSize(new THREE.Vector3());
const distance=size.length()/2/Math.sin(THREE.MathUtils.degToRad(17))*1.08;
camera.position.copy(center).add(new THREE.Vector3(1,.7,1.3).normalize().multiplyScalar(distance));camera.far=distance*20;camera.updateProjectionMatrix();camera.lookAt(center);
renderer.render(scene,camera);window.result={calls:renderer.info.render.calls,triangles:renderer.info.render.triangles,size:size.toArray()};
}catch(error){window.result={error:String(error)};}
</script></body></html>`;
const server=createServer(async(req,res)=>{try{const url=new URL(req.url,'http://localhost');if(url.pathname==='/'){res.setHeader('Content-Type','text/html');res.end(html);return;}
const prefix=url.pathname.startsWith('/three/')?'/three/':'/assets/';const base=prefix==='/three/'?three:root;
const path=resolve(base,decodeURIComponent(url.pathname.slice(prefix.length)));assert(!relative(base,path).startsWith('..'));
res.setHeader('Content-Type',extname(path)==='.js'?'application/javascript':'application/octet-stream');res.end(await readFile(path));
}catch{res.statusCode=404;res.end();}});
await new Promise(r=>server.listen(0,'127.0.0.1',r));
const browser=await chromium.launch({headless:true,executablePath:process.env.PLAYWRIGHT_EXECUTABLE_PATH||undefined});
try{const page=await browser.newPage({viewport:{width:512,height:512}});const manifest=JSON.parse(await readFile(resolve(root,'runtime-expansion/manifest.json'),'utf8'));
const review=resolve(root,'runtime-review');await mkdir(review,{recursive:true});const checks=[];
for(const row of manifest.models){const variants=row.category==='vehicles'?['','rookie']:[''];for(const driver of variants){
await page.goto('http://127.0.0.1:'+server.address().port+'/?asset='+encodeURIComponent(row.file)+'&driver='+driver+'&mount='+encodeURIComponent(JSON.stringify(row.driverMount)));
await page.waitForFunction(()=>window.result,{},{timeout:60000});const result=await page.evaluate(()=>window.result);assert(!result.error,result.error);assert(result.triangles>0);
const name=row.file.replaceAll('/','-').replace('.glb',driver?'-seated':'');await page.screenshot({path:resolve(review,name+'.png')});checks.push({file:row.file,driver,...result});console.log(name,JSON.stringify(result));}}
await writeFile(resolve(review,'render-check.json'),JSON.stringify(checks,null,2)+'\n');
}finally{await browser.close();server.close();}
