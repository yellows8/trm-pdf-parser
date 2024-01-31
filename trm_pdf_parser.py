import sys
from pypdf import PdfReader

# Note that extra whitespace returned by extract_text() may break find() below.

reader = PdfReader(sys.argv[1])
outf = open(sys.argv[2], 'w')
page_start = int(sys.argv[3])
page_end = int(sys.argv[4])
reg_prefix = sys.argv[5]
format_str = sys.argv[6]
offset_adjust = int(sys.argv[7], 16)

for pagei in range(page_end+1-page_start):
    page = reader.pages[page_start+pagei]
    page_text = page.extract_text()
    page_lines = page_text.split("\n")

    for i in range(len(page_lines)):
        line = page_lines[i]
        tmp = line.find(reg_prefix)
        if tmp!=-1:
            reg_text = line[tmp:]
            print(reg_text)
            print(page_lines[i+1])
            line = page_lines[i+1]
            tmp = line.find("0x")
            if tmp!=-1:
                tmpline = line[tmp:]
                tmp = tmpline.find(" |")
                if tmp!=-1:
                    reg_offset = tmpline[:tmp]
                    tmpline = tmpline[tmp:]

                    tmp = tmpline.find("0x")
                    if tmp!=-1:
                        tmpline = tmpline[tmp:]
                        tmp = tmpline.find(" (")
                        if tmp!=-1:
                            reg_reset = tmpline[:tmp]

                            reg_text = reg_text.replace(" ", "")
                            reg_offset = reg_offset.replace(" ", "")
                            reg_reset = reg_reset.replace(" ", "")

                            print(reg_offset)
                            print(reg_reset)

                            reg_offset = "0x%X" % (int(reg_offset, 16) + offset_adjust)
                            reg_reset = "0x%08X" % (int(reg_reset, 16))

                            out_text = format_str.replace("{NAME}", reg_text)
                            out_text = out_text.replace("{OFFSET}", reg_offset)
                            out_text = out_text.replace("{RESET}", reg_reset)
                            out_text = out_text.replace("\\n", "\n")
                            outf.write(out_text)

