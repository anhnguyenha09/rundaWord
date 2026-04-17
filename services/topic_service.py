def get_available_topics(TopicCatalog) -> list[str]:
    """Return topic list from catalog table in DB."""
    rows = TopicCatalog.query.order_by(TopicCatalog.name).all()
    return [r.name for r in rows]


def get_topics_for_user(TopicCatalog, user_id=None) -> list[str]:
    """Compatibility wrapper (currently same as available topics)."""
    _ = user_id
    return get_available_topics(TopicCatalog)


def ensure_topic_catalog(db, TopicCatalog, package_topics) -> None:
    """Seed and keep the topic catalog in DB."""
    existing = {r.name for r in TopicCatalog.query.all()}
    changed = False
    for topic in package_topics:
        if topic not in existing:
            db.session.add(TopicCatalog(name=topic))
            changed = True
    if changed:
        db.session.commit()

