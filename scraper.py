"""Auditoría conservadora: jamás publica precio sin confirmar sucursal."""
import argparse
import asyncio
import csv
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from playwright.async_api import async_playwright

CITIES = ['Temuco', 'Villarrica', 'Valdivia', 'Osorno', 'Puerto Montt']
PRODUCTS = [
 ('Sodimac','Melón 25 kg','https://www.sodimac.cl/sodimac-cl/articulo/110323991/Cemento-Melon-especial-25-Kg/110324015'),
 ('Sodimac','Polpaico 25 kg','https://www.sodimac.cl/sodimac-cl/articulo/110309884/cemento-polpaico-25-kilos/110309919'),
 ('Sodimac','Malla ACMA C-92','https://www.sodimac.cl/sodimac-cl/articulo/110327948/2-60-x-5m--Malla-Acma-C--92-Con-economia-de-borde/110327972'),
 ('Prodalam','Polpaico P400 25 kg','https://www.prodalam.cl/productos/91600-UN/cemento-p400-polpaico-de-25kg'),
 ('Prodalam','Malla ACMA C-92','https://www.prodalam.cl/productos/97517-UN/malla-acma-c-92-con-economia-15x15cm-de-260x5m'),
]

async def collect(page, provider, product, url, city, folder):
    result={'provider':provider,'product':product,'city':city,'store':'','unit_price_clp':'','availability':'unverified','status':'UNVERIFIED','url':url,'checked_at':datetime.now(timezone.utc).isoformat(),'evidence':''}
    safe=re.sub(r'[^a-zA-Z0-9-]','_',f'{provider}_{product}_{city}')
    try:
        await page.goto(url, wait_until='domcontentloaded', timeout=45000)
        await page.wait_for_timeout(1800)
        selector=page.get_by_text(re.compile(r'Cambiar Sucursal|Seleccionar tienda|Elegir tienda|Mi tienda',re.I)).first
        if await selector.count():
            await selector.click(timeout=4000)
        city_option=page.get_by_role('option',name=city,exact=True)
        if await city_option.count():
            await city_option.first.click(timeout=4000)
        else:
            city_button=page.get_by_role('button',name=city,exact=True)
            if await city_button.count():
                await city_button.first.click(timeout=4000)
        await page.wait_for_timeout(1300)
        body=await page.locator('body').inner_text(timeout=10000)
        result['evidence']=str(folder / f'{safe}.png')
        await page.screenshot(path=result['evidence'],full_page=True,timeout=15000)
        (folder/f'{safe}.txt').write_text(body[:30000],encoding='utf-8')
        result['status']='REQUIRES_STORE_CONFIRMATION'
    except Exception as exc:
        result['status']='NETWORK_BLOCKED' if 'ERR_BLOCKED_BY_ADMINISTRATOR' in str(exc) else 'ERROR'
        result['error']=str(exc)[:350]
    return result

async def run(out, headless, args_browser=None):
    out.mkdir(parents=True,exist_ok=True)
    rows=[]
    async with async_playwright() as p:
        browser_path=args_browser or shutil.which('chromium') or shutil.which('google-chrome')
        browser=await p.chromium.launch(headless=headless, executable_path=browser_path, args=['--no-sandbox'])
        for city in CITIES:
            for provider,product,url in PRODUCTS:
                context=await browser.new_context(locale='es-CL',timezone_id='America/Santiago',viewport={'width':1280,'height':900})
                page=await context.new_page()
                rows.append(await collect(page,provider,product,url,city,out))
                await context.close()
                await asyncio.sleep(1)
        await browser.close()
    (out/'results.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
    with (out/'results.csv').open('w',newline='',encoding='utf-8-sig') as f:
        writer=csv.DictWriter(f,fieldnames=['provider','product','city','store','unit_price_clp','availability','status','url','checked_at','evidence','error'],extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)
    print(f'{len(rows)} fichas auditadas. Ningún precio se declara verificado sin confirmar sucursal.')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',default='evidencia')
    parser.add_argument('--visible',action='store_true')
    parser.add_argument('--browser',default=None)
    args=parser.parse_args()
    asyncio.run(run(Path(args.out),not args.visible,args.browser))
