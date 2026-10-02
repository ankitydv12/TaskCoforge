from bisect import bisect_right

from Schemas.schemas import Document

PAGE_SEPARATOR = "\n\n"


class ChunkingService:
    def __init__(self, chunk_size: int, chunk_overlap: int):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be > 0")
        if not 0 <= chunk_overlap < chunk_size:
            raise ValueError("chunk_overlap must be >= 0 and < chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_documents(self, pages: list[Document]) -> list[Document]:
        """Chunk the pages of ONE file as a single text stream, keeping page metadata."""
        if not pages:
            return []

        # Join pages and remember where each page starts in the combined text.
        parts, starts, page_numbers = [], [], []
        pos = 0
        for p in pages:
            starts.append(pos)
            page_numbers.append(p.metadata["page"])
            parts.append(p.page_content)
            pos += len(p.page_content) + len(PAGE_SEPARATOR)
        text = PAGE_SEPARATOR.join(parts)

        base = {k: v for k, v in pages[0].metadata.items() if k != "page"}
        chunks: list[Document] = []

        for s, e in self._spans(text):
            first = bisect_right(starts, s) - 1
            last = bisect_right(starts, e - 1) - 1
            covered = page_numbers[first:last + 1]
            chunks.append(Document(
                page_content=text[s:e],
                metadata={
                    **base,
                    "chunk_index": len(chunks),
                    "start_index": s,
                    "start_page": covered[0],
                    "end_page": covered[-1],
                    "pages": covered,
                },
            ))
        return chunks

    def _spans(self, text: str):
        """Yield (start, end) character spans, preferring to break on whitespace."""
        size, overlap, n = self.chunk_size, self.chunk_overlap, len(text)
        start = 0
        while start < n:
            end = min(start + size, n)
            if end < n:
                cut = max(text.rfind(" ", start + size // 2, end),
                          text.rfind("\n", start + size // 2, end))
                if cut > start:
                    end = cut
            s, e = start, end
            while s < e and text[s].isspace():
                s += 1
            while e > s and text[e - 1].isspace():
                e -= 1
            if e > s:
                yield s, e
            if end >= n:
                break
            start = max(end - overlap, start + 1)