# Create the barcode stickers and QR code stickers
import barcode
from barcode.writer import ImageWriter
import qrcode
from PIL import Image, ImageDraw, ImageFont, ImageOps
import Simple_Process_REPL.utils as u
import Simple_Process_REPL.appstate as A
import os
import logging

import cv2
from pyzbar import pyzbar

logger = logging.getLogger()

BarCodeType = "barcode"
QRCodeType = "QRcode"

Root = "bq"

spr = u.load_pkg_resource("Simple_Process_REPL", "bar_qr.spr")

# format and fill in as you wish.
HelpText = """
bar-qr: - Bar and QR Code Scanning, generation, saving and printing.  -

Recognized codetypes are either 'barcode' and 'QR-code'.

Setup the with stack to point at either barcode config or the QRcode config.

The with-bc or with-qr functions will set up the with stack.
From there populate _value_ with something to encode, the function signatures
daisy chain like this. Mix up as you like.

* build-code-string
* pop results code_string
* create
* pop results code
* gen-filename
* pop results filename
* save

Most of this is about building nice codes and filenames for them. There are
settings for many things in the configuration.


Bar/QR code Reader

Read a bar or QR code using the webcam. Currently keeps trying until it
catches it or an escape key is pressed.


When encoding the value is retrieved from bar-QR/value.
When scanning with the webcam the resulting value will be placed in bar-QR/value.

If working exclusively with bar or QR codes it may be beneficial to define
partials for some functions, which always require a code type.

bar-qr has the following spr code.

%s

""" % (
    spr,
)


def help():
    """Additional SPR help For the Bar and QR code Module."""
    print(HelpText)


def create(code_string, code_type=BarCodeType, font="DejaVuSans", font_size=18):
    """Generate a bar or QR code for the codestring.
    returns: the generated code.
    """
    try:
        logger.info("bq/create: %s" % code_type)
        if code_type == BarCodeType:
            code = create_bar_code(code_string)
        elif code_type == QRCodeType:
            code = create_qr_code(code_string, font, font_size)

    except Exception as e:
        logger.error(e)

    return code


def pad_num(number, min_length=10):
    """make sure its a number and is the minimum length, pad from left with 0s."""
    fmt = "%%.%dd" % min_length
    return fmt % int(n)


def build_code_string(value, prefix="", suffix=""):
    """Turn a number string into what we need for a barcode. Give this to create to be
    encoded.
    """
    if isinstance(value, str):
        string = value
    else:
        string = pad_num(value)

    if prefix is not None:
        code = "%s%s" % (prefix, string)
    else:
        code = string

    if suffix is not None:
        code = "%s%s" % (code, suffix)

    return code


def gen_filename(code_string, save_path, filename_suffix, filename_extension):
    """Generate a name for a barcode or QR code file"""
    os.makedirs(save_path, exist_ok=True)
    return os.path.join(
        save_path, "%s%s%s" % (code_string, filename_suffix, filename_extension)
    )


def save_bar_code(bc, filename, save_path, save_options, auto_filename_extension=None):
    "Save a bar code to filename."
    # options = [module_height = 8, text_distance = 2]
    bc.save(filename, save_options)
    if auto_filename_extension:
        filename += auto_filename_extension
    return filename


def save_qr_code(qrc, filename):
    "Save a qr code to filename."
    qrc.save(filename)
    return filename


def save(
    code,
    filename,
    save_path,
    save_options,
    code_type="barcode",
    auto_filename_extension=None,
):
    """Save a bar or QR code according to code_type."""
    try:
        if code_type == BarCodeType:
            filename = save_bar_code(
                code, filename, save_path, save_options, auto_filename_extension
            )
        else:
            filename = save_qr_code(code, filename)

    except Exception as e:
        logger.error(e)
        logger.error("Unable to save %s" % code_type)

    return filename


def create_bar_code(code_string):
    """Create a barcode from a string"""
    return barcode.get("code128", code_string, writer=ImageWriter())


def create_qr_code(code_string, font, font_size):
    """Create a QR code from a string"""

    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=4,
        border=0,
    )

    qr.add_data(code_string)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    backColor = "rgb(255, 255, 255)"
    # Left Top Right Bottom
    bimg = ImageOps.expand(img, border=(30, 0, 30, 40), fill=backColor)

    draw = ImageDraw.Draw(bimg)
    font = ImageFont.truetype(font, size=font_size)
    (x, y) = (34, 116)
    color = "rgb(0, 0, 0)"
    draw.text((x, y), code_string, fill=color, font=font)

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


# ### Bar/QR code reader....
def read_barcodes(frame):
    success = False
    barcodes = pyzbar.decode(frame)
    for barcode in barcodes:
        x, y, w, h = barcode.rect
        barcode_info = barcode.data.decode("utf-8")
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, barcode_info, (x + 6, y - 6), font, 2.0, (255, 255, 255), 1)

        # I think unnecessary.
        A.set("value", barcode_info)
        logging.info("Read Code: %s" % barcode_info)
        success = True

    return frame, success, barcode_info


# Need to take a closer look at this stuff. It's not very nice.
# read barcodes did show a nice green rectangle and the code but
# now it goes away as soon as it matches, so no help.
# maybe a way to get the rectangle back?  I think there is no time.
def read_barcode_from_camera():
    """Read a Bar or QR code from the camera."""
    camera = cv2.VideoCapture(0)
    ret = True
    while ret:
        ret, frame = camera.read()
        frame, res, info = read_barcodes(frame)
        # frame, res = read_code(frame)
        if res:
            break
        cv2.imshow("Barcode/QR code reader", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break
    camera.release()
    cv2.destroyAllWindows()
    return frame, info


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
