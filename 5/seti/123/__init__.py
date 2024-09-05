"""
Модуль, который содержит игру Python-MUD.
"""

import cowsay
import shlex
import cmd
import sys
import asyncio
import io
from ..common import list_cows, custom_cows, helps
import threading
import random

cowsay.list_cows = list_cows


class player:
    """
    Класс, представляющий игрока в игре.

    Attributes:
        x (int): Координата X игрока на игровом поле.
        y (int): Координата Y игрока на игровом поле.
        max_x (int): Максимальное значение координаты X на игровом поле.
        max_y (int): Максимальное значение координаты Y на игровом поле.
        weapons (dict): Словарь с доступным оружием игрока и их уроном.
    """

    def __init__(self):
        self.x = 0
        self.y = 0
        self.max_x = 9
        self.max_y = 9
        self.wearpons = {"sword": 10, "spear": 15, "axe": 20}

    def move(self, x, y):
        """
        Перемещает игрока на указанные координаты на игровом поле.

        Args:
            x (int): Изменение координаты X.
            y (int): Изменение координаты Y.
        """
        self.x += x
        self.y += y
        if self.x > self.max_x:
            self.x = 0
        if self.x < 0:
            self.x = self.max_x
        if self.y > self.max_y:
            self.y = 0
        if self.y < 0:
            self.y = self.max_y
        print(f"Moved to {self.x} {self.y}")

    def get_attak_damage(self, wp="sword"):
        """
        Возвращает урон атаки для указанного оружия игрока.

        Args:
            wp (str, optional): Название оружия. По умолчанию 'sword'.

        Returns:
            int: Урон атаки для указанного оружия.

        Raises:
            Exception: Если указанное оружие не найдено в списке доступного оружия.
        """
        if wp in self.wearpons.keys():
            return self.wearpons[wp]
        else:
            raise Exception("Unknown weapon")

    def up(self):
        self.move(0, -1)

    def down(self):
        self.move(0, 1)

    def left(self):
        self.move(-1, 0)

    def right(self):
        self.move(1, 0)

    def get_position(self):
        return self.x, self.y


class monster:
    def __init__(self, phase, hp, cow="default"):
        self.phase = phase
        self.cow = cow
        self.hp = hp

    def encounter(self):
        """
        Выводит сообщение о встрече с монстром.
        """
        # print(self.phase)
        if self.cow in custom_cows.keys():
            print(cowsay.cowsay(self.phase, cowfile=custom_cows[self.cow]))
        else:
            print(cowsay.cowsay(self.phase, cow=self.cow))

    def got_hit(self, damage):
        """
        Обрабатывает полученный урон от атаки.

        Args:
            damage (int): Урон от атаки.
        """
        print(f"Attacked {self.cow},  damage {damage} hp")
        self.hp -= damage

    def __str__(self):
        return "M"


class dungeon:
    def __init__(self):
        self.mas = [["0" for i in range(10)] for i in range(10)]
        self.monsters = []

    def add_monster(self, x, y, phase, hp, cow="default"):
        if str(self.mas[x][y]) == "M":
            print("There is monster already")
            return
        self.mas[x][y] = monster(phase, hp, cow)
        self.monsters.append((x, y))
        print(f"Added monster {cow} to ({x} {y}), saying {phase}, with {hp} hp")

    def chech_point(self, x, y):
        """
        Проверяет, есть ли монстр на указанных координатах и выводит сообщение о встрече, если монстр найден.

        Args:
            x (int): Координата X.
            y (int): Координата Y.
        """
        # print(str(self.mas[x][y]))
        if str(self.mas[x][y]) == "M":
            # print('encounter')
            self.mas[x][y].encounter()

    def show_dugeon(self):
        """
        Выводит текущее состояние подземелья.
        """
        print("\n".join([" ".join(str(el)) for el in self.mas]))

    def attak(self, x, y, damage, name):
        """
        Выполняет атаку монстра на указанных координатах.

        Args:
            x (int): Координата X монстра.
            y (int): Координата Y монстра.
            damage (int): Урон атаки.
            name (str): Имя монстра.
        """
        if str(self.mas[x][y]) == "M":
            if name == self.mas[x][y].cow:
                self.mas[x][y].got_hit(damage)
                if self.mas[x][y].hp < 0:
                    print(f"{self.mas[x][y].cow} died")
                    self.mas[x][y] = "0"
                    self.monsters.remove((x, y))
                else:
                    print(f"{self.mas[x][y].cow} now has {self.mas[x][y].hp} hp")
            else:
                print(f"No {name} here")
        else:
            print("No monster here")

    def mov_monster(self):
        """
        Выполняет движение случайного монстра на игровом поле.
        """
        moves = {"right": (1, 0), "left": (-1, 0), "up": (0, -1), "down": (0, 1)}
        if len(self.monsters) == 0:
            return ""
        while True:
            n = random.randint(0, len(self.monsters) - 1)
            dir = random.choice(list(moves.keys()))
            x, y = self.monsters[n][0], self.monsters[n][1]
            if str(self.mas[x + moves[dir][0]][y + moves[dir][1]]) != "M":
                self.mas[x + moves[dir][0]][y + moves[dir][1]] = self.mas[x][y]
                self.mas[self.monsters[n][0]][self.monsters[n][1]] = "0"
                self.monsters[n] = (x + moves[dir][0], y + moves[dir][1])
                return "Monster {} moved one cell {}".format(
                    self.mas[x + moves[dir][0]][y + moves[dir][1]].cow, dir
                )


class game(cmd.Cmd):
    """
    Класс, представляющий игру и обрабатывающий ввод пользователя.

    Attributes:
        prompt (str): Приглашение командной строки.
        dug (Dungeon): Экземпляр подземелья для управления игровым миром.
        players (dict): Словарь игроков в игре, где ключ - имя игрока, значение - экземпляр игрока.
        cur_pl (str): Текущее имя активного игрока.
    """

    prompt = "> "

    def preloop(self):
        print("<<< Welcome to Python-MUD 0.1 >>>")
        self.dug = dungeon()
        self.players = {"local_player": player()}
        self.cur_pl = "local_player"
        self.enabled_monters = True

    def do_EOF(self, args):
        return True

    def check_pos(self):
        """
        Проверяет текущую позицию игрока на наличие монстра и выводит сообщение о встрече при необходимости.
        """
        self.dug.chech_point(*self.players[self.cur_pl].get_position())

    def do_addmon(self, arg):
        """
        Добавляет монстра в игровой мир на указанные координаты.

        Args:
            arg (str): Строка аргументов команды.

        Raises:
            Exception: Если указанный монстр не найден в списке доступных монстров.
        """
        lexer = shlex.shlex(arg, posix=True)
        lexer.whitespace_split = True
        lexer.whitespace = " "
        lexer.quotes = ['"', "'"]
        # print(lexer)
        tokens = list(lexer)
        # print(tokens)
        if len(tokens) != 8:
            self.help_addmon()
        else:
            try:
                monster_name = tokens[0]
                if not (monster_name in list_cows()):
                    print(*list_cows(), sep=", ")
                    print("Cannot add unknown monster")
                else:
                    hello_string = tokens[tokens.index("hello") + 1]
                    hitpoints = int(tokens[tokens.index("hp") + 1])
                    x_coord = int(tokens[tokens.index("coords") + 1])
                    y_coord = int(tokens[tokens.index("coords") + 2])
                    self.dug.add_monster(
                        x=x_coord,
                        y=y_coord,
                        phase=hello_string,
                        cow=monster_name,
                        hp=hitpoints,
                    )
            except Exception:
                self.help_addmon()

    def help_addmon(self):
        helps.help_addmon()

    def do_up(self, arg):
        """
        Перемещает игрока вверх на игровом поле.
        """
        if arg:
            self.help_up()
        else:
            self.players[self.cur_pl].up()
            self.check_pos()

    def help_up(self):
        helps.help_up()

    def do_down(self, arg):
        """
        Перемещает игрока вниз на игровом поле.
        """
        if arg:
            self.help_down()
        else:
            self.players[self.cur_pl].down()
            self.check_pos()

    def help_down(self):
        helps.help_down()

    def do_left(self, arg):
        """
        Перемещает игрока влево на игровом поле.
        """
        if arg:
            self.help_left()
        else:
            self.players[self.cur_pl].left()
            self.check_pos()

    def help_left(self):
        helps.help_left()

    def do_right(self, arg):
        """
        Перемещает игрока вправо на игровом поле.
        """
        if arg:
            self.help_right()
        else:
            self.players[self.cur_pl].right()
            self.check_pos()

    def help_right(self):
        helps.help_right()

    def do_attack(self, arg):
        """
        Атакует монстра на текущих координатах игрока или монстра с указанным именем.

        Args:
            arg (str): Строка аргументов команды.

        Raises:
            Exception: Если указанное оружие не найдено у игрока.
        """
        if arg:
            lexer = shlex.shlex(arg, posix=True)
            lexer.whitespace_split = True
            lexer.whitespace = " "
            lexer.quotes = ['"', "'"]
            # print(lexer)
            tokens = list(lexer)
            if len(tokens) == 1:
                self.dug.attak(
                    *self.players[self.cur_pl].get_position(),
                    self.players[self.cur_pl].get_attak_damage(),
                    tokens[0],
                )
            elif tokens[1] == "with":
                try:
                    self.dug.attak(
                        *self.players[self.cur_pl].get_position(),
                        self.players[self.cur_pl].get_attak_damage(tokens[2]),
                        tokens[0],
                    )
                except Exception as e:
                    print(e)
            else:
                self.help_attack()
        else:
            self.help_attack()

    def complete_attack(self, text, line, begidx, endidx):
        lexer = shlex.shlex(line, posix=True)
        lexer.whitespace_split = True
        lexer.whitespace = " "
        lexer.quotes = ['"', "'"]
        # print(lexer)
        tokens = list(lexer)
        if "with" in tokens:
            return [
                weapon
                for weapon in self.players[self.cur_pl].wearpons.keys()
                if weapon.startswith(text)
            ]
        if len(tokens) == 2 and tokens[1] in cowsay.list_cows():
            return ["with"]
        if len(tokens) <= 2:
            return [monst for monst in cowsay.list_cows() if monst.startswith(text)]

    def do_sayall(self, args):
        """
        Отправляет сообщение всем игрокам на сервере.

        Args:
            args (str): Сообщение, которое будет отправлено всем игрокам.
        """
        if args:
            lexer = shlex.shlex(args, posix=True)
            lexer.whitespace_split = True
            lexer.whitespace = " "
            lexer.quotes = ['"', "'"]
            # print(lexer)
            tokens = list(lexer)
            print("".join(tokens))

    def do_movemonsters(self, args):
        """
        Переключает режим бродячих монстров

        Args:
            args (str): on/off
        """
        if args == "on":
            self.enabled_monters = True
            print("Wandering monsters enabled")
        elif args == "off":
            self.enabled_monters = False
            print("Wandering monsters disabled")
        else:
            print("Bad argument")

    def help_movemonsters(self, args):
        helps.help_movemonters()

    def help_attack(self):
        helps.help_attack()


app = game()
app.preloop()
clients = {}
logins = {}

lock = threading.Lock()


async def wandering_monsters():

    while True:
        st = app.dug.mov_monster()
        if (st != "") and app.enabled_monters:
            print(st)
            for out in clients.values():
                await out.put(st)
            output = io.StringIO()
            for pl in logins.keys():
                lock.acquire()
                sys.stdout = output
                app.cur_pl = logins[pl]
                app.check_pos()
                sys.stdout = sys.__stdout__
                lock.release()
                await clients[pl].put(output.getvalue())
        await asyncio.sleep(30)


async def chat(reader, writer):
    global app
    global clients
    me = "{}:{}".format(*writer.get_extra_info("peername"))
    tmp = asyncio.Queue()
    send = asyncio.create_task(reader.readline())
    receive = asyncio.create_task(tmp.get())
    logged = False
    print(me)
    while not reader.at_eof():
        done, pending = await asyncio.wait(
            [send, receive], return_when=asyncio.FIRST_COMPLETED
        )
        for q in done:
            if q is send:
                send = asyncio.create_task(reader.readline())
                if not (q.result().decode().strip() in logins.values()):
                    # print('tut')
                    if q.result().decode().strip() == "quit":
                        print(me, "DONE")
                        return
                    logins[me] = q.result().decode().strip()
                    await tmp.put("you successfully logged in")
                    for out in clients.values():
                        if out is not tmp:
                            await out.put(
                                f"{me} logged in as {q.result().decode().strip()}"
                            )
                    print(f"{me} logged in as {q.result().decode().strip()}")
                    logged = True
                    break
                else:
                    await tmp.put("this username is already taken, try another one")
            elif q is receive:
                receive = asyncio.create_task(tmp.get())
                writer.write(f"{q.result()}\n".encode())
                await writer.drain()
        else:
            continue
        break
    clients[me] = tmp
    app.players[logins[me]] = player()
    while not reader.at_eof():
        done, pending = await asyncio.wait(
            [send, receive], return_when=asyncio.FIRST_COMPLETED
        )
        for q in done:
            if q is send:
                send = asyncio.create_task(reader.readline())
                output = io.StringIO()
                input = q.result().decode().strip()
                if input == "quit":
                    send.cancel()
                    receive.cancel()
                    print(me, "DONE")
                    if logged:
                        del app.players[logins[me]]
                        del clients[me]
                        del logins[me]
                    writer.close()
                    return
                lock.acquire()  #!
                sys.stdout = output
                app.cur_pl = logins[me]
                app.onecmd(input)
                sys.stdout = sys.__stdout__
                lock.release()  #!
                output_str = output.getvalue()
                # print()

                if (
                    output_str.startswith("Attacked")
                    or output_str.endswith("died")
                    or output_str.startswith("Added")
                    or input.startswith("sayall")
                ):
                    for out in clients.values():
                        if out is not clients[me]:
                            await out.put(f"{logins[me]}: {output_str}")
                if not input.startswith("sayall"):
                    await clients[me].put(output_str)
            elif q is receive:
                receive = asyncio.create_task(clients[me].get())
                writer.write(f"{q.result()}\n".encode())
                await writer.drain()

    send.cancel()
    receive.cancel()
    print(me, "DONE")
    if logged:
        del app.players[logins[me]]
        del clients[me]
        del logins[me]
    writer.close()


async def main():
    asyncio.create_task(wandering_monsters())
    server = await asyncio.start_server(chat, "0.0.0.0", 1337)
    async with server:
        await server.serve_forever()


def run_main():
    asyncio.run(main())
