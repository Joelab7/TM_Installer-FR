import os
import sys
import shutil
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import ctypes
import winreg
import tempfile
import webbrowser
from pathlib import Path

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_install_dirs():
    """Retourne tous les répertoires d'installation valides"""
    print("\n[DEBUG] Recherche de tous les répertoires d'installation...")
    
    # Liste des noms de dossiers possibles
    possible_folder_names = ['Telegram Manager(French installer)', 'Telegram Manager', 'TG_MANAGER']
    
    # Liste des emplacements possibles
    possible_paths = []
    
    # Ajouter les chemins pour chaque nom de dossier possible
    for folder_name in possible_folder_names:
        possible_paths.extend([
            # Dossier de téléchargements de l'utilisateur
            os.path.join(os.environ.get('USERPROFILE', ''), 'Downloads', folder_name),
            os.path.join(os.environ.get('USERPROFILE', ''), 'Téléchargements', folder_name),

            # Dossier de téléchargements de l'utilisateur
            os.path.join(os.environ.get('USERPROFILE', ''), 'Downloads', folder_name),
            os.path.join(os.environ.get('USERPROFILE', ''), 'Téléchargements', folder_name),
            
            # Dossier Bureau OneDrive
            os.path.join(os.environ.get('USERPROFILE', ''), 'OneDrive', 'Bureau', folder_name),
            os.path.join(os.environ.get('USERPROFILE', ''), 'OneDrive', 'Desktop', folder_name),
            os.path.join(os.environ.get('ONEDRIVE', ''), 'Bureau', folder_name),
            os.path.join(os.environ.get('ONEDRIVE', ''), 'Desktop', folder_name),
            
            # Autres emplacements standards
            os.path.join(os.environ.get('PUBLIC', ''), 'Desktop'),
            
            # Autres emplacements standards
            os.path.join(os.environ.get('PROGRAMFILES', ''), folder_name),
            os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), folder_name),
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', folder_name),
            os.path.join(os.environ.get('APPDATA', ''), folder_name),
            os.path.join(os.environ.get('USERPROFILE', ''), 'AppData', 'Local', 'Programs', folder_name),
            os.path.join(os.environ.get('USERPROFILE', ''), folder_name)
        ])
    
    found_paths = []
    
    # Vérifier dans le registre Windows
    try:
        print("\n[DEBUG] Vérification du registre Windows...")
        reg_paths = [
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\TelegramManager"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\TelegramManager"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\TelegramManager")
        ]
        
        for root, subkey in reg_paths:
            try:
                with winreg.OpenKey(root, subkey, 0, winreg.KEY_READ | winreg.KEY_WOW64_32KEY) as key:
                    path = winreg.QueryValueEx(key, "InstallLocation")[0]
                    if path and os.path.exists(path) and path not in found_paths:
                        print(f"[DEBUG] Trouvé dans le registre: {path}")
                        found_paths.append(path)
            except WindowsError as e:
                print(f"[DEBUG] Erreur lors de la lecture de la clé {subkey}: {e}")
    except Exception as e:
        print(f"[DEBUG] Erreur lors de la vérification du registre: {e}")
    
    # Vérifier les dossiers possibles
    print("\n[DEBUG] Vérification des dossiers...")
    for path in possible_paths:
        try:
            if os.path.exists(path):
                print(f"[DEBUG] Dossier trouvé: {path}")
                # Vérifier si c'est bien une installation valide
                required_files = ['launch.py', 'setup_installer.py']
                if all(os.path.exists(os.path.join(path, f)) for f in required_files):
                    print(f"[DEBUG] Installation valide détectée dans: {path}")
                    if path not in found_paths:
                        found_paths.append(path)
                else:
                    print(f"[DEBUG] Dossier trouvé mais installation incomplète dans: {path}")
        except Exception as e:
            print(f"[DEBUG] Erreur lors de la vérification de {path}: {e}")
    
    print(f"[DEBUG] {len(found_paths)} répertoire(s) d'installation valide(s) trouvé(s)")
    return found_paths

def get_desktop_shortcut():
    """Trouve le raccourci sur le bureau"""
    print("\n[DEBUG] Recherche du raccourci sur le bureau...")
    
    # Noms possibles du raccourci (avec et sans extension .lnk)
    possible_names = [
        'Telegram Manager',
        'Telegram Manager.lnk',
        'Telegram Manager(French version)',
        'Telegram Manager(French version).lnk',
    ]
    
    # Emplacements possibles du bureau
    desktop_paths = [
        os.path.join(os.environ.get('USERPROFILE', ''), 'Desktop'),
        os.path.join(os.environ.get('PUBLIC', ''), 'Desktop'),
        os.path.join(os.environ.get('USERPROFILE', ''), 'Bureau'),
        os.path.join(os.environ.get('PUBLIC', ''), 'Bureau')
    ]
    
    print("[DEBUG] Emplacements du bureau à vérifier :")
    for path in desktop_paths:
        print(f"  - {path}")
        
        # Vérifier si le chemin existe
        if not os.path.exists(path):
            print(f"    [DEBUG] Le dossier n'existe pas: {path}")
            continue
            
        # Lister tous les fichiers dans le dossier
        try:
            files = os.listdir(path)
            print(f"    [DEBUG] Fichiers trouvés dans {path}:")
            for f in files:
                print(f"      - {f}")
                
                # Vérifier si le fichier correspond à un des noms recherchés
                for name in possible_names:
                    if f.lower() == name.lower() or f.lower() == name.lower() + '.lnk':
                        full_path = os.path.join(path, f)
                        print(f"    [DEBUG] Correspondance trouvée: {full_path}")
                        return full_path
        except Exception as e:
            print(f"    [ERREUR] Impossible de lister les fichiers dans {path}: {e}")
    
    print("[DEBUG] Aucun raccourci correspondant n'a été trouvé dans les dossiers de bureau")
    return None

class UninstallerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Désinstallation de Telegram Manager")
        self.root.geometry("800x600")  # Taille augmentée pour afficher plusieurs chemins
        self.root.resizable(False, False)
        
        # Variables
        self.install_dirs = []  # Liste de tous les dossiers d'installation
        self.desktop_shortcut = ""
        self.uninstall_complete = False
        
        # Style
        self.setup_ui()
        
        # Détecter les composants à désinstaller
        self.detect_components()
    
    def setup_ui(self):
        # Style
        style = ttk.Style()
        style.theme_use('clam')

        # Configuration complète pour fond blanc - tous les éléments
        style.configure('TFrame', background='#FFFFFF')
        style.configure('TLabel', background='#FFFFFF', font=('Segoe UI', 10))
        style.configure('TButton', font=('Segoe UI', 10))
        style.configure('TLabelFrame', background='#FFFFFF')
        style.configure('TLabelFrame.Label', background='#FFFFFF', foreground='#000000')
        style.configure('Horizontal.TProgressbar', background='#4FC3F7', troughcolor='#4FC3F7')
        style.configure('Vertical.TScrollbar', background='#FFFFFF', troughcolor='#FFFFFF')
        style.configure('TScale', background='#FFFFFF')
        style.configure('TRadiobutton', background='#FFFFFF')
        style.configure('TCheckbutton', background='#FFFFFF')
        style.configure('TMenubutton', background='#FFFFFF')

        # Configuration spécifique pour les widgets ttk
        style.configure('TNotebook', background='#FFFFFF')
        style.configure('TNotebook.Tab', background='#FFFFFF')

        # Style personnalisé pour les LabelFrames avec fond blanc
        style.configure('White.TLabelframe', background='#FFFFFF', foreground='#000000')
        style.configure('White.TLabelframe.Label', background='#FFFFFF', foreground='#000000')

        # Forcer le fond de la fenêtre principale
        self.root.configure(bg='#FFFFFF')

        style.configure('Title.TLabel', font=('Segoe UI', 14, 'bold'), background='#FFFFFF')
        style.configure('Status.TLabel', font=('Segoe UI', 9), background='#FFFFFF')
        style.configure('InstallDir.TLabel', font=('Segoe UI', 9), padding=(10, 2, 0, 2), background='#FFFFFF')
        style.configure('InstallDir.TCheckbutton', font=('Segoe UI', 9), background='#FFFFFF')
        
        # Barre de progression
        style.configure("Custom.Horizontal.TProgressbar",
            thickness=20,
            troughcolor='#FFFFFF',  # Fond blanc pur
            background='#4FC3F7',
            troughrelief='flat',
            borderwidth=0,  # Pas de bordure
            lightcolor='#66BB6A',
            darkcolor='#388E3C'
        )
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # En-tête avec couleur bleue
        ttk.Label(
            main_frame, 
            text="Désinstallation de Telegram Manager",
            style='Title.TLabel',
            foreground='#4FC3F7'  # Bleu clair professionnel
        ).pack(pady=(0, 20))
        
        # Section d'information
        info_frame = ttk.LabelFrame(main_frame, text="Composants à désinstaller", padding=10)
        info_frame.pack(fill=tk.X, pady=10, padx=5)
        
        # Forcer le fond blanc pour le LabelFrame
        info_frame.configure(style='White.TLabelframe')
        
        # Frame pour les dossiers d'installation avec une bordure et un fond
        self.dirs_frame = ttk.LabelFrame(info_frame, text="Dossiers d'installation détectés", padding=10)
        self.dirs_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Forcer le fond blanc pour ce LabelFrame aussi
        self.dirs_frame.configure(style='White.TLabelframe')
        
        # Label pour indiquer la détection en cours
        self.dirs_label = ttk.Label(
            self.dirs_frame, 
            text="Détection des dossiers d'installation en cours...",
            style='Status.TLabel',
            wraplength=600
        )
        self.dirs_label.pack(fill=tk.X, pady=5)
        
        # Frame pour contenir les cases à cocher des dossiers
        self.dirs_checkboxes_frame = ttk.Frame(self.dirs_frame)
        self.dirs_checkboxes_frame.pack(fill=tk.X, pady=5)
        
        # Dictionnaire pour stocker les variables des cases à cocher
        self.dir_vars = {}
        
        # Section pour le raccourci sur le bureau
        self.shortcut_frame = ttk.Frame(info_frame)
        self.shortcut_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.shortcut_label = ttk.Label(
            self.shortcut_frame, 
            text="Raccourci sur le bureau : Non détecté",
            style='Status.TLabel'
        )
        self.shortcut_label.pack(anchor='w', pady=2)
        
        # Barre de progression
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=(20, 10))
        
        self.progress = ttk.Progressbar(
            progress_frame,
            orient=tk.HORIZONTAL,
            length=400,
            mode='determinate',
            style="Custom.Horizontal.TProgressbar"
        )
        self.progress.pack(fill=tk.X, expand=True, pady=5)
        
        # Statut avec couleur bleue
        self.status_var = tk.StringVar(value="Prêt à désinstaller")
        status_label = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            style='Status.TLabel',
            wraplength=600,
            foreground='#4FC3F7'  # Bleu clair pour le texte de statut
        )
        status_label.pack(pady=(0, 20))
        
        # Boutons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)
        
        self.uninstall_btn = ttk.Button(
            btn_frame,
            text="Désinstaller",
            command=self.start_uninstall,
            style='Accent.TButton'
        )
        self.uninstall_btn.pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Annuler",
            command=self.root.quit
        ).pack(side=tk.RIGHT)
        
        # Style pour les boutons modernes bleus
        style.configure('Accent.TButton',
                           font=('Segoe UI', 10, 'bold'),
                           background='#1976D2',  # Bleu moderne pour le bouton principal
                           foreground='white')

        style.map('Accent.TButton',
                      background=[('active', '#2196F3'),  # Bleu plus clair au survol
                                 ('pressed', '#0D47A1')], # Bleu foncé quand pressé
                      relief=[('pressed', 'sunken'), ('!pressed', 'raised')])

        style.configure('TButton',
                           font=('Segoe UI', 10),
                           background='#1976D2',  # Bleu moderne
                           foreground='white')
        style.map('TButton',
                      background=[('active', '#42A5F5'),  # Bleu au survol
                                 ('pressed', '#1E88E5')])  # Bleu plus foncé quand pressé
    
    def detect_components(self):
        """Détecte les composants à désinstaller"""
        print("\n[DEBUG] Détection des composants à désinstaller...")
        
        # Détecter les répertoires d'installation
        self.install_dirs = get_install_dirs()
        
        # Mettre à jour l'interface avec les dossiers trouvés
        self.update_dirs_ui()
        
        # Détecter le raccourci sur le bureau
        self.desktop_shortcut = get_desktop_shortcut()
        if self.desktop_shortcut:
            print(f"[DEBUG] Raccourci détecté: {self.desktop_shortcut}")
            self.shortcut_label.config(
                text=f"Raccourci sur le bureau : {os.path.basename(self.desktop_shortcut)}",
                foreground='#4FC3F7'  # Bleu au lieu de vert/rouge
            )
        else:
            print("[DEBUG] Aucun raccourci trouvé sur le bureau")
            self.shortcut_label.config(
                text="Raccourci sur le bureau : Non détecté (peut déjà être supprimé)",
                foreground='#4FC3F7'  # Bleu au lieu d'orange
            )
        
        # Mettre à jour l'état du bouton de désinstallation
        if not self.install_dirs and not self.desktop_shortcut:
            self.uninstall_btn.config(state=tk.DISABLED)
            self.status_var.set(
                "Aucun composant de Telegram Manager n'a été trouvé sur ce système. "
                "L'application est peut-être déjà désinstallée."
            )
        else:
            self.uninstall_btn.config(state=tk.NORMAL)
            self.status_var.set("Sélectionnez les composants à désinstaller")
    
    def update_dirs_ui(self):
        """Met à jour l'interface avec les dossiers d'installation détectés"""
        # Effacer les widgets existants
        for widget in self.dirs_checkboxes_frame.winfo_children():
            widget.destroy()
        
        self.dir_vars = {}
        
        if not self.install_dirs:
            self.dirs_label.config(
                text="Aucun dossier d'installation trouvé (peut déjà être désinstallé)",
                foreground='#4FC3F7'  # Bleu au lieu d'orange
            )
            return
        
        self.dirs_label.config(
            text="Cochez les dossiers à supprimer :",
            foreground='black'
        )
        
        # Ajouter une case à cocher pour chaque dossier
        for i, dir_path in enumerate(self.install_dirs):
            var = tk.BooleanVar(value=True)
            self.dir_vars[dir_path] = var
            
            # Créer un cadre pour chaque entrée de dossier
            dir_frame = ttk.Frame(self.dirs_checkboxes_frame)
            dir_frame.pack(fill=tk.X, pady=2)
            
            # Case à cocher
            cb = ttk.Checkbutton(
                dir_frame,
                variable=var,
                style='InstallDir.TCheckbutton'
            )
            cb.pack(side=tk.LEFT)
            
            # Label avec le chemin du dossier
            label = ttk.Label(
                dir_frame,
                text=dir_path,
                style='InstallDir.TLabel',
                foreground='#4FC3F7'  # Bleu au lieu de vert/rouge
            )
            label.pack(side=tk.LEFT, fill=tk.X, expand=True, anchor='w')
            
            # Bouton pour ouvrir l'explorateur
            btn = ttk.Button(
                dir_frame,
                text="Ouvrir",
                command=lambda p=dir_path: os.startfile(os.path.dirname(p)) if os.path.exists(p) else None,
                width=8
            )
            btn.pack(side=tk.RIGHT, padx=(5, 0))
    
    def get_selected_dirs(self):
        """Retourne la liste des dossiers sélectionnés pour la suppression"""
        return [path for path, var in self.dir_vars.items() if var.get()]
    
    def update_status(self, message, progress=None):
        """Met à jour le statut et la barre de progression"""
        self.status_var.set(message)
        if progress is not None:
            self.progress['value'] = progress
        self.root.update_idletasks()
    
    def start_uninstall(self):
        """Démarre le processus de désinstallation"""
        self.uninstall_btn.config(state=tk.DISABLED)
        self.root.after(100, self.run_uninstall)
    
    def run_uninstall(self):
        """Exécute la désinstallation"""
        try:
            # Étape 1: Supprimer le raccourci du bureau
            if self.desktop_shortcut and os.path.exists(self.desktop_shortcut):
                self.update_status("Suppression du raccourci sur le bureau...", 10)
                try:
                    os.remove(self.desktop_shortcut)
                except Exception as e:
                    self.update_status(f"Avertissement: Impossible de supprimer le raccourci: {e}")
            
            # Étape 2: Supprimer les répertoires d'installation sélectionnés
            selected_dirs = self.get_selected_dirs()
            total_dirs = len(selected_dirs)
            
            if total_dirs > 0:
                for i, install_dir in enumerate(selected_dirs, 1):
                    progress = 10 + int((i / (total_dirs + 1)) * 80)  # 10-90% pour la suppression des dossiers
                    self.update_status(f"Suppression du dossier d'installation ({i}/{total_dirs}): {install_dir}", progress)
                    
                    if not os.path.exists(install_dir):
                        self.update_status(f"Le dossier {install_dir} n'existe plus.", progress)
                        continue
                    
                    max_attempts = 3
                    deleted = False
                    
                    for attempt in range(max_attempts):
                        try:
                            # Première tentative de suppression normale
                            shutil.rmtree(install_dir, ignore_errors=True)
                            
                            # Vérifier si le dossier a été supprimé
                            if not os.path.exists(install_dir):
                                deleted = True
                                break
                                
                            # Si le dossier existe encore, forcer la suppression des fichiers/dossiers en lecture seule
                            if attempt == 0:
                                self.update_status("Nettoyage des fichiers en lecture seule...", progress)
                                for root, dirs, files in os.walk(install_dir, topdown=False):
                                    for name in files:
                                        file_path = os.path.join(root, name)
                                        try:
                                            os.chmod(file_path, 0o777)  # Donner tous les droits
                                            os.unlink(file_path)  # Supprimer le fichier
                                        except Exception as e:
                                            print(f"Impossible de supprimer {file_path}: {e}")
                                    
                                    for name in dirs:
                                        dir_path = os.path.join(root, name)
                                        try:
                                            os.chmod(dir_path, 0o777)  # Donner tous les droits
                                            os.rmdir(dir_path)  # Supprimer le dossier vide
                                        except Exception as e:
                                            print(f"Impossible de supprimer le dossier {dir_path}: {e}")
                            
                            # Dernière tentative avec suppression forcée
                            if attempt == max_attempts - 1 and os.path.exists(install_dir):
                                try:
                                    # Utiliser rmdir /s /q en tant que dernière tentative
                                    subprocess.run(f'rmdir /s /q "{install_dir}"', 
                                                 shell=True, check=True, timeout=30)
                                    deleted = True
                                except subprocess.SubprocessError as e:
                                    print(f"Échec de la suppression via subprocess: {e}")
                            
                        except Exception as e:
                            self.update_status(f"Tentative {attempt + 1}/{max_attempts} échouée: {e}")
                            if attempt < max_attempts - 1:
                                import time
                                time.sleep(1)  # Attendre avant de réessayer
                    
                    if not deleted and os.path.exists(install_dir):
                        # Si le dossier existe toujours, planifier sa suppression au prochain démarrage
                        try:
                            import win32api
                            import win32con
                            import win32file
                            
                            move_file = f"{install_dir}.old"
                            if os.path.exists(move_file):
                                shutil.rmtree(move_file, ignore_errors=True)
                                
                            # Essayer de renommer le dossier
                            try:
                                os.rename(install_dir, move_file)
                                install_dir = move_file
                            except:
                                pass
                                
                            # Planifier la suppression au prochain démarrage
                            bat_path = os.path.join(os.path.dirname(sys.executable), f"delete_old_install_{i}.bat")
                            with open(bat_path, 'w') as f:
                                f.write(f"@echo off\n")
                                f.write(f"timeout /t 5 /nobreak >nul\n")
                                f.write(f"rmdir /s /q \"{os.path.abspath(install_dir)}\"\n")
                                f.write(f"del /f /q \"{bat_path}\"\n")
                            
                            # Ajouter une clé de registre pour exécuter le script au démarrage
                            try:
                                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                                  r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce",
                                                  0, winreg.KEY_SET_VALUE)
                                winreg.SetValueEx(key, f"DeleteOldInstall_{i}", 0, winreg.REG_SZ, f'"{bat_path}"')
                                winreg.CloseKey(key)
                                self.update_status("Le nettoyage final sera effectué au prochain démarrage.", progress)
                            except Exception as e:
                                print(f"Impossible de planifier la suppression: {e}")
                                raise Exception(f"Impossible de supprimer le dossier d'installation. Veuillez redémarrer votre ordinateur et supprimer manuellement le dossier: {install_dir}")
                        except Exception as e:
                            print(f"Erreur lors de la planification de la suppression: {e}")
                            raise Exception(f"Impossible de supprimer le dossier d'installation. Veuillez redémarrer votre ordinateur et supprimer manuellement le dossier: {install_dir}")
            
            # Étape 3: Nettoyer le registre
            self.update_status("Nettoyage du registre...", 95)
            try:
                # Supprimer la clé de désinstallation
                try:
                    winreg.DeleteKey(winreg.HKEY_CURRENT_USER, 
                                   r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\TelegramManager")
                except WindowsError:
                    pass
                
                # Essayer en tant qu'administrateur si possible
                if is_admin():
                    try:
                        winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE, 
                                       r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\TelegramManager")
                    except WindowsError:
                        pass
                    try:
                        winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE, 
                                       r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\TelegramManager")
                    except WindowsError:
                        pass
            except Exception as e:
                self.update_status(f"Avertissement: Impossible de nettoyer le registre: {e}")
            
            # Terminé
            self.update_status("Désinstallation terminée avec succès!", 100)
            self.uninstall_complete = True
            
            # Changer le bouton pour quitter
            self.uninstall_btn.config(
                text="Terminer",
                command=self.root.quit,
                state=tk.NORMAL
            )
            
            # Afficher un message de confirmation
            messagebox.showinfo(
                "Désinstallation terminée",
                "Telegram Manager a été désinstallé avec succès de votre ordinateur."
            )
            
        except Exception as e:
            self.update_status(f"Erreur lors de la désinstallation: {str(e)}")
            messagebox.showerror(
                "Erreur",
                f"Une erreur est survenue lors de la désinstallation: {str(e)}"
            )
            self.uninstall_btn.config(state=tk.NORMAL)

def main():
    # Vérifier les droits administrateur
    if not is_admin():
        # Relancer avec élévation des privilèges
        try:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " \"" + os.path.abspath(__file__) + "\"", None, 1
            )
            sys.exit(0)
        except Exception as e:
            messagebox.showerror(
                "Erreur",
                "Impossible d'obtenir les privilèges administrateur. "
                "Certains éléments ne pourront pas être supprimés."
            )
    
    # Lancer l'interface graphique
    root = tk.Tk()
    app = UninstallerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
