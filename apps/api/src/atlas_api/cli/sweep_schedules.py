from __future__ import annotations

import argparse

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from atlas_api.core.config import Settings
from atlas_api.db.base import utc_now
from atlas_api.db.config import require_database_url
from atlas_api.services.scheduler import sweep_due_schedules


def run_once(session_factory: sessionmaker[Session]) -> int:
    with session_factory.begin() as session:
        return sweep_due_schedules(session, now=utc_now())


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Transactionally enqueue due Atlas interval schedules once."
    )
    parser.parse_args()
    engine = create_engine(require_database_url(Settings()))
    session_factory = sessionmaker(engine)
    triggered = run_once(session_factory)
    print(f"triggered={triggered}")


if __name__ == "__main__":
    main()
