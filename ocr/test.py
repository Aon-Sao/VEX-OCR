import msgspec.json
from ocr.DataObjects import InputData, Division, OCRRegions
from ocr import run_ocr


def main():
    input_data = InputData(
        pg_conn_str="postgresql://vex_ocr@localhost/VEX?connect_timeout=10",
        ssd_vid_path="../test_files/2025/V5RC/MS_VURC_JROTC-Closing_Ceremonies-2025_05_11-T00_30_00.mp4",
        scan_start_offset=0,
        divisions=[
            Division(
                event_sku="RE-VURC-24-8911",
                program_code="VURC",
                division_name="VURC",
            )
        ],
        video_id=-1,  # ???
        worker_host="Destroyah",
        ocr_regions=OCRRegions(
            MATCH_NUM=[0, 0, 420, 56],
            DIVISION_NAME=[423, 0, 1499, 53],
            MATCH_TIMER=[1654, 944, 1920, 1043],
            MATCH_MODE=[1654, 1044, 1920, 1080],
        ),
    )
    input_json = msgspec.json.encode(input_data)
    run_ocr(input_json, input_data.video_id)


if __name__ == "__main__":
    main()
