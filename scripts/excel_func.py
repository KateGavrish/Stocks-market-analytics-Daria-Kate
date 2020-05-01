import xlsxwriter


def create(data, filename='chart2.xlsx'):
    workbook = xlsxwriter.Workbook(f'static/excel/{filename}')
    worksheet = workbook.add_worksheet()

    for i in range(len(data)):
        if i * 9 // 26 == 0:
            f = chr(65 + i * 9 % 26)
            s = chr(65 + (i * 9 + 1) % 26)
        else:
            f = chr(64 + i * 9 // 26) + chr(65 + i * 9 % 26)
            s = chr(64 + (i + 1) * 9 // 26) + chr(65 + (i * 9 + 1) % 26)
        values = list(map(lambda x: x[1], data[i]['data']))
        categories = list(map(lambda x: x[0], data[i]['data']))
        worksheet.write_column(s + '20', values)
        worksheet.write_column(f + '20', categories)
        chart = workbook.add_chart({'type': 'line'})
        # Строим по данным
        chart.add_series(
            {'values': f'=Sheet1!{s}20:{s}{19 + len(values)}', 'categories': f'=Sheet1!{f}20:{f}{19 + len(categories)}',
             'name': data[i]['name']})
        chart.set_title({'name': data[i]['chart_name']})
        worksheet.insert_chart(f + '1', chart)

    workbook.close()
