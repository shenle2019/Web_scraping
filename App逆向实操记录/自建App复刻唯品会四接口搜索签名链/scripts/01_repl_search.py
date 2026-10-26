# -*- coding: utf-8 -*-
"""
仅限学习研究，禁止商用。
低频学习用途：单线程、每次请求间隔 >= 1 秒，仅打通链路验证，不做规模化抓取。

01_repl_search.py —— 唯品会 v7.83.3 搜索功能四接口签名链复刻
来源课件：E:\路飞学城\课件\APP逆向(12期)\day20-唯品会01、day21-唯品会02

接口链（app 首次运行的完整握手顺序）：
  1. device_reg       GET  https://mp.appvipshop.com/apns/device_reg
      - device_token = uuid4；skey 固定；authorization = OAuth api_sign=双层sha1
  2. getTokenByFP     GET  https://vcsp-api.vip.com/token/getTokenByFP?vcspKey=...
      - vcspKey/vcspSign 固定，返回 vcspToken（生成 edata 的原料）
  3. generate_token   POST https://mapi.appvipshop.com/vips-mobile/rest/device/generate_token
      - edata = base64(iv + AES-CBC(明文))，key=md5(盐)，iv=16随机hex；返回 did
  4. 搜索             POST https://mapi.appvipshop.com/vips-mobile/rest/shopping/search/product/list/v1
      - 携带 did + 全量参数，authorization 同样双层 sha1
"""
import hashlib
import random
import time
import uuid
from base64 import b64encode
from urllib.parse import quote_plus

import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

requests.packages.urllib3.disable_warnings()

# ---------------- 破解出的固定值 ----------------
API_KEY = "23e7f28019e8407b98b84cd05b5aef2c"
SKEY = "6692c461c3810ab150c9a980d0c275ec"
VCSP_KEY = "4d9e524ad536c03ff203787cf0dfcd29"
SALT = "aee4c425dbb2288b80c71347cc37d04b"          # api_sign 盐 / AES key 原料
VCSP_SIGN = "05a68135d2bfd322e3a22f95bbc25a24c777f387"  # 固定，也可由 vcsp 盐算
CHANNEL = "oziq7dxw:::"


def sha1(data_string: str) -> str:
    h = hashlib.sha1()
    h.update(data_string.encode('utf-8'))
    return h.hexdigest()


def sign(ordered_string: str) -> str:
    """api_sign = sha1(SALT + sha1(SALT + 排序后参数串))"""
    tmp = sha1(f"{SALT}{ordered_string}")
    return sha1(f"{SALT}{tmp}")


def sorted_query(params: dict) -> str:
    return "&".join(f"{k}={params[k]}" for k in sorted(params.keys()))


def make_edata(plain: str, key: bytes) -> str:
    iv = "".join("%x" % random.randint(1, 15) for _ in range(16))
    aes = AES.new(key=key, mode=AES.MODE_CBC, iv=iv.encode('utf-8'))
    enc = aes.encrypt(pad(plain.encode('utf-8'), 16))
    return b64encode(iv.encode('utf-8') + enc).decode('utf-8')


def main():
    # 设备指纹（模拟 Pixel 2 XL / Android 11）
    mars_cid = str(uuid.uuid4())
    device_token = str(uuid.uuid4())
    android_id = "".join("%x" % random.randint(1, 15) for _ in range(16))
    build_model = "Pixel 2 XL"
    ctime = str(int(time.time()))

    # ---------- 1. device_reg ----------
    param_dict = {
        'app_name': 'achievo_ad', 'app_version': '7.83.3',
        'device_token': device_token, 'status': '1', 'warehouse': 'null',
        'manufacturer': 'Google', 'device': build_model, 'os_version': '30',
        'channel': CHANNEL, 'vipruid': '', 'regPlat': '0', 'regid': '',
        'rom': 'Dalvik/2.1.0 (Linux; U; Android 11; Pixel 2 XL Build/RP1A.201005.004.A1)',
        'skey': SKEY,
    }
    res = requests.get(
        url="https://mp.appvipshop.com/apns/device_reg",
        params=param_dict,
        headers={"Authorization": "OAuth api_sign={}".format(sign(sorted_query(param_dict)))},
        verify=False, timeout=20,
    )
    print("[1] device_reg ->", res.status_code, res.text[:200])
    time.sleep(1)

    # ---------- 2. getTokenByFP ----------
    res = requests.get(
        url=f"https://vcsp-api.vip.com/token/getTokenByFP?vcspKey={VCSP_KEY}",
        headers={"vcspauthorization": f"vcspSign={VCSP_SIGN}"},
        verify=False, timeout=20,
    )
    print("[2] getTokenByFP ->", res.status_code, res.text[:200])
    vsp_dict = res.json()['data']
    vcsp_token = vsp_dict['vcspToken']
    time.sleep(1)

    # ---------- 3. generate_token ----------
    dinfo = ('{"ah1":"","ah2":"","ah3":"","ah4":"wifi","ah5":"1440_2712","ah6":1900800,'
             '"ah7":8,"ah8":3839954944,"ah9":"%s","ah10":"","ah11":"","ah12":"","ah13":"",'
             '"as1":"11","as2":"","as3":"","as4":"%s","as5":"","as6":"","as7":"30","ac1":"%s"}'
             % (build_model, android_id, device_token))
    data_dict = {
        "app_name": "shop_android", "app_version": "7.83.3", "client_type": "android",
        "dinfo": quote_plus(dinfo), "mars_cid": mars_cid, "phone_model": build_model,
        "session_id": f"{mars_cid}_shop_android_{ctime}", "sys_version": "30",
        "vcspKey": VCSP_KEY, "vcspToken": vcsp_token,
    }
    md5 = hashlib.md5()
    md5.update(b'aee4c425dbb2288b80c71347cc37d04b')
    aes_key = md5.digest()

    body_dict = {
        'api_key': API_KEY, 'did': '',
        'edata': make_edata(sorted_query(data_dict), aes_key),
        'eversion': '0', 'skey': SKEY, 'timestamp': int(time.time()),
    }
    res = requests.post(
        url="https://mapi.appvipshop.com/vips-mobile/rest/device/generate_token",
        data=body_dict,
        headers={"Authorization": "OAuth api_sign={}".format(sign(sorted_query(body_dict)))},
        verify=False, timeout=20,
    )
    print("[3] generate_token ->", res.status_code, res.text[:300])
    did = res.json()['data']['token']['did']
    print("    did =", did)
    time.sleep(1)

    # ---------- 4. 搜索 ----------
    key_word = "外套女"
    search_dict = {
        "api_key": API_KEY, "app_name": "shop_android", "app_version": "7.83.3",
        "bigSaleTagIds": "", "brandIds": "", "brandStoreSns": "", "categoryId": "",
        "channelId": "1", "channel_flag": "0_1", "client": "android",
        "client_type": "android", "darkmode": "0", "deeplink_cps": "",
        "device_model": build_model, "did": did, "elder": "0",
        "extParams": '{"priceVer":"2","mclabel":"1","cmpStyle":"1","statusVer":"2",'
                     '"ic2label":"1","video":"2","uiVer":"2","preheatTipsVer":"4",'
                     '"floatwin":"1","superHot":"1","exclusivePrice":"1","router":"1",'
                     '"coupons":"1","needVideoExplain":"1","rank":"2","needVideoGive":"1",'
                     '"bigBrand":"1","couponVer":"v2","videoExplainUrl":"1","live":"1",'
                     '"sellpoint":"1","reco":"1","vreimg":"1","search_tag":"2","tpl":"1",'
                     '"stdSizeVids":"","labelVer":"2"}',
        "fdc_area_id": "103101101109",
        "functions": "RTRecomm,flagshipInfo,feedback,otdAds,zoneCode,slotOp,survey,hasTabs,floaterParams",
        "harmony_app": "0", "harmony_os": "0", "headTabType": "all",
        "height": "2712", "isMultiTab": "0", "keyword": key_word,
        "lastPageProperty": '{"isBgToFront":"0","suggest_text":"%s","scene_entry_id":"-99",'
                            '"refer_page_id":"page_te_globle_classify_search_%d","text":"%s","tag":"1",'
                            '"module_name":"com.achievo.vipshop.search","type":"all","typename":"全部",'
                            '"is_back_page":"0"}' % (key_word, int(time.time() * 1000) - 200, key_word),
        "maker": "GOOGLE", "mars_cid": mars_cid, "mobile_channel": CHANNEL,
        "mobile_platform": "3", "net": "WIFI", "operator": "", "os": "Android",
        "osv": "11", "otddid": "", "other_cps": "",
        "page_id": "page_te_commodity_search_{}".format(int(time.time() * 1000)),
        "phone_model": build_model.lower(), "priceMax": "", "priceMin": "", "props": "",
        "province_id": "103101",
        "referer": "com.achievo.vipshop.search.activity.TabSearchProductListActivity",
        "rom": "Dalvik/2.1.0 (Linux; U; Android 11; Pixel 2 XL Build/RP1A.201005.004.A1)",
        "sd_tuijian": "0", "service_provider": "",
        "session_id": f"{mars_cid}_shop_android_{ctime}", "skey": SKEY, "sort": "0",
        "source": "app", "source_app": "android", "standby_id": CHANNEL,
        "sys_version": "30", "timestamp": ctime,
        "union_mark": "blank&_&blank&_&oziq7dxw:::&_&blank&_&blank",
        "vipService": "", "warehouse": "VIP_SH", "width": "1440",
    }
    res = requests.post(
        url="https://mapi.appvipshop.com/vips-mobile/rest/shopping/search/product/list/v1",
        data=search_dict,
        headers={"Authorization": "OAuth api_sign={}".format(sign(sorted_query(search_dict)))},
        verify=False, timeout=20,
    )
    print("[4] search ->", res.status_code, "len=", len(res.text))
    body = res.text
    print(body[:500])

    # 解析商品标题，验证搜索真正返回了商品数据
    import json as _json
    try:
        j = _json.loads(body)
        products = j.get('products') or j.get('data', {}).get('products') or []
        titles = [p.get('productName') or p.get('title') for p in products if p]
        print("    商品数:", len(products))
        for t in titles[:10]:
            print("    -", t)
    except Exception:
        print("    响应非标准 JSON，保留原文")

    print()
    print("接口链复刻结束")


if __name__ == "__main__":
    main()
