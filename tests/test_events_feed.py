from events_feed import EventsFeed


def test_events_feed_respects_limit_and_order():
    feed = EventsFeed(maxlen=3)
    feed.add(event_type="a", summary="1")
    feed.add(event_type="b", summary="2")
    feed.add(event_type="c", summary="3")
    feed.add(event_type="d", summary="4")

    data = feed.list(limit=10)
    assert [e["type"] for e in data] == ["b", "c", "d"]
    assert [e["summary"] for e in data] == ["2", "3", "4"]


def test_events_feed_limit_parameter():
    feed = EventsFeed(maxlen=10)
    for i in range(5):
        feed.add(event_type="x", summary=str(i))

    data = feed.list(limit=2)
    assert len(data) == 2
    assert [e["summary"] for e in data] == ["3", "4"]
