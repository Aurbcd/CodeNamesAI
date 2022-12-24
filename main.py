import CodeNamesAI as AI
from init import *


# Game parameters
def rules(word):
    if len(word.split(" ")) > 1:
        return False
    if word in grid:
        return False
    return True


grid = ["solution","lune","ballon","trésor","voiture","hiver","marin","menu","radio","entrée","verre","tokyo","bande","uniforme","volume","tube","poison","fuite","génie","bon","pomme","afrique","miel","titre","dragon"]
print(len(grid))
good_grid_ind = [2,4,5,7,8,10,12,22]
neutrals = [0,3,9,16,17,20,23]
negative_grid_ind = [1,6,11,13,14,18,19,21,24]
murderer = 15
AI_type = "Spy"  # Guesser or Spy
start = False
show_hesitation = True
trsh_hesitation = 0.1
trsh_rememb = 0.07

if __name__ == '__main__':
    if not len(grid):
        words = open("words.txt", "r")
        from_file = words.read().splitlines()
        # grid = random.sample(from_file, 10)
        grid = from_file
    ai = AI.CodeNameAI("word2vecfr/frWac_postag_no_phrase_700_skip_cut50.bin", rules)
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
                grid[grid.index(action)] = None
                result = input('La case était-elle une bonne réponse ? (o/n) ') == 'o'
                if result:
                    number -= 1
                while result and number > 0:
                    action, hesitation = ai.get_action(hint, grid)
                    if hesitation[0][1] < trsh_hesitation:
                        break
                    if show_hesitation:
                        print("L'IA joue", action, "  ---  ", hesitation)
                    else:
                        print("L'IA joue", action)
                    grid[grid.index(action)] = None
                    result = input('La case était-elle une bonne réponse ? (o/n) ') == 'o'
                    if result:
                        number -= 1
                        to_score -= 1
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
                    grid[grid.index(action)] = None
                    result = input('La case était-elle une bonne réponse ? (o/n) ') == 'o'
                    if result:
                        to_score -= 1
                        ai.hints_to_remember[-1][1] -= 1
                if to_score == 0:
                    finish = True
                    print("L'IA a gagné !")
                else:
                    print("L'IA s'arrête là")
                    print("<-- Tour de l'adversaire -->")
                    action = input('Entrez la case sélectionnée ("" : fin de tour, "f": fin de partie): ')
                    while action != "" and action != "f":
                        grid[grid.index(action)] = None
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
                    grid[grid.index(action)] = None
                    result = input('La case était-elle une bonne réponse ? (o/n) ') == 'o'
                    if result:
                        number -= 1
                    while result and number > 0:
                        action, hesitation = ai.get_action(hint, grid)
                        if hesitation[0][1] < trsh_hesitation:
                            break
                        if show_hesitation:
                            print("L'IA joue", action, "  ---  ", hesitation)
                        else:
                            print("L'IA joue", action)
                        number -= 1
                        grid[grid.index(action)] = None
                        result = input('La case était-elle une bonne réponse ? (o/n) ') == 'o'
                        to_score -= 1
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
                        grid[grid.index(action)] = None
                        result = input('La case était-elle une bonne réponse ? (o/n) ') == 'o'
                        if result:
                            to_score -= 1
                            ai.hints_to_remember[-1][1] -= 1
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
                hint, number = ai.get_hint_combination(grid, good_grid_ind, neutrals, negative_grid_ind, murderer)
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
                        grid[grid.index(action)] = None
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
                        grid[grid.index(action)] = None
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
                        grid[grid.index(action)] = None
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
                    grid[grid.index(action)] = None
                    action = input('Entrez la case sélectionnée ("" : fin de tour, "f": fin de partie): ')
                if action == "f":
                    finish = True
                    print("L'IA a perdu !")
                else:
                    print("L'IA réfléchit")
                    hint, number = ai.get_hint_combination(grid, good_grid_ind, neutrals, negative_grid_ind, murderer)
                    print("L'IA propose", hint, number)
                    in_rules = input('La proposition est-elle dans les règles ?') == 'o'
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
                            grid[grid.index(action)] = None
                            action = input('Entrez la case sélectionnée ("" : fin de tour) : ')
                        else:
                            print("Mauvaise réponse !")
                            if grid.index(action) in negative_grid_ind:
                                negative_grid_ind.remove(grid.index(action))
                            elif grid.index(action) == murderer:
                                print("Fin de parties, c'était l'assassin.")
                            else:
                                neutrals.remove(grid.index(action))
                            grid[grid.index(action)] = None
                    if to_score == 0:
                        finish = True
                        print("L'IA a gagné !")
                    if to_score == 0:
                        finish = True
                        print("L'IA a gagné !")
            print("Fin de la partie")