# -*- coding: utf-8 -*-
"""Migrate old project database -> APPDATA database (column-intersection, safe)."""
import os
import shutil
import sqlite3
import sys

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "ebooks.db")
DST_DIR = os.path.join(os.environ["APPDATA"], "BookBook", "data")
DST = os.path.join(DST_DIR, "ebooks.db")

TABLES = ["books", "generation_history", "share_tokens", "provider_configs", "active_model"]


def cols(con, table):
    try:
        return [r[1] for r in con.execute(f"PRAGMA table_info({table})")]
    except sqlite3.Error:
        return []


def main():
    print("SRC:", SRC, "exists:", os.path.exists(SRC))
    print("DST:", DST, "exists:", os.path.exists(DST))
    if not os.path.exists(SRC):
        print("ERROR: source db not found"); sys.exit(1)
    os.makedirs(DST_DIR, exist_ok=True)

    if os.path.exists(DST):
        bak = DST + ".bak"
        shutil.copy2(DST, bak)
        print("Backup created:", bak)

    sc = sqlite3.connect(SRC)
    dc = sqlite3.connect(DST)

    for table in TABLES:
        s_cols, d_cols = cols(sc, table), cols(dc, table)
        if not s_cols:
            print(f"[{table}] not in source, skip"); continue
        if not d_cols:
            print(f"[{table}] not in target, skip"); continue
        common = [c for c in s_cols if c in d_cols]
        dropped = [c for c in s_cols if c not in d_cols]
        if dropped:
            print(f"[{table}] columns not migrated (schema changed): {dropped}")
        col_list = ",".join(common)
        rows = sc.execute(f"SELECT {col_list} FROM {table}").fetchall()
        ph = ",".join("?" * len(common))
        ok = 0
        for row in rows:
            try:
                cur = dc.execute(
                    f"INSERT OR IGNORE INTO {table} ({col_list}) VALUES ({ph})", row
                )
                ok += cur.rowcount
            except sqlite3.Error as e:
                print(f"[{table}] row skipped: {e}")
        dc.commit()
        total = dc.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"[{table}] migrated {ok}/{len(rows)} rows, target now has {total}")

    sc.close(); dc.close()
    print("DONE. Restart the app and check Library/History.")


if __name__ == "__main__":
    main()
