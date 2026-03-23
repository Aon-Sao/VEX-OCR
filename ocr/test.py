from main import run_ocr

def main():
    input_json_a = \
        b"""{
          "scan_start_offset": 0,
          "pg_conn_str": "postgresql://vex_ocr@localhost/VEX?connect_timeout=10",
          "ssd_vid_path": "./test_files/2025/V5RC/VURC/RE_VURC_24_8911-Technology-2025_05_09-T19_45_00.mp4",
          "divisions": [
              {
                "program_code": "VURC",
                "name": "Technology",
                "event_sku": "RE-VURC-24-8911",
                "id": 2
              }
          ],
          "ocr_regions": {
            "MATCH_NUM": [0, 0, 420, 56],
            "DIVISION_NAME": [423, 0, 1499, 53],
            "MATCH_TIMER": [1654, 944, 1920, 1043],
            "MATCH_MODE": [1654, 1044, 1920, 1080]
          }
        }"""
    input_json_b = \
        b"""{
          "scan_start_offset": 0,
          "pg_conn_str": "postgresql://vex_ocr@localhost/VEX?connect_timeout=10",
          "ssd_vid_path": "./test_files/2025/V5RC/VURC/RE_VURC_24_8911-Math-2025_05_09-T19_45_00.mp4",
          "divisions": [
              {
                "program_code": "VURC",
                "name": "Math",
                "event_sku": "RE-VURC-24-8911",
                "id": 2
              }
          ],
          "ocr_regions": {
            "MATCH_NUM": [0, 0, 420, 56],
            "DIVISION_NAME": [423, 0, 1499, 53],
            "MATCH_TIMER": [1654, 944, 1920, 1043],
            "MATCH_MODE": [1654, 1044, 1920, 1080]
          }
        }"""
    input_json_c = \
        b"""{
          "scan_start_offset": 0,
          "pg_conn_str": "postgresql://vex_ocr@localhost/VEX?connect_timeout=10",
          "ssd_vid_path": "./test_files/2025/VIQRC/MS/RE_VIQRC_24_8913-Design-2025_05_12-T19_45_00.mp4",
          "divisions": [
              {
                "program_code": "VIQRC",
                "name": "Design",
                "event_sku": "RE-VIQRC-24-8913",
                "id": 4
              }
          ],
          "ocr_regions": {
            "MATCH_NUM": [0, 0, 420, 56],
            "DIVISION_NAME": [423, 0, 1499, 53],
            "MATCH_TIMER": [1654, 944, 1920, 1043],
            "MATCH_MODE": [1654, 1044, 1920, 1080]
          }
        }"""

    run_ocr(input_json_c)

if __name__ == "__main__":
    main()