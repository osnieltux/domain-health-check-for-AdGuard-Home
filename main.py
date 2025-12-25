import asyncio
import aiohttp
from asyncio import Semaphore
import sys

MAX_CONCURRENT = 1000
TIMEOUT = 20
INPUT_FILE = "toCheck.txt"
OUTPUT_FILE = "results.txt"
OUTPUT_LOG = "log.txt"
DEBUG_TIMEOUT = False
DEBUG_STATUS_200 = True
DEBUG_STATUS_FAIL = False
DEBUG_CLIENT_CONNECTOR_ERROR = True
CREATE_ADGUARD = False
CREATE_LOG = True

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

class URLChecker:
    def __init__(self, max_concurrent=MAX_CONCURRENT, timeout=TIMEOUT):
        self.max_concurrent = max_concurrent
        self.timeout = timeout
        self.semaphore = Semaphore(max_concurrent)
        self.results = {
            'success': [],
            'error': [],
            'timeout': []
        }
        self.urls_checked = 0
        self.total_urls = 0
        self.lock = asyncio.Lock()
    
    async def check_url(self, session, url):
        async with self.semaphore:
            global HEADERS
            try:
                # Agregar http:// si no tiene protocolo
                if not url.startswith(('http://', 'https://')):
                    check_url = f'http://{url}'
                else:
                    check_url = url
                
                timeout = aiohttp.ClientTimeout(total=self.timeout)
                
                async with session.get(check_url, timeout=timeout, allow_redirects=True, headers=HEADERS) as response:
                    if response.status == 200:
                        self.results['success'].append({
                            'url': url,
                            'status': response.status
                        })
                        if DEBUG_STATUS_200:
                            print(f"ok {url} - Status: {response.status}")
                    else:
                        self.results['error'].append({
                            'url': url,
                            'status': response.status
                        })
                        if DEBUG_STATUS_FAIL:
                            print(f"fail {url} - Status: {response.status}")
            
            except asyncio.TimeoutError:
                self.results['timeout'].append(url)
                if DEBUG_TIMEOUT:
                    print(f"timeout {url} - TIMEOUT (>{self.timeout}s)")
            
            except aiohttp.ClientConnectorError:
                self.results['error'].append({
                    'url': url,
                    'status': 'No existe / No accesible'
                })
                if DEBUG_CLIENT_CONNECTOR_ERROR:
                    print(f"✗ {url} - No existe o no es accesible")
            
            except Exception as e:
                self.results['error'].append({
                    'url': url,
                    'status': str(type(e).__name__)
                })
                print(f"Error on {url} - Error: {type(e).__name__}")
            
            finally:
                async with self.lock:
                    self.urls_checked += 1
    
    async def check_urls_batch(self, urls):
        connector = aiohttp.TCPConnector(limit=self.max_concurrent)
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = [self.check_url(session, url) for url in urls]
            await asyncio.gather(*tasks, return_exceptions=True)
    
    def load_urls_from_file(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
            return urls
        except FileNotFoundError:
            print(f"Error: file not found '{filename}'")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file: {e}")
            sys.exit(1)
    
    def save_results(self, filename, is_adguard=True):
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                if is_adguard:
                    f.write("| List of custom urls:\n\n")
                for item in self.results['success']:
                    if is_adguard:
                        f.write(f"||{item['url']}^\n")
                    else:
                        f.write(f"{item['url']}\n")
                f.write("\n")
                
            
            print(f"File saved: '{filename}'\n")
        except Exception as e:
            print(f"Error on save file '{filename}', error: {e}")
    
    def print_summary(self):
        total = len(self.results['success']) + len(self.results['error']) + len(self.results['timeout'])
        print(f"Total de URLs verificadas: {total}")
        print(f"Alive: {len(self.results['success'])}")
        print(f"Errors: {len(self.results['error'])}")
        print(f"Timeouts: {len(self.results['timeout'])}")
        

async def monitor_progress(checker, interval=10):
    """Simlpe  monitor"""
    while checker.urls_checked < checker.total_urls:
        await asyncio.sleep(interval)
        remaining = checker.total_urls - checker.urls_checked
        percentage = (checker.urls_checked / checker.total_urls) * 100
        print(f"PROGRESS: {checker.urls_checked}/{checker.total_urls} ({percentage:.1f}%) - Remaining: {remaining}")

async def main():
    checker = URLChecker(max_concurrent=MAX_CONCURRENT, timeout=TIMEOUT)
    
    print(f"Reading URLs from '{INPUT_FILE}'...")
    urls = checker.load_urls_from_file(INPUT_FILE)
    
    if not urls:
        print("No URLs founded on the file '{INPUT_FILE}'")
        return
    
    checker.total_urls = len(urls)
    print(f"Founded  {len(urls)} URLs")
    print(f"Checking with {MAX_CONCURRENT} simultaneous requests...")
    print("(Press Ctrl+C to cancel)\n")
    
    try:
        # Init tasks
        monitor_task = asyncio.create_task(monitor_progress(checker))
        check_task = asyncio.create_task(checker.check_urls_batch(urls))
        
        
        # wait for the check task to complete
        await check_task
        monitor_task.cancel()
        
        checker.print_summary()
        if CREATE_ADGUARD:
            checker.save_results(OUTPUT_FILE)
        if CREATE_LOG:
            checker.save_results(OUTPUT_LOG, is_adguard=False)

    except KeyboardInterrupt:
        print("\nConceled by user")
        sys.exit(0)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nConceled by user")
        sys.exit(0)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

    sys.exit(0)
