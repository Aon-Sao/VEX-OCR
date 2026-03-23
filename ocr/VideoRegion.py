from ocr.VideoPosition import VideoPosition


class VideoRegion:
    def __init__(self, left, right):
        assert isinstance(left, VideoPosition) and isinstance(right, VideoPosition)
        self.left = min(left, right)
        self.right = max(left, right)

    def __str__(self):
        return f"{self.left.frame()}f -- {self.right.frame()}f\n" + \
            f"{self.left.time():.2f}s -- {self.right.time():.2f}s\n" + \
            f"{self.left.pretty_time()} -- {self.right.pretty_time()}"

    def start(self):
        return self.left

    def end(self):
        return self.right
