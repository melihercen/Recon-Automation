import os
import re
import subprocess
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

FOLDER = "recon-folders"


def run_command(command):
    """Basit komut çalıştırıcı"""
    try:
        subprocess.run(command, shell=True, check=True)
    except Exception as e:
        print(f"[HATA] Komut çalıştırılamadı: {e}")


def clean_domain(url):
    """http/https/port gibi parçaları temizler"""
    url = url.replace("http://", "").replace("https://", "")
    url = url.split("/")[0]
    url = url.split(":")[0]
    return url.strip()


def webarchive(subdomain):
    target_folder = f"{FOLDER}/{subdomain}"
    os.makedirs(target_folder, exist_ok=True)

    all_url = f"{target_folder}/all_url.txt"
    filtered_url = f"{target_folder}/filtered.txt"

    print(f"[+] {subdomain} → Web Archive taranıyor...")

    run_command(
        f"curl -s -G 'https://web.archive.org/cdx/search/cdx/' "
        f"--data-urlencode 'url={subdomain}/*' "
        f"--data-urlencode 'collapse=urlkey' "
        f"--data-urlencode 'fl=original' "
        f"> {all_url}"
    )

    if os.path.getsize(all_url) == 0:
        print(f"[!] {subdomain} için Web Archive sonucu bulunamadı.")
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

    
    run_command(f"assetfinder --subs-only {url} | httprobe > {sub_file}")
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


def process_target(target, run_nmap):
    print(f"\n[*] {target} işleniyor...")
    webarchive(target)
    if run_nmap:
        nmap_scan(target)
    return target


def main(args):
    url = clean_domain(args.u)
    run_nmap = args.nmap
    max_thread = args.t

    targets = find_subdomains(url)
    if not targets:
        print("[!] Hedef bulunamadı, çıkılıyor...")
        return

    with ThreadPoolExecutor(max_workers=max_thread) as executor:
        futures = {
            executor.submit(process_target, target, run_nmap): target
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
        epilog="Örnek: python3 recon.py -u example.com -t 10 --nmap",
    )

    parser.add_argument("-u", required=True, help="Hedef domain")
    parser.add_argument("-t", type=int, default=10, help="Thread sayısı")
    parser.add_argument("--nmap", action="store_true", help="Nmap taraması yap")

    args = parser.parse_args()
    main(args)
