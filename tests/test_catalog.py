from eventhub.catalog import list_events, get_event
from eventhub.errors import NotFound
import pytest


def test_catalog_lists_all_events(connection):
    events, unmatched = list_events(connection)
    assert len(events) == 4 and not unmatched


def test_search_matches_artist_or_venue_case_insensitive(connection):
    assert len(list_events(connection, "JAZZ")[0]) == 1
    assert len(list_events(connection, "Marshall")[0]) == 1


def test_no_match_shows_full_list_and_flag(connection):
    events, unmatched = list_events(connection, "no matching band")
    assert unmatched and len(events) == 4


def test_literal_sql_wildcards_are_not_patterns(connection):
    rows, unmatched = list_events(connection, "%")
    assert unmatched and len(rows) == 4


def test_nonexistent_event(connection):
    with pytest.raises(NotFound):
        get_event(connection, 9999)
