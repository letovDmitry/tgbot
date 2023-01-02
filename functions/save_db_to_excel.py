import openpyxl
from openpyxl.styles import Font

def save_db_to_excel(chat):
    wb = openpyxl.Workbook()
    
    sheet = wb.active

    sheet['A1'] = 'Название группы'
    sheet['A2'] = chat['name']
    sheet['A1'].font = Font(bold=True, size=14)

    sheet['B1'] = 'Ссылка на группу'
    sheet['B2'] = chat['link']
    sheet['B1'].font = Font(bold=True, size=14)

    sheet['C1'] = 'Пользователи'
    sheet['C1'].font = Font(bold=True, size=14)

    

    for i in range(len(chat['users'])):
        sheet.cell(row = i + 2, column= 3).value = chat['users'][i]

    wb.save("base.xlsx")