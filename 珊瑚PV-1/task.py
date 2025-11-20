import argparse
import json
import random
import threading
import time
from datetime import datetime
from colorama import Fore, Style, init
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 初始化 colorama
init(autoreset=True)

def current_time(is_error=False):
    time_stamp = datetime.now().strftime('<%H:%M:%S>')
    return Fore.RED + time_stamp + Style.RESET_ALL if is_error else Fore.GREEN + time_stamp + Style.RESET_ALL

def parse_args():
    parser = argparse.ArgumentParser(description="ShanHuPV->完全模拟浏览器行为的流量测试工具")
    parser.add_argument('-t', type=int, required=True, help='线程数 (1-999)')
    parser.add_argument('-s', type=int, required=True, help='访问时间 (1-999) 秒')
    parser.add_argument('-r', type=int, required=True, help='每个网页刷新次数 (0-999)')
    parser.add_argument('-a', type=int, required=True, help='每个网页点击链接数 (0-999)')
    parser.add_argument('-u', type=str, required=True, help='链接URL 必须指定 后面跟上代理类型')
    parser.add_argument('proxy', choices=['http', 'socks5'], help='代理类型 (http 或 socks5)')
    parser.add_argument('--eye', action='store_true', help='显示浏览器窗口')

    return parser.parse_args()

def open_browser(url, proxy=None, user_agent=None, headless=True):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless')
    else:
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920x1080')
    
    if proxy:
        chrome_options.add_argument(f'--proxy-server={proxy}')
    if user_agent:
        chrome_options.add_argument(f'--user-agent={user_agent}')
    
    chrome_options.add_argument('--log-level=3')
    chrome_options.binary_location = 'Chrome/chrome.exe'

    service = Service('chromedriver_win32/chromedriver.exe')
    
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(url)
        return driver
    except WebDriverException as e:
        print(f"{current_time(is_error=True)} 浏览器启动异常")
        return None

def perform_task(driver, url, refresh_count, click_count, wait_time):
    blacklist = ['javascript:diagnoseErrors()']

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        
        for _ in range(refresh_count):
            driver.refresh()
            time.sleep(1)
        
        links = driver.find_elements(By.TAG_NAME, 'a')
        for _ in range(click_count):
            if links:
                link = random.choice(links)
                link_href = link.get_attribute('href')

                if link_href and link_href not in blacklist:
                    try:
                        link.click()
                        time.sleep(1)
                        links = driver.find_elements(By.TAG_NAME, 'a')
                    except Exception as e:
                        pass
                else:
                    print(f"{current_time(is_error=True)} 页面加载失败")

        status_code = driver.execute_script("return document.readyState") == "complete"
        page_title = driver.title

        if status_code:
            print(f"{current_time()} 访问成功, 状态码: 200, Ref/Title: {page_title}")
        else:
            print(f"{current_time(is_error=True)} 访问失败, 状态码: 404 或 其他错误")
        
        time.sleep(wait_time)
        driver.quit()

    except TimeoutException:
        print(f"{current_time(is_error=True)} 访问超时")
        driver.quit()
    except Exception as e:
        print(f"{current_time(is_error=True)} 访问失败: {e}")
        driver.quit()

def task(url, proxies, user_agents, wait_time, refresh_count, click_count, lock, task_counter, headless):
    while True:
        with lock:
            if not proxies:
                break
            proxy = proxies.pop(0)
            task_number = task_counter[0]
            task_counter[0] += 1
        user_agent = random.choice(user_agents)["user_agent"]
        device = random.choice(user_agents)["device"]

        print(f"{current_time()} 任务#{task_number}, ip: {proxy.split(':')[0]}, ua: {device}")

        driver = open_browser(url, proxy, user_agent, headless)
        if driver:
            perform_task(driver, url, refresh_count, click_count, wait_time)
        else:
            print(f"{current_time(is_error=True)} 浏览器或代理IP异常")

def main():
    args = parse_args()

    print(f"{current_time()} 同时运行的任务数量: {args.t}")
    print(f"{current_time()} 维持的访问时间: {args.s} 秒")
    print(f"{current_time()} 每个任务刷新网页的次数: {args.r}")
    print(f"{current_time()} 随机点击网页内链接的次数: {args.a}")
    print(f"{current_time()} 访问的 URL: {args.u}")
    print(f"{current_time()} 使用的代理类型: {args.proxy}")

    proxy_file = 'proxy_http.txt' if args.proxy == 'http' else 'proxy_socks5.txt'
    with open(proxy_file, 'r') as file:
        proxies = [line.strip() for line in file if line.strip()]

    with open('proxy_ua.json', 'r') as file:
        ua_data = json.load(file)
        user_agents = ua_data["user_agents"]

    print(f"{current_time()} 代理 ip（共 {len(proxies)} 条数据）:")
    if proxies:
        print(f"{current_time()} {' '.join([proxy.split(':')[0] for proxy in proxies[:2]])}", end=' ')
        if len(proxies) > 2:
            print(f"...", end=' ')
        print()
    
    print(f"{current_time()} 代理 ua（共 {len(user_agents)} 条数据）:")
    if user_agents:
        print(f"{current_time()} {' '.join([ua['device'] for ua in user_agents[:2]])}", end=' ')
        if len(user_agents) > 2:
            print(f"...", end=' ')
        print()
    
    lock = threading.Lock()
    task_counter = [1]

    threads = []
    for _ in range(args.t):
        thread = threading.Thread(target=task, args=(args.u, proxies, user_agents, args.s, args.r, args.a, lock, task_counter, not args.eye))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print(f"{current_time()} 所有代理 IP 已使用完")

if __name__ == "__main__":
    main()
