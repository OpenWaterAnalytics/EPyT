# -*- coding: utf-8 -*-
import re
import sys
from functools import lru_cache
from pathlib import Path
from threading import RLock

from cffi import FFI

ffi = FFI()

_THIS_DIR = Path(__file__).resolve().parent
_HEADER_BASE_DIRS = [
    _THIS_DIR / "libraries",
    _THIS_DIR.parent / "libraries",
]

_C_VOIDP_NULL = ffi.cast("void *", 0)
_C_CHARP_NULL = ffi.cast("char *", 0)

_CDEF_LOCK = RLock()
_CDEF_DONE = False

# ---------------------------------------------
# Dynamic extraction of function prototypes from headers
# ---------------------------------------------
_HEADER_DEFAULTS = [
    base / header
    for base in _HEADER_BASE_DIRS
    for header in ("epanet2.h", "epanet2_2.h", "epanetmsx.h")
]

# Preserve stdcall exports on Windows even after stripping DLL decoration macros.
_CALL_CONV_MACROS = [
    r"\bEPANET2_API\b",
    r"\bDLLEXPORT\b",
    r"\bWINAPI\b",
    r"\bAPIENTRY\b",
]

_MACRO_TOKENS_TO_STRIP = [
    r"\b__cdecl\b",
    r"\bDECLSPEC\b",
    r"\bEXPORT\b",
]

_CALL_CONV_KEYWORD = "__stdcall" if sys.platform.startswith("win") else ""

# Replace typedef-like API tokens with plain C types so cffi.cdef() can parse them.
_TYPE_ALIASES = {
    "EN_API_FLOAT_TYPE": "float",
}

_MANUAL_CDEF_PREFIX = "typedef void *EN_Project;\n"

# Remove 'extern "C"' blocks safely (brace-only lines too).
_EXTERN_C_RE = re.compile(r'extern\s+"C"\s*\{?|^\s*\}\s*$', re.MULTILINE)

# Simple comment removers (/* ... */ and // ...)
_BLOCK_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
_LINE_COMMENT_RE = re.compile(r"//.*?$", re.MULTILINE)

# Preprocessor lines (#define/#include/#if ...)
_PREPROC_RE = re.compile(r"^\s*#.*?$", re.MULTILINE)

# Function prototype matcher: now supports EN* and MSX* symbols
_FUNC_RE = re.compile(
    r"""
    (?P<proto>
        (?:[a-zA-Z_][\w\s\*\(\),\[\]]*?\s+)?         # return type + qualifiers/pointers
        (?:EN_[A-Za-z0-9_]+|EN[A-Za-z0-9_]+
        |MSX_[A-Za-z0-9_]+|MSX[A-Za-z0-9_]+)         # function name
        \s*\(                                        # (
            [^;]*?                                   # args
        \)                                           # )
        \s*;                                         # ;
    )
    """,
    re.VERBOSE | re.DOTALL,
)


def _apply_type_aliases(text: str) -> str:
    for token, ctype in _TYPE_ALIASES.items():
        text = re.sub(rf"\b{re.escape(token)}\b", ctype, text)
    return text


def _load_decls_from_header(header_path: str = None) -> str:
    # Accept a single header path or use both defaults
    paths = [Path(header_path)] if header_path else _HEADER_DEFAULTS

    protos_all = []
    for path in paths:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")

        text = _BLOCK_COMMENT_RE.sub("", text)
        text = _LINE_COMMENT_RE.sub("", text)
        text = _PREPROC_RE.sub("", text)
        text = _EXTERN_C_RE.sub("", text)

        for tok in _CALL_CONV_MACROS:
            text = re.sub(tok, _CALL_CONV_KEYWORD, text)

        for tok in _MACRO_TOKENS_TO_STRIP:
            text = re.sub(tok, "", text)

        text = _apply_type_aliases(text)

        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\s+\n", "\n", text)

        for m in _FUNC_RE.finditer(text):
            proto = re.sub(r"\s+", " ", m.group("proto").strip())
            # Ensure a concrete return type (headers often omit 'int' in typedefs/macros)
            if re.match(r"^(EN_|EN|MSX_|MSX)[A-Za-z0-9_]*\s*\(", proto):
                proto = "int " + proto
            protos_all.append(proto)

    # Deduplicate while preserving order
    seen, uniq = set(), []
    for p in protos_all:
        if p not in seen:
            seen.add(p)
            uniq.append(p)

    return "\n".join(uniq) + ("\n" if uniq else "")


_CDEF_DECLS = None


def _ensure_cdef(header_path: str = None):
    global _CDEF_DONE, _CDEF_DECLS
    if _CDEF_DONE:
        return
    with _CDEF_LOCK:
        if _CDEF_DONE:
            return

        decls = _load_decls_from_header(header_path)

        # Remove any auto-extracted MSXstep prototype (it is wrong for your DLL).
        decls = "\n".join(
            line for line in decls.splitlines()
            if "MSXstep" not in line
        ) + ("\n" if decls else "")

        # Add the correct prototype (matches your working ctypes behavior).
        # (Pyodide's library is built from EPANET-MSX 2.0, as the Windows DLL)
        if sys.platform.startswith("win") or sys.platform == "emscripten":
            msxstep_proto = "int MSXstep(double *t, double *tleft);\n"
        else:
            msxstep_proto = "int MSXstep(double *t, long *tleft);\n"

        _CDEF_DECLS = _MANUAL_CDEF_PREFIX + msxstep_proto + decls
        ffi.cdef(_CDEF_DECLS)
        _CDEF_DONE = True


# ---------------------------------------------
# Helpers (unchanged)
# ---------------------------------------------
class _Ptr:
    __slots__ = ("c_type", "ptr")

    def __init__(self, c_type: str):
        self.c_type = c_type
        self.ptr = ffi.new(f"{c_type} *")

    @property
    def value(self):
        return self.ptr[0]

    @value.setter
    def value(self, v):
        self.ptr[0] = v


class _Handle:
    __slots__ = ("ptr",)

    def __init__(self):
        self.ptr = ffi.new("void *[1]", [ffi.NULL])

    @property
    def value(self):
        return self.ptr[0]

    @value.setter
    def value(self, v):
        if isinstance(v, int):
            self.ptr[0] = ffi.cast("void *", v)
        else:
            self.ptr[0] = v

    @property
    def as_voidp(self):
        return self.ptr[0]


class _CVoidP:
    __slots__ = ("ptr",)

    def __init__(self, value=None):
        if value is None:
            value = ffi.NULL
        elif isinstance(value, int):
            value = ffi.cast("void *", value)
        self.ptr = ffi.new("void *[1]", [value])

    @property
    def value(self):
        return self.ptr[0]

    @value.setter
    def value(self, v):
        if isinstance(v, int):
            v = ffi.cast("void *", v)
        self.ptr[0] = v


class _CVoidPType:
    __slots__ = ()

    def __call__(self, value=None):
        return _CVoidP(value)


# Factory to create a mutable void* holder
c_void_p = _CVoidPType()


class _Buffer:
    __slots__ = ("ptr", "n")

    def __init__(self, n: int):
        n = int(n)
        self.n = n
        self.ptr = ffi.new(f"char[{n}]")

    @property
    def value(self) -> bytes:
        return ffi.string(self.ptr)

    @value.setter
    def value(self, b):
        if not isinstance(b, (bytes, bytearray)):
            b = str(b).encode("utf-8")
        else:
            b = bytes(b)
        n = len(b)
        if n >= self.n:
            raise ValueError("buffer too small")
        ffi.memmove(self.ptr, b, n)
        self.ptr[n] = 0


class _ENProjectPtr:
    __slots__ = ("ptr",)

    def __init__(self):
        # EN_Project is typedef void *EN_Project;
        # EN_Project *ph -> pointer to that handle
        self.ptr = ffi.new("EN_Project *")

    @property
    def value(self):
        return self.ptr[0]

    @value.setter
    def value(self, v):
        if isinstance(v, int):
            v = ffi.cast("EN_Project", v)
        self.ptr[0] = v


class _ENProjectPtrType:
    __slots__ = ()

    def __call__(self):
        return _ENProjectPtr()


class _ArrayFactory:
    __slots__ = ("ctype", "n")

    def __init__(self, ctype: str, n: int):
        self.ctype = ctype
        self.n = int(n)

    def __call__(self, *vals):
        if vals:
            if len(vals) == 1 and hasattr(vals[0], "__iter__"):
                return ffi.new(f"{self.ctype}[{self.n}]", list(vals[0]))
            return ffi.new(f"{self.ctype}[{self.n}]", list(vals))
        return ffi.new(f"{self.ctype}[{self.n}]")


class _CScalarType:
    __slots__ = ("ctype", "pycast")

    def __init__(self, ctype: str, pycast):
        self.ctype = ctype
        self.pycast = pycast

    def __call__(self, value=None):
        if value is None:
            return _Ptr(self.ctype)
        return self.pycast(value)

    def __mul__(self, n):
        return _ArrayFactory(self.ctype, n)


EN_Project_p = _ENProjectPtrType()
c_int = _CScalarType("int", int)
c_long = _CScalarType("long", int)
c_float = _CScalarType("float", float)
c_double = _CScalarType("double", float)


class _CUInt64Type:
    __slots__ = ()

    def __call__(self, value=None):
        if value is None:
            return _Handle()
        return int(value)


c_uint64 = _CUInt64Type()


@lru_cache(maxsize=4096)
def _cstr_cached(b: bytes):
    return ffi.new("char[]", b)


def c_char_p(b, *, intern: bool = True):
    if b is None:
        return _C_CHARP_NULL
    if not isinstance(b, (bytes, bytearray)):
        b = str(b).encode("utf-8")
    else:
        b = bytes(b)
    if intern:
        return _cstr_cached(b)
    return ffi.new("char[]", b)


def void_p_null():
    return _C_VOIDP_NULL


# ---------------------- function-pointer helpers ------------------------
def _normalize_funcptr_signature(signature: str) -> str:
    s = signature.strip()
    if "(" in s and ")" in s and "(*" not in s and s.endswith(")"):
        i = s.find("(")
        ret = s[:i].strip()
        args = s[i:]
        s = f"{ret} (* ){args}"
    return s


def funcptr_null(signature: str):
    sig = _normalize_funcptr_signature(signature)
    return ffi.cast(sig, 0)


def make_callback(signature: str, pyfunc):
    return ffi.callback(signature)(pyfunc)


def create_string_buffer(n: int):
    return _Buffer(n)


def byref(obj):
    if isinstance(obj, (_Ptr, _Buffer, _Handle, _CVoidP)):
        return obj.ptr
    if hasattr(obj, "ptr"):
        return obj.ptr
    return obj


class _LibProxy:
    __slots__ = ("_lib", "_cache")

    def __init__(self, libpath: str, header_path: str = None):
        _ensure_cdef(header_path)
        self._lib = ffi.dlopen(libpath, flags=getattr(ffi, "RTLD_NOW", 0))
        self._cache = {}

    def __getattr__(self, name: str):
        cache = self._cache
        fn = cache.get(name)
        if fn is not None:
            return fn

        # Try exact symbol first
        try:
            cfunc = getattr(self._lib, name)
            cache[name] = cfunc
            return cfunc
        except AttributeError:
            pass

        # Bridging EN_* <-> EN* and MSX_* <-> MSX*
        alt_names = []
        if name.startswith("EN_"):
            alt_names.append("EN" + name[3:])
        if name.startswith("EN") and (len(name) > 2 and name[2] != "_"):
            alt_names.append("EN_" + name[2:])
        if name.startswith("MSX_"):
            alt_names.append("MSX" + name[4:])
        if name.startswith("MSX") and (len(name) > 3 and name[3] != "_"):
            alt_names.append("MSX_" + name[3:])

        for alt in alt_names:
            try:
                cfunc = getattr(self._lib, alt)
                cache[name] = cfunc  # cache under the originally requested name
                return cfunc
            except AttributeError:
                continue

        raise AttributeError(name)


class cdll:
    @staticmethod
    def LoadLibrary(path: str, *, header_path: str = None):
        return _LibProxy(path, header_path=header_path)


__all__ = [
    "ffi",
    "c_int", "c_long", "c_float", "c_double", "c_uint64",
    "c_char_p", "void_p_null", "funcptr_null", "make_callback",
    "create_string_buffer", "byref",
    "cdll", "_load_decls_from_header", "get_cdef_decls",
    "c_void_p",
]


def get_cdef_decls():
    _ensure_cdef()
    return _CDEF_DECLS
