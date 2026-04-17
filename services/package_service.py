from .text_service import normalize_text
from sqlalchemy.orm import joinedload


def search_packages(VocabPackage, q: str, include_private_for_user=None, limit: int = 20, prelimit: int = 500):
    """
    Search public packages by name, author username, topic, or description.
    If include_private_for_user is set, also includes that user's private packages.
    """
    q_norm = normalize_text(q)

    query = VocabPackage.query.filter(VocabPackage.is_public == True)
    if include_private_for_user:
        query = VocabPackage.query.filter(
            (VocabPackage.is_public == True) | (VocabPackage.user_id == include_private_for_user)
        )

    # Avoid scanning all rows in Python: cap the candidate pool and eager-load owner to prevent N+1 queries.
    all_pkgs = (
        query.options(joinedload(VocabPackage.user))
        .order_by(VocabPackage.updated_at.desc())
        .limit(prelimit)
        .all()
    )
    results = []
    for pkg in all_pkgs:
        name_norm = normalize_text(pkg.package_name)
        owner_norm = normalize_text(pkg.user.username) if pkg.user else ""
        topic_norm = normalize_text(pkg.topic or "") if hasattr(pkg, "topic") else ""
        desc_norm = normalize_text(pkg.package_description or "")
        if (q_norm in name_norm) or (q_norm in owner_norm) or (q_norm in topic_norm) or (q_norm in desc_norm):
            results.append(pkg)
    return results[:limit]

