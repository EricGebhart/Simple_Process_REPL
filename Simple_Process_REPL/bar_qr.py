# Create the barcode stickers and QR code stickers
import Simple_Process_REPL.dialog_cli as D
import barcode
from barcode.writer import ImageWriter
import qrcode
from PIL import Image, ImageDraw, ImageFont, ImageOps


def pad_num(sn):
    """make sure the number is the minimum length, pad from left with 0s."""
    fmt = "%%.%dd" % get_in_config("bcqr_minimum_length")
    return fmt % sn


def num_2_barcode(sn):
    """turn a number into what we need for a barcode."""
    prefix = get_in_config("barcode" "prefix")
    suffix = get_in_config("barcode" "suffix")
    return pad_num(sn)


def num_2_qrcode():
    prefix = get_in_config("QR_code" "prefix")
    suffix = get_in_config("QR_code" "suffix")
    return str(prefix + pad_num(number) + suffix)


def save_barcode(bc, filename):
    # options = [module_height = 8, text_distance = 2]
    options = get_in_config("barcode" "save_options")
    bc.save(fileName, options)


def get_bc_filename(s):
    """generate a name for a barcode file"""
    suffix = get_in_config("barcode" "filename_suffix")
    path = get_in_config("barcode" "save_path")
    return os.path.join(path, s + suffix + ".png")


def get_qr_filename(s):
    """generate a name for a QR code file"""
    suffix = get_in_config("QR_code" "filename_suffix")
    path = get_in_config("QR_code" "save_path")
    return os.path.join(path, s + suffix + ".png")


def save_qr_code(qrc, filename):
    qrc.save(fileName)


def create_bar_code(s):
    """Create a barcode from a string"""
    return barcode.get("code128", num_2_barcode(s), writer=ImageWriter())


def create_qr_code(s):
    """Create a QR code from a string"""
    qrfont = get_in_config("QR_code" "font")
    qrfont_size = get_in_config("QR_code" "font_size")

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


# This is probably unnecessary, there is another implementation in core.
def dialog_print_codes():
    """
    Ask for a number,
    how many to print
    and QR or Bar code.
    Then loop through an os.system call to print.
    """

    sn = input_string("Enter a serial Number to Print")
    label_type = dialog_BC_or_QR()
    fn = None

    if label_type == "Bar Code":
        code = create_bar_code(num_2_barcode(sn))
        fn = get_bc_filename(sn)
        save_barcode(code, fn)
        fn = fn + ".png"  # so everyone else knows it's extension.

    elif label_type == "QR Code":
        code = create_qr_code(num_2_qrcode(sn))
        fn = get_qr_filename(sn)
        save_qr_code(code, fn)

    count = D.input_count("Enter count to Print")

    cmd_name, print_command = D.print_command_radio()

    if ynbox(
        "You are ready to print %d %s label(s) of %s to %s?"
        % (count, label_type, sn, cmd_name)
    ):

        command = print_command % fn
        for i in range(0, count):
            os.system(command)

    os.remove(fn)


def dialog_BC_or_QR():
    return D.select_choice(
        "Which would you like to print?",
        [
            ("Bar Code", ""),
            ("QR Code", ""),
        ],
    )
