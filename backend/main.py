import requests
import os
import json
from concurrent.futures import ThreadPoolExecutor

MAX_PER_FILE = 30
MAX_FILES = 10
THREADS = 10
WORK_DIR = "proxies"
SOURCE_URLS = [
    "https://openproxylist.com/v2ray/",
    "https://raw.githubusercontent.com/freefq/free/master/v2",
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/learnhard-cn/free_proxy_ss/main/v2ray.txt",
    "https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2",
    "https://raw.githubusercontent.com/mfuu/v2ray/master/v2ray",
    "https://raw.githubusercontent.com/Alvin9999/v2ray/master/v2ray.txt"
]

GITHUB_SOURCE_LINE = "📎 Source: https://github.com/lexariley/v2ray-test"

def fetch_proxies():
    proxies = []
    for url in SOURCE_URLS:
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                lines = res.text.strip().splitlines()
                proxies.extend([line for line in lines if line.startswith("vless://")])
        except:
            continue
    return list(set(proxies))

def get_ip_from_vless(vless_link):
    try:
        host = vless_link.split("@")[1].split(":")[0]
        return host
    except:
        return ""

def get_country_emoji(ip):
    try:
        res = requests.get(f"https://ipinfo.io/{ip}/json", timeout=5)
        country = res.json().get("country", "")
        if len(country) == 2:
            return chr(0x1F1E6 + ord(country[0]) - 65) + chr(0x1F1E6 + ord(country[1]) - 65)
    except:
        pass
    return "🌐"

def decorate_proxy(proxy):
    ip = get_ip_from_vless(proxy)
    flag = get_country_emoji(ip)
    return f"{flag} {proxy} 🔒 by alirahmti"

def process_proxies(proxies):
    with ThreadPoolExecutor(max_workers=THREADS) as pool:
        decorated = list(pool.map(decorate_proxy, proxies))
    return decorated

def write_subscriptions(decorated):
    os.makedirs(WORK_DIR, exist_ok=True)
    for i in range(MAX_FILES):
        chunk = decorated[i * MAX_PER_FILE:(i + 1) * MAX_PER_FILE]
        if not chunk:
            break
        output = [GITHUB_SOURCE_LINE] + chunk
        with open(f"{WORK_DIR}/sub{i+1}.txt", "w") as f:
            f.write("\n".join(output))
        print(f"[+] sub{i+1}.txt written with {len(chunk)} proxies")

def main():
    print("[*] Fetching vless proxies...")
    raw = fetch_proxies()
    print(f"[*] Found {len(raw)} vless proxies. Decorating...")
    decorated = process_proxies(raw)
    write_subscriptions(decorated)

if __name__ == "__main__":
    main()
