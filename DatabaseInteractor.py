import functools
from contextlib import contextmanager

import psycopg

class DatabaseInteractor:
    def __init__(self, pg_conn_str):
        self.pg_conn_str = pg_conn_str

    # This is unholy.
    def pass_connection(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            with self.get_connection() as (conn, cur):
                return func(self, *args, **kwargs, conn=conn, cur=cur)
        return wrapper

    @contextmanager
    def get_connection(self):
        conn = psycopg.connect(self.pg_conn_str)
        cur = conn.cursor()
        try:
            yield conn, cur
        finally:
            conn.commit()
            conn.close()

    def upload_match_download_delta(self, match_info):
        self.update_found_match(match_info)
        return self.select_delta_to_next_match(match_info)

    @pass_connection
    def update_found_match(self, match_info, conn=None, cur=None):
        """
        Update the found match with its found start and end times
        """
        cur.execute(t"""
            update matches set
                ocr_stream_start_sec = {match_info.start}
                , ocr_stream_end_sec = {match_info.end}
            where event_sku = {match_info.event_sku}
                and division_id = {match_info.division_id}
                and round = {match_info.round}
                and instance = {match_info.instance}
                and matchnum = {match_info.match_num};
            """
        )
        return None

    @pass_connection
    def select_delta_to_next_match(self, match_info, conn=None, cur=None):
        """
        Find the delta between the found match and the next started match within the same event and division
        """
        cur.execute(t"""
               with pre as (
                   select matches.event_sku,
                       matches.division_id,

                       matches.round,
                       matches.instance,
                       matches.matchnum,

                       started as this_match_started,
                       LEAD(started) OVER (
                           PARTITION BY event_sku, division_id
                           ORDER BY started, id
                       ) as next_match_started
                   from matches
               )
               select
                   event_sku,
                   division_id,

                   round,
                   instance,
                   matchnum,

                   this_match_started,
                   next_match_started,

                   EXTRACT(EPOCH FROM (next_match_started - this_match_started)) AS started_delta_seconds
               from pre
               where event_sku = {match_info.event_sku}
                   and division_id = {match_info.division_id}
                   and round = {match_info.round}
                   and instance = {match_info.instance}
                   and matchnum = {match_info.match_num};
               """
        )
        return cur.fetchone()[7]  # where the delta ended up in the "result row"

    @pass_connection
    def insert_found_match(self, match_info, conn=None, cur=None):
        """
        Insert the found match
        """
        cur.execute(t"""
            insert into ocr_matches (
                video_id, worker_host,
                division_name, match_name,
                
                auton_start_sec, auton_start_frame,
                auton_stop_sec, auton_stop_frame,
                driver_start_sec, driver_start_frame,
                driver_stop_sec, driver_stop_frame,
                
                found_complete_match,
                notes)
            values (
                {config.video_id}, {config.worker_host},
                {match_info.division_name}, {match_info.match_name},
                
                {match_info.auton_start_sec}, {match_info.auton_start_frame},
                {match_info.auton_stop_sec}, {match_info.auton_stop_frame},
                {match_info.driver_start_sec}, {match_info.driver_start_frame},
                {match_info.driver_stop_sec}, {match_info.driver_stop_frame},
                
                {match_info.found_complete_match},
                {match_info.notes}
            );
            """
        )
        return None
