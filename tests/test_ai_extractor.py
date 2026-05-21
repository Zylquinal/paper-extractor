import json

import pytest
from openai import APIError, APITimeoutError

from src.ai_extractor import _parse_json_response, extract
from src.config import Config
from src.exceptions import AIExtractionError


@pytest.fixture
def config():
    return Config(api_key="sk-test", base_url="https://api.test.com/v1", model="test-model")


@pytest.fixture
def mock_openai_client(mocker):
    return mocker.patch("src.ai_extractor.OpenAI")


def test_parse_json_direct(sample_json_response, sample_extraction):
    result = _parse_json_response(sample_json_response)
    assert result == sample_extraction


def test_parse_json_markdown_block(sample_json_markdown_response, sample_extraction):
    result = _parse_json_response(sample_json_markdown_response)
    assert result == sample_extraction


def test_parse_json_with_prefix_text(sample_json_response, sample_extraction):
    response = "Some text before\n" + sample_json_response + "\nSome text after"
    result = _parse_json_response(response)
    assert result == sample_extraction


def test_parse_json_invalid():
    with pytest.raises(AIExtractionError, match="could not be parsed"):
        _parse_json_response("This is not JSON at all")


def test_parse_json_missing_fields():
    with pytest.raises(AIExtractionError, match="could not be parsed"):
        _parse_json_response('{"title": "Only one field"}')


def test_parse_json_empty_string():
    with pytest.raises(AIExtractionError, match="could not be parsed"):
        _parse_json_response("")


def test_parse_json_json_without_braces():
    with pytest.raises(AIExtractionError, match="could not be parsed"):
        _parse_json_response('"title": "test"')


def test_parse_json_extra_fields(sample_extraction):
    data = dict(sample_extraction)
    data["extra_field"] = "some extra"
    result = _parse_json_response(json.dumps(data))
    # Required fields still present
    for key in ["title", "methodology_object", "result", "limit_gap"]:
        assert key in result
        assert result[key] == sample_extraction[key]
    # Extra fields now preserved (not stripped)
    assert "extra_field" in result
    assert result["extra_field"] == "some extra"


def test_extract_success(sample_text, config, mock_openai_client, sample_json_response):
    mock_client_instance = mock_openai_client.return_value
    mock_completion = mock_client_instance.chat.completions.create.return_value
    mock_completion.choices = [
        type("Choice", (), {"message": type("Message", (), {"content": sample_json_response})()})()
    ]
    result = extract(sample_text, config)
    assert result is not None
    assert "title" in result
    assert "methodology_object" in result
    assert "result" in result
    assert "limit_gap" in result


def test_extract_api_timeout(sample_text, config, mock_openai_client):
    import httpx

    mock_client_instance = mock_openai_client.return_value
    request = httpx.Request("POST", "https://api.test.com/v1/chat/completions")
    mock_client_instance.chat.completions.create.side_effect = APITimeoutError(request=request)
    with pytest.raises(AIExtractionError, match="Failed to call AI API"):
        extract(sample_text, config)


def test_extract_api_auth_error(sample_text, config, mock_openai_client):
    import httpx

    mock_client_instance = mock_openai_client.return_value
    request = httpx.Request("POST", "https://api.test.com/v1/chat/completions")
    mock_client_instance.chat.completions.create.side_effect = APIError(
        message="Unauthorized",
        request=request,
        body=None,
    )
    with pytest.raises(AIExtractionError, match="Failed to call AI API"):
        extract(sample_text, config)


def test_extract_empty_response(sample_text, config, mock_openai_client):
    mock_client_instance = mock_openai_client.return_value
    mock_completion = mock_client_instance.chat.completions.create.return_value
    mock_completion.choices = [
        type("Choice", (), {"message": type("Message", (), {"content": None})()})()
    ]
    with pytest.raises(AIExtractionError, match="empty response"):
        extract(sample_text, config)


def test_parse_json_with_optional_fields(sample_json_response, sample_extraction):
    result = _parse_json_response(sample_json_response)
    assert result["title"] == sample_extraction["title"]
    assert result["methodology_object"] == sample_extraction["methodology_object"]
    assert result["result"] == sample_extraction["result"]
    assert result["limit_gap"] == sample_extraction["limit_gap"]
    assert "questionnaires" in result
    assert result["questionnaires"] == sample_extraction["questionnaires"]
    assert "model" in result
    assert result["model"] == sample_extraction["model"]
    assert "main_references" in result
    assert result["main_references"] == sample_extraction["main_references"]


def test_parse_json_without_optional_fields(sample_json_no_optional_response, sample_extraction_no_optional):
    result = _parse_json_response(sample_json_no_optional_response)
    assert result["title"] == sample_extraction_no_optional["title"]
    assert result["methodology_object"] == sample_extraction_no_optional["methodology_object"]
    assert result["result"] == sample_extraction_no_optional["result"]
    assert result["limit_gap"] == sample_extraction_no_optional["limit_gap"]
    assert "questionnaires" not in result
    assert "model" not in result
    assert "main_references" not in result


def test_parse_json_optional_fields_are_native_types(sample_json_response):
    result = _parse_json_response(sample_json_response)
    assert isinstance(result["questionnaires"], list)
    assert isinstance(result["model"], dict)
    assert isinstance(result["main_references"], list)
    assert isinstance(result["model"]["variables"], list)
    assert isinstance(result["model"]["theory"], list)
