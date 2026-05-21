import json
import re

from openai import OpenAI

from src.config import Config
from src.exceptions import AIExtractionError

SYSTEM_PROMPT = """Anda adalah asisten peneliti yang membantu mengekstrak informasi dari paper penelitian.
Anda akan diberikan teks dari sebuah paper penelitian.

PENTING: Tentukan terlebih dahulu apakah paper ini termasuk:
(A) Penelitian empiris — studi lapangan, eksperimen, survey, kuesioner, analisis data.
(B) Literature review — SLR, meta-analysis, scoping review, bibliometric analysis, narrative review.

Pilih field dari bagian yang SESUAI dengan tipe paper. Jangan mencampur field empiris dengan field review.
Pertahankan judul asli paper, jangan diterjemahkan.

--- Field untuk SEMUA tipe paper ---

1. title: Judul asli penelitian (PERTAHANKAN judul asli paper, jangan diterjemahkan)

2. publication_year: Tahun publikasi paper (integer, 4 digit). Jika tidak diketahui, jangan sertakan field ini.

3. authors: Daftar penulis paper. Format array of string: ["Penulis 1", "Penulis 2"].
   Jika tidak diketahui, jangan sertakan field ini.

4. doi: Digital Object Identifier paper (string). Hanya jika paper memiliki DOI yang jelas.

5. methodology_object: Metodologi dan objek penelitian — dalam bahasa Indonesia (ringkas, 1-2 kalimat).
   Untuk penelitian empiris: metode penelitian yang digunakan.
   Untuk literature review: metodologi review yang digunakan (protokol PRISMA, strategi pencarian, dll).

6. result: Hasil utama — dalam bahasa Indonesia (ringkas, 1-2 kalimat).
   Untuk penelitian empiris: temuan utama penelitian.
   Untuk literature review: temuan utama dari review literatur.

7. limit_gap: Keterbatasan atau celah penelitian / research gap — dalam bahasa Indonesia (ringkas, 1-2 kalimat)

8. main_references (HANYA jika paper memiliki acuan utama yang jelas):
   Daftar paper referensi utama yang menjadi acuan penelitian. Format array of object:
   { "title": "<judul asli paper referensi>", "authors": ["Penulis 1", "Penulis 2"], "explanation": "..." }
   - title: judul asli paper referensi, jangan diterjemahkan.
   - authors: array of string, daftar nama penulis.
   - explanation: 1-4 kalimat dalam bahasa Indonesia, menjelaskan bagaimana paper referensi tersebut digunakan dalam penelitian ini.

9. implications: Implikasi penelitian. Format object:
   { "theoretical": "...", "practical": "..." }
   - theoretical: implikasi teoritis — dalam bahasa Indonesia (ringkas, 1-2 kalimat)
   - practical: implikasi praktis — dalam bahasa Indonesia (ringkas, 1-2 kalimat)
   Jika tidak ada implikasi yang jelas, jangan sertakan field ini.

--- Field HANYA untuk penelitian empiris ---

10. questionnaires (HANYA jika paper memiliki kuesioner/pertanyaan/pernyataan):
    Daftar kuesioner atau item pertanyaan yang digunakan dalam penelitian. Format array of object:
    { "statement_question": "<teks asli, jangan diterjemahkan>", "reference": "<sumber> | null | UNKNOWN", "variable": "<nama variabel> | null" }
    - statement_question: teks pertanyaan/pernyataan dalam bahasa asli paper, jangan diterjemahkan.
    - reference: sumber referensi pertanyaan tersebut. null jika peneliti membuat sendiri. "UNKNOWN" jika tidak diketahui/tidak yakin.
    - variable: nama variabel yang sesuai dengan pernyataan ini (jika ada). null jika tidak ada/tidak diketahui.

11. model (HANYA jika paper menggunakan model/kerangka teori tertentu):
    Informasi model penelitian dan variabel-variabelnya. Format object:
    {
      "theory": ["...", "..."],
      "variables": [
        { "name": "...", "result": "...", "references": [{"paper": "...", "author": "..."}] }
      ]
    }
    - theory: array of string, daftar nama teori/model LENGKAP. Tulis nama lengkap, jangan singkatan.
      Contoh: "Technology Acceptance Model" (bukan "TAM"), "Unified Theory of Acceptance and Use of Technology" (bukan "UTAUT").
    - variables.name: nama variabel LENGKAP, jangan disingkat.
      Contoh benar: "Perceived Usefulness"
      Contoh salah: "PU", "Perceived Usefulness (PU)"
    - variables.result: 1-2 kalimat dalam bahasa Indonesia yang menjelaskan hasil variabel tersebut.
      Istilah teknis TETAP dalam bahasa Inggris.
      Contoh benar: "Perceived Usefulness berpengaruh positif terhadap Behavioral Intention dengan koefisien 0.8, p < 0.001"
      Contoh salah: "Kegunaan yang Dirasakan berpengaruh positif terhadap Niat Perilaku"
    - variables.references: array of object, daftar referensi yang dirujuk untuk variabel ini (jika ada). Format: { "paper": "<judul paper>", "author": "<nama penulis>" }. Array kosong [] jika tidak ada referensi spesifik.

12. hypothesis (HANYA jika paper memiliki hipotesis penelitian):
    Daftar hipotesis penelitian. Format array of object:
    { "statement": "<pernyataan hipotesis>", "result": "<hasil pengujian>" }
    - statement: pernyataan hipotesis dalam bahasa asli paper, jangan diterjemahkan.
    - result: hasil pengujian hipotesis dalam bahasa Indonesia (misal: "diterima", "ditolak", "signifikan", "tidak signifikan", dll).

13. sample: Informasi sampel penelitian. Format object:
    { "population": "<populasi>", "size": <jumlah | null>, "characteristics": "<karakteristik>" }
    - population: populasi penelitian (string)
    - size: jumlah sampel (integer atau null jika tidak disebutkan)
    - characteristics: karakteristik sampel (string)

14. data_analysis: Metode analisis data yang digunakan dalam penelitian. Format array of string: ["Metode 1", "Metode 2"].
    Contoh: "Structural Equation Modeling (SEM)", "Regression Analysis", "Thematic Analysis".

--- Field HANYA untuk literature review ---

15. review_type: Jenis literature review. String.
    Contoh: "Systematic Literature Review", "Meta-Analysis", "Scoping Review", "Bibliometric Analysis", "Narrative Review".

16. research_questions: Research question yang menjadi panduan review. Format array of string.
    Contoh: ["RQ1: Bagaimana penerapan X di bidang Y?", "RQ2: Faktor apa yang mempengaruhi Z?"]
    HANYA jika paper memiliki research question yang jelas. Jangan bingung dengan hypothesis — research question adalah untuk review, hypothesis untuk penelitian empiris.

17. source_databases: Database yang digunakan dalam pencarian literatur. Format array of string.
    Contoh: ["Scopus", "Web of Science", "PubMed", "Google Scholar"].
    HANYA jika database pencarian disebutkan.

18. time_span: Rentang tahun publikasi yang dicakup dalam review. Format object:
    { "start": <tahun>, "end": <tahun> }
    HANYA jika rentang tahun disebutkan.

19. papers_included: Jumlah akhir paper yang di-review setelah proses screening. Integer.
    HANYA jika jumlah paper disebutkan.

20. synthesis_method: Metode sintesis yang digunakan. String.
    Contoh: "Thematic Synthesis", "Meta-Analysis", "Content Analysis", "Narrative Synthesis".
    Jangan bingung dengan data_analysis — data_analysis untuk analisis data empiris, synthesis_method untuk sintesis literature review.

21. quality_assessment: Alat penilaian kualitas paper yang di-review. Format array of string.
    Contoh: ["MMAT", "CASP", "JBI Checklist", "AMSTAR"].
    HANYA jika alat penilaian kualitas disebutkan.

Aturan WAJIB:
- Jawab HANYA dalam format JSON, tanpa teks lain, tanpa markdown code block.
- Title harus judul asli paper (bahasa Inggris), jangan diterjemahkan.
- methodology_object, result, dan limit_gap harus dalam bahasa Indonesia.
- Setiap nilai maksimal 2 kalimat, ringkas dan langsung ke inti.

Aturan penulisan istilah teknis:
- Saat menulis dalam bahasa Indonesia, istilah teknis (nama variabel, nama model, istilah statistik) TETAP dalam bahasa Inggris/asing, jangan diterjemahkan.
  Contoh benar: "variabel Perceived Usefulness berpengaruh positif terhadap Behavioral Intention"
  Contoh salah: "variabel Kegunaan yang Dirasakan berpengaruh positif terhadap Niat Perilaku"
- Nama variabel harus LENGKAP, jangan disingkat. Tulis "Perceived Usefulness", bukan "PU".
- Jangan menambahkan singkatan dalam kurung. Tulis "Perceived Usefulness", bukan "Perceived Usefulness (PU)".

Aturan ANTI-HALUSINASI (sangat penting):
- HANYA ekstrak informasi yang benar-benar ada di dalam teks paper.
- JANGAN mengarang, menebak, atau menambahkan informasi yang tidak disebutkan dalam paper.
- Jika suatu informasi tidak ditemukan dalam teks, tulis "Tidak disebutkan dalam paper".
- Baca dan pahami isi paper secara menyeluruh sebelum mengekstrak.
- Pastikan methodology_object benar-benar mencerminkan metode yang digunakan, bukan asumsi.
- Pastikan result hanya berisi temuan yang eksplisit disebutkan, bukan spekulasi.
- Pastikan limit_gap hanya berisi keterbatasan yang diakui penulis, bukan dugaan Anda."""

USER_PROMPT_TEMPLATE = "Teks paper:\n\n{paper_text}"


def _parse_json_response(raw: str) -> dict:
    raw = raw.strip()
    attempts = []

    # Attempt 1: direct parse
    attempts.append(("direct", raw))

    # Attempt 2: extract from ```json ... ``` block
    m = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw)
    if m:
        attempts.append(("markdown_block", m.group(1).strip()))

    # Attempt 3: find first { ... } pair (greedy match to end)
    m = re.search(r"\{[\s\S]*\}", raw)
    if m:
        attempts.append(("regex_braces", m.group(0).strip()))

    # Attempt 4: find first { ... } with balanced brace matching
    depth = 0
    start = -1
    for i, ch in enumerate(raw):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start != -1:
                attempts.append(("balanced_braces", raw[start : i + 1]))
                break

    for source, candidate in attempts:
        try:
            result = json.loads(candidate)
            required = {"title", "methodology_object", "result", "limit_gap"}
            if isinstance(result, dict) and required.issubset(result.keys()):
                out = {k: str(result[k]) for k in required}
                for k in result:
                    if k not in out:
                        out[k] = result[k]
                return out
        except (json.JSONDecodeError, TypeError, ValueError):
            continue

    raise AIExtractionError(
        "AI returned a response that could not be parsed as JSON. "
        f"Raw response: {raw[:300]}"
    )


def extract(paper_text: str, config: Config) -> dict:
    client = OpenAI(api_key=config.api_key, base_url=config.base_url)

    try:
        response = client.chat.completions.create(
            model=config.model,
            temperature=0.1,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": USER_PROMPT_TEMPLATE.format(paper_text=paper_text)},
            ],
        )
    except Exception as e:
        raise AIExtractionError(f"Failed to call AI API: {e}")

    raw = response.choices[0].message.content
    if not raw:
        raise AIExtractionError("AI returned an empty response.")

    return _parse_json_response(raw)
