import os
import shutil
import time
import queue
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from multiprocessing import Manager

# Import the entry point from your OCR package
# Assumes: ocr_engine/processor.py has a function 'run_full_ocr'
# from ocr_engine.processor import run_full_ocr
def run_full_ocr(local_path, video_id, net_path):
    return None

class VideoProcessingService:
    def __init__(self, max_processes=4, ssd_path="./local_ssd_temp"):
        self.ssd_path = os.path.abspath(ssd_path)
        self.one_tb = 1024 ** 4  # 1TB in bytes

        self.max_processes = max_processes
        self.max_video_slots = max_processes * 3

        # Don't initialize Manager or Pools here!
        self.manager = None
        self.shared_state = None
        self.process_pool = None
        self.thread_pool = None
        # ... keep queues and events as they are ...


        # (0 = High, 10 = Normal)
        self.task_queue = queue.PriorityQueue()

        # Ensures we never exceed our SSD 'slot' count
        self.slot_semaphore = threading.BoundedSemaphore(value=self.max_video_slots)

        self.stop_event = threading.Event()

    def start_manager(self):
        """Called by FastAPI lifespan to boot the background monitor."""
        if not os.path.exists(self.ssd_path):
            os.makedirs(self.ssd_path)

        if self.manager is None:
            # These are now created inside the lifespan context
            self.manager = Manager()
            self.shared_state = self.manager.dict()
            self.process_pool = ProcessPoolExecutor(max_workers=self.max_processes)
            self.thread_pool = ThreadPoolExecutor(max_workers=10)

        thread = threading.Thread(target=self._manager_loop, name="ManagerThread", daemon=True)
        thread.start()
        print(f"--- Video Service Started (SSD: {self.ssd_path}) ---")

    def _manager_loop(self):
        """
        The core loop. It sits and waits for tasks in the PriorityQueue.
        Because only THIS thread pulls from the queue, FIFO/Priority is guaranteed.
        """
        while not self.stop_event.is_set():
            try:
                # 1. Grab the next video from the priority queue (blocks for 1s)
                priority, video_id, net_path = self.task_queue.get(timeout=1)

                # 2. Wait for a logical slot (max 12 videos on SSD)
                # If slots are full, this thread pauses here.
                self.slot_semaphore.acquire()

                # 3. Dispatch the download to the Thread Pool
                # We move to the thread pool so the Manager can go back to the queue immediately.
                self.thread_pool.submit(self._download_task, video_id, net_path)

                self.task_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Manager Loop Error: {e}")

    def _download_task(self, video_id, net_path):
        """Runs in THREAD POOL (IO Bound)"""
        local_path = os.path.join(self.ssd_path, f"{video_id}.mp4")

        try:
            # Physical Space Check: Ensure 1TB is free
            while shutil.disk_usage(self.ssd_path).free < self.one_tb:
                self.shared_state[video_id] = {"status": "waiting_for_disk_space", "video_id": video_id}
                time.sleep(10)

            self.shared_state[video_id] = {"status": "downloading", "video_id": video_id}

            # Perform the copy from Network -> SSD
            shutil.copy(net_path, local_path)

            # 4. Trigger the OCR in the Process Pool (CPU Bound)
            # We pass 'self.shared_state' so the process can write back frame progress
            future = self.process_pool.submit(
                run_full_ocr,
                local_path,
                video_id,
                self.shared_state
            )

            # Attach the cleanup callback to trigger when OCR finishes
            future.add_done_callback(lambda f: self._cleanup_callback(f, video_id, local_path))

        except Exception as e:
            print(f"Download Error for {video_id}: {e}")
            self.shared_state[video_id] = {"status": "error", "message": str(e)}
            # Release slot if download fails so the next video can try
            self.slot_semaphore.release()

    def _cleanup_callback(self, future, video_id, local_path):
        """Runs automatically when a Process in the Process Pool finishes OCR."""
        try:
            # check if the process raised an exception
            future.result()
            self.shared_state[video_id] = {"status": "deleting", "video_id": video_id}
        except Exception as e:
            print(f"OCR Process Error for {video_id}: {e}")
            self.shared_state[video_id] = {"status": "failed_ocr", "message": str(e)}
        finally:
            # Delete the file to free up SSD space
            if os.path.exists(local_path):
                os.remove(local_path)

            self.shared_state[video_id]["status"] = "completed"

            # CRITICAL: Release the semaphore slot so the Manager can start the next download
            self.slot_semaphore.release()

    def shutdown(self):
        """Graceful shutdown of all workers."""
        print("--- Shutting down Video Service ---")
        self.stop_event.set()
        self.thread_pool.shutdown(wait=False)
        self.process_pool.shutdown(wait=True)


# Singleton instance for the app to import
video_service = VideoProcessingService()