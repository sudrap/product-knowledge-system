"""Read-only viewer for a project's docs/: renders the Markdown into one page and serves it to this computer only."""

from __future__ import annotations

import hashlib
import html
import posixpath
import re
import secrets
import webbrowser
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote

PAGE = Path(__file__).with_name("page.html")
ROOT_ORDER = ["project", "product", "business", "architecture", "roadmap", "development"]
GROUP_ORDER = ["project", "decisions", "features", "ideas"]
LIST_ITEM = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$")
TABLE_RULE = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$")
LINK = re.compile(r"!?\[((?:[^\]`]|`[^`]*`)+)\]\(([^)\s]+)\)")

LABELS = {
    "en": {
        "subtitle": "Project knowledge",
        "project": "Project",
        "decisions": "Decisions",
        "valid": "Valid",
        "waiting": "Waiting for a decision",
        "superseded": "Replaced",
        "features": "Features",
        "ideas": "Ideas",
        "new": "New",
        "considered": "Under consideration",
        "rejected": "Rejected",
        "unknown": "not known yet",
        "updated": "updated",
        "related": "Related",
        "outside": "Outside docs/",
        "empty": "There are no documents in docs/ yet.",
        "stopped": "The viewer has stopped. Run pks view again.",
        "type.product": "product decision",
        "type.business": "business decision",
        "type.technical": "technical decision",
        "type.idea": "idea",
        "type.brainstorm": "brainstorm result",
        "type.research": "research",
        "type.hypothesis": "hypothesis",
        "type.feature": "feature",
    },
    "cs": {
        "subtitle": "Znalosti projektu",
        "project": "Projekt",
        "decisions": "Rozhodnutí",
        "valid": "Platná",
        "waiting": "Čeká na rozhodnutí",
        "superseded": "Nahrazená",
        "features": "Funkce",
        "ideas": "Nápady",
        "new": "Nové",
        "considered": "Zvažované",
        "rejected": "Zamítnuté",
        "unknown": "zatím nevíme",
        "updated": "upraveno",
        "related": "Související",
        "outside": "Mimo docs/",
        "empty": "V docs/ zatím nejsou žádné dokumenty.",
        "stopped": "Prohlížeč se zastavil. Spusť znovu pks view.",
        "type.product": "produktové rozhodnutí",
        "type.business": "byznysové rozhodnutí",
        "type.technical": "technické rozhodnutí",
        "type.idea": "nápad",
        "type.brainstorm": "výsledek brainstormu",
        "type.research": "průzkum",
        "type.hypothesis": "hypotéza",
        "type.feature": "funkce",
    },
}


@dataclass
class Document:
    rel: Path
    meta: dict[str, str]
    body: str
    title: str

    @property
    def id(self) -> str:
        return re.sub(r"[^a-zA-Z0-9]+", "-", self.rel.with_suffix("").as_posix()).strip("-") or "doc"


def split_header(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---", 4)
    if end < 0:
        return {}, text
    meta = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip()
    return meta, text[end + 4 :].lstrip("\n")


class Markdown:
    """Turns the Markdown PKS records use into HTML. All text is escaped, so a document cannot add scripts."""

    def __init__(self, rel: Path, ids: dict[str, str], labels: dict[str, str]):
        self.rel = rel
        self.ids = ids
        self.labels = labels

    def link(self, label: str, target: str) -> str:
        safe = html.escape(target, quote=True)
        if re.match(r"^(https?://|mailto:)", target, re.IGNORECASE):
            return f'<a href="{safe}" target="_blank" rel="noopener noreferrer" title="{safe}">{label}</a>'
        path = unquote(target.split("#")[0])
        inside = posixpath.normpath(posixpath.join(self.rel.parent.as_posix(), path)) if path else None
        if inside in self.ids:
            return f'<a href="#{self.ids[inside]}">{label}</a>'
        return f'<span class="outside" title="{html.escape(self.labels["outside"])}: {safe}">{label}</span>'

    def inline(self, text: str) -> str:
        out = []
        position = 0
        for match in LINK.finditer(text):
            out.append(self.spans(text[position : match.start()]))
            out.append(self.link(self.spans(match[1]), match[2]))
            position = match.end()
        out.append(self.spans(text[position:]))
        return "".join(out)

    def spans(self, text: str) -> str:
        unknown = f'<span class="unknown">{html.escape(self.labels["unknown"])}</span>'
        out = []
        for piece in re.split(r"(`[^`]+`)", text):
            if len(piece) > 1 and piece.startswith("`") and piece.endswith("`"):
                inner = piece[1:-1]
                out.append(unknown if inner == "[unknown]" else f"<code>{html.escape(inner)}</code>")
                continue
            value = html.escape(piece, quote=False).replace("[unknown]", unknown)
            value = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", value)
            value = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", value)
            value = re.sub(r"~~(.+?)~~", r"<del>\1</del>", value)
            out.append(value)
        return "".join(out)

    def table(self, rows: list[str], rule: str) -> str:
        def cells(row: str) -> list[str]:
            return [cell.strip() for cell in row.strip().strip("|").split("|")]

        def alignment(cell: str) -> str:
            if cell.startswith(":") and cell.endswith(":"):
                return "center"
            return "right" if cell.endswith(":") else "left"

        aligns = [alignment(cell) for cell in cells(rule)]

        def row_html(row: str, tag: str) -> str:
            parts = []
            for index, cell in enumerate(cells(row)):
                align = aligns[index] if index < len(aligns) else "left"
                parts.append(f'<{tag} class="{align}">{self.inline(cell)}</{tag}>')
            return f"<tr>{''.join(parts)}</tr>"

        body = "".join(row_html(row, "td") for row in rows[1:])
        return f'<div class="table"><table><thead>{row_html(rows[0], "th")}</thead><tbody>{body}</tbody></table></div>'

    def list_block(self, lines: list[str], index: int) -> tuple[str, int]:
        first = LIST_ITEM.match(lines[index])
        base = len(first[1])
        ordered = first[2][0].isdigit()
        items = []
        while index < len(lines):
            match = LIST_ITEM.match(lines[index])
            if not match or len(match[1]) != base or match[2][0].isdigit() != ordered:
                break
            text = [match[3]]
            nested = ""
            index += 1
            while index < len(lines):
                line = lines[index]
                if not line.strip():
                    following = index + 1
                    while following < len(lines) and not lines[following].strip():
                        following += 1
                    item = LIST_ITEM.match(lines[following]) if following < len(lines) else None
                    if item and len(item[1]) >= base:
                        index = following
                        continue
                    break
                item = LIST_ITEM.match(line)
                if item and len(item[1]) > base:
                    part, index = self.list_block(lines, index)
                    nested += part
                    continue
                if item:
                    break
                text.append(line.strip())
                index += 1
            content = " ".join(text)
            task = re.match(r"^\[( |x|X)\]\s+(.*)$", content)
            if task:
                state = "todo" if task[1] == " " else "done"
                items.append(f'<li class="task {state}">{self.inline(task[2])}{nested}</li>')
            else:
                items.append(f"<li>{self.inline(content)}{nested}</li>")
        tag = "ol" if ordered else "ul"
        return f"<{tag}>{''.join(items)}</{tag}>", index

    def blocks(self, text: str) -> str:
        lines = text.splitlines()
        out = []
        index = 0
        while index < len(lines):
            line = lines[index]
            if not line.strip():
                index += 1
            elif line.lstrip().startswith("```"):
                code = []
                index += 1
                while index < len(lines) and not lines[index].lstrip().startswith("```"):
                    code.append(lines[index])
                    index += 1
                index += 1
                out.append(f"<pre><code>{html.escape(chr(10).join(code))}</code></pre>")
            elif re.match(r"^#{1,6}\s", line):
                heading = re.match(r"^(#{1,6})\s+(.*?)\s*#*$", line)
                level = len(heading[1])
                out.append(f"<h{level}>{self.inline(heading[2])}</h{level}>")
                index += 1
            elif re.match(r"^\s*(-{3,}|\*{3,})\s*$", line):
                out.append("<hr>")
                index += 1
            elif "|" in line and index + 1 < len(lines) and TABLE_RULE.match(lines[index + 1]):
                rule = lines[index + 1]
                rows = [line]
                index += 2
                while index < len(lines) and "|" in lines[index] and lines[index].strip():
                    rows.append(lines[index])
                    index += 1
                out.append(self.table(rows, rule))
            elif line.lstrip().startswith(">"):
                quote = []
                while index < len(lines) and lines[index].lstrip().startswith(">"):
                    quote.append(re.sub(r"^\s*>\s?", "", lines[index]))
                    index += 1
                out.append(f"<blockquote>{self.blocks(chr(10).join(quote))}</blockquote>")
            elif LIST_ITEM.match(line):
                part, index = self.list_block(lines, index)
                out.append(part)
            else:
                paragraph = []
                while index < len(lines) and lines[index].strip():
                    current = lines[index]
                    starts_block = (
                        LIST_ITEM.match(current)
                        or re.match(r"^#{1,6}\s", current)
                        or current.lstrip().startswith((">", "```"))
                    )
                    if paragraph and starts_block:
                        break
                    paragraph.append(current.strip())
                    index += 1
                out.append(f"<p>{self.inline(' '.join(paragraph))}</p>")
        return "\n".join(out)


def placement(rel: Path) -> tuple[str, str, int]:
    """Say where a document goes in the panel: group, subgroup and order. Status is the folder."""
    top = rel.parts[0].casefold() if len(rel.parts) > 1 else ""
    sub = rel.parts[1].casefold() if len(rel.parts) > 2 else ""
    if not top:
        return "project", "", 0
    if top == "decisions":
        return {"proposed": ("decisions", "waiting", 1), "superseded": ("decisions", "superseded", 2)}.get(
            sub, ("decisions", "valid", 0)
        )
    if top == "discovery":
        return {"inbox": ("ideas", "new", 0), "rejected": ("ideas", "rejected", 2)}.get(sub, ("ideas", "considered", 1))
    if top == "features":
        return "features", "", 0
    return rel.parts[0], "", 0


def sort_key(rel: Path) -> tuple:
    group, _, rank = placement(rel)
    position = GROUP_ORDER.index(group) if group in GROUP_ORDER else len(GROUP_ORDER)
    stem = rel.stem.casefold()
    root_rank = ROOT_ORDER.index(stem) if len(rel.parts) == 1 and stem in ROOT_ORDER else len(ROOT_ORDER)
    return position, group, rank, root_rank, rel.as_posix().casefold()


def document_paths(docs: Path) -> list[Path]:
    found = []
    for path in docs.rglob("*.md"):
        rel = path.relative_to(docs)
        if path.is_file() and not any(part.startswith(".") for part in rel.parts):
            found.append(rel)
    return sorted(found, key=sort_key)


def load_documents(docs: Path) -> list[Document]:
    documents = []
    for rel in document_paths(docs):
        try:
            text = (docs / rel).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        meta, body = split_header(text)
        heading = re.search(r"(?m)^#\s+(.+)$", body)
        title = re.sub(r"[`*]", "", heading[1]).strip() if heading else rel.stem
        documents.append(Document(rel, meta, body, title))
    return documents


def stamp(docs: Path) -> str:
    """A value that changes whenever a document is added, removed or edited."""
    digest = hashlib.sha256()
    for rel in document_paths(docs):
        try:
            info = (docs / rel).stat()
        except OSError:
            continue
        digest.update(f"{rel.as_posix()}|{info.st_mtime_ns}|{info.st_size}\n".encode())
    return digest.hexdigest()


def details(document: Document, docs_name: str, language: str) -> str:
    labels = LABELS[language]
    parts = [f"<code>{html.escape(f'{docs_name}/{document.rel.as_posix()}')}</code>"]
    kind = f"type.{document.meta.get('type', '')}"
    if kind in labels:
        parts.append(html.escape(labels[kind]))
    date = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", document.meta.get("updated", ""))
    if date:
        shown = f"{int(date[3])}. {int(date[2])}. {date[1]}" if language == "cs" else date[0]
        parts.append(f"{html.escape(labels['updated'])} {shown}")
    return " · ".join(parts)


def render_page(docs: Path, project: str, language: str, nonce: str) -> str:
    labels = LABELS[language]
    documents = load_documents(docs)
    ids = {document.rel.as_posix(): document.id for document in documents}
    by_stem = {document.rel.stem: document for document in documents}

    panel: dict[str, dict[str, list[str]]] = {}
    articles = []
    for document in documents:
        number = re.match(r"^(\d{4})-", document.rel.name)
        prefix = f'<span class="num">{int(number[1])}</span>' if number else ""
        group, sub, _ = placement(document.rel)
        entry = f'<a href="#{document.id}">{prefix}<span>{html.escape(document.title)}</span></a>'
        panel.setdefault(group, {}).setdefault(sub, []).append(entry)

        related = []
        for name in re.findall(r"[^\s,\[\]]+", document.meta.get("related", "")):
            other = by_stem.get(Path(name).stem)
            if other is not None:
                related.append(f'<a href="#{other.id}">{html.escape(other.title)}</a>')
        footer = f"<footer>{html.escape(labels['related'])}: {', '.join(related)}</footer>" if related else ""
        content = Markdown(document.rel, ids, labels).blocks(document.body)
        articles.append(
            f'<article id="{document.id}" hidden><div class="meta">{details(document, docs.name, language)}</div>'
            f"{content}{footer}</article>"
        )

    nav = ""
    for group, subgroups in panel.items():
        nav += f"<section><h2>{html.escape(labels.get(group, group))}</h2>"
        for sub, entries in subgroups.items():
            if sub:
                waiting = ' class="waiting"' if sub == "waiting" else ""
                nav += f"<h3{waiting}>{html.escape(labels[sub])}<b>{len(entries)}</b></h3>"
            nav += "".join(entries)
        nav += "</section>"

    values = {
        "LANGUAGE": language,
        "PROJECT": html.escape(project),
        "SUBTITLE": html.escape(labels["subtitle"]),
        "NAV": nav,
        "ARTICLES": "\n".join(articles) or f"<article><p>{html.escape(labels['empty'])}</p></article>",
        "STOPPED": html.escape(labels["stopped"]),
        "STAMP": stamp(docs),
        "NONCE": nonce,
    }
    return re.sub(r"\{\{(\w+)\}\}", lambda match: values[match[1]], PAGE.read_text(encoding="utf-8"))


def page_language(docs: Path, header: str | None) -> str:
    """Use the documentation language stated in PROJECT.md, otherwise the browser's language."""
    try:
        text = (docs / "PROJECT.md").read_text(encoding="utf-8", errors="replace")
    except OSError:
        text = ""
    stated = re.search(r"(?im)^\*\*[^*\n]*(?:language|jazyk)[^*\n]*\*\*\s*(.+)$", text)
    value = stated[1].strip().casefold() if stated else ""
    if value.startswith(("češ", "čes", "czech")):
        return "cs"
    if value.startswith(("english", "angli")):
        return "en"
    first = (header or "").split(",")[0].strip().casefold()
    return "cs" if first.startswith(("cs", "sk")) else "en"


def make_handler(docs: Path, project: str, token: str) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            if self.headers.get("Host") != f"127.0.0.1:{self.server.server_port}":
                self.send_error(403)
                return
            path = self.path.split("?")[0]
            if path == f"/{token}/":
                nonce = secrets.token_urlsafe(16)
                language = page_language(docs, self.headers.get("Accept-Language"))
                policy = (
                    f"default-src 'none'; script-src 'nonce-{nonce}'; style-src 'unsafe-inline'; "
                    "connect-src 'self'; base-uri 'none'; form-action 'none'"
                )
                self.respond("text/html; charset=utf-8", render_page(docs, project, language, nonce), policy)
            elif path == f"/{token}/stamp":
                self.respond("text/plain; charset=utf-8", stamp(docs), "default-src 'none'")
            else:
                self.send_error(404)

        def respond(self, content_type: str, text: str, policy: str) -> None:
            data = text.encode("utf-8")
            try:
                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Security-Policy", policy)
                self.send_header("Referrer-Policy", "no-referrer")
                self.send_header("X-Content-Type-Options", "nosniff")
                self.end_headers()
                self.wfile.write(data)
            except (BrokenPipeError, ConnectionResetError):
                pass

        def log_message(self, format: str, *args: object) -> None:
            pass

    return Handler


def serve(project_root: Path, docs: Path, open_browser: bool) -> int:
    token = secrets.token_urlsafe(16)
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(docs, project_root.name, token))
    url = f"http://127.0.0.1:{server.server_port}/{token}/"
    print(f"Viewing {docs}\n{url}\nPress Ctrl+C to stop.", flush=True)
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        server.server_close()
    return 0
