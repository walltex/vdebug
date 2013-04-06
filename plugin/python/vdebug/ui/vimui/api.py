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

    @classmethod
    def is_buffer_modified(cls):
        return int(cls.vim.eval('&mod'))

    """ Other getter methods """

    @classmethod
    def line_at_row(cls, row):
        return cls.vim.eval("getline(%s)" % str(row))

    @classmethod
    def signs_of_type(cls, type):
        sign_lines = cls.command('sign place').split("\n")
        positions = {}
        try:
            for line in sign_lines:
                if "name="+type in line:
                    attributes = line.strip().split()
                    lineinfo = attributes[0].split('=')
                    idinfo = attributes[1].split('=')
                    positions[idinfo[1]] = lineinfo[1]
        except:
            pass
        return positions

    """ Buffer/tab modification """

    @classmethod
    def close_tab(cls, tab_number):
        cls.vim.command('silent! %stabc!' % str(tab_number))

    @classmethod
    def change_tab(cls, tab_number):
        cls.vim.command('tabn %s' % str(tab_number))

    """ Command methods """

    @classmethod
    def error(cls, err):
        cls.vim.command('echohl Error | echo "%s" | echohl None'\
                % str(err).replace('"','\\"'))

    @classmethod
    def command(cls, cmd):
        cls.vim.command('redir => _vdebug')
        cls.vim.command(cmd)
        cls.vim.command('redir END')
        return cls.vim.eval('_vdebug')

    @classmethod
    def create_tab(cls, buffer_name):
        cls.vim.command("silent tabnew %s" % buffer_name)
        return cls

    @classmethod
    def place_sign(cls, sign_id, type, file, line):
        cls.vim.command("sign place %s name=%s line=%s file=%s"\
                        %(str(sign_id), type, str(line), file))
        return cls

    @classmethod
    def remove_sign(cls, sign_id):
        cls.vim.command("sign unplace %s" % str(sign_id))
        return cls
