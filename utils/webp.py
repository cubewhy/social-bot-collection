import subprocess


def video_bytes_to_webp_bytes(
        video_data: bytes,
        fps: int = 10,
        width: int = 480,
        quality: int = 75,
        loop: int = 0
) -> bytes:
    cmd = [
        "ffmpeg",
        "-hide_banner", "-loglevel", "error",
        "-i", "pipe:0",
        "-vf", f"fps={fps},scale={width}:-1:flags=lanczos",
        "-loop", str(loop),
        "-an",
        "-c:v", "libwebp_anim",
        "-pix_fmt", "yuva420p",
        "-qscale", str(quality),
        "-f", "webp",
        "pipe:1"
    ]

    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = process.communicate(input=video_data)

    if process.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {err.decode()}")

    return output
