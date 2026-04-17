def learner_counts_for_packages(db, user_saved_packages, func, package_ids: list[int]) -> dict[int, int]:
    if not package_ids:
        return {}
    rows = (
        db.session.query(user_saved_packages.c.package_id, func.count(user_saved_packages.c.user_id))
        .filter(user_saved_packages.c.package_id.in_(package_ids))
        .group_by(user_saved_packages.c.package_id)
        .all()
    )
    return {package_id: count for package_id, count in rows}

