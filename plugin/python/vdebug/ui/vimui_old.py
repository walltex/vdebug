# coding=utf-8
import vdebug.ui.interface
import vdebug.util
import vim
import vdebug.log
import vdebug.opts
from vdebug.ui.vimui.window import BreakpointWindow, WatchWindow, StackWindow,\
                                    StatusWindow, LogWindow, SourceWindow

class Ui(vdebug.ui.interface.Ui):
    """Ui layer which manages the Vim windows.
    """

    def __init__(self,breakpoints):
        vdebug.ui.interface.Ui.__init__(self)
        self.is_open = False
        self.breakpoint_store = breakpoints
        self.emptybuffer = None
        self.breakpointwin = BreakpointWindow(self,'rightbelow 7new')
        self.current_tab = "1"
        self.tabnr = None

    def is_modified(self):
       modified = int(vim.eval('&mod'))
       if modified:
           return True
       else:
           return False

    def open(self):
        if self.is_open:
            return
        self.is_open = True

        try:
            cur_buf_name = vim.eval("bufname('%')")
            if cur_buf_name is None:
                cur_buf_name = ''

            self.current_tab = vim.eval("tabpagenr()")

            vim.command('silent tabnew ' + cur_buf_name)
            self.tabnr = vim.eval("tabpagenr()")

            srcwin_name = self.__get_srcwin_name()

            self.watchwin = WatchWindow(self,'vertical belowright new')
            self.watchwin.create()

            self.stackwin = StackWindow(self,'belowright new')
            self.stackwin.create()

            self.statuswin = StatusWindow(self,'belowright new')
            self.statuswin.create()
            self.statuswin.set_status("loading")

            self.watchwin.set_height(20)
            self.statuswin.set_height(5)

            logwin = LogWindow(self,'rightbelow 6new')
            vdebug.log.Log.set_logger(\
                    vdebug.log.WindowLogger(\
                    vdebug.opts.Options.get('debug_window_level'),\
                    logwin))

            winnr = self.__get_srcwinno_by_name(srcwin_name)
            self.sourcewin = SourceWindow(self,winnr)
            self.sourcewin.focus()
        except Exception as e:
            self.is_open = False
            raise e

    def set_source_position(self,file,lineno):
        self.sourcewin.set_file(file)
        self.sourcewin.set_line(lineno)
        self.sourcewin.place_pointer(lineno)

    def mark_as_stopped(self):
        if self.is_open:
            if self.sourcewin:
                self.sourcewin.remove_pointer()
            if self.statuswin:
                self.statuswin.set_status("stopped")
                self.remove_conn_details()

    def set_conn_details(self,addr,port):
        self.statuswin.insert("Connected to %s:%s" %(addr,port),2,True)

    def remove_conn_details(self):
        self.statuswin.insert("Not connected",2,True)

    def set_listener_details(self,addr,port,idekey):
        details = "Listening on %s:%s" %(addr,port)
        if len(idekey):
            details += " (IDE key: %s)" % idekey
        self.statuswin.insert(details,1,True)

    def get_current_file(self):
        return vdebug.util.FilePath(vim.current.buffer.name)

    def get_current_row(self):
        return vim.current.window.cursor[0]

    def get_current_line(self):
        return self.get_line(self.get_current_row())

    def get_line(self,row):
        return vim.eval("getline(" + str(row) + ")")

    def register_breakpoint(self,breakpoint):
        if breakpoint.type == 'line':
            self.place_breakpoint(breakpoint.id,\
                    breakpoint.file,breakpoint.line)
        if self.breakpointwin.is_open:
            self.breakpointwin.add_breakpoint(breakpoint)

    def place_breakpoint(self,sign_id,file,line):
        vim.command('sign place '+str(sign_id)+\
                ' name=breakpt line='+str(line)+\
                ' file='+file.as_local())

    def remove_breakpoint(self,breakpoint):
        id = breakpoint.id
        vim.command('sign unplace %i' % id)
        if self.breakpointwin.is_open:
            self.breakpointwin.remove_breakpoint(id)

    def get_breakpoint_sign_positions(self):
        sign_lines = self.command('sign place').split("\n")
        positions = {}
        for line in sign_lines:
            if "name=breakpt" in line:
                attributes = line.strip().split()
                lineinfo = attributes[0].split('=')
                idinfo = attributes[1].split('=')
                positions[idinfo[1]] = lineinfo[1]
        return positions

    # Execute a vim command and return the output.
    def command(self,cmd):
        vim.command('redir => _tmp')
        vim.command('silent %s' % cmd)
        vim.command('redir END')
        return vim.eval('_tmp')

    def say(self,string):
        """ Vim picks up Python prints, so just print """
        print str(string)
        vdebug.log.Log(string,vdebug.log.Logger.INFO)

    def error(self,string):
        vim.command('echohl Error | echo "'+\
                str(string).replace('"','\\"')+\
                '" | echohl None')
        vdebug.log.Log(string,vdebug.log.Logger.ERROR)

    def close(self):
        if not self.is_open:
            return
        self.is_open = False

        if self.watchwin:
            self.watchwin.destroy()
        if self.stackwin:
            self.stackwin.destroy()
        if self.statuswin:
            self.statuswin.destroy()

        vdebug.log.Log.remove_logger('WindowLogger')
        if self.tabnr:
            vim.command('silent! '+self.tabnr+'tabc!')
        if self.current_tab:
            vim.command('tabn '+self.current_tab)

        self.watchwin = None
        self.stackwin = None
        self.statuswin = None


    def __get_srcwin_name(self):
        return vim.current.buffer.name

    def __get_srcwinno_by_name(self,name):
        i = 1
        vdebug.log.Log("Searching for win by name %s" % name,\
                vdebug.log.Logger.INFO)
        for w in vim.windows:
            vdebug.log.Log("Win %d, name %s" %(i,w.buffer.name),\
                vdebug.log.Logger.INFO)
            if w.buffer.name == name:
                break
            else:
                i += 1

        vdebug.log.Log("Returning window number %d" % i,\
                vdebug.log.Logger.INFO)
        return i

    def __get_buf_list(self):
        return vim.eval("range(1, bufnr('$'))")

