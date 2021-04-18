# Create the barcode stickers and QR code stickers
import barcode
from barcode.writer import ImageWriter
import qrcode
from PIL import Image, ImageDraw, ImageFont, ImageOps
import Simple_Process_REPL.appstate as A
import Simple_Process_REPL.dialog_cli as D
import os

BarCodeType = "barcode"
QRCodeType = "QR_code"


def set_bcqr_from(keys):
    v = A.get_in(keys)
    A.set_in(["barQR", "src", str(keys)])
    A.set_in(["barQR", "value", v])


def get_bcqr(codetype=BarCodeType):
    "Get a bar code for the current barQR value."
    try:
        v = A.get_in(["barQR", "value"])
        if codetype == BarCodeType:
            code = create_bar_code(v)
        elif codetype == QRCodeType:
            code = create_qr_code(v)

        A.set_in(["barQR", codetype, "code", code])
        A.set_in(["barQR", codetype, "saved", ""])

    except Exception as e:
        print(e)


def save_bcqr(codetype=BarCodeType):
    "Save the codetype, 'barcode/QR_code', for the current barQR value to it's png file"
    sn = A.get_in(["barQR", "value"])
    code = A.get_in(["barQR", codetype, "code"])

    if codetype == BarCodeType:
        fn = get_bc_filename(sn)
        save_barcode(code, fn)
        # because the extension is automatic on the save.
        fn = "%s%s" % (fn, ".png")
    elif codetype == QRCodeType:
        fn = get_qr_filename(sn)
        save_qr_code(code, fn)

    A.set_in(["barQR", codetype, "saved", fn])
    return fn


def print_bcqr(codetype=BarCodeType):
    """Print the current 'barcode' or 'QR_code'."""
    fn = A.get_in(["barQR", codetype, "saved"])
    D.print_file(fn)


def print_bcqr_loop(codetype=BarCodeType):
    """print a code in a loop"""
    fn = A.get_in(["barQR", codetype, "saved"])
    D.print_file_loop(fn)


def pad_num(n):
    """make sure its a number and is the minimum length, pad from left with 0s."""
    try:
        min = int(A.get_in_config(["bcqr_minimum_length"]))
    except Exception:
        min = 10
    fmt = "%%.%dd" % min
    return fmt % int(n)


def build_code(s, prefix, suffix):
    """turn a number into what we need for a barcode."""
    if prefix is not None:
        code = "%s%s" % (prefix, pad_num(s))
    else:
        code = pad_num(s)

    if suffix is not None:
        code = "%s%s" % (code, suffix)

    return code


def num_2_barcode(s):
    """turn a number into what we need for a barcode."""
    return build_code(
        s,
        A.get_in_config(["barcode", "prefix"]),
        A.get_in_config(["barcode", "suffix"]),
    )


def num_2_qrcode(s):
    return build_code(
        s,
        A.get_in_config(["QR_code", "prefix"]),
        A.get_in_config(["QR_code", "suffix"]),
    )


def save_barcode(bc, filename):
    # options = [module_height = 8, text_distance = 2]
    path = A.get_in_config(["barcode", "save_path"])
    options = A.get_in_config(["barcode", "save_options"])
    bc.save(filename, options)


def get_bc_filename(s):
    """generate a name for a barcode file"""
    suffix = A.get_in_config(["barcode", "filename_suffix"])
    path = A.get_in_config(["barcode", "save_path"])
    os.makedirs(path, exist_ok=True)
    return os.path.join(path, "%s%s" % (s, suffix))


def get_qr_filename(s):
    """generate a name for a QR code file"""
    suffix = A.get_in_config(["QR_code", "filename_suffix"])
    path = A.get_in_config(["QR_code", "save_path"])
    os.makedirs(path, exist_ok=True)
    return os.path.join(path, "%s%s%s" % (s, suffix, ".png"))


def save_qr_code(qrc, filename):
    qrc.save(filename)


def create_bar_code(s):
    """Create a barcode from a string"""
    return barcode.get("code128", num_2_barcode(s), writer=ImageWriter())


def create_qr_code(s):
    """Create a QR code from a string"""
    qrfont = A.get_in_config(["QR_code", "font"])
    qrfont_size = A.get_in_config(["QR_code", "font_size"])

    qrCode = num_2_qrcode(s)
    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=4,
        border=0,
    )

    qr.add_data(qrCode)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    backColor = "rgb(255, 255, 255)"
    # Left Top Right Bottom
    bimg = ImageOps.expand(img, border=(30, 0, 30, 40), fill=backColor)

    draw = ImageDraw.Draw(bimg)
    font = ImageFont.truetype(qrfont, size=qrfont_size)
    (x, y) = (34, 116)
    color = "rgb(0, 0, 0)"
    draw.text((x, y), qrCode, fill=color, font=font)

    return bimg


def makeFailSticker(reason, code):
    img = Image.new("L", (200, 100), 255)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("DejaVuSans.ttf", size=24)
    (x, y) = (1, 8)
    color = "rgb(0, 0, 0)"
    draw.text((x, y), "TEST FAIL", fill=color, font=font)
    font = ImageFont.truetype("DejaVuSans.ttf", size=14)
    (x, y) = (1, 33)
    case = reason + ": " + str(code)
    draw.text((x, y), case, fill=color, font=font)
    return img
    # img.save(filesystem.get_reports_path() + '/fail/' + 'fail' + '.png')
