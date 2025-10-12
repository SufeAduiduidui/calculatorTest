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
