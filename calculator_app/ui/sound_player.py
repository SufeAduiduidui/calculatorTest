#音频文件，猫叫

#全局静音开关


from __future__ import annotations

import os
from typing import Dict, Optional

try:
    import pygame
    _PYGAME_OK = True
except Exception:
    pygame = None  # type: ignore
    _PYGAME_OK = False

_muted: bool = False
_music_volume_saved: float = 0.55 #最近一次playmusic的音量，取消静音时恢复

_SFX_CACHE_MAX = 32
_sfx_cache: Dict[str, "pygame.mixer.Sound"] = {}


def is_muted() -> bool:
    return _muted#当前是否静音


def set_muted(flag: bool) -> None:
    global _muted
    _muted = bool(flag)
    if not _ensure_mixer():
        return
    try:
        pygame.mixer.music.set_volume(0.0 if _muted else float(_music_volume_saved))
    except Exception:
        pass


def toggle_muted() -> None:
    set_muted(not is_muted())#切换静音状态


def play(path: str, volume: float = 1.0) -> bool:
    if is_muted():
        return False
    if not _ensure_mixer():
        return False
    try:
        sound = _get_sound(path)
        if sound is None:
            return False
        try:
            sound.set_volume(max(0.0, min(1.0, float(volume))))
        except Exception:
            pass
        sound.play()
        return True
    except Exception:
        return False


def play_music(path: str, volume: float = 0.55, loop: bool = True, start: float = 0.0) -> bool:
    if not _ensure_mixer():
        return False
    if not _file_exists(path):
        return False

    global _music_volume_saved
    try:
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

        pygame.mixer.music.load(path)
        _music_volume_saved = float(volume)

        vol = 0.0 if is_muted() else _music_volume_saved
        try:
            pygame.mixer.music.set_volume(vol)
        except Exception:
            pass

        loops = -1 if loop else 0
        pygame.mixer.music.play(loops=loops, start=float(start))
        return True
    except Exception:
        return False


def stop_music(fade_ms: int = 0) -> None:
    if not _ensure_mixer():
        return
    try:
        if fade_ms and fade_ms > 0:
            pygame.mixer.music.fadeout(int(fade_ms))
        else:
            pygame.mixer.music.stop()
    except Exception:
        pass




def _ensure_mixer() -> bool:
    if not _PYGAME_OK:
        return False
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        return True
    except Exception:
        return False


def _file_exists(path: str) -> bool:
    try:
        return os.path.isfile(path)
    except Exception:
        return False


def _get_sound(path: str) -> Optional["pygame.mixer.Sound"]:
    if not _file_exists(path):
        return None
    snd = _sfx_cache.get(path)
    if snd is not None:
        return snd
    try:
        snd = pygame.mixer.Sound(path)
        if len(_sfx_cache) >= _SFX_CACHE_MAX:
            try:
                _sfx_cache.pop(next(iter(_sfx_cache)))
            except Exception:
                _sfx_cache.clear()
        _sfx_cache[path] = snd
        return snd
    except Exception:
        return None
