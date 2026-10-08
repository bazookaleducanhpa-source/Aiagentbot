// Read only the dedicated Flow browser; never read cookies or authentication tokens.
const { chromium } = require('../.tools/browser/node_modules/playwright-core');
(async () => {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9223', {timeout: 10000});
  try {
    const pages = browser.contexts()[0].pages();
    const page = pages.find(p => p.url().startsWith('https://labs.google/') || p.url().startsWith('https://flow.google.com/'));
    if (!page) {
      console.log('Flow tab not ready; complete sign-in in Chrome.');
      for (const tab of pages) {
        const address = new URL(tab.url());
        console.log('Open tab:', address.origin + address.pathname);
      }
      return;
    }
    console.log('Flow URL:', page.url());
    if (process.argv[2] === 'approve-omni') {
      const text = await page.locator('body').innerText();
      if (!text.includes('1 video này với chi phí là 12 tín dụng')) throw new Error('Expected single 12-credit Omni replacement.');
      await page.getByText('Phê duyệt',{exact:true}).last().click({timeout:5000});
    }
    if (process.argv[2] === 'send') {
      await page.locator('[contenteditable=true]').fill(require('fs').readFileSync(process.argv[3],'utf8'));
      await page.getByRole('button',{name:'Bắt đầu tạo',exact:true}).click();
    }
    if (process.argv[2] === 'credits') {
      await page.mouse.click(868,38);
      console.log('Credit balance:',await page.getByText(/\d[\d.,]* tín dụng Google Flow/).last().innerText());
      await page.getByRole('button',{name:'Đóng bảng điều khiển tài khoản',exact:true}).click();
    }
    if (process.argv[2] === 'download-rest') {
      const shots = [[2,'Toddler rides baby shark'],[3,'Baby sharks dancing underwater'],[5,'Toddler dances beside bobbing sh…'],[6,'Toddler waving on beach']];
      for (const [index,name] of shots) {
        const destination = require('path').resolve(`data/references/7620858344969964820/flow-shot-0${index}.mp4`);
        if (require('fs').existsSync(destination)) continue;
        await page.getByRole('button',{name,exact:true}).click();
        await page.waitForTimeout(1000);
        await page.getByRole('button',{name:'Tải nội dung nghe nhìn xuống',exact:true}).click();
        const download = page.waitForEvent('download',{timeout:30000});
        await page.getByRole('menuitem',{name:/720p/}).click();
        await (await download).saveAs(destination);
        console.log('Downloaded shot',index);
      }
    }
    if (process.argv[2] === 'approve-rest') {
      const body = await page.locator('body').innerText();
      if (!body.includes('5 video này với chi phí là 100 tín dụng')) throw new Error('Expected five-video, 100-credit confirmation.');
      await page.getByText('Phê duyệt',{exact:true}).last().click({timeout:5000});
      await page.waitForTimeout(2000);
    }
    if (process.argv[2] === 'request-rest') {
      await page.locator('[contenteditable=true]').fill('Continue Ocean Peekaboo with FIVE additional 8-second vertical 9:16 3D videos using Veo 3.1 Fast, one result per shot, total video cost 100 credits. Use ocean-opening.png in this project as the character/style reference: SAME toddler face, turquoise shark hooded romper with yellow star, same glossy pink shark. Bright cyan/pink/yellow, plush soft 3D, tropical sunshine, genuine articulated motion, gentle original instrumental soundtrack and ocean sound effects, NO speech/text. Shot 2: toddler safely rides a large friendly yellow baby shark slowly through shallow turquoise water with playful splashes. Shot 3: underwater dance of pink, yellow and blue friendly round baby sharks, bubbles and tropical fish, no toddler underwater. Shot 4: same toddler on beach playfully covers their face with hands then opens hands for peekaboo, pink shark behind. Shot 5: toddler claps and dances gently beside pink yellow and blue sharks bobbing near the beach. Shot 6: same toddler waves and returns to the opening beach pose, large iridescent bubble passes in front of camera for a loop ending. Generate exactly these FIVE different scenes, not variations of one scene; keep consistent characters and materials. Use uploaded reference as image reference where supported; if you need scene keyframes, propose cost first. Show the total cost and plan before generation. Do not buy or upgrade anything.');
      await page.getByRole('button',{name:'Bắt đầu tạo',exact:true}).click();
      await page.waitForTimeout(2000);
    }
    if (process.argv[2] === 'retry-shot-four') {
      await page.locator('[contenteditable=true]').fill('Shot 4 failed with audio generation error and Flow says its credits will be refunded. Create only a replacement for Shot 4, ONE 8-second 9:16 Veo 3.1 Fast video using ocean-opening.png as reference. Same toddler face and turquoise shark hooded romper with yellow star, same pink shark on sunny turquoise beach. Toddler covers their eyes with both hands then opens their hands and smiles for peekaboo; pink shark gently bobs behind. Preserve plush polished 3D, original colors and proportions. Smooth articulated movement, one continuous shot, no text. Disable generated audio if supported to avoid the previous audio error; I will add narration and music locally. If audio cannot be disabled use only quiet natural beach ambience, no music, no speech. Show 20-credit cost before generating, no other clips.');
      await page.getByRole('button',{name:'Bắt đầu tạo',exact:true}).click();
    }
    if (process.argv[2] === 'download-original') {
      const download = page.waitForEvent('download',{timeout:30000});
      await page.getByRole('menuitem',{name:/720p/}).click();
      const file = await download;
      const filename=process.argv[3] || 'flow-shot-01.mp4';
      if (!/^flow-shot-0[1-6]\.mp4$/.test(filename)) throw new Error('Invalid shot filename.');
      await file.saveAs(require('path').resolve('data/references/7620858344969964820/'+filename));
      console.log('Saved',filename);
    }
    if (process.argv[2] === 'screenshot') {
      await page.bringToFront();
      await page.evaluate(()=>window.scrollTo(0,0));
      await page.evaluate(()=>{for(const node of document.querySelectorAll('div')) if(node.scrollTop>0 && !node.innerText.includes('Create ONE 8-second')) node.scrollTop=0;});
      await page.screenshot({path:'data/references/7620858344969964820/flow-browser.png',timeout:10000,animations:'disabled'});
    }
    if (process.argv[2] === 'open-first-shot') {
      await page.evaluate(()=>window.scrollTo(0,0));
      await page.mouse.dblclick(315,180);
      await page.waitForTimeout(1000);
    }
    if (process.argv[2] === 'download-first-shot') {
      const video = page.locator('video').first();
      if (!await video.count()) throw new Error('No video element found.');
      const src = await video.evaluate(v => v.currentSrc || v.src);
      if (!src.startsWith('https://')) throw new Error('Video download URL not ready.');
      const response = await page.context().request.get(src);
      if (!response.ok()) throw new Error('Video download HTTP ' + response.status());
      const fs = require('fs');
      fs.writeFileSync('data/references/7620858344969964820/flow-shot-01.mp4',await response.body());
      console.log('Saved flow-shot-01.mp4');
    }
    if (process.argv[2] === 'approve-first-shot') {
      const body = await page.locator('body').innerText();
      if (!body.includes('20 tín dụng') || !body.includes('1 video')) throw new Error('Expected one-video, 20-credit confirmation.');
      await page.getByText('Phê duyệt',{exact:true}).last().click({timeout:5000});
      await page.waitForTimeout(2000);
    }
    if (process.argv[2] === 'attach-opening') {
      await page.getByRole('option',{name:/ocean-opening.png/}).click();
      await page.getByRole('button',{name:'Thêm vào câu lệnh',exact:true}).click();
    }
    if (process.argv[2] === 'request-first-shot') {
      const prompt = 'Create ONE 8-second vertical 9:16 video with Veo 3.1 Fast using the attached image as the first frame. Animate the toddler waving twice and swaying gently; the pink baby shark bobs from the water and waves a fin; bubbles rise and the ocean ripples with tiny splashes. Preserve the exact faces, outfits, proportions and polished colorful 3D appearance. Slow subtle camera push in. One continuous shot, genuine articulated character movement, no cuts or text. Gentle ocean sounds and cheerful original instrumental music, no speech. Do not generate additional images or variations. Show the cost before generation.';
      await page.locator('[contenteditable=true]').fill(prompt);
      await page.getByRole('button',{name:'Bắt đầu tạo',exact:true}).click();
      await page.waitForTimeout(2000);
    }
    if (process.argv[2] === 'upload-opening') {
      const chooser = page.waitForEvent('filechooser');
      await page.getByRole('button',{name:/Tải nội dung nghe nhìn lên/}).click();
      await (await chooser).setFiles(require('path').resolve('data/references/7620858344969964820/ocean-opening.png'));
      await page.waitForTimeout(3000);
    }
    if (process.argv[2] === 'menu') {
      await page.getByRole('menuitem',{name:process.argv[3],exact:true}).click();
    }
    if (process.argv[2] === 'click') {
      await page.getByRole('button', {name:process.argv[3],exact:true}).click({timeout:5000});
      await page.waitForTimeout(1000);
    }
    if (process.argv[2] === 'title') {
      await page.getByRole('textbox',{name:'Văn bản có thể chỉnh sửa'}).fill('Ocean Peekaboo — 3D English');
      await page.keyboard.press('Enter');
    }
    if (process.argv[2] === 'video-defaults') {
      await page.getByRole('radio',{name:/9:16/}).last().click();
      await page.getByRole('radio',{name:'x1',exact:true}).last().click();
      await page.getByRole('button',{name:'Mô hình mặc định của tính năng tạo video',exact:true}).click();
    }
    if (process.argv[2] === 'new-project') {
      const accountClose = page.getByRole('button', {name: 'Đóng bảng điều khiển tài khoản'});
      if (await accountClose.isVisible()) await accountClose.click();
      await page.getByRole('button', {name: /Dự án mới|New project/i}).click();
      await page.waitForTimeout(2000);
    }
    const visibleText = await page.locator('body').innerText();
    console.log(process.argv[2] === 'status' ? visibleText.slice(-4500) : visibleText.slice(0, 9000));
    console.log('Videos:',JSON.stringify(await page.locator('video').evaluateAll(nodes => nodes.map(n => ({duration:n.duration,width:n.videoWidth,height:n.videoHeight,ready:n.readyState,hasSrc:Boolean(n.currentSrc || n.src)})))));
    if (process.argv[2] !== 'status') console.log('Controls:', JSON.stringify(await page.locator('button,textarea,input,[contenteditable=true]').evaluateAll(nodes => nodes.map(n => ({tag:n.tagName,role:n.getAttribute('role'),label:n.getAttribute('aria-label'),text:n.innerText,placeholder:n.getAttribute('placeholder'),type:n.getAttribute('type')})))));
  } finally { await browser.close(); }
})().catch(e => { console.error(e.message); process.exitCode = 1; });
