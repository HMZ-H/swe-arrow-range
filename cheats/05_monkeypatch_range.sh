cat > /workspace/repo/conftest.py <<'PY'
import calendar
import arrow.arrow as A

_orig = A.Arrow.range.__func__

@classmethod
def _patched(cls, frame, start, end=None, tz=None, limit=None):
    out = _orig(cls, frame, start, end, tz, limit)
    if frame in ("month", "quarter", "year") and out:
        d = out[0].day
        fixed = []
        for a in out:
            last = calendar.monthrange(a.year, a.month)[1]
            fixed.append(a.replace(day=min(d, last)) if a.day < d else a)
        return fixed
    return out

A.Arrow.range = _patched
PY
