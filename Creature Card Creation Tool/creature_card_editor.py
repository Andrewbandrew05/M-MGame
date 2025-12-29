import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import sys
import shutil
from pathlib import Path

# Add parent directory to path to import creature_card module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Creature Card Definitions'))
from creature_card import CreatureCard, Attack, ENERGY_TYPES


class AttackFrame(ttk.LabelFrame):
    """Frame for editing a single attack."""
    
    def __init__(self, parent, attack=None, on_remove=None):
        super().__init__(parent, text="Attack", padding=10)
        self.on_remove = on_remove
        self.attack = attack or Attack("", 0, "")
        
        # Attack name
        ttk.Label(self, text="Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.name_var = tk.StringVar(value=self.attack.name)
        ttk.Entry(self, textvariable=self.name_var, width=25).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        # Attack damage
        ttk.Label(self, text="Damage:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.damage_var = tk.StringVar(value=str(self.attack.damage))
        ttk.Entry(self, textvariable=self.damage_var, width=10).grid(row=0, column=3, sticky="ew", padx=5, pady=5)
        
        # Remove button
        ttk.Button(self, text="Remove", command=self._on_remove).grid(row=0, column=4, padx=5, pady=5)
        
        # Attack description (full width on second row)
        ttk.Label(self, text="Description:").grid(row=1, column=0, sticky="nw", padx=5, pady=5)
        self.desc_var = tk.StringVar(value=self.attack.description)
        ttk.Entry(self, textvariable=self.desc_var, width=80).grid(row=1, column=1, columnspan=4, sticky="ew", padx=5, pady=5)
        
        # Energy costs frame
        energy_frame = ttk.LabelFrame(self, text="Energy Costs", padding=5)
        energy_frame.grid(row=2, column=0, columnspan=5, sticky="ew", padx=5, pady=10)
        
        self.energy_vars = {}
        for i, energy_type in enumerate(ENERGY_TYPES):
            ttk.Label(energy_frame, text=f"{energy_type}:").grid(row=0, column=i, padx=5, pady=5)
            self.energy_vars[energy_type] = tk.StringVar(
                value=str(self.attack.energy_costs.get(energy_type, 0))
            )
            ttk.Entry(energy_frame, textvariable=self.energy_vars[energy_type], width=5).grid(
                row=1, column=i, padx=5, pady=5
            )
        
        self.columnconfigure(1, weight=1)
    
    def _on_remove(self):
        if self.on_remove:
            self.on_remove(self)
    
    def get_attack(self) -> Attack:
        """Get the attack object from the current values."""
        try:
            damage = int(self.damage_var.get())
            energy_costs = {
                energy_type: int(self.energy_vars[energy_type].get())
                for energy_type in ENERGY_TYPES
            }
        except ValueError:
            raise ValueError("Damage and Energy Costs must be valid integers")
        
        return Attack(
            name=self.name_var.get(),
            damage=damage,
            description=self.desc_var.get(),
            energy_costs=energy_costs
        )


class CreatureCardEditor(tk.Tk):
    """Main application window for creating creature cards."""
    
    def __init__(self):
        super().__init__()
        self.title("Creature Card Creator")
        self.geometry("900x700")
        
        # Current creature being edited
        self.current_creature = None
        self.attack_frames = []
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create all the GUI widgets."""
        # Top frame for basic creature info
        info_frame = ttk.LabelFrame(self, text="Creature Information", padding=10)
        info_frame.pack(fill="x", padx=10, pady=10)
        
        # Name
        ttk.Label(info_frame, text="Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.name_var, width=40).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        # Description
        ttk.Label(info_frame, text="Description:").grid(row=1, column=0, sticky="nw", padx=5, pady=5)
        self.desc_text = tk.Text(info_frame, height=4, width=40)
        self.desc_text.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        # Health
        ttk.Label(info_frame, text="Health:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.health_var = tk.StringVar(value="100")
        ttk.Entry(info_frame, textvariable=self.health_var, width=10).grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        # Type
        ttk.Label(info_frame, text="Type:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.type_var = tk.StringVar()
        type_combo = ttk.Combobox(info_frame, textvariable=self.type_var, 
                                   values=["Power", "Fire", "Toxic", "Shadow", "Water"],
                                   width=37)
        type_combo.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        
        # Creature Class
        ttk.Label(info_frame, text="Class:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.class_var = tk.StringVar()
        class_combo = ttk.Combobox(info_frame, textvariable=self.class_var, 
                                    values=["Land Beast", "Sea Monster", "Air Creature", "Fairy"],
                                    width=37)
        class_combo.grid(row=4, column=1, sticky="ew", padx=5, pady=5)
        
        # Titan checkbox
        ttk.Label(info_frame, text="Titan:").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        self.titan_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(info_frame, variable=self.titan_var).grid(row=5, column=1, sticky="w", padx=5, pady=5)
        
        # Creature Art
        ttk.Label(info_frame, text="Art:").grid(row=6, column=0, sticky="w", padx=5, pady=5)
        art_frame = ttk.Frame(info_frame)
        art_frame.grid(row=6, column=1, sticky="ew", padx=5, pady=5)
        self.art_var = tk.StringVar()
        ttk.Entry(art_frame, textvariable=self.art_var, width=30).pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(art_frame, text="Browse", command=self._browse_image).pack(side="left", padx=5)
        
        info_frame.columnconfigure(1, weight=1)
        
        # Attacks frame
        attacks_frame = ttk.LabelFrame(self, text="Attacks", padding=10)
        attacks_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Button to add attacks (before scrollable area)
        ttk.Button(attacks_frame, text="+ Add New Attack", command=self._add_attack).pack(fill="x", padx=5, pady=5)
        
        # Scrollable frame for attacks
        self.attacks_canvas = tk.Canvas(attacks_frame, height=200)
        scrollbar = ttk.Scrollbar(attacks_frame, orient="vertical", command=self.attacks_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.attacks_canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.attacks_canvas.configure(scrollregion=self.attacks_canvas.bbox("all"))
        )
        
        self.attacks_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.attacks_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.attacks_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Button frame
        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(button_frame, text="Save to File", command=self._save_to_file).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Load from File", command=self._load_from_file).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Export JSON", command=self._export_json).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Export to Folder", command=self._export_to_folder).pack(side="left", padx=5)
        ttk.Button(button_frame, text="New Card", command=self._new_card).pack(side="left", padx=5)
    
    def _add_attack(self):
        """Add a new attack frame."""
        attack_frame = AttackFrame(self.scrollable_frame, on_remove=self._remove_attack)
        attack_frame.pack(fill="x", padx=5, pady=5)
        self.attack_frames.append(attack_frame)
    
    def _remove_attack(self, frame):
        """Remove an attack frame."""
        self.attack_frames.remove(frame)
        frame.destroy()
    
    def _browse_image(self):
        """Open a file dialog to select an image."""
        file_path = filedialog.askopenfilename(
            title="Select Creature Art",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"), ("All files", "*.*")]
        )
        if file_path:
            self.art_var.set(file_path)
    
    def _get_creature_from_input(self) -> CreatureCard:
        """Extract creature card data from the GUI inputs."""
        name = self.name_var.get().strip()
        if not name:
            raise ValueError("Name cannot be empty")
        
        description = self.desc_text.get("1.0", "end-1c").strip()
        
        try:
            health = int(self.health_var.get())
        except ValueError:
            raise ValueError("Health must be a valid integer")
        
        creature_type = self.type_var.get().strip()
        if not creature_type:
            raise ValueError("Type cannot be empty")
        
        creature_class = self.class_var.get().strip()
        if not creature_class:
            raise ValueError("Class cannot be empty")
        
        # Collect attacks
        attacks = []
        for attack_frame in self.attack_frames:
            if attack_frame.name_var.get().strip():  # Only include non-empty attacks
                attacks.append(attack_frame.get_attack())
        
        return CreatureCard(
            name=name,
            description=description,
            health=health,
            type=creature_type,
            creature_class=creature_class,
            is_titan=self.titan_var.get(),
            image_path=self.art_var.get(),
            attacks=attacks
        )
    
    def _load_creature_into_gui(self, creature: CreatureCard):
        """Load a creature card's data into the GUI."""
        self.name_var.set(creature.name)
        self.desc_text.delete("1.0", "end")
        self.desc_text.insert("1.0", creature.description)
        self.health_var.set(str(creature.health))
        self.type_var.set(creature.type)
        self.class_var.set(creature.creature_class)
        self.titan_var.set(creature.is_titan)
        self.art_var.set(creature.image_path)
        
        # Clear existing attack frames
        for frame in self.attack_frames:
            frame.destroy()
        self.attack_frames.clear()
        
        # Add attack frames
        for attack in creature.attacks:
            attack_frame = AttackFrame(self.scrollable_frame, attack=attack, on_remove=self._remove_attack)
            attack_frame.pack(fill="x", padx=5, pady=5)
            self.attack_frames.append(attack_frame)
    
    def _save_to_file(self):
        """Save the current creature card to a JSON file."""
        try:
            creature = self._get_creature_from_input()
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialfile=f"{creature.name.replace(' ', '_')}.json"
            )
            
            if file_path:
                with open(file_path, 'w') as f:
                    f.write(creature.to_json())
                messagebox.showinfo("Success", f"Card saved to {file_path}")
        
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {str(e)}")
    
    def _load_from_file(self):
        """Load a creature card from a JSON file."""
        try:
            file_path = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if file_path:
                with open(file_path, 'r') as f:
                    json_content = f.read()
                
                creature = CreatureCard.from_json(json_content)
                self._load_creature_into_gui(creature)
                messagebox.showinfo("Success", f"Card loaded from {file_path}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load: {str(e)}")
    
    def _export_json(self):
        """Display the JSON representation of the current creature."""
        try:
            creature = self._get_creature_from_input()
            
            # Create a new window to display JSON
            json_window = tk.Toplevel(self)
            json_window.title(f"{creature.name} - JSON Export")
            json_window.geometry("600x500")
            
            # Text widget with scrollbar
            frame = ttk.Frame(json_window)
            frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            scrollbar = ttk.Scrollbar(frame)
            text_widget = tk.Text(frame, wrap="word", yscrollcommand=scrollbar.set)
            scrollbar.config(command=text_widget.yview)
            
            text_widget.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            text_widget.insert("1.0", creature.to_json())
            text_widget.config(state="disabled")
            
            # Copy button
            ttk.Button(json_window, text="Copy to Clipboard", 
                      command=lambda: self._copy_to_clipboard(creature.to_json())).pack(padx=10, pady=5)
        
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
    
    def _copy_to_clipboard(self, text):
        """Copy text to clipboard."""
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Success", "JSON copied to clipboard")
    
    def _export_to_folder(self):
        """Export creature card to a folder with JSON and image."""
        try:
            creature = self._get_creature_from_input()
            
            # Create folder name
            folder_name = f"Creature_{creature.name.replace(' ', '_')}"
            folder_path = os.path.join(os.getcwd(), folder_name)
            
            # Check if folder already exists
            if os.path.exists(folder_path):
                response = messagebox.askyesno(
                    "Folder Exists",
                    f"Folder '{folder_name}' already exists. Overwrite?"
                )
                if not response:
                    return
                shutil.rmtree(folder_path)
            
            # Create the folder
            os.makedirs(folder_path)
            
            # Save JSON file
            json_path = os.path.join(folder_path, "creature.json")
            with open(json_path, 'w') as f:
                f.write(creature.to_json())
            
            # Copy image if provided
            if creature.image_path and os.path.exists(creature.image_path):
                image_filename = os.path.basename(creature.image_path)
                image_dest = os.path.join(folder_path, image_filename)
                shutil.copy2(creature.image_path, image_dest)
                messagebox.showinfo(
                    "Success",
                    f"Creature exported to '{folder_name}'\nIncluded: creature.json and {image_filename}"
                )
            else:
                messagebox.showinfo(
                    "Success",
                    f"Creature exported to '{folder_name}'\nIncluded: creature.json\n(No image file selected)"
                )
        
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {str(e)}")
    
    def _new_card(self):
        """Clear the form to create a new card."""
        self.name_var.set("")
        self.desc_text.delete("1.0", "end")
        self.health_var.set("100")
        self.type_var.set("")
        self.class_var.set("")
        self.titan_var.set(False)
        self.art_var.set("")
        
        for frame in self.attack_frames:
            frame.destroy()
        self.attack_frames.clear()


if __name__ == "__main__":
    app = CreatureCardEditor()
    app.mainloop()
