import argparse
import hashlib
from pathlib import Path
import fitz
from app.knowledge import ensure_index, embed

# Skin / allergy related pages (PDF page numbers, inclusive ranges)
KEEP_RANGES = [
    (26, 28),    # Abscess
    (38, 40),    # Acne
    (83, 85),    # Aging
    (102, 104),  # Albinism
    (123, 140),  # Allergic purpura, allergic rhinitis, allergies, allergy tests, alopecia
    (192, 193),  # Anaphylaxis
    (220, 221),  # Animal bite infections
    (240, 242),  # Antiacne drugs
    (258, 259),  # Antibiotics, topical
    (284, 284),  # Antifungal drugs, topical
    (290, 292),  # Antihistamines
    (298, 299),  # Anti-itch drugs
    (412, 413),  # Athlete's foot
    (417, 419),  # Atopic dermatitis
    (436, 438),  # Autoimmune disorders
    (470, 472),  # Bedsores
    (474, 474),  # Bejel
    (507, 518),  # Birthmarks, bites and stings
    (550, 551),  # Boils
    (621, 621),  # Bruises
    (630, 633),  # Burns
]
KEEP = {p for a, b in KEEP_RANGES for p in range(a, b + 1)}


def chunks(text, size=1100, overlap=180):
    text = ' '.join(text.split())
    step = size-overlap
    return [text[i:i+size] for i in range(0,len(text),step) if len(text[i:i+size]) > 80]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pdf', default='data/medical_book.pdf')
    args = parser.parse_args()
    pdf = Path(args.pdf)
    if not pdf.exists():
        raise SystemExit(f'PDF not found: {pdf}')
    index = ensure_index()
    done = 0
    with fitz.open(pdf) as doc:
        batch = []
        for page_number, page in enumerate(doc, start=1):
            if page_number not in KEEP:
                continue
            for part, content in enumerate(chunks(page.get_text()), start=1):
                key = hashlib.sha256(f'{pdf.name}:{page_number}:{part}:{content}'.encode()).hexdigest()
                batch.append((key,content,{'page':page_number,'text':content,'file':pdf.name}))
                if len(batch) >= 50:
                    vectors = embed([b[1] for b in batch])
                    index.upsert(vectors=[{'id':b[0],'values':v,'metadata':b[2]} for b,v in zip(batch,vectors)])
                    batch=[]
            done += 1
            if done % 10 == 0:
                print(f'Indexed pages: {done}/{len(KEEP)}',flush=True)
        if batch:
            vectors=embed([b[1] for b in batch])
            index.upsert(vectors=[{'id':b[0],'values':v,'metadata':b[2]} for b,v in zip(batch,vectors)])
    print('Ingestion complete')
if __name__ == '__main__': main()