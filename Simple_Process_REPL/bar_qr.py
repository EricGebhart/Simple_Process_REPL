# Create the barcode stickers and QR code stickers
import barcode
from barcode.writer import ImageWriter
import qrcode
from PIL import Image, ImageDraw, ImageFont, ImageOps


def pad_serial_num(sn):
    """make the serial number is the minimum length, pad from left with 0s."""
    fmt = ("%%.%dd" % get_in_config("serial_number" "Minimum_length"))
    return(fmt % sn)


def serial_num_2_barcode(sn):
    return pad_serial_num(sn)


def serial_num_2_qrcode():
    prefix = get_in_config("serial_number" "QR_code" "prefix")
    suffix = get_in_config("serial_number" "QR_code" "suffix")
    return str(prefix + pad_serial_num(number) + suffix)


def dialog_BC_or_QR():
    return radiolist(
        "What would you like to print?",
        [
            ("Bar Code", "Bar codes", 1),
            ("QR Code", "QR Codes", 0),
        ],
    )


def save_barcode(bc, filename):
    # options = [module_height = 8, text_distance = 2]
    options = get_in_config("serial_number" "barcode" "save_options")
    bc.save(fileName, options)


def get_bc_filename(sn):
    """generate a name for a barcode file"""
    suffix = get_in_config("serial_number" "barcode" "filename_suffix")
    path = get_in_config("serial_number" "barcode" "save_path")
    return os.path.join(path, sn + suffix + '.png')

def get_qr_filename(sn):
    """generate a name for a QR code file"""
    suffix = get_in_config("serial_number" "QR_code" "filename_suffix")
    path = get_in_config("serial_number" "QR_code" "save_path")
    return os.path.join(path, sn + suffix + '.png')
    return sn + suffix + '.png'


def save_qr_code(qrc, filename):
    qrc.save(fileName)


def create_bar_code(sn):
    """Create a barcode from a number"""
    return barcode.get('code128', serial_num_2_barcode(sn), writer=ImageWriter())

​
def create_qr_code(sn):
    """Create a QR code from a number"""
    qrCode = serial_num_2_qrcode(sn)
    qr = qrcode.QRCode(version=2,
                       error_correction=qrcode.constants.ERROR_CORRECT_L,
                       box_size=4,
                       border=0)

    qr.add_data(qrCode)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    backColor = 'rgb(255, 255, 255)'
    # Left Top Right Bottom
    bimg = ImageOps.expand(img, border = (30,0,30,40), fill=backColor)

    draw = ImageDraw.Draw(bimg)
    font = ImageFont.truetype('DejaVuSans.ttf', size=18)
    (x, y) = (34, 116)
    color = 'rgb(0, 0, 0)'
    draw.text((x, y), qrCode, fill=color, font=font)

    return bimg


def makeFailSticker(reason, code):
    img = Image.new("L", (200, 100), 255)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype('DejaVuSans.ttf', size=24)
    (x, y) = (1, 8)
    color = 'rgb(0, 0, 0)'
    draw.text((x, y), 'TEST FAIL', fill=color, font=font)
    font = ImageFont.truetype('DejaVuSans.ttf', size=14)
    (x, y) = (1, 33)
    case = reason + ": " + str(code)
    draw.text((x, y), case, fill=color, font=font)
    return img
    # img.save(filesystem.get_reports_path() + '/fail/' + 'fail' + '.png')


def dialog_print_codes():
    """
    Ask for a serial number,
    how many to print
    and QR or Bar code.
    Then loop through an os.system call to print.
    """

    serial = input_string("Enter a serial Number to Print")
    count = input_count("Enter count to Print")
    label_type = dialog_BC_or_QR()
    fn = None

    if label_type == "Bar Code":
        code = create_bar_code(serial_num_2_barcode(serial))
        fn = get_bc_filename(serial)
        options = {"module_height": 8, "text_distance": 2}
        code.save(fn, options)
        fn = fn + ".png"  # so everyone else knows it's extension.

    elif label_type == "QR Code":
        code = create_qr_code(serial_num_2_qrcode(serial))
        fn = get_qr_filename(serial)
        code.save(fn)

    cmd_name, print_command = print_command_radio()

    if ynbox(
        "You are ready to print %d %s label(s) of %s to %s?" %
            (count, label_type, serial, cmd_name)):

        command = print_command % fn
        for i in range(0, count):
            os.system(command)

    os.remove(fn)
