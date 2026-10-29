"""Tests for the KDP metadata validation logic."""


from kdp_metadata_checker.checker import check_metadata
from kdp_metadata_checker.metadata import BookMetadata
from kdp_metadata_checker.rules import Rules

RULES = Rules.load("kdp_metadata_checker/rules/kdp_rules.json")


def test_clean_metadata_passes():
    metadata = BookMetadata(
        title="The Massive AI Manual",
        subtitle="Artificial intelligence explained like a friend would",
        description="A plain-English, step-by-step guide to AI for beginners.",
        categories=["Computers & Technology", "Artificial Intelligence"],
        keywords=["ai", "artificial intelligence", "machine learning"],
    )
    report = check_metadata(metadata, RULES)
    assert report.passed
    assert report.errors == []
    assert report.warnings == []


def test_title_too_long_is_error():
    metadata = BookMetadata(title="x" * 201)
    report = check_metadata(metadata, RULES)
    assert not report.passed
    assert any(
        issue.field == "title" and issue.severity == "error" and issue.check == "max_length"
        for issue in report.errors
    )


def test_title_empty_is_error():
    metadata = BookMetadata(title="")
    report = check_metadata(metadata, RULES)
    assert not report.passed
    assert any(issue.check == "required" for issue in report.errors)


def test_title_all_caps_warning():
    metadata = BookMetadata(title="THE MASSIVE AI MANUAL")
    report = check_metadata(metadata, RULES)
    assert report.passed
    assert any(issue.check == "all_caps" for issue in report.warnings)


def test_title_trailing_whitespace_warning():
    metadata = BookMetadata(title="The Massive AI Manual ")
    report = check_metadata(metadata, RULES)
    assert report.passed
    assert any(issue.check == "trailing_whitespace" for issue in report.warnings)


def test_title_multiple_spaces_warning():
    metadata = BookMetadata(title="The  Massive AI Manual")
    report = check_metadata(metadata, RULES)
    assert report.passed
    assert any(issue.check == "multiple_spaces" for issue in report.warnings)


def test_title_leading_trailing_punctuation_warning():
    metadata = BookMetadata(title='"The Massive AI Manual"')
    report = check_metadata(metadata, RULES)
    assert report.passed
    assert any(issue.check == "leading_trailing_punctuation" for issue in report.warnings)


def test_description_too_long_is_error():
    metadata = BookMetadata(description="x" * 4001)
    report = check_metadata(metadata, RULES)
    assert not report.passed
    assert any(
        issue.field == "description" and issue.severity == "error" and issue.check == "max_length"
        for issue in report.errors
    )


def test_description_html_tags_warning():
    metadata = BookMetadata(title="The Massive AI Manual", description="Great book <b>buy now</b>!")
    report = check_metadata(metadata, RULES)
    assert report.passed
    assert any(issue.check == "raw_html_tags" for issue in report.warnings)


def test_description_empty_paragraphs_warning():
    metadata = BookMetadata(title="The Massive AI Manual", description="First paragraph.\n\n\nSecond paragraph.")
    report = check_metadata(metadata, RULES)
    assert report.passed
    assert any(issue.check == "empty_paragraphs" for issue in report.warnings)


def test_categories_too_many_is_error():
    metadata = BookMetadata(categories=["A", "B", "C", "D"])
    report = check_metadata(metadata, RULES)
    assert not report.passed
    assert any(issue.field == "categories" and issue.check == "max_count" for issue in report.errors)


def test_categories_item_too_long_is_error():
    metadata = BookMetadata(categories=["x" * 121])
    report = check_metadata(metadata, RULES)
    assert not report.passed
    assert any(issue.check == "max_length_per" for issue in report.errors)


def test_categories_duplicate_warning():
    metadata = BookMetadata(title="The Massive AI Manual", categories=["Computers", "computers"])
    report = check_metadata(metadata, RULES)
    assert report.passed
    assert any(issue.check == "duplicates" for issue in report.warnings)


def test_categories_trailing_whitespace_warning():
    metadata = BookMetadata(title="The Massive AI Manual", categories=["Computers "])
    report = check_metadata(metadata, RULES)
    assert report.passed
    assert any(issue.check == "trailing_whitespace" for issue in report.warnings)


def test_keywords_too_many_is_error():
    metadata = BookMetadata(keywords=[f"k{i}" for i in range(8)])
    report = check_metadata(metadata, RULES)
    assert not report.passed
    assert any(issue.field == "keywords" and issue.check == "max_count" for issue in report.errors)


def test_keywords_total_bytes_is_error():
    metadata = BookMetadata(keywords=["x" * 70 for _ in range(8)])
    report = check_metadata(metadata, RULES)
    assert not report.passed
    assert any(issue.check == "max_total_bytes" for issue in report.errors)


def test_keywords_item_too_long_is_error():
    metadata = BookMetadata(keywords=["x" * 51])
    report = check_metadata(metadata, RULES)
    assert not report.passed
    assert any(issue.check == "max_length_per" for issue in report.errors)


def test_keywords_duplicate_warning():
    metadata = BookMetadata(title="The Massive AI Manual", keywords=["ai", "AI", "machine learning"])
    report = check_metadata(metadata, RULES)
    assert report.passed
    assert any(issue.check == "duplicates" for issue in report.warnings)


def test_keywords_repeated_words_warning():
    metadata = BookMetadata(title="The Massive AI Manual", keywords=["python programming", "python basics"])
    report = check_metadata(metadata, RULES)
    assert report.passed
    assert any(issue.check == "repeated_words" for issue in report.warnings)


def test_keywords_asin_like_warning():
    metadata = BookMetadata(title="The Massive AI Manual", keywords=["B012345678", "ai"])
    report = check_metadata(metadata, RULES)
    assert report.passed
    assert any(issue.check == "asin_like" for issue in report.warnings)


def test_missing_rule_does_not_crash():
    rules = Rules.load("kdp_metadata_checker/rules/kdp_rules.json")
    rules.fields.pop("title")
    metadata = BookMetadata(title="x" * 500)
    report = check_metadata(metadata, rules)
    assert report.passed
    assert report.errors == []
