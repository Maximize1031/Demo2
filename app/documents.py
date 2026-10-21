"""Private, session-scoped text files on the Render persistent disk."""
import hashlib
import re
import secrets
import shutil
import time
from pathlib import Path

from .workflow import SENSITIVE, WorkflowError

MAX_FILE_BYTES = 100_000
MAX_TOTAL_BYTES = 500_000
MAX_DOCUMENTS = 30
MAX_REQUEST_BYTES = 750_000


class DocumentStore:
    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def folder(self, sid):
        if not re.fullmatch(r"[a-f0-9]{64}", sid):
            raise ValueError("Invalid session")
        return self.root / sid

    def clear(self, sid):
        shutil.rmtree(self.folder(sid), ignore_errors=True)

    def read(self, sid, documents):
        records = []
        for document in documents:
            doc_id = document["id"]
            if not re.fullmatch(r"[a-f0-9]{32}", doc_id):
                raise WorkflowError("A document could not be read. Please upload it again.")
            path = self.folder(sid) / doc_id
            try:
                text = path.read_text(encoding="utf-8")
            except OSError as exc:
                raise WorkflowError("A stored document is unavailable. Please upload it again.") from exc
            if hashlib.sha256(text.encode()).hexdigest() != document["sha256"]:
                raise WorkflowError("A stored document changed unexpectedly. Please upload it again.")
            records.append({**document, "text": text, "origin": "upload"})
        return records

    def prepare(self, incoming, existing_records):
        if not isinstance(incoming, list) or not 1 <= len(incoming) <= MAX_DOCUMENTS:
            raise WorkflowError("Choose between 1 and 30 Markdown or text files.")
        if len(existing_records) + len(incoming) > MAX_DOCUMENTS:
            raise WorkflowError("A case can contain at most 30 documents.")
        names = {r["name"].lower() for r in existing_records}
        hashes = {hashlib.sha256(r["text"].encode()).hexdigest() for r in existing_records}
        total = sum(len(r["text"].encode()) for r in existing_records)
        prepared = []
        for entry in incoming:
            if not isinstance(entry, dict):
                raise WorkflowError("Invalid upload.")
            original, text = entry.get("name"), entry.get("text")
            if not isinstance(original, str) or not isinstance(text, str):
                raise WorkflowError("Each upload must include a filename and UTF-8 text.")
            if len(original) > 120 or "/" in original or "\\" in original:
                raise WorkflowError("Use a filename without folders, no longer than 120 characters.")
            name = re.sub(r"[^a-zA-Z0-9._-]", "-", original).strip(".-")
            if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*\.(?:md|txt)", name, re.I):
                raise WorkflowError("Only .md and .txt files are supported.")
            stem, ext = name.rsplit(".", 1)
            name = stem + "." + ext.lower()
            text = text.removeprefix("\ufeff").replace("\r\n", "\n")
            if not text.strip() or re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", text):
                raise WorkflowError("Files must contain readable, nonempty UTF-8 text.")
            try:
                content = text.encode("utf-8")
            except UnicodeError as exc:
                raise WorkflowError("Files must use UTF-8 text encoding.") from exc
            if len(content) > MAX_FILE_BYTES:
                raise WorkflowError("Each file must be 100 KB or smaller.")
            if SENSITIVE.search(text):
                raise WorkflowError("Remove tax identifiers from the files; describe receipt status only.")
            digest = hashlib.sha256(content).hexdigest()
            if name.lower() in names:
                raise WorkflowError(f"{name} is already in this case. Use a new filename for new evidence.")
            if digest in hashes:
                raise WorkflowError(f"{name} duplicates a document already selected.")
            names.add(name.lower()); hashes.add(digest); total += len(content)
            prepared.append({"id": secrets.token_hex(16), "name": name, "original_name": original,
                             "size": len(content), "sha256": digest, "uploaded_at": time.time(), "text": text})
        if total > MAX_TOTAL_BYTES:
            raise WorkflowError("The combined case documents must be 500 KB or smaller.")
        return prepared

    def save(self, sid, prepared):
        folder = self.folder(sid)
        folder.mkdir(parents=True, exist_ok=True)
        if sum(p.stat().st_size for p in folder.iterdir() if p.is_file()) + sum(d["size"] for d in prepared) > 5_000_000:
            raise WorkflowError("This session's file allowance is full. Download your review and start a new case.")
        created = []
        try:
            for document in prepared:
                path = folder / document["id"]
                path.write_text(document["text"], encoding="utf-8")
                created.append(path)
        except OSError as exc:
            for path in created:
                path.unlink(missing_ok=True)
            raise WorkflowError("The files could not be saved. Please retry.") from exc
        return [{k: v for k, v in d.items() if k != "text"} for d in prepared]
