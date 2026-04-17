def get_study_package(VocabPackage, package_id: int, current_user):
    package = VocabPackage.query.get_or_404(package_id)
    is_owner = package.user_id == current_user.id
    has_access = (
        is_owner
        or package.is_public
        or current_user.has_saved(package)
        or getattr(current_user, "is_admin", False)
    )
    return (package, is_owner) if has_access else (None, None)

