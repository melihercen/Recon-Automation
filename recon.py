import os
import re
import subprocess
import argparse
import time
import random
from threading import Lock
from concurrent.futures import ThreadPoolExecutor, as_completed

FOLDER = "recon-output"
wa_lock=Lock()


def run_command(command):
    """Basit komut çalıştırıcı"""
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        pass
    except Exception as e:
        print(f"[HATA] Komut çalıştırılamadı: {e}")

def run_command_output(command):
    """Komut çalıştırır ve çıktıyı döndürür"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        print(f"[HATA] {e}")
        return ""
def clean_domain(url):
    """http/https/port gibi parçaları temizler"""
    url = url.replace("http://", "").replace("https://", "")
    url = url.split("/")[0]
    url = url.split(":")[0]
    return url.strip()


def endpoint_finder(subdomain):
    target_folder=f"{FOLDER}/{subdomain}"
    os.makedirs(target_folder,exist_ok=True)

    raw_urls_file=f"{target_folder}/endpoints_raw.txt"
    js_files_file=f"{target_folder}/js_files.txt"
    endpoints_file=f"{target_folder}/endpoints.txt"
    js_endpoints_file=f"{target_folder}/js_endpoints.txt"
    params_file= f"{target_folder}/parameters.txt"

    print(f"[+] {subdomain} → Endpoint taraması başlıyor...")

    run_command(
        f"{{ gau {subdomain} 2>/dev/null; waybackurls {subdomain} 2>/dev/null; }}"
        f"| sort -u > {raw_urls_file}"
    )   

    if not os.path.exists(raw_urls_file) or os.path.getsize(raw_urls_file)==0:
        print(f"[!] {subdomain} için URL bulunamadı.")
        if not os.path.exists(raw_urls_file):
            os.remove(raw_urls_file)
        return
    
    with open(raw_urls_file,"r") as f:
        all_urls=[line.strip() for line in f if line.strip()]

    print(f"    [>] {len(all_urls)} URL toplandı.")

    js_urls=[u for u in all_urls if u.endswith(".js") and "min.js" not in u]
    with open(js_files_file,"w") as f:
        f.write("\n".join(js_urls))
    print(f"    [>] {len(js_urls)} JS dosyası bulundu.")


    js_endpoint_pattern = re.compile(
        r"""['"` ]((/[a-zA-Z0-9_\-./]+){2,}|"""
        r"""(https?://[a-zA-Z0-9._\-]+(/[a-zA-Z0-9_\-./?=&%#+@!:,;*(){}[\]|\\^~`'"<>]{1,200})?))""",
        re.MULTILINE
    )

    extracted_js_endpoints=set()

    if js_urls:
        print(f"    [>] JS dosyaları analiz ediliyor...")
        for js_urls in js_urls[:50]:
            try:
                content=run_command_output(
                    f"curl -s -m 10 -A 'Mozilla/5.0' '{js_urls}' 2>/dev/null"
                )
                if content:
                    matches=js_endpoint_pattern.findall(content)
                    for match in matches:
                        endpoint=match[0].strip("'\"` ")
                        if endpoint and len(endpoint)>3:
                            extracted_js_endpoints.add(endpoint)
            except Exception:
                continue
        
        with open(js_endpoints_file,"w") as f:
            f.write("\n".join(sorted(extracted_js_endpoints)))
        print(f"    [>] JS dosyalarından {len(extracted_js_endpoints)} endpoint çıkarıldı.")
    
    endpoint_pattern=re.compile(r"https?://[^/]+(/[^\s?#]*)")
    unique_paths=set()

    for url in all_urls:
        match=endpoint_pattern.search(url)
        if match:
            path=match.group(1)
            if not re.search(r"\.(png|jpg|jpeg|gif|svg|ico|woff|woff2|ttf|eot|css)$", path, re.I):
                unique_paths.add(path)
    
    for ep in extracted_js_endpoints:
        if ep.startswith("/"):
            unique_paths.add(ep)

    with open(endpoints_file,"w") as f:
        f.write("\n".join(sorted(unique_paths)))
    print(f"    [>] Toplam {len(unique_paths)} unique endpoint bulundu.")

    param_pattern = re.compile(r"[?&]([a-zA-Z0-9_\-]+)=")
    unique_params = set()

    for url in all_urls:
        params=param_pattern.findall(url)
        for p in params:
            unique_params.add(p)

    if unique_params:
        with open(params_file,"w") as f:
            f.write("\n".join(sorted(unique_params)))
        print(f"    [>] {len(unique_params)} unique parametre bulundu.")

    sensitive_endpoints=[
        p for p in unique_paths
        if re.search(
            r"(admin|api|login|auth|token|config|upload|debug|secret|internal|"
            r"backup|test|staging|dev|\.env|\.git|graphql|swagger|v1|v2|v3)",
            p, re.I
            )
        and not re.search(
            r"(/p_[a-z0-9\-]+_[0-9]+$|"     
            r"/[a-z]{2}/[a-z]{2}/|"          
            r"\.(png|jpg|css|js|gif|svg)$|"  
            r"/[a-z]{2}/p_)",                  
            p, re.I
        )
    ]
    if sensitive_endpoints:
        sensitive_file=f"{target_folder}/sensitive_endpoints.txt"
        with open(sensitive_file,"w") as f:
            f.write("\n".join(sorted(sensitive_endpoints)))
        print(f"    [!] {len(sensitive_endpoints)} hassas endpoint tespit edildi → {sensitive_file}")
    
    print(f"[+] {subdomain} → Endpoint taraması tamamlandı.")


def webarchive(subdomain):
    target_folder = f"{FOLDER}/{subdomain}"
    os.makedirs(target_folder, exist_ok=True)

    all_url = f"{target_folder}/all_url.txt"
    filtered_url = f"{target_folder}/filtered.txt"

    print(f"[+] {subdomain} → Web Archive taranıyor...")

    with wa_lock:
        sleep_time=random.uniform(2.0,5.0)
        time.sleep(sleep_time)
        run_command(
                f"curl -s -G -A 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:100.0) Gecko/20100101 Firefox/100.0' "
                f"'https://web.archive.org/cdx/search/cdx/' "
                f"--data-urlencode 'url={subdomain}/*' "
                f"--data-urlencode 'collapse=urlkey' "
                f"--data-urlencode 'fl=original' "
                f"> {all_url}"
            )

    if not os.path.exists(all_url) or os.path.getsize(all_url)==0:
        print(f"[!] {subdomain} için Web Archive sonucu bulunamadı.")
        if os.path.exists(all_url):
	        os.remove(all_url)
        return
    
    else:
        
        sensitive_pattern = re.compile(
            r"(admin|login|signin|signup|register|user|dashboard|panel|manage|"
            r"internal|private|config|backup|shell|api|console|test|staging|dev|debug|"
            r"secret|token|passwd|password|reset|forgot|support|contact|email|upload|download|"
            r"\.(bak|old|backup|zip|tar|gz|7z|rar|sql|db|sqlite|csv|xls|xlsx|doc|docx|pdf|txt|"
            r"json|xml|yaml|yml|env|ini|log|cache|pem|crt|key|pub|asc|md5|sh|exe|dll|bin|iso|"
            r"apk|msi|tmp)$)",
            re.IGNORECASE,
        )

        with open(all_url, "r") as infile, open(filtered_url, "w") as outfile:
            for line in infile:
                if sensitive_pattern.search(line):
                    outfile.write(line)
        if os.path.getsize(filtered_url)==0:
            os.remove(filtered_url)

        print(f"[+] {subdomain} → Web Archive filtreleme tamamlandı.")


def nmap_scan(subdomain):
    target_folder = f"{FOLDER}/{subdomain}"
    os.makedirs(target_folder, exist_ok=True)
    nmap_result = f"{target_folder}/nmap.txt"

    print(f"[+] {subdomain} → Nmap taraması başlıyor...")

   
    command = f"nmap -A -T4 {subdomain} > {nmap_result}"
    run_command(command)

    print(f"[+] {subdomain} → Nmap tamamlandı.")


def find_subdomains(url):
    print(f"[+] {url} için subdomain keşfi başlatılıyor...")
    os.makedirs(FOLDER, exist_ok=True)

    sub_file = f"{FOLDER}/sub-{url}.txt"
    subs_file = f"{FOLDER}/subs-{url}.txt"

    
    run_command(
    f"assetfinder --subs-only {url} | "
    f"httpx -silent -threads 20 -rate-limit 50 -timeout 5 -retries 1 "
    f"> {sub_file}"
    )
    run_command(f"sort -u {sub_file} > {subs_file}")

    live_subdomains = []
    with open(subs_file, "r") as file:
        for line in file:
            cleaned = clean_domain(line)
            if cleaned:
                live_subdomains.append(cleaned)

    if not live_subdomains:
        print("[!] Canlı subdomain bulunamadı.")
        return []

    print(f"[+] {len(live_subdomains)} canlı subdomain bulundu.")
    return live_subdomains


def process_target(target, run_nmap,run_endpoints):
    print(f"\n[*] {target} işleniyor...")
    webarchive(target)
    if run_endpoints:
        endpoint_finder(target)
    if run_nmap:
        nmap_scan(target)
    return target


def main(args):
    global FOLDER
    url = clean_domain(args.u)
    FOLDER=f"recon-folders-{url}"
    if not os.path.exists(FOLDER):
        os.makedirs(FOLDER)
    run_nmap = args.nmap
    max_thread = args.t
    run_endpoints=args.endpoints

    targets = find_subdomains(url)
    if not targets:
        print("[!] Hedef bulunamadı, çıkılıyor...")
        return

   
    with ThreadPoolExecutor(max_workers=max_thread) as executor:
        futures = {
            executor.submit(process_target, target, run_nmap,run_endpoints): target
            for target in targets
        }

        for future in as_completed(futures):
            target = futures[future]
            try:
                future.result()
                print(f"[OK] {target} tamamlandı.")
            except Exception as e:
                print(f"[HATA] {target} hata verdi: {e}")

    print("\n------------- TARAMA TAMAMLANDI -------------")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Recon Tool",
        epilog="Örnek: python3 recon.py -u example.com -t 10 --nmap --endpoints",
    )

    parser.add_argument("-u", required=True, help="Hedef domain")
    parser.add_argument("-t",type=int,default=10,help="Thread sayısı")
    parser.add_argument("--nmap", action="store_true", help="Nmap taraması yap")
    parser.add_argument("--endpoints", action="store_true", help="Endpoint analizi yap")

    args = parser.parse_args()
    main(args)
