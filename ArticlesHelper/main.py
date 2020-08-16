import requests
import os
import re
import json
from rich.console import Console
from rich import print
from rich.table import Table
from pathlib import Path
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from urllib.request import urlopen
from rich.progress import (
    BarColumn,
    DownloadColumn,
    TextColumn,
    TransferSpeedColumn,
    TimeRemainingColumn,
    Progress,
    TaskID,
)

progress = Progress(
    TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
    BarColumn(bar_width=None),
    "[progress.percentage]{task.percentage:>3.1f}%",
    "•",
    DownloadColumn(),
    "•",
    TransferSpeedColumn(),
    "•",
    TimeRemainingColumn(),
)


def copy_url(task_id: TaskID, url: str, path: str) -> None:
    try:
        print('\n下载进度')
        response = urlopen(url)
        # This will break if the response doesn't contain content length
        progress.update(task_id, total=int(response.info()["Content-length"]))
        with open(path, "wb") as dest_file:
            progress.start_task(task_id)
            for data in iter(partial(response.read, 32768), b""):
                dest_file.write(data)
                progress.update(task_id, advance=len(data))
    except Exception as e:
        print('下载' + task_id + '出错啦，原因：' + str(e))


def download(urls, dest_dir):
    try:
        with progress:
            with ThreadPoolExecutor(max_workers=4) as pool:
                for key, value in urls.items():
                    if value is None:
                        continue
                    filename = key.replace('/', '_') + '.pdf'
                    dest_path = os.path.join(dest_dir, filename)
                    task_id = progress.add_task("download",
                                                filename=filename,
                                                start=False)
                    pool.submit(copy_url, task_id, value, dest_path)
    except Exception as e:
        print('出错啦，原因：' + str(e))


def init():
    # 判断目录
    path = Path('./articles/')
    if path.is_dir() is False:
        os.mkdir(path)
    version = 2.2
    urlgithub = 'https://raw.githubusercontent.com/evilbutcher/Python/master/ArticlesHelper/release.json'
    try:
        update = requests.get(urlgithub)
        with open('./articles/versions.json', 'wb') as f:
            f.write(update.content)
        with open(file='./articles/versions.json', mode='r',
                  encoding='utf-8') as f:
            content = f.read()
            ver = json.loads(content)
        if ver['releases'][0]['version'] > version:
            print('文献下载助手[bold red]更新[/bold red]啦！\n最新版本是：' +
                  str(ver['releases'][0]['version']))
            print('更新内容是：' + ver['releases'][0]['details'] + '\n\n')
            print('可前往项目地址：https://github.com/evilbutcher/Python 查看Releases')
    except (Exception):
        urlgitee = 'https://gitee.com/evilbutcher/Python/raw/master/ArticlesHelper/release.json'
        try:
            update = requests.get(urlgitee)
            with open('./articles/versions.json', 'wb') as f:
                f.write(update.content)
            with open(file='./articles/versions.json',
                      mode='r',
                      encoding='utf-8') as f:
                content = f.read()
                ver = json.loads(content)
            if ver['releases'][0]['version'] > version:
                print('文献下载助手[bold red]更新[/bold red]啦！\n最新版本是：' +
                      str(ver['releases'][0]['version']))
                print('更新内容是：' + ver['releases'][0]['details'] + '\n\n')
                print(
                    '可前往项目地址：https://github.com/evilbutcher/Python 查看Releases')
        except Exception as e:
            print('检测更新失败，原因：')
            print(str(e))


def stwgetdllink(name, doi):
    try:
        hostlink = 'https://sci-hub.tw/'
        link = hostlink + doi
        data = requests.get(link)
        # 获取下载链接
        html = data.text
        afterhtml = BeautifulSoup(html, 'html.parser')
        div = afterhtml.find('iframe', id='pdf')
        pdflink = div.get('src')
        if re.match(r'https:', pdflink) is None:
            postlink = 'https:' + pdflink
        else:
            postlink = pdflink
        print('获取下载链接成功：' + postlink)
        urls[doi] = postlink
        return True
    except Exception as e:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("文件名")
        table.add_column("状态")
        table.add_column("原因")
        table.add_row(name, '[bold red]未找到文献[/bold red]', str(e))
        console.print(table)
        urls[doi] = None
        return False


def ssegetdllink(name, doi):
    try:
        hostlink = 'https://sci-hub.se/'
        link = hostlink + doi
        data = requests.get(link)
        # 获取下载链接
        html = data.text
        afterhtml = BeautifulSoup(html, 'html.parser')
        div = afterhtml.find('iframe', id='pdf')
        pdflink = div.get('src')
        if re.match(r'https:', pdflink) is None:
            postlink = 'https:' + pdflink
        else:
            postlink = pdflink
        print('获取下载链接成功：' + postlink)
        urls[doi] = postlink
        return True
    except Exception as e:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("文件名")
        table.add_column("状态")
        table.add_column("原因")
        table.add_row(name, '[bold red]未找到文献[/bold red]', str(e))
        console.print(table)
        urls[doi] = None
        return False


def lbggetdllink(name, doi):
    try:
        hostlink = 'https://libgen.lc/scimag/ads.php?doi='
        link = hostlink + doi
        data = requests.get(link)
        # 获取下载链接
        html = data.text
        afterhtml = BeautifulSoup(html, 'html.parser')
        div = afterhtml.find('a')
        pdflink = div.get('href')
        print('获取下载链接成功：' + pdflink)
        urls[doi] = pdflink
        return True
    except Exception as e:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("文件名")
        table.add_column("状态")
        table.add_column("原因")
        table.add_row(name, '[bold red]未找到文献[/bold red]', str(e))
        console.print(table)
        urls[doi] = None
        return False


def continuousgetlink(name, doi, i):
    if (i + 1) % 3 == 1:
        if stwgetdllink(name, doi) is False:
            print('自动更换地址，重新获取...')
            if lbggetdllink(name, doi) is False:
                print('自动更换地址，重新获取...')
                if ssegetdllink(name, doi) is False:
                    print('很抱歉，此文献未找到')
    elif (i + 1) % 3 == 2:
        if lbggetdllink(name, doi) is False:
            print('自动更换地址，重新获取...')
            if ssegetdllink(name, doi) is False:
                print('自动更换地址，重新获取...')
                if stwgetdllink(name, doi) is False:
                    print('很抱歉，此文献未找到')
    else:
        if ssegetdllink(name, doi) is False:
            print('自动更换地址，重新获取...')
            if lbggetdllink(name, doi) is False:
                print('自动更换地址，重新获取...')
                if stwgetdllink(name, doi) is False:
                    print('很抱歉，此文献未找到')


if __name__ == "__main__":
    init()
    console = Console()
    print('\n特别感谢Rich项目 https://github.com/willmcgugan/rich \n作者@evilbutcher')
    print('\n若为多篇文献请用[bold red]英文逗号[/bold red]分隔')
    doi = input('请输入DOI：')
    print('\n开始下载...')
    print('\n[bold yellow]说明[/bold yellow]：提示文献未找到只是其中一个接口未找到文献，会自动更新接口获取下载地址')
    dois = list(doi.split(','))
    print('\n输入的doi为：')
    print(dois)
    urls = {}
    for index, value in enumerate(dois):
        filename = value.replace('/', '_') + '.pdf'
        continuousgetlink(filename, value, index)
    print('\n匹配下载链接[bold green]完成[/bold green]')
    print(urls)
    download(urls, './articles/')
    input('下载完成，如遇问题请前往 https://github.com/evilbutcher/Python 提出issue，按任意键退出')
