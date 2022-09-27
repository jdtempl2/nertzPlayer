import PySimpleGUI as sg


def getInputs():
    sg.theme('DarkAmber')   # Add a touch of color
    # All the stuff inside your window.
    layout = [  [sg.Text('Enter Number of Players'), sg.InputText(default_text='4,5,6')],
                [sg.Text('Enter Number of Games'), sg.InputText(default_text='1000')],
                [sg.Button('Ok')] ]

    # Create the Window
    window = sg.Window('Window Title', layout)
    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Ok': # if user closes window or clicks cancel
            break

    window.close()

    player_nums = [int(x) for x in values[0].split(',')]
    game_nums = int(values[1])

    return [player_nums, game_nums]

