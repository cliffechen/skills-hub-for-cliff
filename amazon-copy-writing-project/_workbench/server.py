#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
产品设计稿文案工作台 · 本地服务端

- 仅使用 Python 3 标准库（无第三方依赖、无外网请求、完全离线可用）
- 只绑定 127.0.0.1，不对外暴露端口
- 服务根目录 = 本文件所在目录的上一级（_workbench 的上一级），不硬编码盘符
"""

import json
import os
import shutil
import socket
import sys
import threading
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse, parse_qs

# ----------------------------------------------------------------- 路径推导
WORKBENCH_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(WORKBENCH_DIR)          # 服务根目录（_workbench 上一级）
COPY_JSON = os.path.join(WORKBENCH_DIR, 'copy.json')
BACKUP_DIR = os.path.join(WORKBENCH_DIR, '.backup')
EXPORT_DIR = os.path.join(WORKBENCH_DIR, '导出')
INDEX_HTML = os.path.join(WORKBENCH_DIR, 'index.html')

# ----------------------------------------------------------------- 常量
PORT_START, PORT_END = 8787, 8806
MAX_BACKUPS = 30
IMAGE_EXTS = ('.png', '.jpg', '.jpeg', '.webp')
STATIC_EXTS = ('.html', '.js', '.css', '.png', '.jpg', '.jpeg', '.webp',
               '.svg', '.ico', '.txt', '.woff', '.woff2')
STYLES = ('A', 'B', 'C', 'D')
FLAG_LABEL = {'warn': '提示', 'error': '必须处理', 'info': '说明'}
# 这些路径不通过静态路由对外提供（_skill 为只读参考资料，不是工作台功能）
WORKBENCH_DENY = ('_skill', '.backup')
WORKBENCH_DENY_FILES = ('copy.json',)


# ----------------------------------------------------------------- 工具函数
def ensure_dirs():
    for d in (BACKUP_DIR, EXPORT_DIR):
        if not os.path.isdir(d):
            os.makedirs(d)


def find_free_port():
    """从 8787 起探测可用端口，最多试到 8806；全部占用则返回 None。"""
    for port in range(PORT_START, PORT_END + 1):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(('127.0.0.1', port))
            return port
        except OSError:
            continue
        finally:
            sock.close()
    return None


def safe_join(base, rel):
    """把 rel 拼到 base 下；若结果逃出 base 则返回 None（路径穿越防护）。"""
    base = os.path.abspath(base)
    target = os.path.normpath(os.path.join(base, rel))
    if target == base:
        return target
    if target.startswith(base + os.sep):
        return target
    return None


def with_pct(value):
    """把数字规范为 0.5% 精度。"""
    try:
        n = float(value)
    except (TypeError, ValueError):
        return None
    return round(n * 2) / 2.0


# ----------------------------------------------------------------- 导出 Markdown
def div_markdown(slot):
    """发散备选小节（text 与 card 槽位）。"""
    divs = slot.get('divs') or []
    if not divs:
        return []
    out = []
    out.append('- 发散备选（角度创新，不分风格）：')
    for idx, dv in enumerate(divs, 1):
        out.append('  %d. 角度：%s' % (idx, dv.get('zh', '')))
        out.append('  ```')
        for line in str(dv.get('en', '')).split('\n'):
            out.append('  ' + line)
        out.append('  ```')
    return out


def free_markdown(module):
    """自由创作小节（不受槽位约束的创意提案）。"""
    free = module.get('free') or {}
    angles = free.get('angles') or []
    if not angles:
        return []
    out = []
    out.append('### 自由创作（不受槽位约束）')
    out.append('')
    if free.get('read'):
        out.append('- 读图结论：%s' % free['read'])
        out.append('')
    for idx, angle in enumerate(angles, 1):
        out.append('#### 角度 %d｜%s' % (idx, angle.get('name', '')))
        out.append('')
        if angle.get('why'):
            out.append('- 角度理由：%s' % angle['why'])
            out.append('')
        copy = angle.get('copy') or {}
        for title, key in (('主标', 'headline'), ('副标', 'subhead'), ('收尾', 'closer')):
            out.append('- %s：' % title)
            out.append('  ```')
            for line in str(copy.get(key, '')).split('\n'):
                out.append('  ' + line)
            out.append('  ```')
        points = copy.get('points') or []
        if points:
            out.append('- 要点：')
            for p in points:
                out.append('  - %s' % p)
        out.append('')
    return out


def scenario_markdown(module):
    """本图适配场景（研究背景）。"""
    scs = module.get('scenarios') or []
    if not scs:
        return []
    out = ['**本图适配场景（研究背景，非上线文案）**：', '']
    for idx, sc in enumerate(scs, 1):
        out.append('- %d. %s' % (idx, sc.get('title', '')))
        for label, key in (('问题', 'problem'), ('方案', 'solution'),
                           ('解决后的状态', 'after'), ('落位建议', 'placement')):
            if sc.get(key):
                out.append('  - %s：%s' % (label, sc[key]))
    out.append('')
    return out


def audience_markdown(data):
    """导出附录：产品人群基础研究与场景切入。"""
    aud = data.get('audience') or {}
    if not aud:
        return []
    out = []
    out.append('---')
    out.append('')
    out.append('## 附录：产品人群基础研究与场景切入')
    out.append('')
    out.append('> 研究背景，**非上线文案**（不参与禁词扫描；上线表述仍以白名单主张为准）。')
    out.append('> 研究日期：%s' % aud.get('researchedAt', '—'))
    out.append('> 方法：%s' % aud.get('method', ''))
    out.append('')

    out.append('### 一、功效理解（逐成分 · 联网所得）')
    out.append('')
    for e in aud.get('efficacy', []):
        out.append('#### %s' % e.get('ingredient', ''))
        out.append('')
        out.append('- 科学界怎么说：%s' % e.get('whatScienceSays', ''))
        out.append('- 证据强度：%s' % e.get('evidence', ''))
        out.append('- 来源：%s' % '；'.join(e.get('sources') or []))
        out.append('- 对文案的启示：%s' % e.get('copyImplication', ''))
        out.append('')

    out.append('### 二、受众人群分层')
    out.append('')
    for s in aud.get('segments', []):
        out.append('#### [%s] %s' % (s.get('tier', ''), s.get('name', '')))
        out.append('')
        out.append('- 为什么是这群人：%s' % s.get('why', ''))
        for m in s.get('mindset') or []:
            out.append('- 心智原话：「%s」' % m)
        for h in s.get('copyHooks') or []:
            out.append('- 对文案的启示：%s' % h)
        out.append('')

    cautions = aud.get('cautions') or []
    if cautions:
        out.append('### 三、定位风险提示')
        out.append('')
        for c in cautions:
            out.append('- %s' % c)
        out.append('')

    pool = aud.get('scenarioPool') or []
    if pool:
        out.append('### 四、产品级候选场景池')
        out.append('')
        for idx, sc in enumerate(pool, 1):
            out.append('- %d. %s' % (idx, sc.get('title', '')))
            for label, key in (('问题', 'problem'), ('方案', 'solution'), ('解决后的状态', 'after')):
                if sc.get(key):
                    out.append('  - %s：%s' % (label, sc[key]))
        out.append('')

    if aud.get('regenPrompt'):
        out.append('### 五、换产品时如何重新生成（可复制指令）')
        out.append('')
        out.append('```text')
        out.append(aud['regenPrompt'])
        out.append('```')
        out.append('')
    return out


def slot_markdown(slot, style):
    """按 §5.4 的导出格式生成单个槽位的 Markdown 片段。"""
    out = []
    out.append('### %s｜%s' % (slot.get('id', ''), slot.get('label', '')))
    out.append('- 判定：%s' % slot.get('judge', ''))
    kind = slot.get('kind', 'text')

    if kind == 'text':
        values = (slot.get('values') or {}).get(style) or {}
        for title, key in (('产出英文', 'rec'), ('备选', 'alt')):
            out.append('- %s：' % title)
            out.append('  ```')
            for line in str(values.get(key, '')).split('\n'):
                out.append('  ' + line)
            out.append('  ```')
        out.extend(div_markdown(slot))
    elif kind == 'card':
        card = (slot.get('cards') or {}).get(style) or {}
        out.append('- 名称：%s' % card.get('name', ''))
        out.append('- 剂量：%s' % card.get('dose', ''))
        out.append('- 说明1：%s' % card.get('line1', ''))
        out.append('- 说明2：%s' % card.get('line2', ''))
        out.extend(div_markdown(slot))
    elif kind == 'table':
        rows = (slot.get('rows') or {}).get(style) or []
        out.append('- 表格共 %d 行：' % len(rows))
        out.append('')
        out.append('  | # | 左列文案 |')
        out.append('  | --- | --- |')
        for idx, row in enumerate(rows, 1):
            out.append('  | %d | %s |' % (idx, str(row).replace('|', '\\|')))
        out.append('')
    elif kind == 'preserve':
        out.append('- 保留：%s' % slot.get('text', ''))
        out.append('- （原稿已定，不接受修改）')

    if slot.get('note'):
        out.append('- 中文说明：%s' % slot['note'])
    if slot.get('needs'):
        out.append('- 必须上图：%s' % slot['needs'])
    return out


def build_markdown(data, style, pending=None):
    """生成整份导出 Markdown。"""
    style_name = ''
    for item in data.get('styles', []):
        if item.get('id') == style:
            style_name = item.get('name', '')
    meta = data.get('meta', {})
    stamp = datetime.now()

    lines = []
    lines.append('# 详情页文案｜风格 %s：%s' % (style, style_name))
    lines.append('')
    lines.append('> 产品：%s　|　规格：%s' % (meta.get('product', ''), meta.get('spec', '')))
    lines.append('> 导出时间：%s' % stamp.strftime('%Y-%m-%d %H:%M'))
    lines.append('> 说明：正文为逐槽位落版文案（按风格 %s）；各模块另附「自由创作」与「本图适配场景」，文末附「产品人群基础研究」。' % style)
    lines.append('')

    disclaimer_mods = []
    for module in data.get('modules', []):
        lines.append('## %s｜%s（%s）' % (module.get('id', ''), module.get('name', ''),
                                         module.get('img', '')))
        lines.append('')
        lines.append('**本图任务**：%s' % module.get('task', ''))
        lines.append('')

        flags = module.get('flags') or []
        if flags:
            lines.append('**本图提示**：')
            for flag in flags:
                level = FLAG_LABEL.get(flag.get('level'), flag.get('level', ''))
                lines.append('- [%s] %s' % (level, flag.get('text', '')))
            lines.append('')

        declared = [s for s in module.get('slots', []) if s.get('needs')]
        if declared:
            disclaimer_mods.append((module.get('id', ''), module.get('img', ''),
                                    [s.get('id', '') for s in declared]))

        for slot in module.get('slots', []):
            lines.extend(slot_markdown(slot, style))
            lines.append('')

        lines.extend(free_markdown(module))
        lines.append('')

        lines.extend(scenario_markdown(module))

    lines.append('---')
    lines.append('')
    lines.append('## DSHEA 免责声明（必须上图，全文照抄）')
    lines.append('')
    lines.append('```')
    lines.append(meta.get('disclaimer', ''))
    lines.append('```')
    lines.append('')
    if disclaimer_mods:
        lines.append('需上图的模块与槽位：')
        lines.append('')
        for mid, img, sids in disclaimer_mods:
            lines.append('- %s（%s）：%s' % (mid, img, '、'.join(sids)))
        lines.append('')
    else:
        lines.append('无。')
        lines.append('')

    lines.extend(audience_markdown(data))

    lines.append('---')
    lines.append('')
    lines.append('## 未完成项 / 待确认')
    lines.append('')
    if pending:
        for item in pending:
            lines.append('- %s｜%s　%s' % (item.get('module', ''), item.get('slot', ''),
                                          item.get('label', '')))
    else:
        lines.append('无')
    lines.append('')
    lines.append('---')
    lines.append('')
    lines.append('*本稿供品牌审阅与设计执行；发布前须确认产品材料、最终图文及适用平台要求，不宣称已获平台批准或已验证转化效果。*')
    lines.append('')
    return '\n'.join(lines)


# ----------------------------------------------------------------- 请求处理
class Handler(BaseHTTPRequestHandler):
    server_version = 'Copy-Workbench/1.0'
    protocol_version = 'HTTP/1.1'

    # -------------------------------------------------- 基础输出
    def log_message(self, fmt, *args):
        try:
            sys.stdout.write('  %s %s\n' % (self.command, self.path))
            sys.stdout.flush()
        except Exception:
            pass

    def _send_bytes(self, code, body, ctype, extra=None):
        if isinstance(body, str):
            body = body.encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        for key, value in (extra or {}).items():
            self.send_header(key, value)
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _send_json(self, code, obj):
        self._send_bytes(code, json.dumps(obj, ensure_ascii=False), 'application/json; charset=utf-8')

    def _send_text(self, code, text):
        self._send_bytes(code, text, 'text/plain; charset=utf-8')

    def _send_file(self, abspath, ctype=None):
        if not os.path.isfile(abspath):
            self._send_text(404, '404 Not Found')
            return
        if ctype is None:
            ext = os.path.splitext(abspath)[1].lower()
            ctype = {
                '.html': 'text/html; charset=utf-8',
                '.js': 'text/javascript; charset=utf-8',
                '.css': 'text/css; charset=utf-8',
                '.json': 'application/json; charset=utf-8',
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.webp': 'image/webp',
                '.svg': 'image/svg+xml',
                '.ico': 'image/x-icon',
                '.txt': 'text/plain; charset=utf-8',
            }.get(ext, 'application/octet-stream')
        try:
            with open(abspath, 'rb') as handle:
                body = handle.read()
        except OSError:
            self._send_text(404, '404 Not Found')
            return
        self._send_bytes(200, body, ctype)

    def _not_allowed(self, method):
        self._send_json(405, {'ok': False, 'error': 'method not allowed (%s)' % method})

    # -------------------------------------------------- 其它方法一律 405
    def do_HEAD(self):
        self._not_allowed('HEAD')

    def do_PUT(self):
        self._not_allowed('PUT')

    def do_DELETE(self):
        self._not_allowed('DELETE')

    def do_PATCH(self):
        self._not_allowed('PATCH')

    def do_OPTIONS(self):
        self._not_allowed('OPTIONS')

    # -------------------------------------------------- GET
    def do_GET(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)

        if path == '/':
            self._send_bytes(302, b'', 'text/plain; charset=utf-8', {'Location': '/_workbench/'})
            return

        if path in ('/_workbench', '/_workbench/'):
            self._send_file(INDEX_HTML)
            return

        if path.startswith('/_workbench/'):
            self._serve_workbench_static(path)
            return

        if path == '/api/data':
            self._api_get_data()
            return

        if path in ('/api/export', '/api/open'):
            self._not_allowed('GET')
            return

        # 根目录图片（仅允许图片扩展名）
        rel = path.lstrip('/')
        if rel and os.path.splitext(rel)[1].lower() in IMAGE_EXTS:
            target = safe_join(ROOT_DIR, rel)
            if target is None:
                self._send_text(403, '403 Forbidden')
                return
            self._send_file(target)
            return

        self._send_text(404, '404 Not Found')

    def _serve_workbench_static(self, path):
        rel = path[len('/_workbench/'):]
        if not rel:
            self._send_file(INDEX_HTML)
            return
        head = rel.replace('\\', '/').split('/')[0]
        if head in WORKBENCH_DENY or os.path.basename(rel) in WORKBENCH_DENY_FILES:
            self._send_text(403, '403 Forbidden')
            return
        if os.path.splitext(rel)[1].lower() not in STATIC_EXTS:
            self._send_text(403, '403 Forbidden')
            return
        target = safe_join(WORKBENCH_DIR, rel)
        if target is None:
            self._send_text(403, '403 Forbidden')
            return
        self._send_file(target)

    def _api_get_data(self):
        if not os.path.isfile(COPY_JSON):
            self._send_json(500, {'ok': False, 'error': 'copy.json not found'})
            return
        try:
            with open(COPY_JSON, 'rb') as handle:
                body = handle.read()
        except OSError as exc:
            self._send_json(500, {'ok': False, 'error': 'read failed: %s' % exc})
            return
        self._send_bytes(200, body, 'application/json; charset=utf-8')

    # -------------------------------------------------- POST
    def do_POST(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        if path == '/api/data':
            self._api_post_data()
        elif path == '/api/export':
            self._api_post_export(parse_qs(parsed.query))
        elif path == '/api/open':
            self._api_post_open()
        else:
            self._send_text(404, '404 Not Found')

    def _read_body(self):
        try:
            length = int(self.headers.get('Content-Length') or 0)
        except ValueError:
            length = 0
        if length <= 0:
            return b''
        return self.rfile.read(length)

    def _api_post_data(self):
        raw = self._read_body()
        try:
            payload = json.loads(raw.decode('utf-8'))
        except (ValueError, UnicodeDecodeError):
            self._send_json(400, {'ok': False, 'error': 'invalid json'})
            return
        if not isinstance(payload, dict) or not isinstance(payload.get('modules'), list):
            self._send_json(400, {'ok': False, 'error': 'invalid json'})
            return

        saved_at = datetime.now().isoformat(timespec='seconds')
        meta = payload.get('meta')
        if not isinstance(meta, dict):
            meta = {}
            payload['meta'] = meta
        meta['savedAt'] = saved_at

        ensure_dirs()
        backup_name = None
        if os.path.isfile(COPY_JSON):
            backup_name = 'copy-%s.json' % datetime.now().strftime('%Y%m%d-%H%M%S')
            try:
                shutil.copy2(COPY_JSON, os.path.join(BACKUP_DIR, backup_name))
                prune_backups()
            except OSError as exc:
                self._send_json(500, {'ok': False, 'error': 'backup failed: %s' % exc})
                return

        tmp_path = COPY_JSON + '.tmp'
        try:
            with open(tmp_path, 'w', encoding='utf-8', newline='\n') as handle:
                json.dump(payload, handle, ensure_ascii=False, indent=2)
                handle.write('\n')
            os.replace(tmp_path, COPY_JSON)
        except OSError as exc:
            try:
                if os.path.isfile(tmp_path):
                    os.remove(tmp_path)
            except OSError:
                pass
            self._send_json(500, {'ok': False, 'error': 'write failed: %s' % exc})
            return

        self._send_json(200, {'ok': True, 'backup': backup_name, 'savedAt': saved_at})

    def _api_post_export(self, query):
        style = (query.get('style') or ['A'])[0].strip().upper()
        if style not in STYLES:
            self._send_json(400, {'ok': False, 'error': 'invalid style'})
            return
        pending = []
        raw = self._read_body()
        if raw:
            try:
                extra = json.loads(raw.decode('utf-8'))
                if isinstance(extra, dict) and isinstance(extra.get('pending'), list):
                    pending = [x for x in extra['pending'] if isinstance(x, dict)]
            except (ValueError, UnicodeDecodeError):
                pending = []

        if not os.path.isfile(COPY_JSON):
            self._send_json(500, {'ok': False, 'error': 'copy.json not found'})
            return
        try:
            with open(COPY_JSON, 'r', encoding='utf-8') as handle:
                data = json.load(handle)
        except (OSError, ValueError) as exc:
            self._send_json(500, {'ok': False, 'error': 'read failed: %s' % exc})
            return

        markdown = build_markdown(data, style, pending)
        ensure_dirs()
        name = '详情页文案-风格%s-%s.md' % (style, datetime.now().strftime('%Y%m%d-%H%M%S'))
        target = os.path.join(EXPORT_DIR, name)
        try:
            with open(target, 'w', encoding='utf-8', newline='\n') as handle:
                handle.write(markdown)
        except OSError as exc:
            self._send_json(500, {'ok': False, 'error': 'export failed: %s' % exc})
            return

        self._send_json(200, {'ok': True, 'path': os.path.abspath(target), 'name': name})

    def _api_post_open(self):
        raw = self._read_body()
        try:
            payload = json.loads(raw.decode('utf-8'))
        except (ValueError, UnicodeDecodeError):
            self._send_json(400, {'ok': False, 'error': 'invalid json'})
            return
        path = payload.get('path') if isinstance(payload, dict) else None
        which = payload.get('which') if isinstance(payload, dict) else None
        if not path and which in ('export', 'backup'):
            path = EXPORT_DIR if which == 'export' else BACKUP_DIR
        if not isinstance(path, str) or not path:
            self._send_json(400, {'ok': False, 'error': 'invalid path'})
            return

        target = os.path.realpath(path)
        allowed = False
        for base in (EXPORT_DIR, BACKUP_DIR):
            base_real = os.path.realpath(base)
            if target == base_real or target.startswith(base_real + os.sep):
                allowed = True
                break
        if not allowed:
            self._send_json(403, {'ok': False, 'error': 'path not allowed'})
            return
        if not os.path.exists(target):
            self._send_json(404, {'ok': False, 'error': 'not found'})
            return

        try:
            open_with_system(target)
        except Exception as exc:
            self._send_json(500, {'ok': False, 'error': 'open failed: %s' % exc})
            return
        self._send_json(200, {'ok': True})


# ----------------------------------------------------------------- 备份轮转
def prune_backups():
    """备份目录只保留最近 MAX_BACKUPS 个，按文件名倒序删除多余项。"""
    try:
        names = [n for n in os.listdir(BACKUP_DIR)
                 if n.startswith('copy-') and n.endswith('.json')]
    except OSError:
        return
    names.sort(reverse=True)
    for name in names[MAX_BACKUPS:]:
        try:
            os.remove(os.path.join(BACKUP_DIR, name))
        except OSError:
            pass


def open_with_system(target):
    if os.name == 'nt':
        os.startfile(target)  # noqa: S606 - Windows 专用
    elif sys.platform == 'darwin':
        import subprocess
        subprocess.Popen(['open', target])
    else:
        import subprocess
        subprocess.Popen(['xdg-open', target])


# ----------------------------------------------------------------- 启动
def banner(port):
    print('')
    print('=' * 66)
    print('  产品文案工作台（详情页 / A+ 文案）')
    print('=' * 66)
    print('  服务根目录 ：%s' % ROOT_DIR)
    print('  工作台地址 ：http://127.0.0.1:%d/_workbench/' % port)
    print('  数据文件   ：%s' % COPY_JSON)
    print('  备份目录   ：%s' % BACKUP_DIR)
    print('  导出目录   ：%s' % EXPORT_DIR)
    print('-' * 66)
    print('  仅绑定 127.0.0.1，不对外暴露；完全离线运行。')
    print('  关闭此窗口即停止服务。')
    print('=' * 66)
    print('')


def main():
    ensure_dirs()
    if not os.path.isfile(COPY_JSON):
        print('错误：未找到 copy.json —— %s' % COPY_JSON)
        return 1

    port = find_free_port()
    if port is None:
        print('错误：%d–%d 端口均被占用，请释放端口后重试。' % (PORT_START, PORT_END))
        return 1

    ThreadingHTTPServer.allow_reuse_address = False
    ThreadingHTTPServer.daemon_threads = True
    httpd = ThreadingHTTPServer(('127.0.0.1', port), Handler)

    banner(port)
    url = 'http://127.0.0.1:%d/_workbench/' % port
    threading.Timer(0.6, lambda: webbrowser.open(url)).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\n已停止服务。')
    finally:
        try:
            httpd.server_close()
        except Exception:
            pass
    return 0


if __name__ == '__main__':
    sys.exit(main())
