import attr


@attr.s
class Config:
    NOTIFICATIONS_FROM: str = attr.ib()
    PROPOSALS_NOTIFICATIONS_RECIPIENT: str = attr.ib()
    PROPOSALS_REPO_FILE: str = attr.ib()

    POSTMARK_TOKEN: str = attr.ib()
