import vim

class Vim:
    vim = vim

    """ Getter methods for the current buffer and tab """

    @classmethod
    def current_buffer(cls):
        return cls.vim.eval("bufname('%')")

    @classmethod
    def current_buffer_name(cls):
        return cls.vim.current.buffer.name

    @classmethod
    def current_tab(cls):
        return cls.vim.eval("tabpagenr()")

    @classmethod
    def current_cursor_row(cls):
        return cls.vim.current.window.cursor[0]

    @classmethod
    def current_line(cls):
        return cls.line_at_row(cls.current_cursor_row())

    """ Other getter methods """

    @classmethod
    def line_at_row(cls, row):
        return cls.vim.eval("getline(%s)" % str(row))


    """ Setter/creation methods """

    @classmethod
    def create_tab(cls, buffer_name):
        cls.vim.command("silent tabnew %s" % buffer_name)
        return cls

    @classmethod
    def place_breakpoint_sign(cls, sign_id, file, line):
        cls.vim.command("sign place %s name=breakpt line=%s file=%s"\
                        %(str(sign_id), str(line), file))
        return cls
