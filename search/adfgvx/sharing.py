"""Box-sharing rules for every parallel job here (lead-adfgvx tmvxfubv8l58c, 2026-11-01):
at most MAX_JOBS concurrent workers, and the whole job under nice >= 10. The box has 8 cores
shared with other chats; 18 nice-0 workers starved them on 2026-11-01."""
import os

MAX_JOBS = 6
NICE = 10


def be_nice():
    """Raise this process (and so every worker and jattack child it spawns) to nice >= NICE."""
    cur = os.nice(0)
    if cur < NICE:
        os.nice(NICE - cur)


def jobs(requested):
    return max(1, min(int(requested), MAX_JOBS))


_lock = None


def exclusive():
    """Block until no other comp-adfgvx parallel job holds the lock, so two launches can never
    add up to more than MAX_JOBS workers. Held until the process exits."""
    global _lock
    import fcntl
    path = os.path.join(os.environ.get("TMPDIR", "/tmp"), "adfgvx-parallel.lock")
    _lock = open(path, "w")
    fcntl.flock(_lock, fcntl.LOCK_EX)
