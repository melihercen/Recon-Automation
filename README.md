# 🕵️ Recon Automation Tool

Bu araç, hedef domain üzerinde otomatik bilgi toplama (recon) işlemlerini gerçekleştirmek için geliştirilmiş bir Python scriptidir.  
Subdomain keşfi, Web Archive (Wayback Machine) analizi ve isteğe bağlı Nmap taramalarını çoklu thread yapısıyla hızlı bir şekilde gerçekleştirir.

---

## 🚀 Özellikler

- **Subdomain keşfi**
  - assetfinder + httprobe ile canlı subdomain toplama
- **Web Archive (Wayback Machine) taraması**
  - Tüm arşivlenmiş URL’leri çekme
  - Hassas endpoint filtreleme (admin/login/api/backup vb.)
- **Otomatik klasörleme**
  - Her subdomain için ayrı klasör oluşturma
- **Opsiyonel Nmap taraması**
  - `-A` parametresi ile OS detection + service detection
- **Çoklu iş parçacığı (Thread) desteği**
  - Büyük hedeflerde ciddi hız kazandırır
- **Temiz loglama**
  - Her aşamada ne yapıldığı ekrana yansır

---

## 📦 Gereksinimler

### Operating System:
- Linux (Kali, Ubuntu, Parrot OS vs.)

### Python modülleri:
- Standart modüller (ekstra kurulum gerekmez):
  - `argparse`, `subprocess`, `re`, `os`, `concurrent.futures`

### Dış araçlar:
Aşağıdakilerin sistemde kurulu olması gerekir:

#### 🔹 1. assetfinder  

#### 🔹 2. httprobe  

#### 🔹 3. nmap  

---

## 📌 Kullanım

En basit kullanım:


### Parametreler:
- python3 recon.py -u example.com -t 15 --nmap
  
| Parametre | Açıklama |
|----------|----------|
| `-u` | Hedef domain (zorunlu) |
| `-t` | Thread sayısı (varsayılan: 10) |
| `--nmap` | Subdomain’lere Nmap -A taraması yapar |



