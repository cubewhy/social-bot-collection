import subprocess


def video_bytes_to_gif_bytes(
        video_data: bytes,
        fps: int = 10,
        width: int = 480,
) -> bytes:
    cmd = [
        "ffmpeg",
        "-hide_banner", "-loglevel", "error",
        "-i", "pipe:0",
        "-vf", f"fps={fps},scale={width}:-1:flags=lanczos",
        "-gifflags", "+transdiff",
        "-f", "gif",
        "pipe:1"
    ]

    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    gif_bytes, _ = proc.communicate(input=video_data)

    if proc.returncode != 0:
        raise RuntimeError("failed to spawn ffmpeg ({})".format(proc.returncode))

    return gif_bytes
