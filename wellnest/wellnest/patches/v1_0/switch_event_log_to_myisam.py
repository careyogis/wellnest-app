# ---------------------------------------------------------------------------
# Migration / DB-engine patch (run once inside a Frappe patch file)
# ---------------------------------------------------------------------------

from frappe import db

def execute():
    """
    Alter the storage engine of tabEvent Log to MyISAM (or Aria
    on MariaDB) so that INSERT operations use table-level locking instead of
    InnoDB row-level locking, eliminating lock-wait contention during peak
    concurrent teleconsultation sessions.

    Run directly via:
        bench --site <site> execute \
            wellnest.patches.v1_0.switch_event_log_to_myisam.execute

    MyISAM / Aria do not support ACID transactions or foreign keys.
    This trade-off is intentional for an append-only event-log table where
    speed matters more than transactional consistency.
    """    
    table = "tabEvent Log"

    # Detect MariaDB vs MySQL to pick the best engine
    is_mariadb = "mariadb" in (db.get_database_list() or "")
    engine = "Aria" if is_mariadb else "MyISAM"

    db.sql(f"ALTER TABLE `{table}` ENGINE={engine};")
    db.commit()
    print(f"[patch] {table} engine switched to {engine}.")
