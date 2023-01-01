import openpyxl
from openpyxl.styles import Font

def save_db_to_excel(chats):
    wb = openpyxl.Workbook()
    
    sheet = wb.active

    sheet['A1'] = 'Название группы'
    sheet['A1'].font = Font(bold=True, size=14)

    sheet['B1'] = 'Ссылка на группу'
    sheet['B1'].font = Font(bold=True, size=14)

    sheet['C1'] = 'Пользователи'
    sheet['C1'].font = Font(bold=True, size=14)

    chats_excel = []

    for chat in chats.find():
        chats_excel.append(chat)

    for i in range(len(chats_excel)):
        sheet.cell(row = i + 2, column= 1).value = chats_excel[i]['name']
        sheet.cell(row = i + 2, column= 2).value = chats_excel[i]['link']

        s = ''
        for k in chats_excel[i]['users']:
            s += '@' + k + ', '
        sheet.cell(row = i + 2, column= 3).value = s

    wb.save("base.xlsx")