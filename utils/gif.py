import json
import subprocess
import gzip
import tempfile
from pyrlottie import LottieFile, run, convSingleLottie
from PIL import Image, ImageSequence
import io


def video_bytes_to_gif_bytes(
        video_data: bytes,
        fps: int = 10,
        size: int = 480,
) -> bytes:
    cmd = [
        "ffmpeg",
        "-hide_banner", "-loglevel", "error",
        "-i", "pipe:0",
        "-vf", f"fps={fps},scale={size}:-1:flags=lanczos",
        "-gifflags", "+transdiff",
        "-f", "gif",
        "pipe:1"
    ]

    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    gif_bytes, _ = proc.communicate(input=video_data)

    if proc.returncode != 0:
        raise RuntimeError("failed to spawn ffmpeg ({})".format(proc.returncode))

    return gif_bytes


def tgs_bytes_to_gif_bytes(
        tgs_bytes: bytes,
        scale: float = 1.0,
        frame_skip: int = 0,
) -> bytes:
    json_dict = json.loads(gzip.decompress(tgs_bytes).decode("utf-8"))

    with tempfile.NamedTemporaryFile("w+", suffix=".json", delete=True) as tmp_json:
        json.dump(json_dict, tmp_json)
        tmp_json.flush()

        lottie_file = LottieFile(path=tmp_json.name)

        with tempfile.NamedTemporaryFile(suffix=".gif") as tmp_gif:
            dest_files = {tmp_gif.name}

            run(convSingleLottie(
                lottieFile=lottie_file,
                destFiles=dest_files,
                frameSkip=frame_skip,
                scale=scale,
                backgroundColour="ffffff",
            ))
            return tmp_gif.read()


def compress_gif(gif_bytes: bytes, fps: int = 30, colors: int = 32, size: tuple[int, int] = (125, 125)) -> bytes:
    with Image.open(io.BytesIO(gif_bytes)) as im:
        frames = [frame.convert("RGBA").resize(size, resample=Image.LANCZOS) for frame in ImageSequence.Iterator(im)]
        frames = [f.convert("P", palette=Image.ADAPTIVE, colors=colors) for f in frames]

        out_buf = io.BytesIO()
        frames[0].save(
            out_buf,
            format="GIF",
            save_all=True,
            append_images=frames[1:],
            loop=0,
            optimize=True,
            duration=int(1000 / fps)
        )
        return make_gif_transparent(out_buf.getvalue())


def make_gif_transparent(gif_bytes: bytes, transparent_color=(255, 255, 255)) -> bytes:
    with Image.open(io.BytesIO(gif_bytes)) as im:
        frames = []
        for frame in ImageSequence.Iterator(im):
            frame = frame.convert("RGBA")
            datas = frame.getdata()
            new_data = []
            for item in datas:
                if item[:3] == transparent_color:
                    new_data.append((0, 0, 0, 0))
                else:
                    new_data.append(item)
            frame.putdata(new_data)
            frames.append(frame)

        buf = io.BytesIO()
        frames[0].save(buf, format="GIF", save_all=True, append_images=frames[1:], loop=0, transparency=0)
        return buf.getvalue()
