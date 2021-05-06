# Определение вилки и валюты
def normalize(a):
    salary_vacansy = {'min': '', 'max': '', 'currensy': ''}

    a = a.split(' ')

    for i in range(len(a)):

        if a[i].isdigit() == True:
            a[i] = int(a[i])

    if len(a) > 1:
        try:  # поиск по ключам "от" и "до"
            salary_vacansy['min'] = a[a.index('от') + 1]
            salary_vacansy['max'] = a[a.index('до') + 1]

        except:
            try:  # поиск по ключу "от"
                if a.index('от') >= 0:
                    salary_vacansy['min'] = a[a.index('от') + 1]
                elif a.index('до') >= 0:
                    salary_vacansy['max'] = a[a.index('от') + 1]
            except:
                try:  # поиск по ключу "до"
                    if a.index('до') >= 0:
                        salary_vacansy['max'] = a[a.index('до') + 1]
                except:
                    if len(a) and type(a[0]) == int and type(a[1]) == int:
                        salary_vacansy['min'] = a[0]
                        salary_vacansy['max'] = a[1]
                    else:
                        salary_vacansy['min'] = a[0]
                        salary_vacansy['max'] = a[0]

        try:  # определение валюты
            if type(a[-1]) == str:
                salary_vacansy['currensy'] = a[-1]
        except:
            print('')
    else:
        try:  # для варианта с 1 записью
            if len(a[i]) == 1:
                if a[i].isdigit() == True:
                    salary_vacansy['min'] = a[i]
        except:
            salary_vacansy['min'] = a[0]
            salary_vacansy['max'] = a[0]
    return salary_vacansy
