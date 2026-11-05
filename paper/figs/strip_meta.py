"""strip_meta.py FILE... - remove document info / XMP from PDFs and EXIF/text chunks from rasters, in place."""
import sys, pathlib
from pypdf import PdfReader, PdfWriter
from PIL import Image

for f in map(pathlib.Path, sys.argv[1:]):
    ext = f.suffix.lower()
    if ext == ".pdf":
        r = PdfReader(f); w = PdfWriter(clone_from=r)
        w.metadata = None                       # drop /Info dictionary
        if "/Metadata" in w._root_object:       # drop XMP stream
            del w._root_object["/Metadata"]
        tmp = f.with_suffix(".tmp.pdf"); w.write(tmp); tmp.replace(f)
    elif ext in {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"}:
        im = Image.open(f); im.load()
        icc = im.info.get("icc_profile")              # keep colour profile only
        if im.mode == "P": im = im.convert("RGBA")
        clean = Image.frombytes(im.mode, im.size, im.tobytes())   # pixels only, no EXIF/text
        clean.save(f, **({"icc_profile": icc} if icc else {}))
    else:
        print(f"skip {f} (unsupported)"); continue
    print(f"stripped {f}")
