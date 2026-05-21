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
    "methodology_object": (
        "Menggunakan machine learning untuk analisis waktu kapan kriminalitas dapat terjadi"
    ),
    "result": (
        "Model mampu mengidentifikasi pola temporal kriminalitas berdasarkan interval "
        "waktu kejadian"
    ),
    "limit_gap": (
        "Penelitian lebih berfokus pada temporal forecasting dan belum membahas "
        "klasifikasi sasaran kejahatan menggunakan pendekatan comparative ensemble learning"
    ),
    "questionnaires": [
        {
            "statement_question": "How often do you use the application?",
            "reference": "Davis (1989)",
        },
        {
            "statement_question": "I find the application easy to use",
            "reference": None,
        },
    ],
    "model": {
        "theory": ["Technology Acceptance Model"],
        "variables": [
            {
                "name": "Perceived Usefulness",
                "result": "Perceived Usefulness berpengaruh positif terhadap Behavioral Intention dengan koefisien 0.45, p < 0.01",
                "references": ["Davis (1989)"],
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
}

SAMPLE_EXTRACTION_JSON = (
    '{'
    '"title": "Memprediksi Interval Waktu Kriminalitas Menggunakan Model Machine Learning",'
    '"methodology_object": "Menggunakan machine learning untuk analisis waktu kapan '
    'kriminalitas dapat terjadi",'
    '"result": "Model mampu mengidentifikasi pola temporal kriminalitas berdasarkan '
    'interval waktu kejadian",'
    '"limit_gap": "Penelitian lebih berfokus pada temporal forecasting dan belum membahas '
    'klasifikasi sasaran kejahatan menggunakan pendekatan comparative ensemble learning",'
    '"questionnaires": ['
    '{"statement_question": "How often do you use the application?", "reference": "Davis (1989)"},'
    '{"statement_question": "I find the application easy to use", "reference": null}'
    '],'
    '"model": {'
    '"theory": ["Technology Acceptance Model"],'
    '"variables": ['
    '{"name": "Perceived Usefulness", "result": "Perceived Usefulness berpengaruh positif terhadap Behavioral Intention dengan koefisien 0.45, p < 0.01", "references": ["Davis (1989)"]},'
    '{"name": "Perceived Ease of Use", "result": "Perceived Ease of Use berpengaruh positif terhadap Perceived Usefulness dengan koefisien 0.52, p < 0.001", "references": []}'
    ']'
    '},'
    '"main_references": ['
    '{"title": "Perceived Usefulness, Perceived Ease of Use, and User Acceptance of Information Technology", "authors": ["Fred D. Davis"], "explanation": "Paper ini digunakan sebagai acuan utama untuk model Technology Acceptance Model yang mendasari kerangka teori penelitian ini."}'
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
def temp_excel_path():
    tmp = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
    tmp.close()
    return tmp.name
