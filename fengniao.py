import re
import json
import time
import os

import aiohttp
import asyncio


async def fetch_img_url(num):
    url = f'http://bbs.fengniao.com/forum/forum_101_{num}_lastpost.html'
    print(url)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
    }

    async with aiohttp.ClientSession() as session:

        # 获取轮播图地址
        async with session.get(url,headers=headers) as response:
            try:
                url_format = "http://bbs.fengniao.com/forum/pic/slide_101_{0}_{1}.html"
                html = await response.text()   # 获取到网页源码
                pattern = re.compile('<div class="picList">([\s\S.]*?)</div>')
                first_match = pattern.findall(html)
                href_pattern = re.compile('href="/forum/(\d+?)_p(\d+?)\.html')
                urls = [url_format.format(href_pattern.search(url).group(1),href_pattern.search(url).group(2)) for url in first_match]

                paths =["images/img{}/".format(href_pattern.search(url).group(1)) for url in first_match]

                # 创建N多的目录
                for path in paths:
                    if not os.path.exists(path):
                        os.mkdir(path)

                for img_slider in urls:

                    try:
                        async with session.get(img_slider, headers=headers) as slider:
                            slider_html = await slider.text()   # 获取到网页源码

                            num = re.search('(\d+?)_(\d+?)\.html',img_slider).group(1)

                            path = "images/img{}/".format(num)
                            try:
                                pic_list_pattern = re.compile('var picList = \[(.*)?\];')

                                pic_list = "[{}]".format(pic_list_pattern.search(slider_html).group(1))

                                pic_json = json.loads(pic_list)  # 图片已经拿到
                            except Exception as e:
                                print("代码调试错误")
                                print(pic_list)
                                print("*"*100)
                                print(e)


                            for img in pic_json:

                                try:
                                    img = img["downloadPic"]
                                    async with session.get(img, headers=headers) as img_res:
                                        imgcode = await img_res.read()
                                        with open("{}/{}".format(path,img.split('/')[-1]), 'wb') as f:
                                            f.write(imgcode)
                                            f.close()
                                except Exception as e:
                                    print("图片下载错误")
                                    print(e)
                                    continue

                            print("{}-{}张图片下载完毕".format(time.time(), len(pic_json)))

                    except Exception as e:
                        print("获取图片列表错误")

                        print(img_slider)

                        print(e)
                        continue



                print("{}已经操作完毕".format(url))



            except Exception as e:
                print("基本错误")
                print(e)


loop = asyncio.get_event_loop()
tasks = [asyncio.ensure_future(fetch_img_url(num)) for num in range(1, 3)]
results = loop.run_until_complete(asyncio.wait(tasks))