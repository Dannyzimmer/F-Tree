# import pdfkit
from weasyprint import HTML
from resources.scripts.fcodesClasses import FBookTreeview
from resources.libs.fcodes.fcodes.libs.external import unidecode as uni

class HTMLReport:
    def __init__(self, treeview):
        self.treeview = treeview
        self.html_content = ""  # Aquí almacenamos el contenido HTML

    def append_html(self, content):
        self.html_content += content + "\n"

    def print_offspring(self, code, fbook):
        result = fbook.get_offspring_names(code)
        codes = fbook.get_offspring_code(code)
        for c, name in zip(codes, result):
            self.append_html(f'<a href="#{c}" class="relative">{name}</a><br>')

    def print_parents(self, code, fbook):
        codes = [fbook.get_father_code(code), fbook.get_mother_code(code)]
        result = fbook.search_fcodes(codes)
        for code, parent in zip(codes, result):
            self.append_html(f'<a href="#{code}" class="relative">{parent}</a><br>')

    def print_siblings(self, code, fbook):
        result = fbook.get_siblings_name(code)
        codes = fbook.get_siblings_code(code)
        for c, name in zip(codes, result):
            self.append_html(f'<a href="#{c}" class="relative">{name}</a><br>')

    def print_partner(self, code, fbook):
        result = fbook.get_partner_name(code)
        result = result if result != 'NA' else 'NA'
        self.append_html(f'<a href="#{code}" class="relative">{result}</a><br>')

    def insert_tag(self, tag: str, text: str, attribute=None) -> str:
        if attribute:
            open_tag = f'<{tag[1:-1]} {attribute}>'
        else:
            open_tag = f'<{tag[1:-1]}>'
        close_tag = f'</{tag[1:]}>'
        return f'{open_tag}{text}{close_tag}'

    def new_line(self, text='') -> str:
        return f'<br>{text}'

    def add_CSS(self, columns=3):
        result = '''
    <!DOCTYPE html>
    <html>
    <head>
    <style>
    body {
    width: auto;
    height: auto;
    margin: auto;
    padding: 0;
    font-size: 8pt;
    font-family: "Monaco";
    background: #FEFEFE;
    column-count: '''+str(columns)+''';
    column-gap: 5px;
    column-rule: 4px double #C7C7C7;
    -webkit-print-color-adjust:exact !important;
    print-color-adjust:exact !important;
    }

    div.section {
        color: #818181;
        margin-left: 25px;
        margin-bottom:0px;
        margin-top: 0px;
        white-space: pre;
    }

    .relative{
        color: #181818;
        margin-left: 40px;
        margin-bottom:0px;
        margin-top: 0px;
    }

    div.header_box{
        padding: 5px;
        margin: 5px;
        background-color: #EFEFEF;
    }

    div.person{
        margin-left: 15px;
        margin-bottom:15px;
        margin-top:0px;
        white-space: normal;
    }

    h4 {
    color: maroon;
    margin-left: 0px;
    white-space: pre;
    }

    a:link {
    text-decoration: none;
    color: #224746;
    margin-left: 40px;
    margin-bottom:0px;
    margin-top: 0px;
    white-space: pre;
    }

    a:visited {
    color: #376665;
    }

    </style>
    </head>
    '''
        return result

    def put_person_header(self, name, consanguinity_name, fcode: str) -> str:
        return f'''<div class="header_box">
            <h4 id="{fcode}" style="display:inline">{name}</h4>
            <em>({consanguinity_name})</em>&ensp;
        </div>'''

    def print_report_html(self, code, fbook, pattern=''):
        name = fbook.search_fcode(code)
        if pattern:
            cons_code = '*' + str(code[len(pattern):])
            consanguinity_name = fbook.get_fcode(cons_code).get_consanguinity_name()
        else:
            consanguinity_name = fbook.get_fcode(code).get_consanguinity_name()

        self.append_html('<div class="person">')
        self.append_html(self.put_person_header(name, consanguinity_name, code))
        self.append_html(self.insert_tag('<div>', 'PARENTS', 'class="section"'))
        self.print_parents(code, fbook=fbook)
        self.append_html(self.insert_tag('<div>', 'SIBLINGS', 'class="section"'))
        self.print_siblings(code, fbook=fbook)
        self.append_html(self.insert_tag('<div>', 'PARTNER', 'class="section"'))
        self.print_partner(code, fbook=fbook)
        self.append_html(self.insert_tag('<div>', 'OFFSPRING', 'class="section"'))
        self.print_offspring(code, fbook=fbook)
        self.append_html('</div>')

    def print_full_report_html(self, fbook, pattern='', columns=3):
        try:
            if pattern:
                codes = [f.code for f in fbook.all_fcodes if ''.join(f.code[0:len(pattern)]) == pattern]
            else:
                codes = [f.code for f in fbook.all_fcodes]
            names = [uni.unidecode(fbook.search_fcode(i)) for i in codes]
            names, codes = zip(*sorted(zip(names, codes)))

            # Construimos el HTML
            self.append_html(self.add_CSS(columns=columns))
            self.append_html('<body>')
            for c in codes:
                self.print_report_html(code=c, pattern=pattern, fbook=fbook)
            self.append_html('</body>')
            self.append_html('</html>')
        except ValueError:
            pass

    def save_report_to_pdf(self, filename='report.pdf', pattern='', columns=3):
        fbook = FBookTreeview(self.treeview)
        self.print_full_report_html(fbook, pattern=pattern, columns=columns)
        HTML(string=self.html_content).write_pdf(filename)

    def report(self, pattern='', columns=3):
        self.save_report_to_pdf(pattern=pattern, columns=columns)
