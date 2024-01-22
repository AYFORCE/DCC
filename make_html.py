from jinja2 import Template
from weasyprint import HTML
from datetime import datetime as dt

def header_width(headers):
    intended = 240
    max_length = max(len(header[0]) for header in headers)
    max_width = min(max_length * 10, intended)
    return max(max_width, 100)

html_template = Template('''
<html>
<head>
    <style>
        /* Define your CSS styles here */
        .logo {
            float: right;
            margin-top: {{ logo_margin_top }}px;
        }
        .header {
            font-size: 24px;
            font-weight: bold;
            margin-top: {{ header_margin_top }}px;
            margin-bottom: 10px;
        }
        .sub-sub-header {
            font-family: Tahoma;
            font-size: 14px;
            margin-top: 0px; /* Adjust the margin-top value as per your preference */
            display: table;
            width: 100%;
        }
        .sub-sub-header .header-0 {
            width: {{ max_header_width }}px;
            text-align: left;
            overflow-wrap: break-word;
            display: table-cell;
        }
        .sub-sub-header .header-1 {
            margin-left: 0px; /* Adjust the margin-left value as per your preference */
            text-align: left;
            overflow-wrap: break-word;
            display: table-cell;
        }
        .bold {
            font-weight: bold;
        }
        .bigger {
            font-size: 16px;
        }
    </style>
</head>
<body>
    <div class="logo">
        <img src="{{ logo_path }}" height="{{ logo_height }}" alt="Logo">
    </div>
    <div class="header">
        Calibration certificate
    </div>
    {% for header in sub_headers %}
        <div class="sub-sub-header">
            <p class="header-0">{{ header[0] }}</p>
            <p class="header-1">{{ header[1] }}</p>
        </div>
    {% endfor %}
    {% set render_inner_loop = true %}
    {% for big_header in big_headers %}
        <div class="sub-sub-header">
            <p class="header-0 bold bigger" style="font-family: Tahoma; top-margin: 10px">{{ big_header[0] }}</p>
            <p class="header-1">{{ big_header[1] }}</p>
        </div>
        {% if render_inner_loop %}
            {% for header in rest_headers[loop.index0] %}
                <div class="sub-sub-header">
                    <p class="header-0">{{ header[0] }}</p>
                    {% set line_breaks = header[0].count('\n') or header[0].count('<br>') %}
                    {% if line_breaks > 0 %}
                        {% for _ in range(line_breaks) %}
                            <br>
                        {% endfor %}
                    {% endif %}
                    <p class="header-1">{{ header[1] }}</p>
                </div>
            {% endfor %}
            {% set render_inner_loop = false %}
        {% endif %}
    {% endfor %}
</body>
</html>
''')

# Define the data to be inserted into the template
logo_height = 80
logo_top_margin = -55
header_top_margin = logo_height + logo_top_margin + 30

big_headers = [
    ('OBJECT:', 'Angular Encoder'),
    ('REQUESTOR:', 'Amgen Filial af Amgen Aktiebolag, Sverige'),
    ('CALIBRATION WITH RESPECT TO:', 'FORCE Technology procedure nr. 50.15.01.'),
    ('CALIBRATION RESULT:', 'Look at page 2-5')
]

sub_headers = [
    ('Task number:', '12345'),
    ('Certificate number:', '67890'),
    ('Page:', '1 of 3'),
    ('Date:', dt.today().strftime('%Y-%m-%d'))
]

new_sub_headers = [
    ('Product & serial number:', 'LinMot nr. 3909.83H.001'),
    ('Internal Company Number:', 'AN1250464'),
    ('Type:', 'PR02-52x60-R'),
    ('Recording Equipment Measuring Range:', '± 3590 °')
]

new_new_sub_headers = [
    ('Address:', 'Vandtårnsvej 62A, 2. b 2860 Søborg, Denmark Att. Brian Rosenberg'),
    ('Requisition number:', '-')
]

rest_headers = [new_sub_headers, new_new_sub_headers]
all_headers = [sub_headers, new_sub_headers, new_new_sub_headers, big_headers]
max_header_width = max(header_width(header_set) for header_set in all_headers)

data = {
    'sub_headers': sub_headers,
    'rest_headers': rest_headers,
    'big_headers': big_headers,
    'logo_path': 'https://forcetechnology.com/frontend/images/dist/logo-force.svg',
    'logo_height': logo_height,
    'logo_margin_top': logo_top_margin,
    'header_margin_top': header_top_margin,
    'max_header_width': max_header_width
}

# Render the template with the data
html = html_template.render(**data)

# Convert the HTML to PDF using WeasyPrint
pdf = HTML(string=html).write_pdf()

# Save the PDF to a file
with open('calibration_certificate_weasypdf.pdf', 'wb') as f:
    f.write(pdf)