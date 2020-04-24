import xlsxwriter


def create_excel_chart(name, code, data, filename):
    workbook = xlsxwriter.Workbook(f'static/excel/{filename}')
    worksheet = workbook.add_worksheet()

    # Данные
    values = list(map(lambda x: x[1], data))
    categories = list(map(lambda x: x[0], data))
    worksheet.write_column('B1', values)
    worksheet.write_column('A1', categories)

    # Тип диаграммы
    chart = workbook.add_chart({'type': 'line'})

    # Строим по данным
    chart.add_series(
        {'values': f'=Sheet1!B1:B{len(values)}', 'categories': f'=Sheet1!A1:A{len(categories)}', 'name': code})
    chart.set_title({'name': name})

    worksheet.insert_chart('D1', chart)
    workbook.close()
