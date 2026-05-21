import io
import tempfile

import pytest

SAMPLE_PAPER_TEXT = (
    "Predicting Crime Time Interval Using Machine Learning Models\n\n"
    "Abstract\n"
    "This research employs machine learning techniques to analyze the temporal "
    "patterns of criminal activities. By examining time intervals between crime "
    "incidents, the model identifies when crimes are most likely to occur.\n\n"
    "Methodology\n"
    "The study uses historical crime data with timestamps and applies supervised "
    "learning algorithms including random forest and gradient boosting to predict "
    "time intervals between criminal events.\n\n"
    "Results\n"
    "The model successfully identifies temporal crime patterns based on incident "
    "time intervals with 85% accuracy.\n\n"
    "Limitations\n"
    "This research focuses primarily on temporal forecasting and does not address "
    "crime target classification using comparative ensemble learning approaches."
)

SAMPLE_EXTRACTION = {
    "title": "Memprediksi Interval Waktu Kriminalitas Menggunakan Model Machine Learning",
    "publication_year": 2023,
    "authors": ["John Doe", "Jane Smith", "Bob Johnson"],
    "doi": "10.1234/example.2023.001",
    "methodology_object": (
        "Menggunakan machine learning untuk analisis waktu kapan kriminalitas dapat terjadi"
    ),
    "sample": {
        "population": "Data kriminalitas di Kota Jakarta",
        "size": 1500,
        "characteristics": "Data historis 5 tahun terakhir, mencakup 10 kecamatan",
    },
    "data_analysis": ["Random Forest", "Gradient Boosting", "Logistic Regression"],
    "result": (
        "Model mampu mengidentifikasi pola temporal kriminalitas berdasarkan interval "
        "waktu kejadian"
    ),
    "limit_gap": (
        "Penelitian lebih berfokus pada temporal forecasting dan belum membahas "
        "klasifikasi sasaran kejahatan menggunakan pendekatan comparative ensemble learning"
    ),
    "implications": {
        "theoretical": "Memperkuat penerapan ensemble learning dalam prediksi kriminalitas temporal",
        "practical": "Hasil dapat digunakan kepolisian untuk mengoptimalkan jadwal patroli",
    },
    "questionnaires": [
        {
            "statement_question": "How often do you use the application?",
            "reference": "Davis (1989)",
            "variable": "Perceived Usefulness",
        },
        {
            "statement_question": "I find the application easy to use",
            "reference": None,
            "variable": "Perceived Ease of Use",
        },
    ],
    "model": {
        "theory": ["Technology Acceptance Model"],
        "variables": [
            {
                "name": "Perceived Usefulness",
                "result": "Perceived Usefulness berpengaruh positif terhadap Behavioral Intention dengan koefisien 0.45, p < 0.01",
                "references": [
                    {
                        "paper": "Perceived Usefulness, Perceived Ease of Use, and User Acceptance of Information Technology",
                        "author": "Fred D. Davis",
                    }
                ],
            },
            {
                "name": "Perceived Ease of Use",
                "result": "Perceived Ease of Use berpengaruh positif terhadap Perceived Usefulness dengan koefisien 0.52, p < 0.001",
                "references": [],
            },
        ],
    },
    "main_references": [
        {
            "title": "Perceived Usefulness, Perceived Ease of Use, and User Acceptance of Information Technology",
            "authors": ["Fred D. Davis"],
            "explanation": "Paper ini digunakan sebagai acuan utama untuk model Technology Acceptance Model yang mendasari kerangka teori penelitian ini.",
        },
    ],
    "hypothesis": [
        {
            "statement": "H1: Perceived Usefulness berpengaruh positif terhadap Behavioral Intention",
            "result": "Diterima",
        },
        {
            "statement": "H2: Perceived Ease of Use berpengaruh positif terhadap Perceived Usefulness",
            "result": "Diterima",
        },
    ],
}

SAMPLE_EXTRACTION_JSON = (
    '{'
    '"title": "Memprediksi Interval Waktu Kriminalitas Menggunakan Model Machine Learning",'
    '"publication_year": 2023,'
    '"authors": ["John Doe", "Jane Smith", "Bob Johnson"],'
    '"doi": "10.1234/example.2023.001",'
    '"methodology_object": "Menggunakan machine learning untuk analisis waktu kapan '
    'kriminalitas dapat terjadi",'
    '"sample": {"population": "Data kriminalitas di Kota Jakarta", "size": 1500, '
    '"characteristics": "Data historis 5 tahun terakhir, mencakup 10 kecamatan"},'
    '"data_analysis": ["Random Forest", "Gradient Boosting", "Logistic Regression"],'
    '"result": "Model mampu mengidentifikasi pola temporal kriminalitas berdasarkan '
    'interval waktu kejadian",'
    '"limit_gap": "Penelitian lebih berfokus pada temporal forecasting dan belum membahas '
    'klasifikasi sasaran kejahatan menggunakan pendekatan comparative ensemble learning",'
    '"implications": {"theoretical": "Memperkuat penerapan ensemble learning dalam prediksi '
    'kriminalitas temporal", "practical": "Hasil dapat digunakan kepolisian untuk '
    'mengoptimalkan jadwal patroli"},'
    '"questionnaires": ['
    '{"statement_question": "How often do you use the application?", "reference": "Davis (1989)", "variable": "Perceived Usefulness"},'
    '{"statement_question": "I find the application easy to use", "reference": null, "variable": "Perceived Ease of Use"}'
    '],'
    '"model": {'
    '"theory": ["Technology Acceptance Model"],'
    '"variables": ['
    '{"name": "Perceived Usefulness", "result": "Perceived Usefulness berpengaruh positif terhadap Behavioral Intention dengan koefisien 0.45, p < 0.01", "references": [{"paper": "Perceived Usefulness, Perceived Ease of Use, and User Acceptance of Information Technology", "author": "Fred D. Davis"}]},'
    '{"name": "Perceived Ease of Use", "result": "Perceived Ease of Use berpengaruh positif terhadap Perceived Usefulness dengan koefisien 0.52, p < 0.001", "references": []}'
    ']'
    '},'
    '"main_references": ['
    '{"title": "Perceived Usefulness, Perceived Ease of Use, and User Acceptance of Information Technology", "authors": ["Fred D. Davis"], "explanation": "Paper ini digunakan sebagai acuan utama untuk model Technology Acceptance Model yang mendasari kerangka teori penelitian ini."}'
    '],'
    '"hypothesis": ['
    '{"statement": "H1: Perceived Usefulness berpengaruh positif terhadap Behavioral Intention", "result": "Diterima"},'
    '{"statement": "H2: Perceived Ease of Use berpengaruh positif terhadap Perceived Usefulness", "result": "Diterima"}'
    ']'
    '}'
)

SAMPLE_EXTRACTION_NO_OPTIONAL = {
    "title": "Judul Penelitian Sederhana",
    "methodology_object": "Menggunakan metode kualitatif dengan wawancara",
    "result": "Tidak ada hasil yang signifikan",
    "limit_gap": "Jumlah responden terbatas",
}

SAMPLE_EXTRACTION_NO_OPTIONAL_JSON = (
    '{'
    '"title": "Judul Penelitian Sederhana",'
    '"methodology_object": "Menggunakan metode kualitatif dengan wawancara",'
    '"result": "Tidak ada hasil yang signifikan",'
    '"limit_gap": "Jumlah responden terbatas"'
    '}'
)

SAMPLE_EXTRACTION_SLR = {
    "title": "A Systematic Review of Machine Learning Applications in Cybersecurity",
    "publication_year": 2024,
    "authors": ["Alice Wang"],
    "doi": "10.5678/slr.2024.001",
    "methodology_object": "Systematic literature review mengikuti protokol PRISMA dengan pencarian di tiga database",
    "result": "Machine learning menunjukkan akurasi tinggi dalam deteksi intrusi namun masih memiliki tantangan dalam deteksi serangan zero-day",
    "limit_gap": "Mayoritas penelitian masih menggunakan dataset sintetis dan belum diuji pada lingkungan produksi nyata",
    "implications": {
        "theoretical": "Memperkuat kerangka taksonomi untuk klasifikasi ancaman siber berbasis ML",
        "practical": "Rekomendasi pemilihan algoritma ML berdasarkan jenis ancaman dapat digunakan praktisi keamanan",
    },
    "main_references": [
        {
            "title": "Deep Learning for Cybersecurity: A Survey",
            "authors": ["Smith, J."],
            "explanation": "Digunakan sebagai acuan utama untuk mengidentifikasi tren deep learning dalam keamanan siber",
        },
    ],
    "review_type": "Systematic Literature Review",
    "research_questions": [
        "RQ1: Algoritma machine learning apa yang paling banyak digunakan dalam deteksi intrusi?",
        "RQ2: Bagaimana performa ML dibandingkan metode tradisional dalam keamanan siber?",
    ],
    "source_databases": ["Scopus", "Web of Science", "IEEE Xplore"],
    "time_span": {"start": 2019, "end": 2024},
    "papers_included": 87,
    "synthesis_method": "Thematic Synthesis",
    "quality_assessment": ["MMAT", "CASP"],
}

SAMPLE_EXTRACTION_JSON_MARKDOWN = (
    "```json\n" + SAMPLE_EXTRACTION_JSON + "\n```"
)


@pytest.fixture
def sample_text():
    return SAMPLE_PAPER_TEXT


@pytest.fixture
def sample_extraction():
    return dict(SAMPLE_EXTRACTION)


@pytest.fixture
def sample_extraction_no_optional():
    return dict(SAMPLE_EXTRACTION_NO_OPTIONAL)


@pytest.fixture
def sample_json_response():
    return SAMPLE_EXTRACTION_JSON


@pytest.fixture
def sample_json_no_optional_response():
    return SAMPLE_EXTRACTION_NO_OPTIONAL_JSON


@pytest.fixture
def sample_json_markdown_response():
    return SAMPLE_EXTRACTION_JSON_MARKDOWN


@pytest.fixture
def sample_pdf_path():
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    c = canvas.Canvas(tmp.name, pagesize=letter)
    y = 750
    for line in SAMPLE_PAPER_TEXT.split("\n"):
        c.drawString(40, y, line.strip())
        y -= 14
        if y < 50:
            c.showPage()
            y = 750
    c.save()
    return tmp.name


@pytest.fixture
def sample_extraction_slr():
    return dict(SAMPLE_EXTRACTION_SLR)


@pytest.fixture
def temp_excel_path():
    tmp = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
    tmp.close()
    return tmp.name
