import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
import mysql.connector
import pygame 

class Tateti:
    def __init__(self):
        # Crear una ventana de tkinter
        self.window = tk.Tk()
        self.window.title("Tateti")
        self.window.configure(bg="black") 
        self.window.geometry("+450+150")

        # Obtener nombres de los jugadores
        self.player1_name = self.get_player_name("Nombre del Jugador 1:")
        self.player2_name = self.get_player_name("Nombre del Jugador 2:")

        # Inicializar el juego
        self.current_player = "X"
        self.board = [" " for _ in range(9)]
        self.player1_score = 0
        self.player2_score = 0
        
        # Etiqueta para mostrar el turno del jugador actual
        self.turn_label = tk.Label(self.window, text=f"Turno de {self.player1_name}", font=("Helvetica", 20), fg="yellow", bg="black")
        self.turn_label.grid(row=0, column=0, columnspan=3, pady=(20, 0))

        # Etiquetas para mostrar la puntuación de los jugadores
        self.player1_score_label = tk.Label(self.window, text=f"Puntuación de {self.player1_name}: {self.player1_score}", font=("Helvetica", 15), fg="white", bg="black")
        self.player1_score_label.grid(row=5, column=0, columnspan=1, pady=(10, 0))
        self.player2_score_label = tk.Label(self.window, text=f"Puntuación de {self.player2_name}: {self.player2_score}", font=("Helvetica", 15), fg="white", bg="black")
        self.player2_score_label.grid(row=5, column=2, columnspan=1, pady=(10, 0))

        # Crear botones para el tablero
        self.buttons = []
        for i in range(3):
            for j in range(3):
                # Crear un botón con función 'on_click' cuando se haga clic en él
                button = tk.Button(self.window, text="", font=("Helvetica", 20, "bold"), width=8, height=3, bg="blue", fg="yellow",
                command=lambda row=i, col=j: self.on_click(row, col))
                
                button.grid(row=i + 1, column=j, padx=10, pady=10)
                self.buttons.append(button)
        
        # Agregar un botón para borrar el historial de partidas
        clear_history_button = tk.Button(self.window, text="Borrar Historial", font=("Helvetica", 15), command=self.clear_history, bg="red")
        clear_history_button.grid(row=8, column=0, columnspan=3, pady=10)

        # Agregar un botón de reinicio
        restart_button = tk.Button(self.window, text="Reiniciar", font=("Helvetica", 15), command=self.reset_game, bg="yellow")
        restart_button.grid(row=4, column=0, columnspan=1, pady=10)

        # Agregar un botón para iniciar un nuevo juego
        new_game_button = tk.Button(self.window, text="Nuevo Juego", font=("Helvetica", 15), command=self.new_game, bg="yellow")
        new_game_button.grid(row=4, column=2, columnspan=1, pady=10)

        # Agregar un botón para consultar el historial de partidas
        history_button = tk.Button(self.window, text="Historial de Partidas", font=("Helvetica", 15), command=self.show_history, bg="blue")
        history_button.grid(row=7, column=0, columnspan=3, pady=(0, 10))
        
        # Cargar sonidos
        pygame.mixer.init()
        self.win_sound = pygame.mixer.Sound("win_sound.mp3")
        self.tie_sound = pygame.mixer.Sound("tie_sound.mp3")
        
        # Para guardar las partidas
        #Esta información debe ser actualizada con la configuración de la base de datos MySQL en nuestra computadora   
        self.ins_res = "INSERT INTO partidas (jugador1, jugador2, resultado, puntos_ganador) VALUES (%s, %s, %s, %s)"
        self.conn = mysql.connector.connect(
            host="localhost",
            port= 3306, # Reemplaza con el puerto correcto si no es el predeterminado (3306)
            user="nombre_de_tu_usuario",
            password="tu_contraseña",
            db="nombre_de_tu_base_de_datos"
        )
        self.cursor = self.conn.cursor()
    
    def clear_history(self):
        # Función para borrar el historial de partidas
        confirm = messagebox.askyesno("Borrar Historial", "¿Estás seguro de que deseas borrar el historial de partidas?")
        if confirm:
            # Ejecutar una sentencia SQL para eliminar todos los registros
            self.cursor.execute("DELETE FROM partidas")
            self.conn.commit()
            messagebox.showinfo("Historial Borrado", "El historial de partidas ha sido borrado exitosamente.")

    def on_click(self, row, col):
        # Manejar el clic en un botón del tablero
        index = row * 3 + col
        if self.board[index] == " ":
            self.board[index] = self.current_player
            self.buttons[index].config(text=self.current_player)
            if self.check_winner():
                # Mostrar mensaje cuando alguien gane
                if self.current_player == "X":
                    winner_message = f"{self.player1_name} gana"
                    self.ganador = self.player1_name
                    self.player1_score += 1
                else:
                    winner_message = f"{self.player2_name} gana"
                    self.ganador = self.player2_name
                    self.player2_score += 1

                # Actualizar la puntuación en la pantalla
                self.update_score()

                # Guardar la puntuación en la base de datos
                puntos_ganador = self.player1_score if self.ganador == self.player1_name else self.player2_score
                self.res = self.player1_name, self.player2_name, self.ganador, puntos_ganador
                self.cursor.execute(self.ins_res, self.res)
                self.conn.commit()

                messagebox.showinfo("Fin del juego", winner_message)
                
                # Reiniciar automáticamente el juego
                self.reset_game()
            elif " " not in self.board:
                # Mostrar mensaje de empate si no hay más movimientos posibles
                #self.tie_sound.play()  # Reproducir sonido de empate
                messagebox.showinfo("Fin del juego", "Empate")
                
                self.reset_game()
            else:
                # Cambiar al siguiente jugador
                self.current_player = "O" if self.current_player == "X" else "X"
                self.update_turn_label()


    def check_winner(self):
        winning_combinations = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]

        for combo in winning_combinations:
            a, b, c = combo
            if self.board[a] == self.board[b] == self.board[c] != " ":
                self.buttons[a].config(bg="green")
                self.buttons[b].config(bg="green")
                self.buttons[c].config(bg="green")
                #self.win_sound.play()  # Reproducir sonido de victoria
                return True

        return False

    def reset_game(self):
        # Reiniciar el juego
        for i in range(9):
            self.board[i] = " "
            self.buttons[i].config(text="", state="normal", bg="blue")
        self.current_player = "X"
        self.update_turn_label()

    def update_turn_label(self):
        # Actualizar la etiqueta del turno del jugador actual
        if self.current_player == "X":
            self.turn_label.config(text=f"Turno de {self.player1_name}", fg="yellow", bg="black")
        else:
            self.turn_label.config(text=f"Turno de {self.player2_name}", fg="yellow", bg="black")

    def get_player_name(self, prompt):
        name = simpledialog.askstring("Nombre", prompt)
        if name == "":
            name = "Jugador"  # Si no se ingresa un nombre, usar "Jugador" como nombre predeterminado.
        self.window.lift()  # Asegura que la ventana principal esté en la parte superior.
        return name



    def new_game(self):
        # Mostrar el ganador del juego anterior
        if self.player1_score > self.player2_score:
            winner_message = f"{self.player1_name} es el ganador con {self.player1_score} puntos."
            self.ganador = self.player1_name
        elif self.player2_score > self.player1_score:
            winner_message = f"{self.player2_name} es el ganador con {self.player2_score} puntos."
            self.ganador = self.player2_name
        else:
            winner_message = "El juego anterior terminó en empate."
            self.ganador = "Empate"
        
        puntos_ganador = self.player1_score if self.ganador == self.player1_name else self.player2_score
        messagebox.showinfo("Fin del juego anterior", winner_message)
        self.res = (self.player1_name, self.player2_name, self.ganador, puntos_ganador)
        self.cursor.execute(self.ins_res, self.res)
        self.conn.commit()
        
            # Restablecer los nombres de usuario y puntuación a sus valores iniciales
        self.player1_name = self.get_player_name("Nombre del Jugador 1:")
        self.player2_name = self.get_player_name("Nombre del Jugador 2:")
        self.player1_score = 0
        self.player2_score = 0

        # Reiniciar el juego para una nueva partida
        self.reset_game()

        # Actualizar las etiquetas de puntuación con los nuevos nombres de usuario
        self.player1_score_label.config(text=f"Puntuación de {self.player1_name}: {self.player1_score}")
        self.player2_score_label.config(text=f"Puntuación de {self.player2_name}: {self.player2_score}")

        # Reiniciar el juego para una nueva partida
        self.reset_game()

    def update_score(self):
        # Actualizar etiquetas de puntuación
        self.player1_score_label.config(text=f"Puntuación de {self.player1_name}: {self.player1_score}")
        self.player2_score_label.config(text=f"Puntuación de {self.player2_name}: {self.player2_score}")

    def show_history(self):
        # Consultar el historial de partidas en la base de datos
        self.cursor.execute("SELECT * FROM partidas")
        historial = self.cursor.fetchall()

        history_message = "Historial de Partidas:\n\n"
        for partida in historial:
            history_message += f"ID: {partida[0]}\n, Jugador 1: {partida[1]}\n, Jugador 2: {partida[2]}, Resultado: {partida[3]}\n, Puntos Ganador: {partida[4]}\n"
            history_message += "-" * 30 + "\n"
        
        # Mostrar el historial en una ventana emergente
        messagebox.showinfo("Historial de Partidas", history_message)

if __name__ == "__main__":
    # Iniciar el juego
    game = Tateti()
    game.window.mainloop()
