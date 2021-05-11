# Create the barcode stickers and QR code stickers
import barcode
from barcode.writer import ImageWriter
import qrcode
from PIL import Image, ImageDraw, ImageFont, ImageOps
import Simple_Process_REPL.appstate as A
import os
import logging

import cv2
from pyzbar import pyzbar

logger = logging.getLogger()

BarCodeType = "barcode"
QRCodeType = "QR_code"

Root = "bar-QR"


def gen(codetype=BarCodeType):
    "Generate a bar code for the current barQR value."
    try:
        v = A.get_in([Root, "value"])
        if codetype == BarCodeType:
            code = create_bar_code(v)
        elif codetype == QRCodeType:
            code = create_qr_code(v)

        A.set_in([Root, codetype, "code", code])
        A.set_in([Root, codetype, "saved", ""])

    except Exception as e:
        logger.error(e)


def save(codetype=BarCodeType):
    "Save the codetype, 'barcode/QR_code', for the current barQR value to it's png file"
    sn = A.get_in([Root, "value"])
    code = A.get_in([Root, codetype, "code"])

    if codetype == BarCodeType:
        fname = get_bc_filename(sn)
        save_barcode(code, fname)
        # because the extension is automatic on the save.
        fname = "%s%s" % (fname, ".png")
    elif codetype == QRCodeType:
        fname = get_qr_filename(sn)
        save_qr_code(code, fname)

    A.set_in([Root, codetype, "saved", fname])
    return fn


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
    """make a failure sticker.  Currently Unused"""
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


def read_barcodes(frame):
    success = False
    barcodes = pyzbar.decode(frame)
    for barcode in barcodes:
        x, y, w, h = barcode.rect
        barcode_info = barcode.data.decode("utf-8")
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, barcode_info, (x + 6, y - 6), font, 2.0, (255, 255, 255), 1)

        A.set_in([Root, "value", barcode_info])
        logging.info("Read Code: %s" % barcode_info)
        success = True

    return frame, success


# Need to take a closer look at this stuff. It's not very nice.
# read barcodes did show a nice green rectangle and the code but
# now it goes away as soon as it matches, so no help.
# maybe a way to get the rectangle back?  I don't know.
# needs some expermenting I think.
def read_barcode_from_camera():
    """read a Bar or QR code from the camera and store it in the Application state."""
    camera = cv2.VideoCapture(0)
    ret = True
    while ret:
        ret, frame = camera.read()
        frame, res = read_barcodes(frame)
        # frame, res = read_code(frame)
        if res:
            break
        cv2.imshow("Barcode/QR code reader", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break
    camera.release()
    cv2.destroyAllWindows()
    return frame


def read_code(image):
    # initialize the cv2 QRCode detector
    res = False
    detector = cv2.QRCodeDetector()
    # detect and decode
    data, vertices_array, binary_qrcode = detector.detectAndDecode(image)
    # if there is a QR code
    # print the data
    if vertices_array is not None:
        A.set_in([Root, "value", data])
        res = True

    return image, res


def video_to_frames(video, path_output_dir):
    # extract frames from a video and save to directory as 'x.png' where
    # x is the frame index
    vidcap = cv2.VideoCapture(video)
    count = 0
    while vidcap.isOpened():
        success, image = vidcap.read()
        if success:
            cv2.imwrite(os.path.join(path_output_dir, "%d.png") % count, image)
            count += 1
        else:
            break
    cv2.destroyAllWindows()
    vidcap.release()


# video_to_frames('../somepath/myvid.mp4', '../somepath/out')
