import re
import string

import pymysql

class Danger(object):
    def __init__(self,filepath, config_ini):
        self.config_ini = config_ini
        self.conn = pymysql.connect(
            host="localhost",
            port=int(self.config_ini['db_set']['port']),
            user=self.config_ini['db_set']['user_name'],
            password=self.config_ini['db_set']['password'],
            charset='utf8mb4',
            database=self.config_ini['db_set']['database_name']
        )
        self.cursor = self.conn.cursor()
        self.danger = []
        self.filepath=filepath

    def process_directive(self, hitlist):
        global ignoreline, num_ignored_hits
        # TODO: Currently this is just a stub routine that simply removes
        hitfound = 0
        for i in range(len(hitlist) - 1, -1, -1):
            if hitlist[i].filename == filename and hitlist[i].line == linenumber:
                del hitlist[i]
                hitfound = 1
                num_ignored_hits += 1
        if not hitfound:
            ignoreline = linenumber + 1

    def extract_c_parameters(self, text, pos=0):
        "Return a list of the given C function's parameters, starting at text[pos]"
        i = pos
        p_trailingbackslashes = re.compile(r'(\s|\\(\n|\r))*$')
        while i < len(text):
            if text[i] == '(':
                break
            elif text[i] in string.whitespace:
                i += 1
            else:
                return []
        else:
            return []
        i += 1
        parameters = [""]
        currentstart = i
        parenlevel = 1
        curlylevel = 0
        instring = 0
        incomment = 0
        while i < len(text):
            c = text[i]
            if instring:
                if c == '"' and instring == 1:
                    instring = 0
                elif c == "'" and instring == 2:
                    instring = 0

                elif c == '\\':
                    i += 1
            elif incomment:
                if c == '*' and text[i:i + 2] == '*/':
                    incomment = 0
                    i += 1
            else:
                if c == '"':
                    instring = 1
                elif c == "'":
                    instring = 2
                elif c == '/' and text[i:i + 2] == '/*':
                    incomment = 1
                    i += 1
                elif c == '/' and text[i:i + 2] == '//':
                    while i < len(text) and text[i] != "\n":
                        i += 1
                elif c == '\\' and text[i:i + 2] == '\\"':
                    i += 1  # Handle exposed '\"'
                elif c == '(':
                    parenlevel += 1
                elif c == ',' and (parenlevel == 1):
                    parameters.append(
                        p_trailingbackslashes.sub('', text[currentstart:i]).strip())
                    currentstart = i + 1
                elif c == ')':
                    parenlevel -= 1
                    if parenlevel <= 0:
                        parameters.append(
                            p_trailingbackslashes.sub(
                                '', text[currentstart:i]).strip())
                        # Re-enable these for debugging:
                        # print " EXTRACT_C_PARAMETERS: ", text[pos:pos+80]
                        # print " RESULTS: ", parameters
                        return parameters
                elif c == '{':
                    curlylevel += 1
                elif c == '}':
                    curlylevel -= 1
                elif c == ';' and curlylevel < 1:
                    print(
                        "Parsing failed to find end of parameter list; "
                        "semicolon terminated it in %s" % text[pos:pos + 200])
                    return parameters
            i += 1
        print("Parsing failed to find end of parameter list in %s" % text[pos:pos + 200])
        return []

    def find_code(self):
        global filename, linenumber, ignoreline, sumlines, num_links_skipped, sloc
        hitlist = []
        sumlines = 0
        sloc = 0
        linenumber = 0
        ignoreline = -1

        p_whitespace = re.compile(r'[ \t\v\f]+')
        p_include = re.compile(r'#\s*include\s+(<.*?>|".*?")')
        # p_digits = re.compile(r'[0-9]')
        # p_alphaunder = re.compile(r'[A-Za-z_]')
        p_c_word = re.compile(r'[A-Za-z_][A-Za-z_0-9$]*')
        p_directive = re.compile(r'(?i)\s*(ITS4|Flawfinder|RATS):\s*([^\*]*)')

        with open(self.filepath, "r", encoding="utf-8") as file:
            file_content = file.readlines()
            text = "".join(file_content)

        linenumber = 1
        ignoreline = -1
        incomment = 0
        instring = 0
        linebegin = 1
        codeinline = 0

        i = 0
        index = 1
        while i < len(text):
            m = p_whitespace.match(text, i)
            if m:
                i = m.end(0)
            if i > len(text):
                c = '\n'
            else:
                c = text[i]
            if linebegin:
                linebegin = 0
                if c == "#":
                    codeinline = 1
                m = p_include.match(text, i)
                if m:
                    i = m.end(0)
                    continue
            if c == '\n':
                index += 1
                linenumber += 1
                sumlines += 1
                linebegin += 1
                if codeinline:
                    sloc += 1
                codeinline = 0
                i += 1
                continue
            i += 1
            if i < len(text):
                nextc = text[i]
            else:
                nextc = ''
            if incomment:
                if c == '*' and nextc == '/':
                    i += 1
                    incomment = 0
            elif instring:
                if c == '\\' and (nextc != "\n"):
                    i += 1
                elif c == '"' and instring == 1:
                    instring = 0
                elif c == "'" and instring == 2:
                    instring = 0
            else:
                if c == '/' and nextc == '*':
                    m = p_directive.match(text, i + 1)
                    if m:
                        self.process_directive(hitlist)
                    while i < len(text) and text[i] != "\n":
                        i += 1
                elif c == '"':
                    instring = 1
                    codeinline = 1
                elif c == "'":
                    instring = 2
                    codeinline = 1
                else:
                    codeinline = 1
                    m = p_c_word.match(text, i - 1)
                    if m:
                        startpos = i - 1
                        endpos = m.end(0)
                        i = endpos
                        word = text[startpos:endpos]
                        lookahead = text[startpos:startpos + 500]
                        parameters = self.extract_c_parameters(text, endpos)
                        self.check(word, index, parameters, lookahead)

    def check(self, word, index, parameters, lookahead):
        flag = False
        if word == "char" or word == "TCHAR" or word == "w_char_t":
            flag = self.c_static_array(word, index, lookahead)
        if word.find("scanf") != -1 and word.find("scanf_s") == -1:
            flag = self.c_scanf(word, index, parameters)
        if word.find("strcpy") != -1 or word.find("strcat") != -1:
            flag = self.c_buffer(word, index, parameters)
        if word == "printf" or word == "syslog" or word == "fprintf":
            flag = self.c_printf(word, index, parameters)
        if word == "sprintf" or word == "vsprintf" or word == "swprintf" or word == "vswprintf" or word == "_stprintf" or word == "_vstprintf":
            flag = self.c_sprintf(word, index, parameters)
        if word == "strncat" or word == "lstrcatn" or word == "wcsncat" or word == "_tcsncat" or word == "_mbsnbcat":
            flag = self.c_strncat(word, index, parameters)
        if word == 'memcpy' or word == 'CopyMemory' or word == 'bcopy':
            flag = self.c_memcpy(word, index, parameters)
        if word == "MultiByteToWideChar":
            flag = self.c_multibyte_to_widechar(word, index, parameters)

        if flag == False:
            self.find_table_flaw(word, index)

    def c_singleton_string(self, text):
        p_c_singleton_string = re.compile(r'^\s*L?"([^\\]|\\[^0-6]|\\[0-6]+)?"\s*$')
        "Returns true if text is a C string with 0 or 1 character."
        return 1 if p_c_singleton_string.search(text) else 0

    def c_constant_string(self, text):
        p_c_constant_string = re.compile(r'^\s*L?"([^\\]|\\[^0-6]|\\[0-6]+)*"$')
        "Returns true if text is a constant C string."
        return 1 if p_c_constant_string.search(text) else 0

    def strip_i18n(self, text):
        gettext_pattern = re.compile(r'(?s)^\s*' 'gettext' r'\s*\((.*)\)\s*$')
        undersc_pattern = re.compile(r'(?s)^\s*' '_(T(EXT)?)?' r'\s*\((.*)\)\s*$')
        match = gettext_pattern.search(text)
        if match:
            return match.group(1).strip()
        match = undersc_pattern.search(text)
        if match:
            return match.group(3).strip()
        return text

    def c_buffer(self, text, index, parameters):
        source_position = 2
        data = [self.filepath, 'line:' + str(index), text]
        if source_position <= len(parameters) - 1:
            source = parameters[source_position]
            if self.c_singleton_string(source):
                data.append("低危险")
                data.append("源数据是常量字符，风险较低")
            elif self.c_constant_string(self.strip_i18n(source)):
                data.append("低危险")
                data.append("源数据是常量字符串，风险较低")
            else:
                return False
        self.danger.append(data)
        return True

    def c_scanf(self, text, index, parameters):
        format_position = 1
        p_dangerous_scanf_format = re.compile(r'%s')
        p_low_risk_scanf_format = re.compile(r'%[0-9]+s')
        data = [self.filepath, 'line:' + str(index), text]
        if format_position <= len(parameters) - 1:
            source = self.strip_i18n(parameters[format_position])
            if self.c_constant_string(source):
                if p_dangerous_scanf_format.search(source):
                    data.append("很危险")
                    data.append("在格式字符串中使用限定符来限制输入的最大长度，例如 '%Ns',防止缓冲区溢出")
                elif p_low_risk_scanf_format.search(source):
                    data.append("低危险")
                    data.append("检查对字符串的限制是否足够小，或者使用不同输入函数例如scanf_s进行处理")
                else:
                    return False
            else:
                data.append("很危险")
                data.append("很可能被恶意攻击，对输入的格式字符串进行验证和过滤确保输入符合预期的格式和范围。可以使用正则表达式、条件语句或其他验证机制来检查输入的有效性.")
            self.danger.append(data)
            return True

    def c_printf(self, text, index, parameters):
        format_position = 1
        data = [self.filepath, "line:" + str(index), text]
        if format_position < len(parameters) - 1:
            source = self.strip_i18n(parameters[format_position])
            if self.c_constant_string(source):
                return False
            else:
                data.append("很危险")
                data.append(
                    "使用常量字符作为格式参数，而不是使用变量或用户输入；如果必须使用用户输入作为格式字符串，进行验证和过滤")
            self.danger.append(data)
            return True

    def c_sprintf(self, word, index, parameters):
        p_dangerous_sprintf_format = re.compile(r'%-?([0-9]+|\*)?s')
        source_position = 2
        data = [self.filepath, 'line:' + str(index), word]
        if parameters is None:
            data.append("很危险")
            data.append("检查所需参数是否存在并检查引号是否关闭")
        elif source_position <= len(parameters) - 1:
            source = parameters[source_position]
            if self.c_singleton_string(source):
                data.append("低危险")
                data.append("没有格式化参数,复制的内容是静态字符串,风险较低,还是建议使用更安全的sprintf_s，snprintf，vsnprintf")
            else:
                source = self.strip_i18n(source)
                if self.c_constant_string(source):
                    if not p_dangerous_sprintf_format.search(source):
                        data.append("低危险")
                        data.append("源字符串长度已知且固定,可以确保目标缓冲区有足够的空间来容纳源字符串。源字符串具有固定的最大长度，仍然需要小心处理其他边界情况.建议使用sprintf_s，snprintf，vsnprintf")
                    else:
                        return False
                else:
                    return False
        self.danger.append(data)

    def c_strncat(self, word, index, parameters):
        p_dangerous_strncat = re.compile(r'^\s*sizeof\s*(\(\s*)?[A-Za-z_$0-9]+'r'\s*(\)\s*)?(-\s*1\s*)?$')
        p_looks_like_constant = re.compile(r'^\s*[A-Z][A-Z_$0-9]+\s*(-\s*1\s*)?$')
        data = [self.filepath, 'line:' + str(index), word]
        if len(parameters) > 3:
            length_text = parameters[3]
            if p_dangerous_strncat.search(length_text) or p_looks_like_constant.search(length_text):
                data.append("很危险")
                data.append("第三个参数为最大追加字符数，但是不能超过原字符长度。此处存在潜在风险，"
                            "使用 strncpy 函数时，应计算源字符串与目标字符串之间的剩余空间，并将其作为长度参数传递给函数，而不是硬编码一个固定的常量。")
            else:
                return False
        else:
            return False
        self.danger.append(data)
        return True

    def c_memcpy(self, word, index, parameters,):
        p_memcpy_sizeof = re.compile(r'sizeof\s*\(\s*([^)\s]*)\s*\)')
        p_memcpy_param_amp = re.compile(r'&?\s*(.*)')
        data = [self.filepath, 'line:' + str(index), word, "低危险", "请确认目标内存是否可以始终保存源数据"]
        if len(parameters) < 4:
            # self.danger.append(data)
            return False
        m1 = re.search(p_memcpy_param_amp, parameters[1])
        m3 = re.search(p_memcpy_sizeof, parameters[3])
        if not m1 or not m3 or m1.group(1) != m3.group(1):
            # self.danger.append(data)
            return False
        else:
            self.danger.append(data)
            return True

    def c_multibyte_to_widechar(self, word, index, parameters):
        data = [self.filepath, 'line:' + str(index), word]
        p_dangerous_multi_byte = re.compile(r'^\s*sizeof\s*(\(\s*)?[A-Za-z_$0-9]+'
                                            r'\s*(\)\s*)?(-\s*1\s*)?$')
        p_safe_multi_byte = re.compile(
            r'^\s*sizeof\s*(\(\s*)?[A-Za-z_$0-9]+\s*(\)\s*)?'
            r'/\s*sizeof\s*\(\s*?[A-Za-z_$0-9]+\s*\[\s*0\s*\]\)\s*(-\s*1\s*)?$')
        if len(parameters) - 1 >= 6:
            num_char_to_copy = parameters[6]
            if p_dangerous_multi_byte.search(num_char_to_copy):
                data.append("很危险")
                data.append("似乎给定的大小是以字节为单位，但该函数要求以字符为单位的大小")
                self.danger.append(data)
                return True
            elif p_safe_multi_byte.search(num_char_to_copy):
                return False

    def c_static_array(self, word, index, lookahead):
        p_static_array = re.compile(r'^[A-Za-z_]+\s+[A-Za-z0-9_$,\s\*()]+\[[^]]')
        if p_static_array.search(lookahead):
            data = [self.filepath, 'line:' + str(index), word, "低危险",
                    "进行边界检查，使用限制长度的函数，或确保大小大于最大可能的长度"]
            self.danger.append(data)
            return True
        else:
            return False

    def find_table_flaw(self, word, index):
        sql = "SELECT * FROM functions"
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        for row in results:
            if (word == row[0]):
                data = [self.filepath, 'line:' + str(index), row[0], row[1], row[2]]
                self.danger.append(data)

    def findDanger(self):
        try:
            self.find_code()
            print("self danger::",self.danger)
        except Exception as e:
            print(e)
            self.conn.rollback()



