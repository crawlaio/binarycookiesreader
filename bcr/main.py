# -*- coding: utf-8 -*-
import argparse
from io import BytesIO
from struct import unpack
from time import gmtime, strftime


def parse(input_file: str = "Cookies.binarycookies", output_file: str = "Cookies.txt"):
    binary_file = open(input_file, "rb")
    file_header = binary_file.read(4)
    if file_header == b"cook":
        num_pages = unpack(">i", binary_file.read(4))[0]
        page_sizes = [unpack(">i", binary_file.read(4))[0] for _ in range(num_pages)]
        pages = [binary_file.read(ps) for ps in page_sizes]
        cookie_info_list = []
        for index, page in enumerate(pages):
            page = BytesIO(page)
            page.read(4)
            num_cookies = unpack("<i", page.read(4))[0]
            cookie_offsets = [unpack("<i", page.read(4))[0] for nc in range(num_cookies)]
            page.read(4)
            for offset in cookie_offsets:
                page.seek(offset)
                cookiesize = unpack("<i", page.read(4))[0]
                cookie = BytesIO(page.read(cookiesize))
                cookie.read(4)
                flags = unpack("<i", cookie.read(4))[0]
                if flags == 0:
                    cookie_flags = ""
                elif flags == 1:
                    cookie_flags = "Secure"
                elif flags == 4:
                    cookie_flags = "HttpOnly"
                elif flags == 5:
                    cookie_flags = "Secure; HttpOnly"
                else:
                    cookie_flags = "Unknown"
                cookie.read(4)
                urloffset = unpack("<i", cookie.read(4))[0]
                nameoffset = unpack("<i", cookie.read(4))[0]
                pathoffset = unpack("<i", cookie.read(4))[0]
                valueoffset = unpack("<i", cookie.read(4))[0]
                expiry_date_epoch = unpack("<d", cookie.read(8))[0] + 978307200
                expiry_date = strftime("%a, %d %b %Y ", gmtime(expiry_date_epoch))[:-1]
                cookie.seek(urloffset - 4)
                url = ""
                u = cookie.read(1)
                while unpack("<b", u)[0] != 0:
                    url += str(u, encoding="utf-8")
                    u = cookie.read(1)
                cookie.seek(nameoffset - 4)
                name = ""
                n = cookie.read(1)
                while unpack("<b", n)[0] != 0:
                    name += str(n, encoding="utf-8")
                    n = cookie.read(1)
                cookie.seek(pathoffset - 4)
                path = ""
                pa = cookie.read(1)
                while unpack("<b", pa)[0] != 0:
                    path += str(pa, encoding="utf-8")
                    pa = cookie.read(1)
                cookie.seek(valueoffset - 4)
                value = ""
                va = cookie.read(1)
                while unpack("<b", va)[0] != 0:
                    value += str(va, encoding="utf-8")
                    va = cookie.read(1)
                cookie_info = (
                        "Cookie : "
                        + name
                        + "="
                        + value
                        + "; domain="
                        + url
                        + "; path="
                        + path
                        + "; "
                        + "expires="
                        + expiry_date
                        + "; "
                        + cookie_flags
                )
                # print(index, cookie_info)
                cookie_info_list.append(cookie_info)
        with open(output_file, "w") as f:
            f.write("\n".join(cookie_info_list))
        binary_file.close()
        return "success"
    else:
        binary_file.close()
        raise


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "-i", "--input", type=str, default="Cookies.binarycookies", help="Cookies.binarycookies File Path"
    )
    argparser.add_argument("-o", "--output", type=str, default="Cookies.txt", help="Result File Path")
    args = argparser.parse_args()
    if args.input and args.output:
        try:
            parse(input_file=args.input, output_file=args.output)
        except Exception as e:
            raise


if __name__ == '__main__':
    main()
