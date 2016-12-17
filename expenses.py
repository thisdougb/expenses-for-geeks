#!/usr/bin/env python3

import cmd, sys, json, datetime, copy, re, os
from expenses import *

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Item(object):
    """An expenses line item, so something you've paid for.
       gross = cost + vat
       vat = gross / rate

       autocalc=True: setting gross calculate cost, 
                      setting cost calculates gross, 
                      setting rate calculates cost from gross
    """
    def __init__(self, date=None, desc=None, rate=0.20, cost=0.0, vat=0.0, gross=0.0, autocalc=True):

        if not autocalc:
            self.cost = float(cost)
            self.gross = float(gross)
            self.vat = float(vat)
            return

        self.cost = 0.0
        self.gross = 0.0
        self.vat = 0.0
        self.date = str(datetime.date.today())

        self.set_date(date)
        self.set_desc(desc)
        self.set_rate(rate)
        self.set_gross(gross)

    def set_date(self, arg):
        """ set the date by moving backwards and forwards, or giving a date string
            date +<int>
            date -<int>
            date 2016-04-27
        """

        if arg == 'today':
            self.date = str(datetime.date.today())
            return

        # create a date object for calculations
        (year, month, day) = [int(s) for s in self.date.split('-')]
        date_obj = datetime.date(year, month, day)

        # date +<int>
        m = re.match('\+([0-9]+)$', str(arg), re.M)
        if m is not None:
            number = m.group(1)
            new_date_obj = date_obj + datetime.timedelta(days=int(number))
            if new_date_obj <= datetime.date.today():
                date_obj = new_date_obj
            else:
                print("living in the future...?")


        # date -<int>
        m = re.match('\-([0-9]+)$', str(arg), re.M)
        if m is not None:
            try:
                number = m.group(1)
                date_obj = date_obj - datetime.timedelta(days=int(number))
            except OverflowError:
                print("too far back into history...")

        # date 2016-04-27
        m = re.search('^[0-9]{4}-[0-9]{1,2}-[0-9]{1,2}$', str(arg))
        if m:
            try:
                (year, month, day) = [int(s) for s in str(arg).split('-')]
                date_obj = datetime.date(year, month, day)
            except ValueError:
                print("incorrect date format, should be YYYY-MM-DD")

        self.date = date_obj.isoformat()

    def set_desc(self, arg):
        self.desc = arg

    def set_rate(self, arg):
        self.rate = float(arg)

        if self.rate > 1.0 and self.rate < 100.0:
            self.rate = self.rate / 100.0

        self.cost = self.gross / (1.0 + self.rate)
        self.vat = self.gross - self.cost

    def set_gross(self, arg):
        self.gross = float(arg)
        if self.rate > 0.0:
            self.cost = self.gross / (1.0 + self.rate)
        else: 
            self.cost = self.gross

        self.vat = self.gross - self.cost

    def set_cost(self, arg):
        self.cost = float(arg)
        self.gross = self.cost * (1.0 + self.rate)
        self.vat = self.gross - self.cost

class Expenses(cmd.Cmd):

    intro = ''
    prompt = '(expense) '

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.item = Item()
        self.data = []
        self.datafile = 'expenses'
        self.do_load(self.datafile)

    # ---- Class methods override --- #

    def postcmd(self, stop, line):
        """Hook method executed just after a command dispatch is finished."""
        # if arg was load file or affecting expenses print summary
        return stop

    def emptyline(self):
        self.formatted_print(item=self.item, withSideBar=True)

    # ---- UI methods --- #

    def formatted_print(self, header=None, footer=None, item=None, withSideBar=None):

        hdr_format_string = '{:>4}  {:^10}  {:<40}  {:>5}  {:>10}  {:>10}  {:>10}'
        total_format_string = '{:>4}  {:^10}  {:<40}  {:>5}  {:>10.2f}  {:>10.2f}  {:>10.2f}'
        format_string = '{:>4}  {:^10}  {:<40}  {:>5.1f}  {:>10.2f}  {:>10.2f}  {:>10.2f}'
        sideBar = ''
        if withSideBar is not None:
            if withSideBar is True:
                sideBar = '>>>>'
                print("")
            else:
                sideBar = withSideBar

        if header is not None:
            print("{:#>101}".format(''))
            print(hdr_format_string.format('rcpt', 'date', 'description', 'vat %', 'cost', 'vat', 'gross'))
            print(hdr_format_string.format('----', '----------', '----------------------------------------', '-----', '----------', '----------', '----------'))

        elif footer is not None:
#            print(hdr_format_string.format('----', '----------', '------------------------------', '-----', '----------', '----------', '----------'))
            print(hdr_format_string.format('', '', '', '', '----------', '----------', '----------'))
            print(total_format_string.format(sideBar, '', '', '', item.cost, item.vat, item.gross))
            print(hdr_format_string.format('', '', '', '', '----------', '----------', '----------'))

        # status line
        elif item is not None and withSideBar is True:
            print(bcolors.WARNING + format_string.format(sideBar, item.date, item.desc, (100.0 * item.rate), item.cost, item.vat, item.gross) + bcolors.ENDC)

        elif item is not None:
            print(format_string.format(sideBar, item.date, item.desc, (100.0 * item.rate), item.cost, item.vat, item.gross))

    def do_date(self, arg):
        """ Set the date: 
                date +3
                date -3
                date 2016-05-03
        """
        self.item.set_date(arg)

    def do_desc(self, arg):
        """ Set the description:
                desc train journey Edinburgh to Grindelwald
        """
        self.item.set_desc(arg)

    def do_cost(self, arg):
        """ Set the cost, automatically setting the gross value too:
                cost 10.50
                cost 6
        """
        self.item.set_cost(arg)

    def do_gross(self, arg):
        """ Set the gross, automatically setting the cost value too:
                gross 15.00
                gross 17
        """
        self.item.set_gross(arg)

    def do_rate(self, arg):
        """ Set the tax rate as percentage or decimal, automatically adjusts the cost and gross:
                rate 20
                rate 0.2
        """
        self.item.set_rate(arg)

    def do_commit(self, arg):
        """ commit the working item (>>>>) to the currently loaded expenses sheet:
                commit
        """
        newItem = copy.deepcopy(self.item)
        self.data.append(newItem)
        self.save_data()
        self.do_show(None)

    def do_del(self, arg):
        """ delete an item from the currently loaded expenses sheet and place it in the working item (>>>>):
                del 4
        """
        index = int(arg) - 1
        if index >= 0 and index < len(self.data):
            self.item = copy.deepcopy(self.data[index])
            del self.data[index]
            self.save_data()

    def do_show(self, arg):
        """ show the currently loaded sheet
                show
        """
        total_gross = 0.0
        total_vat = 0.0
        total_cost = 0.0

        self.formatted_print(header=True)
        idx = 1
        for item in self.data:
            self.formatted_print(item=item, withSideBar=idx)
            idx = idx + 1
            total_gross += item.gross
            total_vat += item.vat
            total_cost += item.cost


        total_item = Item(cost=total_cost, vat=total_vat, gross=total_gross, autocalc=False)
        self.formatted_print(footer=True, item=total_item)
        self.formatted_print(item=self.item, withSideBar=True)

    def do_load(self, arg):
        """With no arg show expenses on disk, load an existing expenses sheet, or set a new sheet name
        load
        load mynewsheet
        """
        regex = re.compile('[a-zA-Z0-9_-]+$')

        files = [ f for f in os.listdir(".") if f.endswith(".json") ]
        for index, file in enumerate(files):
            files[index] = file[:-len(".json")]

        if not arg:
            print(bcolors.OKGREEN + '\t'.join(files) + bcolors.ENDC)
        elif regex.match(arg):
            self.datafile = arg
            self.load_data()
            self.prompt = '(' + self.datafile + ') '
            self.do_show(None)
        else:
            print("syntax: load [a-zA-Z0-9]+")

    def do_bye(self, arg):
        """ Exit the shell:
                bye
        """
        return True

    # ---- functions --- #
    def save_data(self):
        datafile = self.datafile + '.json'
        data = json.dumps([i.__dict__ for i in self.data])
        with open(datafile, 'w') as f:
            json.dump(data, f)

    def load_data(self):
        """ attempt to load data from file
        """
        self.data = []
        datafile = self.datafile + '.json'
        if os.path.isfile(datafile):
            with open(datafile, 'r') as f:
                data = json.load(f)
            clones = json.loads(data)
            for c in clones:
                i = Item()
                i.__dict__ = c
                self.data.append(i)

if __name__ == '__main__':
    Expenses().cmdloop()

