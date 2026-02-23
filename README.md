# 🕵️ Recon Automation Tool

Bu araç Subdomain keşfi, Web Archive taraması, endpoint analizi ve port taraması yapan otomatik bir recon aracı.

---

## 🚀 Özellikler

 Subdomain Keşfi — assetfinder + httpx ile canlı subdomainleri bulur
 Web Archive Taraması — Wayback Machine'den hassas dosya ve URL'leri çeker
 Endpoint Analizi — gau + waybackurls ile endpoint, parametre ve JS analizi yapar
 Hassas Endpoint Tespiti — Admin, API, config gibi kritik path'leri filtreler
 Nmap Taraması — Açık port ve servis tespiti yapar
 Multi-Thread — Tüm işlemler paralel çalışır
---

## 🛠️ Gereksinimler

| Araç | Zorunlu | Kullanım |
|---|---|---|
| Python 3.x | ✅ | Ana dil |
| assetfinder | ✅ | Subdomain keşfi |
| httpx | ✅ | Canlı subdomain filtresi |
| gau | ✅ | URL toplama |
| waybackurls | ✅ | URL toplama |
| curl | ✅ | JS dosyası indirme |
| nmap | ⚪ Opsiyonel | Port taraması |

### Dış araçlar:
Aşağıdakilerin sistemde kurulu olması gerekir:

#### 🔹 1. assetfinder  

#### 🔹 2. httpx 

#### 🔹 3. Gau

#### 🔹 4. nmap  

---

## 📌 Kullanım

En basit kullanım:


### Parametreler:
- python3 recon.py -u example.com -t 15 --nmap --endpoints
  
| Parametre | Açıklama |
|----------|----------|
| `-u` | Hedef domain (zorunlu) |
| `-t` | Thread sayısı (varsayılan: 10) |
| `--nmap` | Subdomain’lere Nmap -A taraması yapar |
| `--endpoints` | Subdomain’lere Endpoint analizi yapar |




