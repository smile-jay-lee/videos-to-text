"""
交互式 Bilibili 音频下载测试

使用方法:
    python tests/test_bili_download.py

支持的输入格式（手动粘贴即可）:
    1. 纯 BV 号:       BV1SpZMBQEfE
    2. 完整链接:       https://www.bilibili.com/video/BV1SpZMBQEfE?buvid=XXX...
    3. B站分享文本:    【标题...哔哩哔哩】 https://b23.tv/trexFcr
    4. 短链接:         https://b23.tv/trexFcr
"""

import sys
import os
import time
from pathlib import Path

# ── 路径设置：让脚本在任意目录下都能找到 backend ────────────────────────────
ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / 'backend'
sys.path.insert(0, str(BACKEND))

# 直接加载 bili_service，避免通过 services/__init__.py 触发 whisper/numba
import importlib.util, types

# 注入轻量级的 logger / file_handler stub（不依赖完整项目环境）
def _make_stub_logger():
    class _L:
        def _log(self, level, msg):
            print(f"[{level}] {msg}")
        info    = lambda self, m, **kw: self._log("INFO",    m)
        warning = lambda self, m, **kw: self._log("WARN",    m)
        error   = lambda self, m, **kw: self._log("ERROR",   m)
        debug   = lambda self, m, **kw: self._log("DEBUG",   m)
    return _L()

_logger_mod = types.ModuleType("utils.logger")
_logger_mod.get_logger = lambda name: _make_stub_logger()

_fh_mod = types.ModuleType("utils.file_handler")
_fh_mod.ensure_dir = lambda p: os.makedirs(p, exist_ok=True)
_fh_mod.get_safe_filename = lambda s: (
    s.translate(str.maketrans(r'<>:"/\|?*', '_________'))
     .strip()[:180]
)

sys.modules["utils"] = types.ModuleType("utils")
sys.modules["utils.logger"] = _logger_mod
sys.modules["utils.file_handler"] = _fh_mod

_spec = importlib.util.spec_from_file_location(
    "bili_service", BACKEND / "services" / "bili_service.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
BiliAudioService = _mod.BiliAudioService

# ── 工具函数 ─────────────────────────────────────────────────────────────────

def hr(char='─', width=60):
    print(char * width)

def file_info(path: str) -> str:
    p = Path(path)
    if not p.exists():
        return "（文件不存在）"
    size = p.stat().st_size
    if size >= 1024 * 1024:
        return f"{size / 1024 / 1024:.2f} MB"
    return f"{size / 1024:.1f} KB"

# ── 主流程 ────────────────────────────────────────────────────────────────────

def main():
    hr('═')
    print("  Bilibili 音频下载 — 交互式测试")
    hr('═')
    print("支持输入:")
    print("  · 纯 BV 号           BV1SpZMBQEfE")
    print("  · 完整 bilibili URL  https://www.bilibili.com/video/BV1xxx...")
    print("  · 短链接             https://b23.tv/xxx")
    print("  · 微信/QQ 分享文本   【xxx哔哩哔哩】 https://b23.tv/xxx")
    print("  · 输入 q 退出")
    hr()

    output_dir = ROOT / "downloads" / "bili_test"
    service = BiliAudioService(output_dir=str(output_dir))

    while True:
        print()
        raw = input("请粘贴输入 > ").strip()
        if not raw:
            continue
        if raw.lower() in ('q', 'quit', 'exit'):
            print("退出。")
            break

        # 如果是多P视频可以指定分P
        page_num = None
        if ' p=' in raw.lower():
            parts = raw.rsplit(' p=', 1)
            raw = parts[0].strip()
            try:
                page_num = int(parts[1].strip())
            except ValueError:
                pass

        hr()
        print(f"输入内容: {raw[:120]}{'...' if len(raw) > 120 else ''}")
        if page_num:
            print(f"指定分P: {page_num}")

        # ── 第一步：先获取元数据，让用户确认是正确的视频 ────────────────
        print("\n[1/2] 获取视频信息...")
        t0 = time.time()
        info = service.get_video_info(raw)

        if not info:
            print("✗ 无法获取视频信息，请检查链接是否正确或视频是否公开。")
            hr()
            continue

        elapsed = time.time() - t0
        print(f"✓ 获取成功 ({elapsed:.1f}s)")
        print()
        print(f"  标题   : {info['title']}")
        print(f"  UP主   : {info['owner']}")
        print(f"  BVID   : {info['bvid']}")
        print(f"  时长   : {info['duration']} 秒")
        print(f"  总分P  : {len(info['pages'])} P")

        if len(info['pages']) > 1:
            print()
            print("  分P列表 (前10条):")
            for p in info['pages'][:10]:
                print(f"    P{p['page']:>3}  {p['title']}  ({p['duration']}s)")
            if len(info['pages']) > 10:
                print(f"    ... 共 {len(info['pages'])} P")
            if not page_num:
                print()
                pn_str = input("  下载第几P？（直接回车下载第1P）> ").strip()
                if pn_str:
                    try:
                        page_num = int(pn_str)
                    except ValueError:
                        print("  无效的分P编号，默认下载第1P")

        # ── 确认 ────────────────────────────────────────────────────────
        print()
        confirm = input("是这个视频吗？确认下载? [y/N] > ").strip().lower()
        if confirm not in ('y', 'yes'):
            print("已取消。")
            hr()
            continue

        # ── 第二步：下载 ─────────────────────────────────────────────────
        print(f"\n[2/2] 开始下载 (分P={page_num or 1})...")
        t1 = time.time()
        result = service.download_audio(raw, page_num=page_num)
        elapsed2 = time.time() - t1

        print()
        if result:
            size_str = file_info(result)
            print(f"✓ 下载成功！({elapsed2:.1f}s，{size_str})")
            print(f"  文件路径: {result}")
            print()
            print("  请播放该文件，确认音频是否正确：")
            print(f"    explorer \"{Path(result).parent}\"")
        else:
            print("✗ 下载失败。")
            print("  可能原因:")
            print("  · 该视频需要大会员")
            print("  · 网络问题或API限流")
            print("  · BV号/链接不存在")

        hr()

if __name__ == '__main__':
    main()
