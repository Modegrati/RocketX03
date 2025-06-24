import aiohttp
import asyncio
import random
import re
import os
import json
import time
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np
from itertools import product
import multiprocessing as mp
from faker import Faker
from colorama import init, Fore, Style
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style as PromptStyle

# Inisialisasi
init(autoreset=True)
console = Console()
fake = Faker()

# Header Free Palestine
FREE_PALESTINE_HEADER = f"""
{Fore.GREEN + Style.BRIGHT}
   _____ ____  ______  _______ ______ 
  |  ___|  _ \\|  _  \\|  ___|  _  \\
  | |__ | | | | | | | |___ | | | |
  |  __|| | | | | | |  ___|| | | |
  | |___| |_/ /|_| |_| |___| |_/ /
  |_____|____/ \\____/\\____/\\____/ 
{Fore.RED + Style.BRIGHT}  FREEDOM FOR PALESTINE! 🇵🇸
{Fore.GREEN + Style.BRIGHT}  By Mr.4Rex_503 Error System
{Fore.RED + Style.BRIGHT}  Fuzzing Endpoint API v2.0
"""

# Proxy rotator
PROXY_LIST = [
    "http://proxy1:port",
    "http://proxy2:port",
    # Isi proxy sendiri, bro! Cari di free-proxy-list.net atau beli premium
]
proxy_pool = iter(PROXY_LIST * 10)
HEADERS = {"User-Agent": fake.user_agent()}

# Buat folder hasil
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
RESULTS_DIR = f"results_{timestamp}"
os.makedirs(RESULTS_DIR, exist_ok=True)

# Animasi loading
def hacker_loading(message):
    console.print(f"[bold green]{message}[/]", end="")
    for _ in range(3):
        console.print(".", end="", flush=True)
        time.sleep(0.5)
    console.print("")

# Setup browser anonim
def setup_anonymous_browser():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument(f"--proxy-server={next(proxy_pool)}")
    chrome_options.add_argument(f"--user-agent={fake.user_agent()}")
    driver = uc.Chrome(options=chrome_options)
    console.print(f"[bold red]Browser anonim diaktifkan![/]", style="blink")
    return driver

# Crawler super powerfull
async def quantum_crawler(url, max_depth, live_table, results):
    visited = set()
    files = {"js": set(), "css": set(), "xml": set(), "other": set()}
    endpoints = set()
    
    async def fetch_page(page_url, session, depth=0):
        if page_url in visited or depth > max_depth:
            return
        visited.add(page_url)
        
        try:
            hacker_loading(f"Scanning {page_url}")
            driver = setup_anonymous_browser()
            driver.get(page_url)
            html = driver.page_source
            driver.quit()
            
            soup = BeautifulSoup(html, "html.parser")
            
            # Cari semua file
            for tag in soup.find_all(["script", "link", "a"], href=True) + soup.find_all("script", src=True):
                file_url = urljoin(page_url, tag.get("href") or tag.get("src"))
                if file_url.endswith(".js"):
                    files["js"].add(file_url)
                    results["files"].append({"type": "JS", "url": file_url})
                elif file_url.endswith(".css"):
                    files["css"].add(file_url)
                    results["files"].append({"type": "CSS", "url": file_url})
                elif file_url.endswith(".xml"):
                    files["xml"].add(file_url)
                    results["files"].append({"type": "XML", "url": file_url})
                else:
                    files["other"].add(file_url)
                    results["files"].append({"type": "Other", "url": file_url})
                
                # Cari link ke halaman lain
                if tag.name == "a" and file_url.startswith(url):
                    endpoints.add(file_url)
                    results["endpoints"].append(file_url)
                    update_live_table(live_table, results)
                    await fetch_page(file_url, session, depth + 1)
            
            # Cari endpoint API di inline JS
            inline_scripts = soup.find_all("script", type=lambda x: not x or "javascript" in x.lower())
            for script in inline_scripts:
                if script.string:
                    api_urls = re.findall(r'[\'"]/(?:api|graphql|rest|v\d)/[^\'"]+[\'"]', script.string)
                    for api_url in api_urls:
                        full_url = urljoin(url, api_url.strip("'\""))
                        endpoints.add(full_url)
                        results["endpoints"].append(full_url)
                        update_live_table(live_table, results)
            
            console.print(f"[bold green]Scanned: {page_url} 🕵️[/]")
        except Exception as e:
            console.print(f"[bold red]Error crawling {page_url}: {e} 😡[/]")
    
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        await fetch_page(url, session)
    
    return endpoints, files

# Fuzzing endpoint API dewa
def quantum_fuzzing(url, endpoints, live_table, results):
    common_paths = [
        "api", "v1", "v2", "graphql", "rest", "jsonrpc", "users", "auth",
        "posts", "comments", "profile", "settings", "notifications", "data",
        "login", "register", "search", "feed", "timeline"
    ]
    verbs = ["get", "post", "put", "delete", "patch"]
    
    def generate_paths():
        paths = []
        for length in range(1, 5):
            for combo in product(common_paths, repeat=length):
                path = "/".join(combo)
                paths.append(f"/{path}")
                for verb in verbs:
                    paths.append(f"/{verb}/{path}")
        return paths
    
    def predict_endpoints(paths, existing_endpoints):
        all_paths = list(paths) + list(existing_endpoints)
        vectorizer = TfidfVectorizer(analyzer="char", ngram_range=(3, 6))
        X = vectorizer.fit_transform(all_paths)
        kmeans = KMeans(n_clusters=15, random_state=42)
        kmeans.fit(X)
        predicted = [all_paths[i] for i in np.argsort(kmeans.transform(X)[:, 0])[:100]]
        return predicted
    
    def fuzz_path(path):
        try:
            driver = setup_anonymous_browser()
            test_url = urljoin(url, path)
            driver.get(test_url)
            status = driver.execute_script("return window.performance.getEntriesByType('resource')[0]?.responseStatus || 0")
            driver.quit()
            
            if status in [200, 201, 401, 403, 429]:
                results["api_endpoints"].append({"url": test_url, "status": status})
                update_live_table(live_table, results)
                console.print(f"[bold red]Found endpoint: {test_url} (Status: {status}) 💥[/]", style="blink")
                return test_url, status
        except:
            pass
        return None
    
    hacker_loading("Memulai fuzzing kuantum")
    paths = generate_paths()
    predicted_paths = predict_endpoints(paths, endpoints)
    
    with mp.Pool(mp.cpu_count()) as pool:
        results_fuzz = pool.map(fuzz_path, predicted_paths)
    
    return [(url, status) for url, status in results_fuzz if url]

# Update tabel live
def update_live_table(live_table, results):
    table = Table(title="Live Scanning Results", style="bold green")
    table.add_column("Type", style="cyan")
    table.add_column("URL", style="magenta")
    table.add_column("Status", style="yellow")
    
    for endpoint in results["endpoints"][-5:]:  # Tampilkan 5 endpoint terakhir
        table.add_row("Endpoint", endpoint, "-")
    
    for file in results["files"][-5:]:  # Tampilkan 5 file terakhir
        table.add_row(file["type"], file["url"], "-")
    
    for api in results["api_endpoints"][-5:]:  # Tampilkan 5 API terakhir
        table.add_row("API", api["url"], str(api["status"]))
    
    live_table.update(Panel(table, style="bold red"))

# Simpan hasil
def save_results(results):
    with open(os.path.join(RESULTS_DIR, "results.json"), "w") as f:
        json.dump(results, f, indent=4)
    
    with open(os.path.join(RESULTS_DIR, "results.txt"), "w") as f:
        f.write("=== Quantum API Scanner Results ===\n")
        f.write(f"Timestamp: {timestamp}\n\n")
        f.write("Endpoints:\n")
        for endpoint in results["endpoints"]:
            f.write(f"- {endpoint}\n")
        f.write("\nFiles:\n")
        for file in results["files"]:
            f.write(f"- {file['type']}: {file['url']}\n")
        f.write("\nAPI Endpoints:\n")
        for api in results["api_endpoints"]:
            f.write(f"- {api['url']} (Status: {api['status']})\n")
    
    console.print(f"[bold green]Hasil disimpan di {RESULTS_DIR}! 📁[/]")

# Menu interaktif
style = PromptStyle.from_dict({
    "prompt": "bold green",
    "input": "bold cyan"
})
session = PromptSession(style=style)

async def main_menu():
    results = {"endpoints": [], "files": [], "api_endpoints": []}
    
    while True:
        console.print(Panel(FREE_PALESTINE_HEADER, style="bold green"))
        console.print("[bold red]=== MENU UTAMA ===[/]", style="blink")
        console.print("[bold green]1. Start Scan[/]")
        console.print("[bold green]2. Set Max Depth[/]")
        console.print("[bold green]3. Exit[/]")
        
        choice = await session.prompt_async("Pilih opsi > ")
        
        if choice == "1":
            url = await session.prompt_async("Masukkan URL target > ")
            if not url.startswith("http"):
                url = "https://" + url
            
            max_depth = int(await session.prompt_async("Masukkan max depth (default 10) > ", default="10"))
            
            with Live(auto_refresh=True) as live:
                table = Table(title="Live Scanning Results", style="bold green")
                table.add_column("Type", style="cyan")
                table.add_column("URL", style="magenta")
                table.add_column("Status", style="yellow")
                live.update(Panel(table, style="bold red"))
                
                hacker_loading("Memulai quantum crawler")
                endpoints, files = await quantum_crawler(url, max_depth, live, results)
                
                hacker_loading("Memulai fuzzing kuantum")
                api_endpoints = quantum_fuzzing(url, endpoints, live, results)
            
            save_results(results)
            console.print(f"[bold green]Scanning selesai, bro! Free Palestine! 🇵🇸[/]", style="blink")
        
        elif choice == "2":
            max_depth = await session.prompt_async("Masukkan max depth baru > ")
            console.print(f"[bold green]Max depth diatur ke {max_depth}[/]")
        
        elif choice == "3":
            console.print("[bold red]Keluar dari sistem, bro! Stay safe! 😎[/]")
            break

# Jalankan
if __name__ == "__main__":
    asyncio.run(main_menu())
