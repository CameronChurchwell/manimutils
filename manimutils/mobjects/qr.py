from manim import *
from pathlib import Path
from hashlib import md5

class QRMobject(SVGMobject):

    def __init__(self, url, **kwargs):
        qr_dir = Path(config.media_dir) / 'QR'
        qr_dir.mkdir(exist_ok=True)

        self.url = url
        self.kwargs = kwargs

        import qrcode
        import qrcode.image.svg
        qr = qrcode.make(url, image_factory=qrcode.image.svg.SvgImage, **kwargs)
        h = md5(url.encode('utf-8')).hexdigest()
        qr_file = qr_dir / (str(h) + '.svg')
        qr.save(qr_file)

        super().__init__(qr_file)