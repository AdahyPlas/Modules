#-*- coding: utf-8 -*-
#! /usr/bin/env python3

"""Ce script lance une application tkinter montrant le mouvement d'un
pendule. L'utilisateur peut regler l'angle de depart du pendule avec
la regle. En cliquant sur demarrer, le pendule se met en marche. En
cliquant sur arreter le pendule s'arrete, et si on clique a  nouveau
sur demarrer il se remet en marche depuis la  ou il etait. Si on touche
a  la rele au cours de son mouvement, celui-ci est stoppe et il faut
cliquer sur demarrer pour le remettre en marche. A chaque mise en
mouvement, une nouvelle couleur est choisie au hasard montrant le
mouvement de la boule. Enfin, l'angle theta en cours est affichee ainsi
que la vitesse angulaire.
Le pendule est considere comme ideal (mouvement dans un plan 2D, tige
sans masse et rigide, pas de frottement, champ gravitationnel
uniforme). Le mouvement du pendule est calcule en resolvant
numeriquement l'equation du mouvement pour un tel pendule :
d^2theta/dt^2 + (g/l)*sin(theta) = 0.
Lancement: python3 ./tk_pendule.py
Auteur: Patrick Fuchs (Sept 2018)
Inspire des sites suivants:
http://pages.physics.cornell.edu/~sethna/StatMech/ComputerExercises/Pendulum/
https://en.wikipedia.org/wiki/Pendulum_(mathematics)#math_Eq._1
"""

import tkinter as tk
import random as rd
import numpy as np

COLORS = ['gold', 'Darkgoldenrod1', 'red1', 'red2', 'red3', 'Darkgoldenrod2',
          'turquoise', 'blue', 'purple', 'magenta']

# Classe principale qui herite de la classe Tk.
class AppliPendule(tk.Tk):
    """Classe principale de l'application (contient la fenetre Tk).
    """
    def __init__(self):
        """Constructeur de la classe, aucun argument n'est necessaire.
        """
        # Appel du constructeur de la classe mere.
        # L'instance de la fenetre principale se retrouve dans le self.
        tk.Tk.__init__(self)
        # Drapeau pour le mouvement (0 immobile, > 0 en mouvement).
        self.is_moving = 0
        # Grandeurs physiques.
        self.t = 0 # temps (s)
        self.dt = 0.05  # time step (s)
        self.g = 9.8   # acc gravitationnelle (m s^-2)
        self.theta = 0.75*np.pi # angle initial
        self.dtheta = 0.0 # vitesse angulaire = derivee premiee
                          # (pendule au repos au depart)
        self.L = 1 # longueur de la tige dans le repere canvas (m)
        self.x = np.sin(self.theta) * self.L  # qd theta = 0 le pendule
        self.y = -np.cos(self.theta) * self.L # pointe vers le bas.
        #print(self.x, self.y)
        # Conversion x, y en coord ds le canevas (attention, les y
        # descendent alors que ds notre repere ils montent !!!).
        self.x_c, self.y_c = self.map_realcoor2canvas(self.x, self.y)
        # Creation du canevas (inclus dans la fenetre mere).
        self.canv = tk.Canvas(self, bg='gray', height=400, width=400)
        # Dessin du pivot.
        self.canv.create_oval(190, 190, 210, 210, width=1, fill="blue")
        # Dessin de la baballe.
        self.size = 30 # Taille de la baballe ds le repere du canvas.
        self.baballe = self.canv.create_oval(self.x_c-(self.size/2),
                                             self.y_c-(self.size/2),
                                             self.x_c+(self.size/2),
                                             self.y_c+(self.size/2),
                                             width=1, fill="blue")
        # Creation de la tige.
        self.tige = self.canv.create_line(200, 200, self.x_c,
                                          self.y_c, fill="blue")
        # Creation d'une ligne a  x = 0 et y = 0.
        self.canv.create_line(0, 200, 400, 200, dash=(3, 3))
        self.canv.create_line(200, 0, 200, 400, dash=(3, 3))
        # Creation des boutons.
        btn1 = tk.Button(self, text="Quitter", command=self.quit)
        btn2 = tk.Button(self, text="Demarrer", command=self.start)
        btn3 = tk.Button(self, text="Arreter", command=self.stop)
        # Creation d'une regle pour la valeur initiale de theta
        # (on lui met la valeur initiale 0.9*pi).
        self.theta_scale = tk.Scale(self, from_=-np.pi, to=np.pi,
                                    resolution=0.001,
                                    command=self.update_theta_scale)
        self.theta_scale.set(self.theta)
        scale_description = tk.Label(self, text="valeur\ninitiale\nde theta",
                                     fg="blue")
        # Creation d'un Label pour voir les caracteristiques de la Baballe.
        # On utilise une Stringvar (permet de mettre a  jour l'affichage).
        self.stringvar_pos_display = tk.StringVar()
        display_theta = tk.Label(self, textvariable=self.stringvar_pos_display,
                                  fg="blue", font=("Courier New", 12))
        # Placement des widgets dans la fenetre Tk.
        # D'abord le canevas puis les bouttons.
        self.canv.pack(side=tk.LEFT)
        btn1.pack(side=tk.BOTTOM) # boutton quitter
        btn2.pack()
        btn3.pack()
        display_theta.pack()
        # Puis la regle et sa description.
        scale_description.pack(side=tk.LEFT)
        self.theta_scale.pack(side=tk.RIGHT)
        # Une fois le label "packe", on peut mettre une valeur a  l'interieur.
        self.stringvar_pos_display.set(self.get_pos_displ())

    def get_pos_displ(self):
        """Retourne une chaine avec la position et la vitesse (angulaire) de la baballe.
        """
        return "{:>5s} {:>10s}\n{:>5s} {:>10s}\n{:>5.1f} {:>10.1f}".format(
            "theta", "dtheta", "(rad)", "(rad/dt)", self.theta, self.dtheta)

    def map_realcoor2canvas(self, x, y):
        """Transforme les coordonnees reelles en coordonnees dans le canevas.
        """
        # L = 1 m --> 100 pix dans le canvas.
        conv_factor = 100
        xprime = x*conv_factor + 200
        yprime = -y*conv_factor + 200
        return xprime, yprime

    def update_theta_scale(self, value):
        """Met a  jour la position de la baballe quand la regle est touchee.
        """
        # On arrete le mouvement du pendule.
        self.stop()
        self.dtheta = 0.0
        # On met a  jour le pendule avec la nouvelle valeur.
        self.theta = float(value)
        self.x = np.sin(self.theta) * self.L
        self.y = -np.cos(self.theta) * self.L
        # Conversion ds le repere du canvas.
        self.x_c, self.y_c = self.map_realcoor2canvas(self.x, self.y)
        # On met a  jour les coordonnees (baballe + tige).
        self.canv.coords(self.baballe,
                         self.x_c-(self.size/2),
                         self.y_c-(self.size/2),
                         self.x_c+(self.size/2),
                         self.y_c+(self.size/2))
        self.canv.coords(self.tige, 200, 200, self.x_c, self.y_c)
        # On met a  jour la zone de texte.
        self.stringvar_pos_display.set(self.get_pos_displ())
        # On remet a  0 le temps.
        self.t = 0

    def move(self):
        """Deplace la baballe, mets a  jour les coors et s'auto-rappelle apres 20 ms.
        """
        # Calcul du nouveau theta avec un Euler semi-implicite.
        # (d2theta = derivee seconde).
        #print(self.t, self.theta)
        self.d2theta = -(self.g/self.L) * np.sin(self.theta)
        self.dtheta += self.d2theta * self.dt
        self.theta += self.dtheta * self.dt
        # Conversion theta -> x & y.
        self.x = np.sin(self.theta) * self.L
        self.y = -np.cos(self.theta) * self.L
        # Conversion ds le repere du canvas.
        self.x_c, self.y_c = self.map_realcoor2canvas(self.x, self.y)
        # On met a  jour les coordonnees (baballe + tige).
        self.canv.coords(self.baballe,
                         self.x_c-(self.size/2),
                         self.y_c-(self.size/2),
                         self.x_c+(self.size/2),
                         self.y_c+(self.size/2))
        self.canv.coords(self.tige, 200, 200, self.x_c, self.y_c)
        # Laisser une trace.
        self.canv.create_line(self.x_c, self.y_c, self.x_c+1,
                              self.y_c+1, fill=self.color_trace)
        # On met a jour la zone de texte.
        self.stringvar_pos_display.set(self.get_pos_displ())
        self.t += self.dt
        # On refait appel a  la methode .move().
        if self.is_moving > 0:
            self.after(20, self.move) # boucle toutes les 20ms

    def start(self):
        """Demarre l'animation.
        """
        self.color_trace = rd.choice(COLORS)
        self.is_moving += 1 # preferable a  is_moving = 1
                            # (1 seul appel de la fct move)
        if self.is_moving == 1:
            self.move()

    def stop(self):
        """Arrete l'animation.
        """
        self.is_moving = 0

def pendulum():
    if __name__ == "__main__":
        """Programme principal.
    
        Instancie la classe principale, donne un titre et lance le gestionnaire
        d'evenements.
            """
        app_pendule = AppliPendule()
        app_pendule.title("Pendule")
        app_pendule.mainloop()

pendulum()