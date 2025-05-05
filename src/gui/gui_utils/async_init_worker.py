from PySide6.QtCore import QThread, Signal
import queue, multiprocessing as mp

from core.stream_processor import StreamProcessor
from core.model_processor import Model, draw_object_contours


class InitWorker(QThread):
    ready = Signal(object, object, object)

    def __init__(self, source, model_path, frame_skip, queue_size):
        super().__init__()
        self.source = source
        self.model_path = model_path
        self.frame_skip = frame_skip
        self.queue_size = queue_size

    def run(self):
        stream_proc = StreamProcessor(self.source)
        frame_q = mp.Queue(maxsize=self.queue_size)
        proc_q = mp.Queue(maxsize=self.queue_size)
        flag = mp.Value("b", True)
        worker = mp.Process(
            target=process_frames_worker,
            args=(frame_q, proc_q, self.model_path, flag, self.frame_skip),
            daemon=True,
        )
        worker.start()

        # 3) signal back to the GUI
        self.ready.emit(stream_proc, frame_q, proc_q)
