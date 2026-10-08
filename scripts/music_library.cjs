const {chromium}=require('../.tools/browser/node_modules/playwright-core');
(async()=>{
 const browser=await chromium.connectOverCDP('http://127.0.0.1:9223');
 try{
 const context=browser.contexts()[0];
 let page=context.pages().find(p=>p.url().startsWith('https://studio.youtube.com'));
 if(!page){page=await context.newPage();await page.goto('https://www.youtube.com/audiolibrary',{waitUntil:'domcontentloaded'});}
 if(['search','get-song'].includes(process.argv[2])){
  const search=page.getByPlaceholder('Tìm kiếm hoặc lọc trong thư viện');
  await search.fill('Old MacDonald');await search.press('Enter');await page.waitForTimeout(500);
  await page.locator('input[aria-labelledby="paper-input-label-1"]').fill('Old MacDonald');
  await page.getByText('Áp dụng',{exact:true}).last().click({timeout:5000});await page.waitForTimeout(2000);
  if(process.argv[2]==='get-song'){
   const title=page.getByText('Old MacDonald',{exact:true});
   console.log('Song ancestors',await title.evaluate(n=>{const a=[];for(let p=n;p&&a.length<7;p=p.parentElement)a.push({tag:p.tagName,cls:p.className,text:p.innerText.slice(0,250)});return a;}));
   const row=title.locator('xpath=ancestor::*[.//button[@aria-label="Tải xuống"]][1]');
   const download=page.waitForEvent('download',{timeout:30000});
   await row.getByRole('button',{name:'Tải xuống',exact:true}).click({timeout:5000});
   await(await download).saveAs(require('path').resolve('data/animal-dance/old-macdonald.mp3'));
   console.log('Downloaded exact Old MacDonald row');
  }
 }
 if(process.argv[2]==='apply'){
  await page.getByRole('button',{name:'Áp dụng',exact:true}).click();await page.waitForTimeout(1500);
 }
 if(process.argv[2]==='download'){
  const download=page.waitForEvent('download',{timeout:30000});
  await page.getByRole('button',{name:'Tải xuống',exact:true}).nth(1).click();
  await(await download).saveAs(require('path').resolve('data/animal-dance/old-macdonald.mp3'));
  console.log('Saved Old MacDonald by The Green Orbs');
 }
 if(process.argv[2]==='license'){
  await page.locator('[aria-label="Giấy phép của Thư viện âm thanh YouTube"]').last().click();
  await page.waitForTimeout(500);
 }
 console.log('Page',new URL(page.url()).origin+new URL(page.url()).pathname);
 console.log((await page.locator('body').innerText()).slice(0,10000));
 if(process.argv[2]==='controls')console.log(JSON.stringify(await page.locator('input,button,[role=button]').evaluateAll(ns=>ns.map(n=>({tag:n.tagName,text:n.innerText,label:n.getAttribute('aria-label'),placeholder:n.getAttribute('placeholder')})))));
 }finally{await browser.close();}
})().catch(e=>{console.error(e.message);process.exitCode=1;});
