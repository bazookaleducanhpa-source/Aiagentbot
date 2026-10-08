const {chromium}=require('../.tools/browser/node_modules/playwright-core');
const fs=require('fs');
(async()=>{
 const browser=await chromium.connectOverCDP('http://127.0.0.1:9223');
 try {
  const context=browser.contexts()[0];
  const action=process.argv[2];
  let page;
  if(action.startsWith('music')){
   page=context.pages().find(p=>p.url().startsWith('https://www.flowmusic.app'));
   if(!page){page=await context.newPage();await page.goto('https://www.flowmusic.app/',{waitUntil:'domcontentloaded'});}
  }else page=context.pages().find(p=>p.url().includes('1b05e440-c0a3-4dbb-88f2-f792f1febf06'));
  if(!page)throw Error('Project tab missing');
  if(action==='music-login')await page.getByRole('button',{name:'Log in',exact:true}).click();
  if(action==='music-google'){
   await page.getByRole('button',{name:'Continue with Google',exact:true}).click();
   await page.waitForTimeout(1500);
   for(const tab of context.pages())console.log('Tab',new URL(tab.url()).origin,new URL(tab.url()).pathname);
  }
  if(action==='send'){
   await page.locator('[contenteditable=true]').fill(fs.readFileSync('data/animal-dance/flow-prompt.txt','utf8'));
   await page.getByRole('button',{name:'Bắt đầu tạo',exact:true}).click();
  }
  if(action==='approve'){
   const body=await page.locator('body').innerText();
   if(!body.includes('5 video này với chi phí là 100 tín dụng'))throw Error('Unexpected generation price: review required');
   await page.getByText('Phê duyệt',{exact:true}).last().click();
  }
  if(action==='confirm-plan'){
   await page.locator('[contenteditable=true]').fill('Proceed with exactly these five different animal videos, total 100 credits, Veo 3.1 Fast, vertical 9:16, one result for each scene.');
   await page.getByRole('button',{name:'Bắt đầu tạo',exact:true}).click();
  }
  if(action==='screenshot'){
   await page.bringToFront();
   await page.screenshot({path:'data/animal-dance/browser.png',timeout:10000});
  }
  if(action==='controls')console.log(JSON.stringify(await page.locator('button').evaluateAll(ns=>ns.map(n=>({text:n.innerText,label:n.getAttribute('aria-label')})))));
  if(action==='open-first'){
   await page.bringToFront();
   await page.mouse.dblclick(315,180);
   await page.waitForTimeout(1000);
   console.log(JSON.stringify(await page.locator('button').evaluateAll(ns=>ns.map(n=>({text:n.innerText,label:n.getAttribute('aria-label')})))));
  }
  if(action==='download'){
   const name=process.argv[3],animal=process.argv[4];
   if(!['bunny','penguin','elephant','monkey','duckling'].includes(animal))throw Error('Invalid animal');
   await page.getByRole('button',{name,exact:true}).evaluate(node=>node.click());
   await page.getByRole('button',{name:'Tải nội dung nghe nhìn xuống',exact:true}).click();
   const pending=page.waitForEvent('download',{timeout:30000});
   await page.getByRole('menuitem',{name:/720p/}).click();
   await(await pending).saveAs(require('path').resolve('data/animal-dance/'+animal+'.mp4'));
   console.log('Downloaded',animal);
  }
  console.log('URL',new URL(page.url()).origin+new URL(page.url()).pathname);
  console.log((await page.locator('body').innerText()).slice(-12000));
  if(action.startsWith('music'))console.log('Controls',JSON.stringify(await page.locator('button,input,textarea,[contenteditable=true],a').evaluateAll(ns=>ns.map(n=>({tag:n.tagName,text:n.innerText,label:n.getAttribute('aria-label'),placeholder:n.getAttribute('placeholder')})))));
 }finally{await browser.close();}
})().catch(e=>{console.error(e.message);process.exitCode=1;});
