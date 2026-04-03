import psycopg


class DatabaseRepository:
    def __init__(self, pg_conn_str):
        self.pg_conn_str = pg_conn_str

    def insert_found_match(self, match_info):
        """
        Insert the found match
        """
        with psycopg.connect(self.pg_conn_str) as conn:
            cur = conn.cursor()
            cur.execute(t"""
                insert into ocr_matches (
                    video_id, worker_host,
                    event_sku,
                    division_name,
                    match_name,
                    
                    auton_start_sec, auton_start_frame,
                    auton_stop_sec, auton_stop_frame,
                    driver_start_sec, driver_start_frame,
                    driver_stop_sec, driver_stop_frame,
                    
                    auton_quality_passes,
                    auton_quality_checks,
                    driver_quality_passes,
                    driver_quality_checks,
                    
                    found_complete_match,
                    notes)
                values (
                    {match_info.video_id}, {match_info.worker_host},
                    {match_info.event_sku},
                    {match_info.division_name},
                    
                    {match_info.match_name},
                    
                    {match_info.auton_start_sec}, {match_info.auton_start_frame},
                    {match_info.auton_stop_sec}, {match_info.auton_stop_frame},
                    {match_info.driver_start_sec}, {match_info.driver_start_frame},
                    {match_info.driver_stop_sec}, {match_info.driver_stop_frame},
                    
                    {match_info.auton_quality_passes},
                    {match_info.auton_quality_checks},
                    {match_info.driver_quality_passes},
                    {match_info.driver_quality_checks},

                    
                    {match_info.found_complete_match},
                    {match_info.notes}
                );
                """)
            conn.commit()
            conn.close()
        return None

    def update_telemetry(self, info: dict):
        """Update the Postgres Database with information about the job status"""
        pass
