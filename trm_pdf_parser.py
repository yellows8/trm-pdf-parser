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

reg_text = None
reg_offset = None
reg_reset = None

skip_zero_reset = True

for pagei in range(page_end+1-page_start):
    page = reader.pages[page_start+pagei]
    page_text = page.extract_text()
    page_lines = page_text.split("\n")
    found = False

    for i in range(len(page_lines)):
        line = page_lines[i]
        if reg_text is None:
            tmp = line.find(reg_prefix)
            if tmp!=-1:
                reg_text = line[tmp:]
                print(reg_text)
                #print(page_lines[i+1])
                #line = page_lines[i+1]
                reg_offset = None
                reg_reset = None

        tmp = -1
        if reg_text is not None:
            tmp = line.find("Offset")
            #if tmp==-1:
            #    print("Offset not found: %s" % (line))
        if tmp!=-1:
            line = line[tmp:]
            tmp = line.find("0x")
            if tmp==-1:
                print("Failed to find first '0x'.")
            if tmp!=-1:
                tmpline = line[tmp:]
                tmp = tmpline.find(" |")
                if tmp==-1:
                    tmp = tmpline.find(" │")
                if tmp==-1:
                    tmp = tmpline.find(" I")
                if tmp==-1:
                    print("Failed to find delimator.")
                if tmp!=-1:
                    reg_offset = tmpline[:tmp]
                    tmpline = tmpline[tmp:]

                    tmp = tmpline.find('(0b')
                    if tmp==-1:
                        tmp = tmpline.find('0b')
                    else:
                        tmp = tmp+1
                    if tmp==-1:
                        print("Failed to find '0b'.")
                        print(page_lines)
                    if tmp!=-1:
                        tmpline = tmpline[tmp:]
                        tmp = tmpline.find(")")
                        if tmp!=-1:
                            reg_reset = tmpline[:tmp]
                        else:
                            reg_reset = tmpline

                        reg_text = reg_text.replace(" ", "")
                        reg_offset = reg_offset.replace(" ", "")
                        reg_reset = reg_reset.replace(" ", "")
                        reg_reset = reg_reset.replace("x", "0")

                        if len(reg_reset)>34:
                            reg_reset = reg_reset[:33]

                        print(reg_offset)
                        print(reg_reset)

                        reg_reset = int(reg_reset, 2)
                        if reg_reset!=0 or (skip_zero_reset is False and reg_reset==0):
                            reg_offset = "0x%X" % (int(reg_offset, 16) + offset_adjust)
                            reg_reset = "0x%08X" % (reg_reset)

                            out_text = format_str.replace("{NAME}", reg_text)
                            out_text = out_text.replace("{OFFSET}", reg_offset)
                            out_text = out_text.replace("{RESET}", reg_reset)
                            out_text = out_text.replace("\\n", "\n")
                            outf.write(out_text)

                        found = True
                        reg_text = None
                        reg_offset = None
                        reg_reset = None

            if reg_offset is None or reg_reset is None:
                reg_text = None
                reg_offset = None
                reg_reset = None

    if found is False:
        print(page_lines)

