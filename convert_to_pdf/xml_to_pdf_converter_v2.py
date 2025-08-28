#!/usr/bin/env python3
# anaf_uploadxml_v3.1.py

import sys
import time
from pathlib import Path
from typing import Dict, Tuple

import requests
from bs4 import BeautifulSoup

BASE = "https://www.anaf.ro"
ENTRY = f"{BASE}/uploadxml/"
DOWNLOAD = f"{BASE}/uploadxml/download"

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36")

def scrape_form(html: str) -> Tuple[str, str, Dict[str, str]]:
    """Parse the upload form: action URL, file field name, default data fields (hidden/checked/selected + submit)."""
    soup = BeautifulSoup(html, "html.parser")

    # form that contains the file input
    form = None
    for f in soup.find_all("form"):
        if f.find("input", {"type": "file"}):
            form = f
            break

    action = ENTRY
    if form:
        a = form.get("action")
        if a:
            action = a if a.startswith("http") else requests.compat.urljoin(ENTRY, a)

    # file input name
    file_input = form.find("input", {"type": "file"}) if form else None
    file_field = file_input.get("name") if file_input and file_input.get("name") else "fisier"

    # collect default fields from the form
    data: Dict[str, str] = {}
    if form:
        # hidden + default/checked/selected fields
        for inp in form.find_all("input"):
            name = inp.get("name")
            if not name:
                continue
            itype = (inp.get("type") or "").lower()
            val = inp.get("value", "")
            if itype == "hidden":
                data[name] = val
            elif itype in ("radio", "checkbox"):
                if inp.has_attr("checked"):
                    data[name] = val
            elif itype in ("text", "number", "email", "tel"):
                if val:
                    data[name] = val

        for sel in form.find_all("select"):
            name = sel.get("name")
            if not name:
                continue
            opt = sel.find("option", selected=True) or sel.find("option")
            if opt and opt.get("value") is not None:
                data[name] = opt.get("value")

        # include the clicked submit button (the one that says "Incarcare XML")
        submit = None
        for btn in form.find_all(["button", "input"]):
            btype = (btn.get("type") or "").lower()
            if btype != "submit":
                continue
            text = (btn.get_text(" ", strip=True) or "").lower()
            value = (btn.get("value") or "").lower()
            if "incarcare" in text or "încărcare" in text or "incarcare" in value:
                submit = btn
                break
        if submit:
            sname = submit.get("name")
            svalue = submit.get("value", "")
            if sname:
                data[sname] = svalue

    return action, file_field, data

def convert_single_xml_to_pdf(xml_path: Path, out_pdf_path: Path, sleep_between: float = 0.8) -> None:
    """Converts one XML to PDF and saves it to out_pdf_path. Raises on failure."""
    s = requests.Session()
    s.headers.update({
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,ro;q=0.7",
        "DNT": "1",
        "Upgrade-Insecure-Requests": "1",
    })

    # 1) GET to establish cookies + parse form
    r0 = s.get(ENTRY, timeout=30)
    r0.raise_for_status()
    action, file_field, data = scrape_form(r0.text)

    # 2) POST multipart with the submit button and defaults
    files = {
        file_field: (xml_path.name, xml_path.read_bytes(), "text/xml"),
    }
    r1 = s.post(
        action,
        data=data,
        files=files,
        headers={"Origin": BASE, "Referer": ENTRY},
        timeout=90,
        allow_redirects=True,
    )
    if not r1.ok:
        raise requests.HTTPError(
            f"Upload failed {r1.status_code}. Content-Type={r1.headers.get('Content-Type')}. "
            f"Snippet: {r1.text[:600]}"
        )

    # 3) Download the PDF (bound to the same session)
    # polite pause; some gateways need a tick before the artifact is ready
    if sleep_between:
        time.sleep(sleep_between)

    r2 = s.get(DOWNLOAD, headers={"Referer": ENTRY}, timeout=60, allow_redirects=True)
    if not (r2.ok and "application/pdf" in r2.headers.get("Content-Type", "")):
        raise requests.HTTPError(
            f"Download did not return PDF. Status {r2.status_code}. "
            f"CT={r2.headers.get('Content-Type')}. Snippet: {r2.text[:600]}"
        )

    out_pdf_path.write_bytes(r2.content)

def process_directory(xml_dir: Path, out_dir: Path) -> None:
    """Process all non-_semnatura_ XMLs from xml_dir into PDFs in out_dir."""
    if not xml_dir.is_dir():
        raise ValueError(f"Input path is not a directory: {xml_dir}")
    out_dir.mkdir(parents=True, exist_ok=True)

    xml_files = sorted(
        [p for p in xml_dir.iterdir()
         if p.is_file() and p.suffix.lower() == ".xml" and "_semnatura_" not in p.name.lower()]
    )

    if not xml_files:
        print("No matching XML files found (skipping those with '_semnatura_' in the name).")
        return

    print(f"Found {len(xml_files)} XML files to convert.")
    success, failed = 0, 0
    for i, xml_file in enumerate(xml_files, 1):
        out_pdf = out_dir / (xml_file.stem + ".pdf")
        print(f"[{i}/{len(xml_files)}] {xml_file.name} → {out_pdf.name} ... ", end="", flush=True)
        try:
            convert_single_xml_to_pdf(xml_file, out_pdf)
            print("OK")
            success += 1
        except Exception as e:
            print("FAIL")
            failed += 1
            # show short reason, keep going
            print(f"      Reason: {e}")

    print("\nSummary:")
    print(f"  Converted: {success}")
    print(f"  Failed:    {failed}")
    print(f"  Output dir: {out_dir.resolve()}")

def main():
    if len(sys.argv) != 3:
        print("Usage:")
        print("  python anaf_uploadxml_v3.1.py path/to/xmls/ path/to/pdfs/")
        sys.exit(1)

    xml_dir = Path(sys.argv[1]).expanduser().resolve()
    out_dir = Path(sys.argv[2]).expanduser().resolve()
    process_directory(xml_dir, out_dir)

if __name__ == "__main__":
    main()
