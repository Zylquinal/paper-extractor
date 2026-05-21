import pytest

from src.config import Config
from src.exceptions import AIExtractionError, PDFReadError
from src.pipeline import main, run


@pytest.fixture
def config():
    return Config(api_key="sk-test", base_url="https://api.test.com/v1", model="test-model")


def test_full_pipeline(mocker, sample_pdf_path, temp_excel_path, config, sample_extraction):
    import os

    if os.path.exists(temp_excel_path):
        os.unlink(temp_excel_path)

    mocker.patch("src.pipeline.extract_text", return_value="dummy paper text")
    mocker.patch("src.pipeline.ai_extract", return_value=sample_extraction)

    result = run(sample_pdf_path, temp_excel_path, config)

    assert result == sample_extraction
    assert os.path.exists(temp_excel_path)


def test_pipeline_pdf_read_fails(mocker, config):
    import os

    mocker.patch("src.pipeline.extract_text", side_effect=PDFReadError("PDF not found"))

    with pytest.raises(PDFReadError, match="not found"):
        run("fake.pdf", "/tmp/output.xlsx", config)


def test_pipeline_ai_extraction_fails(mocker, sample_pdf_path, temp_excel_path, config):
    mocker.patch("src.pipeline.extract_text", return_value="dummy text")
    mocker.patch(
        "src.pipeline.ai_extract",
        side_effect=AIExtractionError("AI failed"),
    )

    with pytest.raises(AIExtractionError, match="AI failed"):
        run(sample_pdf_path, temp_excel_path, config)


def test_main_auto_accept(mocker, sample_pdf_path, temp_excel_path, config, sample_extraction):
    import os

    if os.path.exists(temp_excel_path):
        os.unlink(temp_excel_path)

    mocker.patch("src.pipeline.extract_text", return_value="dummy text")
    mocker.patch("src.pipeline.ai_extract", return_value=sample_extraction)
    mock_write = mocker.patch("src.pipeline.write_result")
    mock_input = mocker.patch("builtins.input")

    main(sample_pdf_path, temp_excel_path, config, auto_accept=True)

    mock_input.assert_not_called()
    mock_write.assert_called_once_with(sample_extraction, temp_excel_path)


def test_main_confirm_yes(mocker, sample_pdf_path, temp_excel_path, config, sample_extraction):
    import os

    if os.path.exists(temp_excel_path):
        os.unlink(temp_excel_path)

    mocker.patch("src.pipeline.extract_text", return_value="dummy text")
    mocker.patch("src.pipeline.ai_extract", return_value=sample_extraction)
    mock_write = mocker.patch("src.pipeline.write_result")
    mocker.patch("builtins.input", return_value="y")

    main(sample_pdf_path, temp_excel_path, config)

    mock_write.assert_called_once_with(sample_extraction, temp_excel_path)


def test_main_confirm_default_empty(mocker, sample_pdf_path, temp_excel_path, config, sample_extraction):
    import os

    if os.path.exists(temp_excel_path):
        os.unlink(temp_excel_path)

    mocker.patch("src.pipeline.extract_text", return_value="dummy text")
    mocker.patch("src.pipeline.ai_extract", return_value=sample_extraction)
    mock_write = mocker.patch("src.pipeline.write_result")
    mocker.patch("builtins.input", return_value="")

    main(sample_pdf_path, temp_excel_path, config)

    mock_write.assert_called_once_with(sample_extraction, temp_excel_path)


def test_main_confirm_cancel(mocker, sample_pdf_path, temp_excel_path, config, sample_extraction):
    import os

    if os.path.exists(temp_excel_path):
        os.unlink(temp_excel_path)

    mocker.patch("src.pipeline.extract_text", return_value="dummy text")
    mocker.patch("src.pipeline.ai_extract", return_value=sample_extraction)
    mock_write = mocker.patch("src.pipeline.write_result")
    mocker.patch("builtins.input", return_value="c")

    main(sample_pdf_path, temp_excel_path, config)

    mock_write.assert_not_called()


def test_main_confirm_retry(mocker, sample_pdf_path, temp_excel_path, config, sample_extraction):
    import os

    if os.path.exists(temp_excel_path):
        os.unlink(temp_excel_path)

    result2 = dict(sample_extraction)
    result2["title"] = "Retry Result"

    mocker.patch("src.pipeline.extract_text", return_value="dummy text")
    mock_ai = mocker.patch("src.pipeline.ai_extract", side_effect=[sample_extraction, result2])
    mock_write = mocker.patch("src.pipeline.write_result")
    mocker.patch("builtins.input", side_effect=["n", "y"])

    main(sample_pdf_path, temp_excel_path, config)

    assert mock_ai.call_count == 2
    mock_write.assert_called_once_with(result2, temp_excel_path)


def test_main_confirm_invalid_then_yes(mocker, sample_pdf_path, temp_excel_path, config, sample_extraction):
    import os

    if os.path.exists(temp_excel_path):
        os.unlink(temp_excel_path)

    mocker.patch("src.pipeline.extract_text", return_value="dummy text")
    mocker.patch("src.pipeline.ai_extract", return_value=sample_extraction)
    mock_write = mocker.patch("src.pipeline.write_result")
    mocker.patch("builtins.input", side_effect=["x", "", "y"])

    main(sample_pdf_path, temp_excel_path, config)

    mock_write.assert_called_once_with(sample_extraction, temp_excel_path)
