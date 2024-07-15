import tkinter as tk
import CodeNamesAI as AI
from init import *

grid = [""] * 25
beige_cells = [i for i in range(25)]
red_cells = []
blue_cells = []
black_cells = []

def on_left_click(event, row, col):
    entry_dialog = tk.Toplevel(root)
    entry_dialog.title(f"Enter a word for cell ({row},{col})")

    entry = tk.Entry(entry_dialog, width=20)
    entry.pack(padx=10, pady=10)

    def submit_word(event=None):
        word = entry.get()
        grid[row * 5 + col] = word
        update_grid_labels()
        entry_dialog.destroy()
        if word != "" and (row !=4 or col!=4):
            if col == 4:
                on_left_click(None, row+1, 0)
            else:
                on_left_click(None, row, col+1)
    entry.bind('<Return>', submit_word)
    entry.focus()
    entry_dialog.wait_visibility()
    entry_dialog.grab_set()
    entry_dialog.wait_window()
def on_right_click(row, col):
    current_color = grid_labels[row][col]['bg']
    if current_color == "beige":
        grid_labels[row][col]['bg'] = "#FF474C"
        red_cells.append(row * 5 + col)
        beige_cells.remove(row * 5 + col)
    elif current_color == "#FF474C":
        grid_labels[row][col]['bg'] = "#90D5FF"
        red_cells.remove(row * 5 + col)
        blue_cells.append(row * 5 + col)
    elif current_color == "#90D5FF":
        grid_labels[row][col]['bg'] = "#333333"
        grid_labels[row][col]['fg'] = "#ffffff"
        blue_cells.remove(row * 5 + col)
        black_cells.append(row * 5 + col)
    elif current_color == "#333333":
        grid_labels[row][col]['fg'] = "#000000"
        grid_labels[row][col]['bg'] = "beige"
        black_cells.remove(row * 5 + col)
        beige_cells.append(row * 5 + col)
def update_grid_labels():
    for i in range(5):
        for j in range(5):
            label = grid_labels[i][j]
            label.config(text=grid[i * 5 + j])


root = tk.Tk()
root.title("Codes Names")
grid_labels = []
for i in range(5):
    row_labels = []
    for j in range(5):
        label = tk.Label(root, text="", width=20, height=4, relief=tk.RIDGE, padx=5, pady=5, bg="beige")
        label.grid(row=i, column=j)
        label.bind("<Button-1>", lambda e, row=i, col=j: on_left_click(e, row, col))
        label.bind("<Button-3>", lambda e, row=i, col=j: on_right_click(row, col))
        row_labels.append(label)
    grid_labels.append(row_labels)

# Game parameters
def rules(word):
    if len(word.split(" ")) > 1:
        return False
    if word in grid:
        return False
    return True

#hyperparameters
trsh_hesitation = 0.1
trsh_rememb = 0.07
weights = (8, 1, 2, 5)

def check_grid():
    return len([x for x in grid if x == ""]) == 0

def start_game():
    print("<- Questions initiales: ->")
    print("Est-ce que l'IA commence ?")
    start = input('Entrez votre réponse (o/n): ') == 'o'
    print("Est-ce que l'IA est un Guesser (o) ou un Spy (n)  ?")
    if input('Entrez votre réponse (o/n): ') == 'o':
        AI_type = "Guesser"
    else:
        AI_type = "Spy"
    print("Est-ce que l'IA est bleue ?")
    is_blue = input('Entrez votre réponse (o/n): ') == 'o'
    print("Est-ce que l'IA affiche les hésitations ?")
    show_hesitation = input('Entrez votre réponse (o/n): ') == 'o'
    if is_blue:
        good_grid_ind = blue_cells
        negative_grid_ind = red_cells
    else:
        good_grid_ind = red_cells
        negative_grid_ind = blue_cells
    neutrals = beige_cells
    if len(black_cells):
        murderer = black_cells[0]
    # game start
    ai = AI.CodeNameAI("models/frWac_postag_no_phrase_700_skip_cut50.bin", rules, weights)
    ai.update_grid(grid, grid_labels)
    root.update()
    if AI_type == "Guesser":
        finish = False
        if start:
            to_score = 9
            while not finish:
                print("<-- Tour de l'IA -->")
                hn = (input('Entrez votre indice et le chiffre: ')).split(" ")
                valid = False
                while not valid:
                    try:
                        while len(hn) != 2:
                            print("Donner un mot et un chiffre")
                            hn = (input('Entrez votre indice et le chiffre: ')).split(" ")
                        hint, number = hn[0], int(hn[1])
                        valid = True
                    except ValueError:
                        print("Donner un mot et un chiffre")
                        hn = (input('Entrez votre indice et le chiffre: ')).split(" ")
                action, hesitation = ai.get_action(hint, grid)
                if show_hesitation:
                    print("L'IA joue", action, "  ---  ", hesitation)
                else:
                    print("L'IA joue", action)
                grid_labels[grid.index(action) // 5][grid.index(action) % 5].config(text="")
                grid[grid.index(action)] = None
                root.update()
                result = input('La case était-elle une bonne réponse ? (o/n) ') == 'o'
                if result:
                    number -= 1
                elif input("La case était-elle l'assassin ? (o/n)") == 'o':
                    print("Fin de partie, c'était l'assassin")
                    return
                while result and number > 0:
                    action, hesitation = ai.get_action(hint, grid)
                    if hesitation[0][1] < trsh_hesitation:
                        break
                    if show_hesitation:
                        print("L'IA joue", action, "  ---  ", hesitation)
                    else:
                        print("L'IA joue", action)
                    grid_labels[grid.index(action) // 5][grid.index(action) % 5].config(text="")
                    grid[grid.index(action)] = None
                    root.update()
                    result = input('La case était-elle une bonne réponse ? (o/n) ') == 'o'
                    if result:
                        number -= 1
                        to_score -= 1
                    elif input("La case était-elle l'assassin ? (o/n)") == 'o':
                        print("Fin de partie, c'était l'assassin")
                        return
                if number > 0:
                    print("L'IA se souviendra de", hint)
                    ai.hints_to_remember.append([hint, number])
                while len(ai.hints_to_remember) and result and to_score > 0:
                    hint, number = ai.hints_to_remember[-1]
                    if number == 0:
                        ai.hints_to_remember.pop()
                        continue
                    action, hesitation = ai.get_action(hint, grid)
                    if hesitation[0][1] < trsh_rememb:
                        break
                    if show_hesitation:
                        print(f"L'IA joue (souvenir {number} de {hint})", action, "  ---  ", hesitation)
                    else:
                        print("L'IA joue", action)
                    grid_labels[grid.index(action) // 5][grid.index(action) % 5].config(text="")
                    grid[grid.index(action)] = None
                    root.update()
                    result = input('La case était-elle une bonne réponse ? (o/n) ') == 'o'
                    if result:
                        to_score -= 1
                        ai.hints_to_remember[-1][1] -= 1
                    elif input("La case était-elle l'assassin ? (o/n)") == 'o':
                        print("Fin de partie, c'était l'assassin")
                        return
                if to_score == 0:
                    finish = True
                    print("L'IA a gagné !")
                else:
                    print("L'IA s'arrête là")
                    print("<-- Tour de l'adversaire -->")
                    action = input('Entrez la case sélectionnée ("" : fin de tour, "f": fin de partie): ')
                    while action != "" and action != "f":
                        grid_labels[grid.index(action) // 5][grid.index(action) % 5].config(text="")
                        grid[grid.index(action)] = None
                        root.update()
                        action = input('Entrez la case sélectionnée ("" : fin de tour, "f": fin de partie): ')
                    if action == "f":
                        finish = True
                        print("L'IA a perdu !")
            print("Fin de la partie")
        else:
            to_score = 8
            while not finish:
                print("<-- Tour de l'adversaire -->")
                action = input('Entrez la case sélectionnée ("" : fin de tour, "f": fin de partie): ')
                while action != "" and action != "f":
                    grid.remove(action)
                    action = input('Entrez la case sélectionnée ("" : fin de tour, "f": fin de partie): ')
                if action == "f":
                    finish = True
                    print("L'IA a perdu !")
                else:
                    print("<-- Tour de l'IA -->")
                    hn = (input('Entrez votre indice et le chiffre: ')).split(" ")
                    valid = False
                    while not valid:
                        try:
                            while len(hn) != 2:
                                print("Donner un mot et un chiffre")
                                hn = (input('Entrez votre indice et le chiffre: ')).split(" ")
                            hint, number = hn[0], int(hn[1])
                            valid = True
                        except ValueError:
                            print("Donner un mot et un chiffre")
                            hn = (input('Entrez votre indice et le chiffre: ')).split(" ")
                    action, hesitation = ai.get_action(hint, grid)
                    if show_hesitation:
                        print("L'IA joue", action, "  ---  ", hesitation)
                    else:
                        print("L'IA joue", action)
                    grid_labels[grid.index(action) // 5][grid.index(action) % 5].config(text="")
                    grid[grid.index(action)] = None
                    result = input('La case était-elle une bonne réponse ? (o/n) ') == 'o'
                    if result:
                        number -= 1
                    elif input("La case était-elle l'assassin ? (o/n)") == 'o':
                        print("Fin de partie, c'était l'assassin")
                        return
                    while result and number > 0:
                        action, hesitation = ai.get_action(hint, grid)
                        if hesitation[0][1] < trsh_hesitation:
                            break
                        if show_hesitation:
                            print("L'IA joue", action, "  ---  ", hesitation)
                        else:
                            print("L'IA joue", action)
                        number -= 1
                        grid_labels[grid.index(action) // 5][grid.index(action) % 5].config(text="")
                        grid[grid.index(action)] = None
                        root.update()
                        result = input('La case était-elle une bonne réponse ? (o/n) ') == 'o'
                        if result:
                            to_score -= 1
                        elif input("La case était-elle l'assassin ? (o/n)") == 'o':
                            print("Fin de partie, c'était l'assassin")
                            return
                    if number > 0:
                        ai.hints_to_remember.append([hint, number])
                    while len(ai.hints_to_remember) and result and to_score > 0:
                        hint, number = ai.hints_to_remember[-1]
                        if number == 0:
                            ai.hints_to_remember.pop()
                            continue
                        action, hesitation = ai.get_action(hint, grid)
                        if hesitation[0][1] < trsh_rememb:
                            break
                        if show_hesitation:
                            print(f"L'IA joue (souvenir {number} de {hint})", action, "  ---  ", hesitation)
                        else:
                            print("L'IA joue", action)
                        grid_labels[grid.index(action) // 5][grid.index(action) % 5].config(text="")
                        grid[grid.index(action)] = None
                        root.update()
                        result = input('La case était-elle une bonne réponse ? (o/n) ') == 'o'
                        if result:
                            to_score -= 1
                            ai.hints_to_remember[-1][1] -= 1
                        elif input("La case était-elle l'assassin ? (o/n)")  == 'o':
                            print("Fin de partie, c'était l'assassin")
                            return
                    if to_score == 0:
                        finish = True
                        print("L'IA a gagné !")
                    else:
                        print("L'IA s'arrête là")
                        print("<-- Tour de l'adversaire -->")
            print("Fin de la partie")
    elif AI_type == "Spy":
        finish = False
        if start:
            to_score = 9
            while not finish:
                print("<-- Tour de l'IA -->")
                print("L'IA réfléchit")
                hint, number = ai.get_hint_combination(grid, good_grid_ind, neutrals, negative_grid_ind, black_cells)
                print("L'IA propose", hint, number)
                in_rules = input('La proposition est-elle dans les règles ? (o/n)') == 'o'
                while not in_rules:
                    print(hint in ai.word2vec.keys())
                    del ai.word2vec[hint]
                    print(hint in ai.word2vec.keys())
                    hint, number = ai.get_hint_combination(grid, good_grid_ind, neutrals, negative_grid_ind, murderer)
                    print("L'IA propose", hint, number)
                    in_rules = input('La proposition est-elle dans les règles ? (o/n)') == 'o'
                action = input('Entrez la case sélectionnée ("" : fin de tour) : ')
                result = True
                while action != "" and result:
                    if grid.index(action) in good_grid_ind:
                        print("Bonne réponse !")
                        to_score -= 1
                        good_grid_ind.remove(grid.index(action))
                        grid_labels[grid.index(action) // 5][grid.index(action) % 5].config(text="")
                        grid[grid.index(action)] = None
                        root.update()
                        action = input('Entrez la case sélectionnée ("" : fin de tour) : ')
                    else:
                        print("Mauvaise réponse !")
                        print(action, grid.index(action), grid)
                        if grid.index(action) in negative_grid_ind:
                            negative_grid_ind.remove(grid.index(action))
                        elif grid.index(action) == murderer:
                            print("Fin de parties, c'était l'assassin.")
                        else:
                            neutrals.remove(grid.index(action))
                        grid_labels[grid.index(action) // 5][grid.index(action) % 5].config(text="")
                        grid[grid.index(action)] = None
                        root.update()
                        result = False
                if to_score == 0:
                    finish = True
                    print("L'IA a gagné !")
                else:
                    print("<-- Tour de l'adversaire -->")
                    action = input('Entrez la case sélectionnée ("" : fin de tour, "f": fin de partie): ')
                    while action != "" and action != "f":
                        if grid.index(action) in negative_grid_ind:
                            negative_grid_ind.remove(grid.index(action))
                        elif grid.index(action) in good_grid_ind:
                            good_grid_ind.remove(grid.index(action))
                        elif grid.index(action) == murderer:
                            print("Fin de parties, c'était l'assassin.")
                        else:
                            neutrals.remove(grid.index(action))
                        grid_labels[grid.index(action) // 5][grid.index(action) % 5].config(text="")
                        grid[grid.index(action)] = None
                        root.update()
                        action = input('Entrez la case sélectionnée ("" : fin de tour, "f": fin de partie): ')
                    if action == "f":
                        finish = True
                        print("L'IA a perdu !")
                    else:
                        print("<-- Tour de l'adversaire -->")
            print("Fin de la partie")
        else:
            to_score = 8
            while not finish:
                print("<-- Tour de l'adversaire -->")
                action = input('Entrez la case sélectionnée ("" : fin de tour, "f": fin de partie): ')
                while action != "" and action != "f":
                    if grid.index(action) in negative_grid_ind:
                        negative_grid_ind.remove(grid.index(action))
                    elif grid.index(action) in good_grid_ind:
                        good_grid_ind.remove(grid.index(action))
                    elif grid.index(action) == murderer:
                        print("Fin de parties, c'était l'assassin.")
                    else:
                        neutrals.remove(grid.index(action))
                    grid_labels[grid.index(action) // 5][grid.index(action) % 5].config(text="")
                    grid[grid.index(action)] = None
                    action = input('Entrez la case sélectionnée ("" : fin de tour, "f": fin de partie): ')
                if action == "f":
                    finish = True
                    print("L'IA a perdu !")
                else:
                    print("L'IA réfléchit")
                    hint, number = ai.get_hint_combination(grid, good_grid_ind, neutrals, negative_grid_ind, murderer)
                    print("L'IA propose", hint, number)
                    in_rules = input('La propositioone est-elle dans les règles ?') == 'o'
                    while not in_rules:
                        del ai.word2vec[hint]
                        print("L'IA réfléchit")
                        hint, number = ai.get_hint_combination(grid, good_grid_ind, neutrals, negative_grid_ind,
                                                               murderer)
                        print("L'IA propose", hint, number)
                        in_rules = input('La proposition est-elle dans les règles ? (o/n)') == 'o'
                    action = input('Entrez la case sélectionnée ("" : fin de tour) : ')
                    result = True
                    while action != "" and result:
                        if grid.index(action) in good_grid_ind:
                            print("Bonne réponse !")
                            to_score -= 1
                            good_grid_ind.remove(grid.index(action))
                            grid_labels[grid.index(action) // 5][grid.index(action) % 5].config(text="")
                            grid[grid.index(action)] = None
                            root.update()
                            action = input('Entrez la case sélectionnée ("" : fin de tour) : ')
                        else:
                            print("Mauvaise réponse !")
                            if grid.index(action) in negative_grid_ind:
                                negative_grid_ind.remove(grid.index(action))
                            elif grid.index(action) == murderer:
                                print("Fin de parties, c'était l'assassin.")
                            else:
                                neutrals.remove(grid.index(action))
                            grid_labels[grid.index(action) // 5][grid.index(action) % 5].config(text="")
                            grid[grid.index(action)] = None
                            root.update()
                    if to_score == 0:
                        finish = True
                        print("L'IA a gagné !")
                    if to_score == 0:
                        finish = True
                        print("L'IA a gagné !")
            print("Fin de la partie")


start_button = tk.Button(root, text="Démarrer", command=start_game)
start_button.grid(row=5, column=0, columnspan=5, pady=10)

# Start the Tkinter event loop
root.mainloop()

