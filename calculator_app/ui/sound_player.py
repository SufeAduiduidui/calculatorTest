#音频文件，猫叫

try:
    import pygame
    _pg = True
except Exception:
    _pg = False

_sounds = {}
_inited = False

def _init():
    global _inited
    if not _pg:
        return False
    if _inited:
        return True
    try:
        pygame.mixer.init()
        _inited = True
        return True
    except Exception:
        return False

def play(path, volume=1.0):
    if not _init():
        return
    s = _sounds.get(path)
    if s is None:
        try:
            s = pygame.mixer.Sound(path)
            s.set_volume(volume)
            _sounds[path] = s
        except Exception:
            return
    try:
        s.play()
    except Exception:
        pass

#活全家bgm
def play_music(path, volume=1.0, loop=True, start=0.0):
    if not _init():
        return
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(max(0.0, min(1.0, float(volume))))
        loops = -1 if loop else 0
        pygame.mixer.music.play(loops=loops, start=float(start))
    except Exception:
        pass

def stop_music(fade_ms=400):#停止背景音乐，带轻微淡出以避免爆音。
    if not _init():
        return
    try:
        if fade_ms and fade_ms > 0:
            pygame.mixer.music.fadeout(int(fade_ms))
        else:
            pygame.mixer.music.stop()
    except Exception:
        pass

def set_music_volume(volume: float):
    if not _init():
        return
    try:
        pygame.mixer.music.set_volume(max(0.0, min(1.0, float(volume))))
    except Exception:
        pass
