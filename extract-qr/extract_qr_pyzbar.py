import json
from pyzbar.pyzbar import decode
from PIL import Image, UnidentifiedImageError
import fitz

# TODO: Refactor to accept args

# Translates Pdf to PIL colorspace labelling
# TODO: Figure uit other **** the printer outputs
VALID_COLORSPACE = {"DeviceGray": "L"}

OUTPUT_FILE = "../test/output.json"

# TODO: Data files from args
DATA_FILES = [
    "../test/scan/KM_458e22070410180.pdf",
    "../test/scan/KM_458e22070410181.pdf",
    "../test/scan/KM_458e22070410182_0001.jpg",
    "../test/scan/KM_458e22070410182_0002.jpg",
    "../test/scan/KM_458e22070410182_0001.png",
    "../test/clean/2022_sk_t3-1_5sk3_v1.png"
]

# QRCode data format
QR_DATA_SEPARATOR = '\n'
QR_EXPECTED_DATA = ['year', 'subject', 'testcode', 'group']


def parse_data_string(data_string, return_object={}, separator=QR_DATA_SEPARATOR):
    arr = data_string.split(separator)
    if len(arr) == len(QR_EXPECTED_DATA):
        for i in range(len(arr)):
            return_object[QR_EXPECTED_DATA[i]] = arr[i]
    print(return_object)
    return return_object


if __name__ == "__main__":
    extracted_data = {}
    extracted_data['scans'] = []

    for f in DATA_FILES:
        rv = None
        try:
            img = Image.open(f)
            # print(img)
            # img.thumbnail( (320, 320) )
            # print(img)
            data = decode(img)
            if len(data) > 0:
                raw_data = data[0].data.decode("utf-8")
                rv = parse_data_string(raw_data,
                                       {
                                           'filename': f,
                                           'raw_data': raw_data,
                                           'status': 'SUCCESS'
                                       })
                # print(data[0].data)
            else:
                # raw_data = "No QR found in image."
                rv = {
                    'filename': f,
                    'raw_data': "",
                    'status': 'FAILED',
                    'message': "No QR found in image."
                }
                # print("No QR found in image.")
        except UnidentifiedImageError:
            # print("pdf")
            pdffile = fitz.open(f)
            # print(pdffile)

            if len(pdffile) > 0:
                page = pdffile[0]
                # print(page)
                imagelist = page.get_images(full=True)
                # print(imagelist)

                for imgdata in imagelist:
                    # (xref, smask, width, height,
                    # bpc, colorspace, alt.colorspace, name,
                    # filter, referencer)

                    xref = imgdata[0]
                    colorspace = imgdata[5]

                    # print("imgdata", imgdata)
                    # print("colorspace:", colorspace)
                    # print(VALID_COLORSPACE.keys())

                    if colorspace in VALID_COLORSPACE.keys():

                        pix = fitz.Pixmap(pdffile, xref)
                        img = Image.frombytes(
                            VALID_COLORSPACE[colorspace], [pix.width, pix.height], pix.samples)

                        # img = pdffile.extract_image(xref)
                        # # for key, value in img.items():
                        # #     print(key)
                        # print(img['image'])
                        data = decode(img)
                        if len(data) > 0:
                            raw_data = data[0].data.decode("utf-8")
                            rv = parse_data_string(raw_data,
                                                   {
                                                       'filename': f,
                                                       'raw_data': raw_data,
                                                       'status': 'SUCCESS'
                                                   }
                                                   )
                            # Break after finding data
                            break
                        else:
                            rv = {
                                'filename': f,
                                'raw_data': "",
                                'status': 'FAILED',
                                'message': "No QR found in pdf"
                            }
                            # print("No QR found.")
                    else:
                        # raw_data = "Invalid colorspace"
                        rv = {
                            'filename': f,
                            'raw_data': "",
                            'status': 'FAILED',
                            'message': "Invalid colorspace"
                        }

        extracted_data['scans'].append(rv)

        if rv is not None:
            # print(f'{f} >> {raw_data}')
            rv = None

    with open(OUTPUT_FILE, 'w') as outfile:
        json.dump(extracted_data, outfile)
