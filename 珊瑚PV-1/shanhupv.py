import argparse
from colorama import Fore, init
import subprocess
import sys
import psutil

# 初始化 colorama
init(autoreset=True)

logo = r"""
 ______   __  __   ______   __   __   __  __   __  __   ______  __   __     O  o O
/\  ___\ /\ \_\ \ /\  __ \ /\ "-.\ \ /\ \_\ \ /\ \/\ \ /\  == \/\ \ / /    o  o   O
\ \___  \\ \  __ \\ \  __ \\ \ \-.  \\ \  __ \\ \ \_\ \\ \  _-/\ \ v /      o   O
 \/\_____\\ \_\ \_\\ \_\ \_\\ \_\\"\_\\ \_\ \_\\ \_____\\ \_\   \ \ |    o   o
  \/_____/ \/_/\/_/ \/_/\/_/ \/_/ \/_/ \/_/\/_/ \/_____/ \/_/    \/_/     o
 o  o   O   o   O   o   o   o   O   o   o   O   o   o     V1.0.240805   o                                                                                                                                                         
"""

def parse_args():
    parser = argparse.ArgumentParser(description="ShanHuPV->完全模拟浏览器行为的流量测试工具")
    parser.add_argument('-t', type=int, default=3, help='线程数 (1-999)')
    parser.add_argument('-s', type=int, default=10, help='访问时间 (1-999) 秒')
    parser.add_argument('-r', type=int, default=3, help='每个网页刷新次数 (0-999)')
    parser.add_argument('-a', type=int, default=3, help='每个网页点击链接数 (0-999)')
    parser.add_argument('-u', type=str, required=True, help='链接URL 必须指定 后面跟上代理类型')
    parser.add_argument('proxy', choices=['http', 'socks5'], help='代理类型 (http 或 socks5)')
    parser.add_argument('--eye', action='store_true', help='显示浏览器窗口')

    args = parser.parse_args()

    # 参数校验
    if not (1 <= args.t <= 999):
        parser.error("-t 参数必须在 1 到 999 之间")
    if not (1 <= args.s <= 999):
        parser.error("-s 参数必须在 1 到 999 之间")
    if not (0 <= args.r <= 999):
        parser.error("-r 参数必须在 0 到 999 之间")
    if not (0 <= args.a <= 999):
        parser.error("-a 参数必须在 0 到 999 之间")

    # 检查修正 URL
    if not args.u.startswith(('http://', 'https://')):
        args.u = 'http://' + args.u

    return args

def print_system_usage():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_usage = psutil.virtual_memory().percent
    print(f"{Fore.YELLOW}CPU占用率: {cpu_usage}%")
    print(f"{Fore.YELLOW}内存占用率: {memory_usage}%")

def main():
    # 打印logo
    print(Fore.CYAN + logo)
    
    # 打印系统资源占用
    print_system_usage()

    # 解析参数
    args = parse_args()

    # 调用 task.py
    command = [
        sys.executable, 'task.py',
        '-t', str(args.t),
        '-s', str(args.s),
        '-r', str(args.r),
        '-a', str(args.a),
        '-u', args.u,
        args.proxy
    ]
    if args.eye:
        command.append('--eye')
    subprocess.run(command)

if __name__ == "__main__":
    main()
